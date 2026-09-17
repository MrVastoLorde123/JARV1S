"""M43: bounded qualification of world-model facts.

This module assesses freshness and same-domain conflicts in an existing
WorldModelSnapshot. It does not select truth, mutate the snapshot, infer user
intent, authorize actions, execute capabilities, or mutate memory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from .world_model import WorldModelFact, WorldModelSnapshot


class WorldFactFreshness(str, Enum):
    CURRENT = "CURRENT"
    STALE = "STALE"
    FUTURE = "FUTURE"
    INVALID = "INVALID"


class WorldFactQualification(str, Enum):
    USABLE = "USABLE"
    STALE = "STALE"
    CONFLICTING = "CONFLICTING"
    INVALID = "INVALID"
    INSUFFICIENT = "INSUFFICIENT"


@dataclass(frozen=True)
class WorldFactAssessment:
    """Immutable qualification result for one world-model fact."""

    fact_id: str
    freshness: WorldFactFreshness
    qualification: WorldFactQualification
    conflicting_fact_ids: tuple[str, ...] = ()
    reason: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.fact_id, str) or not self.fact_id.strip():
            raise ValueError("fact_id must be a non-empty string")
        if not isinstance(self.freshness, WorldFactFreshness):
            raise TypeError("freshness must be a WorldFactFreshness")
        if not isinstance(self.qualification, WorldFactQualification):
            raise TypeError("qualification must be a WorldFactQualification")
        if not isinstance(self.conflicting_fact_ids, tuple):
            raise TypeError("conflicting_fact_ids must be a tuple")
        if len(set(self.conflicting_fact_ids)) != len(self.conflicting_fact_ids):
            raise ValueError("conflicting_fact_ids must be unique")
        if any(not isinstance(item, str) or not item.strip() for item in self.conflicting_fact_ids):
            raise ValueError("conflicting_fact_ids must contain non-empty strings")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "fact_id": self.fact_id,
            "freshness": self.freshness.value,
            "qualification": self.qualification.value,
            "conflicting_fact_ids": self.conflicting_fact_ids,
            "reason": self.reason,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "authority_granted": False,
        }


@dataclass(frozen=True)
class WorldModelQualification:
    """Immutable snapshot-level qualification without truth arbitration."""

    model_id: str
    assessed_at: str
    assessments: tuple[WorldFactAssessment, ...]
    snapshot_source_observation_ids: tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.model_id, str) or not self.model_id.strip():
            raise ValueError("model_id must be a non-empty string")
        if not isinstance(self.assessed_at, str) or not self.assessed_at.strip():
            raise ValueError("assessed_at must be a non-empty string")
        if not isinstance(self.assessments, tuple) or any(not isinstance(item, WorldFactAssessment) for item in self.assessments):
            raise TypeError("assessments must be a tuple of WorldFactAssessment values")
        ids = tuple(item.fact_id for item in self.assessments)
        if len(set(ids)) != len(ids):
            raise ValueError("assessment fact IDs must be unique")
        if not isinstance(self.snapshot_source_observation_ids, tuple):
            raise TypeError("snapshot_source_observation_ids must be a tuple")
        if len(set(self.snapshot_source_observation_ids)) != len(self.snapshot_source_observation_ids):
            raise ValueError("snapshot_source_observation_ids must be unique")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def usable_fact_ids(self) -> tuple[str, ...]:
        return tuple(item.fact_id for item in self.assessments if item.qualification is WorldFactQualification.USABLE)

    @property
    def conflicting_fact_ids(self) -> tuple[str, ...]:
        return tuple(item.fact_id for item in self.assessments if item.qualification is WorldFactQualification.CONFLICTING)

    def for_fact(self, fact_id: str) -> WorldFactAssessment | None:
        if not isinstance(fact_id, str) or not fact_id.strip():
            raise ValueError("fact_id must be a non-empty string")
        return next((item for item in self.assessments if item.fact_id == fact_id.strip()), None)

    def to_context(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "assessed_at": self.assessed_at,
            "assessments": tuple(item.to_context() for item in self.assessments),
            "usable_fact_ids": self.usable_fact_ids,
            "conflicting_fact_ids": self.conflicting_fact_ids,
            "snapshot_source_observation_ids": self.snapshot_source_observation_ids,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "authority_granted": False,
            "permissions_granted": False,
        }


def _parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _fact_timestamp(fact: WorldModelFact, snapshot: WorldModelSnapshot) -> str:
    timestamp = fact.metadata.get("observed_at")
    if isinstance(timestamp, str) and timestamp.strip():
        return timestamp
    return snapshot.generated_at


def assess_world_model(
    snapshot: WorldModelSnapshot,
    *,
    assessed_at: str,
    max_age_seconds: float,
) -> WorldModelQualification:
    """Assess freshness and same-subject/domain conflicts deterministically."""
    if not isinstance(snapshot, WorldModelSnapshot):
        raise TypeError("snapshot must be a WorldModelSnapshot")
    if not isinstance(max_age_seconds, (int, float)) or isinstance(max_age_seconds, bool) or max_age_seconds < 0:
        raise ValueError("max_age_seconds must be a non-negative number")

    assessment_time = _parse_time(assessed_at)
    facts = snapshot.facts
    by_scope: dict[tuple[str, str], list[WorldModelFact]] = {}
    for fact in facts:
        by_scope.setdefault((fact.subject_id, fact.domain), []).append(fact)

    assessments: list[WorldFactAssessment] = []
    for fact in facts:
        timestamp_value = _fact_timestamp(fact, snapshot)
        try:
            observed_at = _parse_time(timestamp_value)
        except ValueError:
            freshness = WorldFactFreshness.INVALID
        else:
            delta = (assessment_time - observed_at).total_seconds()
            if delta < 0:
                freshness = WorldFactFreshness.FUTURE
            elif delta > float(max_age_seconds):
                freshness = WorldFactFreshness.STALE
            else:
                freshness = WorldFactFreshness.CURRENT

        conflicts = tuple(
            other.fact_id
            for other in by_scope[(fact.subject_id, fact.domain)]
            if other.fact_id != fact.fact_id and other.value != fact.value
        )
        conflicts = tuple(dict.fromkeys(conflicts))

        if freshness is WorldFactFreshness.INVALID:
            qualification = WorldFactQualification.INVALID
            reason = "fact observation timestamp is invalid"
        elif conflicts:
            qualification = WorldFactQualification.CONFLICTING
            reason = "peer facts for the same subject/domain disagree"
        elif freshness is WorldFactFreshness.STALE:
            qualification = WorldFactQualification.STALE
            reason = "fact exceeds the configured freshness bound"
        elif freshness is WorldFactFreshness.FUTURE:
            qualification = WorldFactQualification.INVALID
            reason = "fact timestamp is after assessment time"
        else:
            qualification = WorldFactQualification.USABLE
            reason = "fact is current and has no conflicting peer value"

        assessments.append(
            WorldFactAssessment(
                fact_id=fact.fact_id,
                freshness=freshness,
                qualification=qualification,
                conflicting_fact_ids=conflicts,
                reason=reason,
                metadata={"source_observation_ids": fact.source_observation_ids},
            )
        )

    return WorldModelQualification(
        model_id=snapshot.model_id,
        assessed_at=assessment_time.isoformat(),
        assessments=tuple(assessments),
        snapshot_source_observation_ids=snapshot.source_observation_ids,
        metadata={"source": "M43", "max_age_seconds": float(max_age_seconds)},
    )


__all__ = [
    "WorldFactAssessment",
    "WorldFactFreshness",
    "WorldFactQualification",
    "WorldModelQualification",
    "assess_world_model",
]
