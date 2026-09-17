"""M83: canonical persistent-memory contract.

Persistent memory is durable evidence-bearing state. It is not truth,
authority, authorization, or execution permission.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping


class PersistentMemoryKind(str, Enum):
    EPISODIC = "EPISODIC"
    SEMANTIC = "SEMANTIC"
    PROCEDURAL = "PROCEDURAL"
    WORKING = "WORKING"


class MemoryLifecycle(str, Enum):
    CANDIDATE = "CANDIDATE"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"


@dataclass(frozen=True)
class PersistentMemoryRecord:
    """Immutable canonical representation of one remembered claim/state."""

    memory_id: str
    subject_id: str
    kind: PersistentMemoryKind
    content: str
    confidence: float
    importance: float = 0.5
    status: MemoryLifecycle = MemoryLifecycle.ACTIVE
    created_at: str = ""
    updated_at: str = ""
    supersedes_memory_id: str | None = None
    provenance_ids: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("memory_id", "subject_id", "content"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.kind, PersistentMemoryKind):
            raise TypeError("kind must be a PersistentMemoryKind")
        if not isinstance(self.status, MemoryLifecycle):
            raise TypeError("status must be a MemoryLifecycle")
        for name, value in (("confidence", self.confidence), ("importance", self.importance)):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be numeric")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        for name, value in (("created_at", self.created_at), ("updated_at", self.updated_at)):
            if value and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be a non-empty string when provided")
        if self.supersedes_memory_id is not None and (
            not isinstance(self.supersedes_memory_id, str)
            or not self.supersedes_memory_id.strip()
        ):
            raise ValueError("supersedes_memory_id must be non-empty when provided")
        if not isinstance(self.provenance_ids, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.provenance_ids
        ):
            raise TypeError("provenance_ids must be a tuple of non-empty strings")
        if len(set(self.provenance_ids)) != len(self.provenance_ids):
            raise ValueError("provenance_ids must not contain duplicates")
        if not isinstance(self.tags, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.tags
        ):
            raise TypeError("tags must be a tuple of non-empty strings")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

    @property
    def is_persistent(self) -> bool:
        return self.kind is not PersistentMemoryKind.WORKING

    def to_context(self) -> dict[str, object]:
        """Return a provider-neutral projection without authority semantics."""

        return {
            "memory_id": self.memory_id,
            "subject_id": self.subject_id,
            "kind": self.kind.value,
            "content": self.content,
            "confidence": float(self.confidence),
            "importance": float(self.importance),
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "supersedes_memory_id": self.supersedes_memory_id,
            "provenance_ids": tuple(self.provenance_ids),
            "tags": tuple(self.tags),
            "metadata": dict(self.metadata),
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }


__all__ = [
    "MemoryLifecycle",
    "PersistentMemoryKind",
    "PersistentMemoryRecord",
]
