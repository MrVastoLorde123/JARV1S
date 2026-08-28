from dataclasses import dataclass, field
from typing import Any


SUCCESS = "SUCCESS"
NO_OP = "NO_OP"
FAILED = "FAILED"


@dataclass(frozen=True)
class MemoryExecutionResult:
    """
    Result of executing a MemoryDecision.
    """

    status: str

    action: str

    memory_id: int | None = None

    evidence_id: int | None = None

    affected_memory_ids: tuple[int, ...] = ()

    reason: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self):

        if self.status not in {
            SUCCESS,
            NO_OP,
            FAILED,
        }:
            raise ValueError(
                f"Invalid execution status: "
                f"{self.status}"
            )