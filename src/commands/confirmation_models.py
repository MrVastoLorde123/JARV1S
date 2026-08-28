from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


PENDING = "PENDING"
CONFIRMED = "CONFIRMED"
CANCELLED = "CANCELLED"
EXPIRED = "EXPIRED"


@dataclass(frozen=True)
class PendingOperation:
    """
    An operation waiting for explicit confirmation.

    The operation contains everything required to identify
    exactly what the user is approving.
    """

    operation_id: str

    command: str

    arguments: tuple[str, ...]

    description: str

    created_at: str

    status: str = PENDING

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def is_pending(self) -> bool:
        return self.status == PENDING

    @staticmethod
    def now_iso() -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()