from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from src.agents.coding_worker import CodingAgentPlan, CodingAgentTask


class CodingConfirmationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class CodingPendingOperation:
    """Exact coding task and plan waiting for explicit confirmation."""

    operation_id: str
    task: CodingAgentTask
    plan: CodingAgentPlan
    created_at: str
    status: CodingConfirmationStatus = CodingConfirmationStatus.PENDING
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.operation_id, str) or not self.operation_id.strip():
            raise ValueError("operation_id must be a non-empty string")
        if not isinstance(self.task, CodingAgentTask):
            raise TypeError("task must be a CodingAgentTask")
        if not isinstance(self.plan, CodingAgentPlan):
            raise TypeError("plan must be a CodingAgentPlan")
        if not isinstance(self.created_at, str):
            raise TypeError("created_at must be a string")
        if not isinstance(self.status, CodingConfirmationStatus):
            raise TypeError("status must be a CodingConfirmationStatus")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dict")

    @property
    def is_pending(self) -> bool:
        return self.status == CodingConfirmationStatus.PENDING

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
