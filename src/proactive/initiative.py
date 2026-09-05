"""M21.1 bounded proactive initiative boundary.

A proactive signal may create a structured candidate for future consideration.
This module deliberately stops before proposal, authorization, notification,
scheduling, or execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class ProactiveTriggerSource(str, Enum):
    OBSERVATION = "OBSERVATION"
    STATE_CHANGE = "STATE_CHANGE"
    USER_HISTORY = "USER_HISTORY"
    EXTERNAL_EVENT = "EXTERNAL_EVENT"
    SYSTEM_SIGNAL = "SYSTEM_SIGNAL"


class InitiativeDisposition(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    SUPPRESSED = "SUPPRESSED"
    EXPIRED = "EXPIRED"


@dataclass(frozen=True)
class ProactiveTrigger:
    """Immutable signal record; a trigger is evidence of a signal, not intent."""

    trigger_id: str
    source: ProactiveTriggerSource
    reference_id: str
    signal: str
    observed_at: datetime
    evidence_ids: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("trigger_id", "reference_id", "signal"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.source, ProactiveTriggerSource):
            try:
                object.__setattr__(self, "source", ProactiveTriggerSource(self.source))
            except (TypeError, ValueError) as exc:
                raise TypeError("source must be a ProactiveTriggerSource") from exc
        if not isinstance(self.observed_at, datetime):
            raise TypeError("observed_at must be a datetime")
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        evidence_ids = tuple(self.evidence_ids)
        if len(set(evidence_ids)) != len(evidence_ids):
            raise ValueError("evidence_ids must be unique")
        for evidence_id in evidence_ids:
            if not isinstance(evidence_id, str) or not evidence_id.strip():
                raise ValueError("evidence ids must be non-empty strings")
        object.__setattr__(self, "evidence_ids", evidence_ids)
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "trigger_id": self.trigger_id,
            "source": self.source.value,
            "reference_id": self.reference_id,
            "signal": self.signal,
            "observed_at": self.observed_at.isoformat(),
            "evidence_ids": self.evidence_ids,
            "metadata": dict(self.metadata),
            "authorization_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class InitiativeCandidate:
    """Immutable candidate for consideration; never a task or execution request."""

    candidate_id: str
    trigger_id: str
    title: str
    rationale: str
    evidence_ids: tuple[str, ...] = ()
    expires_at: datetime | None = None
    bounded: bool = True
    authorization_granted: bool = False
    execution_requested: bool = False

    def __post_init__(self) -> None:
        for name in ("candidate_id", "trigger_id", "title", "rationale"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        evidence_ids = tuple(self.evidence_ids)
        if len(set(evidence_ids)) != len(evidence_ids):
            raise ValueError("evidence_ids must be unique")
        for evidence_id in evidence_ids:
            if not isinstance(evidence_id, str) or not evidence_id.strip():
                raise ValueError("evidence ids must be non-empty strings")
        object.__setattr__(self, "evidence_ids", evidence_ids)
        if self.expires_at is not None:
            if not isinstance(self.expires_at, datetime):
                raise TypeError("expires_at must be None or a datetime")
            if self.expires_at.tzinfo is None:
                raise ValueError("expires_at must be timezone-aware")
        for name in ("bounded", "authorization_granted", "execution_requested"):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool")
        if not self.bounded:
            raise ValueError("initiative candidates must remain bounded")
        if self.authorization_granted:
            raise ValueError("initiative candidates cannot grant authorization")
        if self.execution_requested:
            raise ValueError("initiative candidates cannot request execution")

    def to_context(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "trigger_id": self.trigger_id,
            "title": self.title,
            "rationale": self.rationale,
            "evidence_ids": self.evidence_ids,
            "expires_at": None if self.expires_at is None else self.expires_at.isoformat(),
            "bounded": True,
            "authorization_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class InitiativeEvaluation:
    """Immutable disposition of one proactive candidate."""

    candidate_id: str
    trigger_id: str
    disposition: InitiativeDisposition
    reason: str

    def __post_init__(self) -> None:
        for name in ("candidate_id", "trigger_id", "reason"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.disposition, InitiativeDisposition):
            try:
                object.__setattr__(self, "disposition", InitiativeDisposition(self.disposition))
            except (TypeError, ValueError) as exc:
                raise TypeError("disposition must be an InitiativeDisposition") from exc

    def to_context(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "trigger_id": self.trigger_id,
            "disposition": self.disposition.value,
            "reason": self.reason,
            "authority_granted": False,
            "execution_requested": False,
        }


def _now() -> datetime:
    return datetime.now(timezone.utc)


def evaluate_initiative(
    trigger: ProactiveTrigger,
    candidate: InitiativeCandidate,
    *,
    now: datetime | None = None,
    suppressed: bool = False,
    needs_review: bool = False,
) -> InitiativeEvaluation:
    """Deterministically evaluate bounded eligibility without granting permission."""
    if not isinstance(trigger, ProactiveTrigger):
        raise TypeError("trigger must be a ProactiveTrigger")
    if not isinstance(candidate, InitiativeCandidate):
        raise TypeError("candidate must be an InitiativeCandidate")
    if candidate.trigger_id != trigger.trigger_id:
        raise ValueError("candidate/trigger identity mismatch")
    evaluation_now = _now() if now is None else now
    if not isinstance(evaluation_now, datetime):
        raise TypeError("now must be None or a datetime")
    if evaluation_now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    if suppressed:
        return InitiativeEvaluation(
            candidate.candidate_id,
            candidate.trigger_id,
            InitiativeDisposition.SUPPRESSED,
            "initiative is suppressed by explicit policy/context",
        )
    if candidate.expires_at is not None and evaluation_now >= candidate.expires_at:
        return InitiativeEvaluation(
            candidate.candidate_id,
            candidate.trigger_id,
            InitiativeDisposition.EXPIRED,
            "initiative candidate has expired",
        )
    if needs_review:
        return InitiativeEvaluation(
            candidate.candidate_id,
            candidate.trigger_id,
            InitiativeDisposition.NEEDS_REVIEW,
            "initiative requires bounded review before it can be considered further",
        )
    return InitiativeEvaluation(
        candidate.candidate_id,
        candidate.trigger_id,
        InitiativeDisposition.ELIGIBLE,
        "initiative is eligible for a later proposal-stage decision",
    )
