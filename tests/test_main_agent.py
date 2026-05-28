import asyncio
from types import SimpleNamespace

from agents.main_agent.agent import MainAgent


class DummyClinicalAgent:
    def __init__(self):
        self.calls = []

    def classify(self, patient):
        self.calls.append({"patient": patient})
        return ("RED", "HIGH")


class DummyOperationsAgent:
    def __init__(self):
        self.calls = []

    def allocate_resources(self, incident_id: int, risk_level: str):
        self.calls.append({"incident_id": incident_id, "risk_level": risk_level})
        return {
            "incident_id": incident_id,
            "risk_level": risk_level,
            "resources": ["ambulance", "emergency_response_team"],
            "status": "RESOURCES_RESERVED",
            "agent": "operations_agent",
            "role": "operations",
        }


class DummyTriageService:
    def __init__(self):
        self.calls = []

    def save_patient(self, db, incident_id, patient, triage_tag):
        self.calls.append({
            "incident_id": incident_id,
            "triage_tag": triage_tag,
        })
        return SimpleNamespace(id=42, triage_tag=triage_tag, status="NEW")


class DummyWorkflowService:
    def __init__(self):
        self.calls = []

    def transition_patient(self, db, patient, target_status, message=None):
        self.calls.append({
            "patient_id": patient.id,
            "target_status": target_status,
            "message": message,
        })
        patient.status = target_status
        return patient


class DummyAIService:
    def __init__(self):
        self.calls = []

    def summarize_incident(self, payload):
        self.calls.append(payload)
        return "Incident summary generated"


class DummyEventBus:
    def __init__(self):
        self.calls = []

    async def publish(self, topic, payload):
        self.calls.append({"topic": topic, "payload": payload})


class DummyBroadcastManager:
    def __init__(self):
        self.calls = []

    async def broadcast(self, payload):
        self.calls.append(payload)


def test_main_agent_delegates_to_clinical_and_operations_roles():
    clinical_agent = DummyClinicalAgent()
    operations_agent = DummyOperationsAgent()
    triage_service = DummyTriageService()
    workflow_service = DummyWorkflowService()
    ai_service = DummyAIService()
    event_bus = DummyEventBus()
    broadcaster = DummyBroadcastManager()

    main_agent = MainAgent(
        clinical_agent=clinical_agent,
        operations_agent=operations_agent,
        triage_service=triage_service,
        workflow_service=workflow_service,
        ai_service=ai_service,
        event_bus=event_bus,
    )

    import agents.main_agent.agent as main_agent_module

    original_manager = main_agent_module.manager
    try:
        main_agent_module.manager = broadcaster

        async def run():
            patient = SimpleNamespace(can_walk=False, breathing=True, airway_opened=True, resp_rate=35, radial_pulse=True, cap_refill=1.2, follows_commands=True)
            result = await main_agent.process_triage(object(), 77, patient)
            assert result.id == 42
            assert result.triage_tag == "RED"
            assert result.status == "TRIAGED"

            assert clinical_agent.calls == [{"patient": patient}]
            assert operations_agent.calls == [{"incident_id": 77, "risk_level": "HIGH"}]
            assert triage_service.calls == [{"incident_id": 77, "triage_tag": "RED"}]
            assert workflow_service.calls == [{
                "patient_id": 42,
                "target_status": "TRIAGED",
                "message": "Initial triage completed by incident manager",
            }]

            assert ai_service.calls == [{
                "incident_id": 77,
                "patient_id": 42,
                "triage_tag": "RED",
                "risk_level": "HIGH",
                "operations_plan": ["ambulance", "emergency_response_team"],
            }]

            assert event_bus.calls[0]["topic"] == "triage_events"
            payload = event_bus.calls[0]["payload"]
            assert payload["manager"] == "incident_manager"
            assert payload["clinical_assessment"]["agent"] == "clinical_agent"
            assert payload["clinical_assessment"]["role"] == "clinical"
            assert payload["operations_plan"]["agent"] == "operations_agent"
            assert payload["operations_plan"]["role"] == "operations"
            assert payload["operations_plan"]["resources"] == ["ambulance", "emergency_response_team"]
            assert broadcaster.calls == [payload]

        asyncio.run(run())
    finally:
        main_agent_module.manager = original_manager
