# agents/shared/context.py

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorkflowContext:

    patient: dict | None = None

    incident: dict | None = None

    vitals_history: list[dict] = field(default_factory=list)

    resources: dict[str, Any] = field(default_factory=dict)

    queues: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)