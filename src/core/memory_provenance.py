"""M84: provenance-first memory lineage.

Provenance records identify where a memory claim came from. They do not
convert a source into truth or grant authority.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum

from src.core.persistent_memory import PersistentMemoryRecord


class ProvenanceSourceKind(str, Enum):
    USER = "USER"
    CONVERSATION = "CONVERSATION"
    OBSERVATION = "OBSERVATION"
    EXPERIENCE = "EXPERIENCE"
    IMPORT = "IMPORT"
    SYSTEM = "SYSTEM"


@dataclass(frozen=True)
class ProvenanceRef:
    """Opaque reference to a source supporting remembered state."""

    provenance_id: str
    source_kind: ProvenanceSourceKind
    source_id: str
    summary: str
    observed_at: str | None = None
    confidence: float | None = None

    def __post_init__(self) -> None:
        for name in ("provenance_id", "source_id", "summary"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.source_kind, ProvenanceSourceKind):
            raise TypeError("source_kind must be a ProvenanceSourceKind")
        if self.observed_at is not None and (
            not isinstance(self.observed_at, str) or not self.observed_at.strip()
        ):
            raise ValueError("observed_at must be non-empty when provided")
        if self.confidence is not None:
            if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
                raise TypeError("confidence must be numeric or None")
            if not 0.0 <= float(self.confidence) <= 1.0:
                raise ValueError("confidence must be between 0 and 1")

    def canonical(self) -> dict[str, object]:
        return {
            "provenance_id": self.provenance_id,
            "source_kind": self.source_kind.value,
            "source_id": self.source_id,
            "summary": self.summary,
            "observed_at": self.observed_at,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class ProvenanceChain:
    """Deterministic ordered lineage for a memory record."""

    refs: tuple[ProvenanceRef, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.refs, tuple) or any(
            not isinstance(item, ProvenanceRef) for item in self.refs
        ):
            raise TypeError("refs must be a tuple of ProvenanceRef")
        identifiers = [item.provenance_id for item in self.refs]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("provenance ids must be unique within a chain")

    @property
    def digest(self) -> str:
        payload = [item.canonical() for item in self.refs]
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(item.provenance_id for item in self.refs)

    def contains_all(self, provenance_ids: tuple[str, ...]) -> bool:
        available = set(self.ids)
        return set(provenance_ids).issubset(available)


def validate_provenance(
    record: PersistentMemoryRecord,
    chain: ProvenanceChain,
) -> tuple[str, ...]:
    """Validate that all provenance ids referenced by a record exist."""

    if not isinstance(record, PersistentMemoryRecord):
        raise TypeError("record must be a PersistentMemoryRecord")
    if not isinstance(chain, ProvenanceChain):
        raise TypeError("chain must be a ProvenanceChain")

    if chain.contains_all(record.provenance_ids):
        return ()

    missing = tuple(
        item for item in record.provenance_ids if item not in set(chain.ids)
    )
    return (f"missing provenance references: {missing}",)


__all__ = [
    "ProvenanceChain",
    "ProvenanceRef",
    "ProvenanceSourceKind",
    "validate_provenance",
]
