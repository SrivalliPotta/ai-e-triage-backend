from agents.main_agent.agent import MainAgent
from events.redis_event_bus import RedisEventBus
from services.ai_service import AIService
from services.triage_service import TriageService
from services.workflow_service import WorkflowService


class CommandService:
    def __init__(
        self,
        triage_service: TriageService | None = None,
        workflow_service: WorkflowService | None = None,
        ai_service: AIService | None = None,
        main_agent: MainAgent | None = None,
        event_bus: RedisEventBus | None = None,
    ):
        self.event_bus = event_bus or RedisEventBus()
        self.triage_service = triage_service or TriageService()
        self.workflow_service = workflow_service or WorkflowService()
        self.ai_service = ai_service or AIService()
        self.main_agent = main_agent or MainAgent(
            triage_service=self.triage_service,
            workflow_service=self.workflow_service,
            ai_service=self.ai_service,
            event_bus=self.event_bus,
        )

    async def triage_patient(self, db, incident_id, patient):
        return await self.main_agent.process_triage(db, incident_id, patient)
