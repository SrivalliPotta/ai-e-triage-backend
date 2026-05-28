# agents/operations_agent/agent.py

from agents.base_agent import BaseAgent
from agents.shared.context import WorkflowContext
from agents.shared.decision import AgentDecision


class OperationsAgent(BaseAgent):

    async def handle(
        self,
        event: dict,
        context: WorkflowContext
    ) -> AgentDecision:

        patient = context.patient

        triage_tag = context.metadata.get(
            "triage_tag"
        )

        doctor_queue = self._assign_queue(
            triage_tag
        )

        resources = self._allocate_resources(
            triage_tag
        )

        return AgentDecision(
            actions=[
                "ASSIGN_DOCTOR_QUEUE",
                "ALLOCATE_RESOURCES"
            ],
            metadata={
                "doctor_queue": doctor_queue,
                "resources": resources
            },
            recommendations=[
                f"Assign to {doctor_queue}"
            ],
            events=[
                {
                    "type": "QUEUE_UPDATED",
                    "patient_id": patient.get("id"),
                    "queue": doctor_queue
                }
            ]
        )

    def _assign_queue(
        self,
        triage_tag: str
    ) -> str:

        if triage_tag == "RED":
            return "IMMEDIATE_QUEUE"

        if triage_tag == "YELLOW":
            return "DELAYED_QUEUE"

        if triage_tag == "GREEN":
            return "MINOR_QUEUE"

        return "EXPECTANT_QUEUE"

    def _allocate_resources(
        self,
        triage_tag: str
    ) -> list[str]:

        if triage_tag == "RED":

            return [
                "Trauma Team",
                "ICU Bed",
                "Emergency Transport"
            ]

        if triage_tag == "YELLOW":

            return [
                "Observation Bed"
            ]

        return []