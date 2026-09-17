"""M89: bounded personal model built from explicit remembered claims.

The personal model describes remembered preferences, goals, constraints, and
interests with confidence and provenance. It is not user intent, policy, or
authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PersonalModelEntryKind(str, Enum):
    PREFERENCE = "PREFERENCE"
    GOAL = "GOAL"
    CONSTRAINT = "CONSTRAINT"
    INTEREST = "INTEREST"


@dataclass(frozen=True)
class PersonalModelEntry:
    entry_id: str
    kind: PersonalModelEntryKind
    statement: str
    confidence: float
    provenance_ids: tuple[str, ...] = ()
    source_memory_id: str | None = None
    active: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.entry_id, str) or not self.entry_id.strip():
            raise ValueError("entry_id must be a non-empty string")
        if not isinstance(self.kind, PersonalModelEntryKind):
            raise TypeError("kind must be a PersonalModelEntryKind")
        if not isinstance(self.statement, str) or not self.statement.strip():
            raise ValueError("statement must be a non-empty string")
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise TypeError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not isinstance(self.provenance_ids, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.provenance_ids
        ):
            raise TypeError("provenance_ids must be a tuple of non-empty strings")
        if len(set(self.provenance_ids)) != len(self.provenance_ids):
            raise ValueError("provenance_ids must not contain duplicates")
        if self.source_memory_id is not None and (
            not isinstance(self.source_memory_id, str) or not self.source_memory_id.strip()
        ):
            raise ValueError("source_memory_id must be non-empty when provided")
        if not isinstance(self.active, bool):
            raise TypeError("active must be boolean")

    def to_context(self) -> dict[str, object]:
        return {
            "entry_id": self.entry_id,
            "kind": self.kind.value,
            "statement": self.statement,
            "confidence": float(self.confidence),
            "provenance_ids": tuple(self.provenance_ids),
            "source_memory_id": self.source_memory_id,
            "active": self.active,
            "user_intent_established": False,
            "authority_granted": False,
        }


@dataclass(frozen=True)
class PersonalModel:
    subject_id: str
    entries: tuple[PersonalModelEntry, ...] = ()
    model_version: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.subject_id, str) or not self.subject_id.strip():
            raise ValueError("subject_id must be a non-empty string")
        if not isinstance(self.entries, tuple) or any(
            not isinstance(item, PersonalModelEntry) for item in self.entries
        ):
            raise TypeError("entries must be a tuple of PersonalModelEntry")
        identifiers = [entry.entry_id for entry in self.entries]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("personal model entry ids must be unique")
        if not isinstance(self.model_version, int) or isinstance(self.model_version, bool) or self.model_version < 1:
            raise ValueError("model_version must be a positive integer")

    def active_entries(self, kind: PersonalModelEntryKind | None = None) -> tuple[PersonalModelEntry, ...]:
        return tuple(
            entry
            for entry in self.entries
            if entry.active and (kind is None or entry.kind is kind)
        )

    def to_context(self) -> dict[str, object]:
        return {
            "subject_id": self.subject_id,
            "model_version": self.model_version,
            "entries": tuple(entry.to_context() for entry in self.active_entries()),
            "truth_established": False,
            "user_intent_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }


__all__ = ["PersonalModel", "PersonalModelEntry", "PersonalModelEntryKind"]
