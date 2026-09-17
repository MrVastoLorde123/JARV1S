"""M86: validated semantic knowledge model.

A semantic claim is a structured proposition held with explicit evidence and
uncertainty. Supporting evidence never becomes a guarantee of truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.core.memory_provenance import ProvenanceChain
from src.core.persistent_memory import (
    MemoryLifecycle,
    PersistentMemoryKind,
    PersistentMemoryRecord,
)


class SemanticValidationStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"


@dataclass(frozen=True)
class SemanticClaim:
    memory_id: str
    subject_id: str
    subject: str
    predicate: str
    object_value: str
    provenance_ids: tuple[str, ...]
    confidence: float = 0.5
    importance: float = 0.5
    validation: SemanticValidationStatus = SemanticValidationStatus.UNVERIFIED
    status: MemoryLifecycle = MemoryLifecycle.ACTIVE
    valid_from: str | None = None
    valid_until: str | None = None
    qualifiers: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("memory_id", "subject_id", "subject", "predicate", "object_value"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.provenance_ids, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.provenance_ids
        ):
            raise TypeError("provenance_ids must be a tuple of non-empty strings")
        if len(set(self.provenance_ids)) != len(self.provenance_ids):
            raise ValueError("provenance_ids must not contain duplicates")
        for name, value in (("confidence", self.confidence), ("importance", self.importance)):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be numeric")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if not isinstance(self.validation, SemanticValidationStatus):
            raise TypeError("validation must be a SemanticValidationStatus")
        if not isinstance(self.status, MemoryLifecycle):
            raise TypeError("status must be a MemoryLifecycle")
        for name, values in (("qualifiers", self.qualifiers),):
            if not isinstance(values, tuple) or any(not isinstance(item, str) or not item.strip() for item in values):
                raise TypeError(f"{name} must be a tuple of non-empty strings")
        if self.valid_from is not None and (not isinstance(self.valid_from, str) or not self.valid_from.strip()):
            raise ValueError("valid_from must be non-empty when provided")
        if self.valid_until is not None and (not isinstance(self.valid_until, str) or not self.valid_until.strip()):
            raise ValueError("valid_until must be non-empty when provided")

    def validate_against(self, provenance: ProvenanceChain) -> tuple[str, ...]:
        if not isinstance(provenance, ProvenanceChain):
            raise TypeError("provenance must be a ProvenanceChain")
        missing = tuple(
            item for item in self.provenance_ids if item not in set(provenance.ids)
        )
        return () if not missing else (f"missing provenance references: {missing}",)

    def to_record(self, *, observed_at: str = "") -> PersistentMemoryRecord:
        return PersistentMemoryRecord(
            memory_id=self.memory_id,
            subject_id=self.subject_id,
            kind=PersistentMemoryKind.SEMANTIC,
            content=f"{self.subject} {self.predicate} {self.object_value}",
            confidence=self.confidence,
            importance=self.importance,
            status=self.status,
            created_at=self.valid_from or observed_at,
            updated_at=observed_at or self.valid_from or "",
            provenance_ids=self.provenance_ids,
            tags=(self.validation.value,),
            metadata={
                "subject": self.subject,
                "predicate": self.predicate,
                "object_value": self.object_value,
                "validation": self.validation.value,
                "valid_from": self.valid_from,
                "valid_until": self.valid_until,
                "qualifiers": self.qualifiers,
            },
        )


__all__ = ["SemanticClaim", "SemanticValidationStatus"]
