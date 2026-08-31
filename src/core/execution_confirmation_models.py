from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from src.core.execution_plan_models import ExecutionPlan


class ExecutionConfirmationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class ExecutionPendingOperation:
    """
    Exact execution plan waiting for explicit confirmation.

    Confirmation authorizes this plan.
    It does not recreate or reinterpret the original task.
    """

    operation_id: str
    plan: ExecutionPlan
    created_at: str

    status: ExecutionConfirmationStatus = (
        ExecutionConfirmationStatus.PENDING
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self):
        if not isinstance(self.operation_id, str):
            raise TypeError(
                "operation_id must be a string."
            )

        if not self.operation_id.strip():
            raise ValueError(
                "operation_id cannot be empty."
            )

        if not isinstance(self.plan, ExecutionPlan):
            raise TypeError(
                "plan must be an ExecutionPlan."
            )

        if not isinstance(self.created_at, str):
            raise TypeError(
                "created_at must be a string."
            )

        if not isinstance(
            self.status,
            ExecutionConfirmationStatus,
        ):
            raise TypeError(
                "status must be an "
                "ExecutionConfirmationStatus."
            )

    @property
    def is_pending(self) -> bool:
        return (
            self.status
            == ExecutionConfirmationStatus.PENDING
        )

    @staticmethod
    def now_iso() -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()

    