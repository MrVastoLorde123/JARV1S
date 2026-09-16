"""M30: typed durable-memory presentation contract.

Memory is persistent knowledge, not truth, authority, or execution permission.
This contract wraps the existing memory subsystem with explicit identity,
provenance, confidence, and evidence lineage without replacing its store.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping


class MemoryStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"


class MemorySourceKind(str, Enum):
    CONVERSATION = "CONVERSATION"
    OBSERVATION = "OBSERVATION"
    EXPERIENCE = "EXPERIENCE"
    IMPORT = "IMPORT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class MemoryEvidenceRef:
    """Reference to evidence supporting a remembered claim."""

    evidence_id: str
    source_kind: MemorySourceKind
    source_id: str
    summary: str
    observed_at: str | None = None
    confidence: float | None = None

    def __post_init__(self) -> None:
        for name in ("evidence_id", "source_id", "summary"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.source_kind, MemorySourceKind):
            raise TypeError("source_kind must be a MemorySourceKind")
        if self.observed_at is not None and not isinstance(self.observed_at, str):
            raise TypeError("observed_at must be a string or None")
        if self.confidence is not None:
            if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
                raise TypeError("confidence must be numeric or None")
            if not 0.0 <= float(self.confidence) <= 1.0:
                raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class MemoryRecord:
    """Immutable read model over one persistent memory claim."""

    memory_id: str
    memory_key: str
    content: str
    category: str
    confidence: float
    importance: float
    status: MemoryStatus = MemoryStatus.ACTIVE
    source_kind: MemorySourceKind = MemorySourceKind.UNKNOWN
    source_id: str | None = None
    evidence: tuple[MemoryEvidenceRef, ...] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("memory_id", "memory_key", "content", "category"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name, value in (("confidence", self.confidence), ("importance", self.importance)):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be numeric")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if not isinstance(self.status, MemoryStatus):
            raise TypeError("status must be a MemoryStatus")
        if not isinstance(self.source_kind, MemorySourceKind):
            raise TypeError("source_kind must be a MemorySourceKind")
        if self.source_id is not None and (not isinstance(self.source_id, str) or not self.source_id.strip()):
            raise ValueError("source_id must be non-empty when provided")
        if not isinstance(self.evidence, tuple) or any(not isinstance(item, MemoryEvidenceRef) for item in self.evidence):
            raise TypeError("evidence must be a tuple of MemoryEvidenceRef")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")


@dataclass(frozen=True)
class MemoryQuery:
    """Deterministic retrieval request for persistent memory."""

    text: str
    category: str | None = None
    status: MemoryStatus = MemoryStatus.ACTIVE
    limit: int = 20

    def __post_init__(self) -> None:
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("text must be a non-empty string")
        if self.category is not None and (not isinstance(self.category, str) or not self.category.strip()):
            raise ValueError("category must be non-empty when provided")
        if not isinstance(self.status, MemoryStatus):
            raise TypeError("status must be a MemoryStatus")
        if not isinstance(self.limit, int) or isinstance(self.limit, bool):
            raise TypeError("limit must be an integer")
        if not 1 <= self.limit <= 100:
            raise ValueError("limit must be between 1 and 100")


@dataclass(frozen=True)
class MemoryRetrieval:
    """Read-only retrieval result. Retrieval does not imply truth or authority."""

    query: MemoryQuery
    records: tuple[MemoryRecord, ...]
    generated_at: str
    source: str = "memory_store"

    def __post_init__(self) -> None:
        if not isinstance(self.query, MemoryQuery):
            raise TypeError("query must be a MemoryQuery")
        if not isinstance(self.records, tuple) or any(not isinstance(item, MemoryRecord) for item in self.records):
            raise TypeError("records must be a tuple of MemoryRecord")
        if not isinstance(self.generated_at, str) or not self.generated_at.strip():
            raise ValueError("generated_at must be a non-empty string")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be a non-empty string")


__all__ = [
    "MemoryEvidenceRef",
    "MemoryRecord",
    "MemoryQuery",
    "MemoryRetrieval",
    "MemorySourceKind",
    "MemoryStatus",
]
