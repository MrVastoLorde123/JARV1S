"""M85: typed episodic memory.

Episodes preserve observed events and outcomes. They are historical evidence,
not policy, truth, or authorization.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.core.persistent_memory import (
    MemoryLifecycle,
    PersistentMemoryKind,
    PersistentMemoryRecord,
)


class EpisodicOutcome(str, Enum):
    UNKNOWN = "UNKNOWN"
    OBSERVED = "OBSERVED"
    SUCCEEDED = "SUCCEEDED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


@dataclass(frozen=True)
class EpisodicMemory:
    memory_id: str
    subject_id: str
    event_type: str
    summary: str
    observed_at: str
    outcome: EpisodicOutcome = EpisodicOutcome.UNKNOWN
    experience_id: str | None = None
    context_ids: tuple[str, ...] = ()
    provenance_ids: tuple[str, ...] = ()
    confidence: float = 1.0
    importance: float = 0.5
    status: MemoryLifecycle = MemoryLifecycle.ACTIVE

    def __post_init__(self) -> None:
        for name in ("memory_id", "subject_id", "event_type", "summary", "observed_at"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.outcome, EpisodicOutcome):
            raise TypeError("outcome must be an EpisodicOutcome")
        if self.experience_id is not None and not self.experience_id.strip():
            raise ValueError("experience_id must be non-empty when provided")
        for name, values in (("context_ids", self.context_ids), ("provenance_ids", self.provenance_ids)):
            if not isinstance(values, tuple) or any(not isinstance(item, str) or not item.strip() for item in values):
                raise TypeError(f"{name} must be a tuple of non-empty strings")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must not contain duplicates")
        for name, value in (("confidence", self.confidence), ("importance", self.importance)):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be numeric")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if not isinstance(self.status, MemoryLifecycle):
            raise TypeError("status must be a MemoryLifecycle")

    def to_record(self) -> PersistentMemoryRecord:
        return PersistentMemoryRecord(
            memory_id=self.memory_id,
            subject_id=self.subject_id,
            kind=PersistentMemoryKind.EPISODIC,
            content=self.summary,
            confidence=self.confidence,
            importance=self.importance,
            status=self.status,
            created_at=self.observed_at,
            updated_at=self.observed_at,
            provenance_ids=self.provenance_ids,
            metadata={
                "event_type": self.event_type,
                "outcome": self.outcome.value,
                "experience_id": self.experience_id,
                "context_ids": self.context_ids,
            },
        )


__all__ = ["EpisodicMemory", "EpisodicOutcome"]
