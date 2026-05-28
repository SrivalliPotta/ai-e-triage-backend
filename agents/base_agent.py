from abc import ABC, abstractmethod
from agents.shared.context import WorkflowContext
from agents.shared.decision import AgentDecision


class BaseAgent(ABC):

    @abstractmethod
    async def handle(
        self,
        event: dict,
        context: WorkflowContext
    ) -> AgentDecision:
        pass