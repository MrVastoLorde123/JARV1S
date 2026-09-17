"""M44: compose qualified world-model facts into bounded current context.

This module creates a deterministic, read-only reasoning context from an
existing world-model snapshot and its M43 qualification. It excludes stale,
invalid, and conflicting facts rather than resolving them, and it never
establishes truth, infers intent, grants authority, or executes capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .world_model import WorldModelFact, WorldModelSnapshot
from .world_model_qualification import WorldFactQualification, WorldModelQualification


@dataclass(frozen=True)
class CurrentContextFact:
    """One qualified fact admitted into current reasoning context."""

    fact: WorldModelFact
    qualification: WorldFactQualification

    def __post_init__(self) -> None:
        if not isinstance(self.fact, WorldModelFact):
            raise TypeError("fact must be a WorldModelFact")
        if not isinstance(self.qualification, WorldFactQualification):
            raise TypeError("qualification must be a WorldFactQualification")
        if self.qualification is not WorldFactQualification.USABLE:
            raise ValueError("current context only admits USABLE facts")

    def to_context(self) -> dict[str, Any]:
        return {
            "fact": self.fact.to_context(),
            "qualification": self.qualification.value,
            "truth_established": False,
            "authority_granted": False,
        }


@dataclass(frozen=True)
class CurrentContext:
    """Immutable bounded reasoning context assembled from qualified facts."""

    context_id: str
    model_id: str
    assessed_at: str
    facts: tuple[CurrentContextFact, ...] = ()
    excluded_fact_ids: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("context_id", "model_id", "assessed_at"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.facts, tuple) or any(not isinstance(item, CurrentContextFact) for item in self.facts):
            raise TypeError("facts must be a tuple of CurrentContextFact values")
        ids = tuple(item.fact.fact_id for item in self.facts)
        if len(set(ids)) != len(ids):
            raise ValueError("current-context fact IDs must be unique")
        if not isinstance(self.excluded_fact_ids, tuple):
            raise TypeError("excluded_fact_ids must be a tuple")
        if len(set(self.excluded_fact_ids)) != len(self.excluded_fact_ids):
            raise ValueError("excluded_fact_ids must be unique")
        if set(ids) & set(self.excluded_fact_ids):
            raise ValueError("a fact cannot be both admitted and excluded")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def fact_count(self) -> int:
        return len(self.facts)

    @property
    def subjects(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(item.fact.subject_id for item in self.facts))

    def facts_for_subject(self, subject_id: str) -> tuple[CurrentContextFact, ...]:
        if not isinstance(subject_id, str) or not subject_id.strip():
            raise ValueError("subject_id must be a non-empty string")
        return tuple(item for item in self.facts if item.fact.subject_id == subject_id.strip())

    def to_context(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "model_id": self.model_id,
            "assessed_at": self.assessed_at,
            "facts": tuple(item.to_context() for item in self.facts),
            "excluded_fact_ids": self.excluded_fact_ids,
            "fact_count": self.fact_count,
            "subjects": self.subjects,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "authority_granted": False,
            "permissions_granted": False,
            "intent_established": False,
            "execution_requested": False,
        }


def build_current_context(
    snapshot: WorldModelSnapshot,
    qualification: WorldModelQualification,
    *,
    context_id: str,
    metadata: Mapping[str, Any] | None = None,
) -> CurrentContext:
    """Compose only M43-USABLE facts into bounded current reasoning context."""
    if not isinstance(snapshot, WorldModelSnapshot):
        raise TypeError("snapshot must be a WorldModelSnapshot")
    if not isinstance(qualification, WorldModelQualification):
        raise TypeError("qualification must be a WorldModelQualification")
    if qualification.model_id != snapshot.model_id:
        raise ValueError("snapshot/qualification model identity mismatch")
    if not isinstance(context_id, str) or not context_id.strip():
        raise ValueError("context_id must be a non-empty string")

    facts_by_id = {fact.fact_id: fact for fact in snapshot.facts}
    assessments_by_id = {assessment.fact_id: assessment for assessment in qualification.assessments}
    if set(facts_by_id) != set(assessments_by_id):
        raise ValueError("snapshot facts and qualification assessments must match exactly")

    admitted: list[CurrentContextFact] = []
    excluded: list[str] = []
    for fact in snapshot.facts:
        assessment = assessments_by_id[fact.fact_id]
        if assessment.qualification is WorldFactQualification.USABLE:
            admitted.append(CurrentContextFact(fact, assessment.qualification))
        else:
            excluded.append(fact.fact_id)

    return CurrentContext(
        context_id=context_id.strip(),
        model_id=snapshot.model_id,
        assessed_at=qualification.assessed_at,
        facts=tuple(admitted),
        excluded_fact_ids=tuple(excluded),
        metadata={
            "source": "M44",
            "qualification_source_model_id": qualification.model_id,
            **dict(metadata or {}),
        },
    )


__all__ = ["CurrentContext", "CurrentContextFact", "build_current_context"]
