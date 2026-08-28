from dataclasses import dataclass, field
from typing import Any

from src.memory.memory_models import (
    CandidateMemory,
)

from src.memory.memory_retrieval import (
    MemoryResult,
)


CREATE = "CREATE"
CONFIRM = "CONFIRM"
UPDATE = "UPDATE"
CONTRADICT = "CONTRADICT"
IGNORE = "IGNORE"


VALID_DECISIONS = {
    CREATE,
    CONFIRM,
    UPDATE,
    CONTRADICT,
    IGNORE,
}


@dataclass(frozen=True)
class MemoryDecisionContext:
    """
    Provider-neutral information available when deciding
    what should happen to a memory candidate.
    """

    candidate: CandidateMemory

    existing_memory: MemoryResult | None = None

    related_memories: tuple[
        MemoryResult,
        ...
    ] = ()

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class MemoryDecision:
    """
    Structured decision returned by a memory decision provider.
    """

    action: str

    candidate: CandidateMemory

    memory_id: int | None

    reason: str

    confidence: float

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self):

        if self.action not in VALID_DECISIONS:
            raise ValueError(
                f"Invalid memory decision: "
                f"{self.action}"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Decision confidence must be between "
                "0.0 and 1.0."
            )