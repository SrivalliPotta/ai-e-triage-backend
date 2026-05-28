from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentDecision:

    actions: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    recommendations: list[str] = field(default_factory=list)

    events: list[dict] = field(default_factory=list)