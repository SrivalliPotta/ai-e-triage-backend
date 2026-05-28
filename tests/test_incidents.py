import importlib
import os
import sys

from fastapi.testclient import TestClient


def load_app(tmp_path):
    db_path = tmp_path / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ.pop("MYSQL_PASSWORD", None)

    prefixes = ("database", "models", "services", "agents", "events", "api", "websocket", "ai", "core")
    for module_name in list(sys.modules):
        if module_name == "main" or module_name.startswith(prefixes):
            del sys.modules[module_name]

    main_module = importlib.import_module("main")
    return importlib.reload(main_module)


def login_client(client):
    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "admin123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_create_incident_and_attach_patient_to_incident(tmp_path):
    main_module = load_app(tmp_path)
    client = TestClient(main_module.app)

    token = login_client(client)
    incident_response = client.post(
        "/incidents",
        json={
            "name": "Engine Room Explosion",
            "location": "Atlantic Vessel",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert incident_response.status_code == 200
    incident_data = incident_response.json()
    assert incident_data["name"] == "Engine Room Explosion"
    assert incident_data["location"] == "Atlantic Vessel"
    assert incident_data["id"] > 0

    triage_response = client.post(
        f"/triage/{incident_data['id']}",
        json={
            "can_walk": True,
            "breathing": True,
            "airway_opened": True,
            "resp_rate": 18,
            "radial_pulse": True,
            "cap_refill": 1.5,
            "follows_commands": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert triage_response.status_code == 200
    assert triage_response.json()["triage_tag"] == "GREEN"

    db = main_module.SessionLocal()
    try:
        patient = db.query(main_module.PatientModel).first()
        assert patient is not None
        assert patient.incident_id == incident_data["id"]
        assert patient.triage_tag == "GREEN"
    finally:
        db.close()


def test_triage_requires_existing_incident(tmp_path):
    main_module = load_app(tmp_path)
    client = TestClient(main_module.app)

    token = login_client(client)
    response = client.post(
        "/triage/999",
        json={
            "can_walk": True,
            "breathing": True,
            "airway_opened": True,
            "resp_rate": 18,
            "radial_pulse": True,
            "cap_refill": 1.5,
            "follows_commands": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_get_incidents_dashboard_returns_incident_and_patients(tmp_path):
    main_module = load_app(tmp_path)
    client = TestClient(main_module.app)

    token = login_client(client)
    incident_response = client.post(
        "/incidents",
        json={
            "name": "Engine Room Explosion",
            "location": "Atlantic Vessel",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert incident_response.status_code == 200

    triage_response = client.post(
        f"/triage/{incident_response.json()['id']}",
        json={
            "can_walk": False,
            "breathing": True,
            "airway_opened": True,
            "resp_rate": 22,
            "radial_pulse": True,
            "cap_refill": 1.2,
            "follows_commands": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert triage_response.status_code == 200

    dashboard_response = client.get("/incidents", headers={"Authorization": f"Bearer {token}"})

    assert dashboard_response.status_code == 200
    incidents = dashboard_response.json()
    assert len(incidents) == 1
    assert incidents[0]["name"] == "Engine Room Explosion"
    assert incidents[0]["patient_count"] == 1
    assert incidents[0]["patients"][0]["triage_tag"] == "YELLOW"


def test_get_incident_dashboard_summary_returns_counts(tmp_path):
    main_module = load_app(tmp_path)
    client = TestClient(main_module.app)

    token = login_client(client)
    incident_response = client.post(
        "/incidents",
        json={
            "name": "Bridge Fire",
            "location": "Deck 3",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert incident_response.status_code == 200
    incident_id = incident_response.json()["id"]

    db = main_module.SessionLocal()
    try:
        db.add_all(
            [
                main_module.PatientModel(
                    incident_id=incident_id,
                    triage_tag="RED",
                    can_walk=False,
                    breathing=True,
                    airway_opened=True,
                    resp_rate=35,
                    radial_pulse=True,
                    cap_refill=1,
                    follows_commands=True,
                ),
                main_module.PatientModel(
                    incident_id=incident_id,
                    triage_tag="YELLOW",
                    can_walk=False,
                    breathing=True,
                    airway_opened=True,
                    resp_rate=22,
                    radial_pulse=True,
                    cap_refill=1,
                    follows_commands=True,
                ),
                main_module.PatientModel(
                    incident_id=incident_id,
                    triage_tag="GREEN",
                    can_walk=True,
                    breathing=True,
                    airway_opened=True,
                    resp_rate=18,
                    radial_pulse=True,
                    cap_refill=1,
                    follows_commands=True,
                ),
                main_module.PatientModel(
                    incident_id=incident_id,
                    triage_tag="BLACK",
                    can_walk=False,
                    breathing=False,
                    airway_opened=False,
                    resp_rate=0,
                    radial_pulse=False,
                    cap_refill=3,
                    follows_commands=False,
                ),
            ]
        )
        db.commit()
    finally:
        db.close()

    dashboard_response = client.get(f"/incidents/{incident_id}/dashboard", headers={"Authorization": f"Bearer {token}"})

    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.json()
    assert dashboard["id"] == incident_id
    assert dashboard["name"] == "Bridge Fire"
    assert dashboard["location"] == "Deck 3"
    assert dashboard["total_patients"] == 4
    assert dashboard["red_count"] == 1
    assert dashboard["yellow_count"] == 1
    assert dashboard["green_count"] == 1
    assert dashboard["black_count"] == 1
    assert sorted(patient["triage_tag"] for patient in dashboard["patients"]) == ["BLACK", "GREEN", "RED", "YELLOW"]
