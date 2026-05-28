from sqlalchemy.orm import Session

from models.incident import IncidentModel
from schemas.incident_schema import Incident
from models.patient import PatientModel


class IncidentService:
    @staticmethod
    def create_incident(db: Session, incident: Incident) -> IncidentModel:
        # Avoid creating duplicate incidents with same name and location
        existing = (
            db.query(IncidentModel)
            .filter(IncidentModel.name == incident.name)
            .filter(IncidentModel.location == incident.location)
            .first()
        )
        if existing:
            return existing

        db_incident = IncidentModel(name=incident.name, location=incident.location)
        db.add(db_incident)
        db.commit()
        db.refresh(db_incident)
        return db_incident

    @staticmethod
    def list_incidents(db: Session) -> list[dict]:
        incidents = db.query(IncidentModel).all()
        if not incidents:
            return []

        dashboard_incidents = []
        for incident in incidents:
            patients = [
                {
                    "id": p.id,
                    "triage_tag": p.triage_tag,
                    "status": p.status,
                    "can_walk": p.can_walk,
                    "breathing": p.breathing,
                    "airway_opened": p.airway_opened,
                    "resp_rate": p.resp_rate,
                    "radial_pulse": p.radial_pulse,
                    "cap_refill": p.cap_refill,
                    "follows_commands": p.follows_commands,
                }
                for p in db.query(PatientModel).filter(PatientModel.incident_id == incident.id).all()
            ]

            dashboard_incidents.append(
                {
                    "id": incident.id,
                    "name": incident.name,
                    "location": incident.location,
                    "patient_count": len(patients),
                    "patients": patients,
                }
            )

        return dashboard_incidents

    @staticmethod
    def get_incident_by_id(db: Session, incident_id: int) -> IncidentModel | None:
        return db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()

    @staticmethod
    def get_incident_dashboard(db: Session, incident_id: int) -> dict | None:
        incident = db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
        if incident is None:
            return None

        patients = [
            {
                "id": p.id,
                "triage_tag": p.triage_tag,
                "status": p.status,
                "can_walk": p.can_walk,
                "breathing": p.breathing,
                "airway_opened": p.airway_opened,
                "resp_rate": p.resp_rate,
                "radial_pulse": p.radial_pulse,
                "cap_refill": p.cap_refill,
                "follows_commands": p.follows_commands,
            }
            for p in db.query(PatientModel).filter(PatientModel.incident_id == incident.id).all()
        ]

        priority = {"RED": 1, "YELLOW": 2, "GREEN": 3, "BLACK": 4}
        patients.sort(key=lambda patient: priority.get(patient["triage_tag"], 99))
        red_count = sum(1 for patient in patients if patient["triage_tag"] == "RED")
        yellow_count = sum(1 for patient in patients if patient["triage_tag"] == "YELLOW")
        green_count = sum(1 for patient in patients if patient["triage_tag"] == "GREEN")
        black_count = sum(1 for patient in patients if patient["triage_tag"] == "BLACK")

        return {
            "id": incident.id,
            "name": incident.name,
            "location": incident.location,
            "total_patients": len(patients),
            "red_count": red_count,
            "yellow_count": yellow_count,
            "green_count": green_count,
            "black_count": black_count,
            "patients": patients,
        }
