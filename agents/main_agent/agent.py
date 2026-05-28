# agents/main_agent/agent.py

from agents.clinical_agent.agent import ClinicalAgent
from agents.operations_agent.agent import OperationsAgent

from agents.shared.context import WorkflowContext

from services.ai_service import AIService
from services.triage_service import TriageService
from services.workflow_service import WorkflowService

from websocket.manager import manager

from events.redis_event_bus import RedisEventBus


class MainAgent:

    def __init__(
        self,
        clinical_agent: ClinicalAgent | None = None,
        operations_agent: OperationsAgent | None = None,
        triage_service: TriageService | None = None,
        workflow_service: WorkflowService | None = None,
        ai_service: AIService | None = None,
        event_bus: RedisEventBus | None = None,
    ):

        self.manager_name = "incident_manager"

        self.clinical_agent = (
            clinical_agent
            or ClinicalAgent()
        )

        self.operations_agent = (
            operations_agent
            or OperationsAgent()
        )

        self.triage_service = (
            triage_service
            or TriageService()
        )

        self.workflow_service = (
            workflow_service
            or WorkflowService()
        )

        self.ai_service = (
            ai_service
            or AIService()
        )

        self.event_bus = (
            event_bus
            or RedisEventBus()
        )

    async def process_triage(
        self,
        db,
        incident_id: int,
        patient
    ):

        # -----------------------------------
        # Build Shared Workflow Context
        # -----------------------------------

        context = WorkflowContext(
            patient=patient.dict(),
            incident={
                "incident_id": incident_id
            }
        )

        # -----------------------------------
        # Clinical Agent
        # -----------------------------------

        clinical_decision = await self.clinical_agent.handle(
            {
                "type": "NEW_PATIENT"
            },
            context
        )

        # Share decision metadata
        # with downstream agents

        context.metadata.update(
            clinical_decision.metadata
        )

        # -----------------------------------
        # Operations Agent
        # -----------------------------------

        operations_decision = await self.operations_agent.handle(
            {
                "type": "RESOURCE_COORDINATION"
            },
            context
        )

        # -----------------------------------
        # Extract Clinical Outputs
        # -----------------------------------

        triage_tag = clinical_decision.metadata.get(
            "triage_tag"
        )

        risk_level = clinical_decision.metadata.get(
            "risk_level"
        )

        clinical_explanation = clinical_decision.metadata.get(
            "clinical_explanation"
        )

        # -----------------------------------
        # Persist Patient
        # -----------------------------------

        db_patient = self.triage_service.save_patient(
            db=db,
            incident_id=incident_id,
            patient=patient,
            triage_tag=triage_tag
        )

        # -----------------------------------
        # Workflow State Transition
        # -----------------------------------

        db_patient = self.workflow_service.transition_patient(
    db=db,
    patient=db_patient,
    target_status="TRIAGED",
    message="Initial triage completed"
    )

        # -----------------------------------
        # AI Summary
        # -----------------------------------

        incident_summary = await self.ai_service.summarize_incident(
            {
                "incident_id": incident_id,
                "patient_id": db_patient.id,
                "triage_tag": triage_tag,
                "risk_level": risk_level,
                "resources": operations_decision.metadata.get(
                    "resources",
                    []
                ),
            }
        )

        # -----------------------------------
        # Build Event Payload
        # -----------------------------------

        event_payload = {
            "type": "PATIENT_TRIAGED",

            "manager": self.manager_name,

            "incident_id": incident_id,

            "patient_id": db_patient.id,

            "status": db_patient.status,

            "clinical_decision": {
                "triage_tag": triage_tag,
                "risk_level": risk_level,
                "explanation": clinical_explanation,
                "recommendations": (
                    clinical_decision.recommendations
                )
            },

            "operations_decision": {
                "doctor_queue": (
                    operations_decision.metadata.get(
                        "doctor_queue"
                    )
                ),
                "resources": (
                    operations_decision.metadata.get(
                        "resources"
                    )
                ),
                "recommendations": (
                    operations_decision.recommendations
                )
            },

            "summary": incident_summary,
        }

        # -----------------------------------
        # Publish Internal Events
        # -----------------------------------

        await self.event_bus.publish(
            "triage_events",
            event_payload
        )

        # -----------------------------------
        # Realtime WebSocket Broadcast
        # -----------------------------------

        await manager.broadcast(
            event_payload
        )

        # -----------------------------------
        # Final API Response
        # -----------------------------------

        return {
            "patient_id": db_patient.id,
            "incident_id": incident_id,
            "triage_tag": triage_tag,
            "risk_level": risk_level,
            "status": db_patient.status,
            "clinical_explanation": clinical_explanation,
            "doctor_queue": (
                operations_decision.metadata.get(
                    "doctor_queue"
                )
            ),
            "resources": (
                operations_decision.metadata.get(
                    "resources"
                )
            ),
            "summary": incident_summary,
        }