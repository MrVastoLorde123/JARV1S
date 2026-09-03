"""M10.6 learning reliability, conflict, suspension, and reversal boundary.

This module lets learned artifacts become less trusted without deleting history,
changing authority, or silently mutating policy.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class ReliabilityState(str, Enum):
    RETAINED = "RETAINED"
    WATCH = "WATCH"
    CONFLICTED = "CONFLICTED"
    SUSPENDED = "SUSPENDED"
    REVERSED = "REVERSED"
    SUPERSEDED = "SUPERSEDED"


class ReliabilityConflictError(ValueError):
    """Raised when reliability identity or lineage conflicts."""


@dataclass(frozen=True)
class ReliabilityEvidence:
    """Explicit evidence about whether a learned artifact remains reliable."""

    evidence_id: str
    signal: str
    supports_reliability: bool | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_id, str) or not self.evidence_id.strip():
            raise ValueError("evidence_id must be a non-empty string")
        if not isinstance(self.signal, str) or not self.signal.strip():
            raise ValueError("signal must be a non-empty string")
        if self.supports_reliability is not None and not isinstance(self.supports_reliability, bool):
            raise TypeError("supports_reliability must be bool or None")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "signal": self.signal,
            "supports_reliability": self.supports_reliability,
            "provenance": dict(self.provenance),
            "truth_guaranteed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class ReliabilityAssessment:
    """Immutable assessment of current reliability; not a truth claim."""

    assessment_id: str
    artifact_id: str
    evidence_ids: tuple[str, ...]
    state: ReliabilityState
    confidence: float | None
    rationale: str
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("assessment_id", "artifact_id", "rationale"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.evidence_ids, tuple):
            raise TypeError("evidence_ids must be a tuple")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("evidence_ids must be unique")
        if not all(isinstance(item, str) and item.strip() for item in self.evidence_ids):
            raise ValueError("evidence_ids must contain non-empty strings")
        if not self.evidence_ids:
            raise ValueError("at least one evidence item is required")
        if not isinstance(self.state, ReliabilityState):
            try:
                object.__setattr__(self, "state", ReliabilityState(self.state))
            except (TypeError, ValueError) as exc:
                raise TypeError("state must be a ReliabilityState") from exc
        if self.confidence is not None:
            if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
                raise TypeError("confidence must be a number or None")
            if not 0.0 <= float(self.confidence) <= 1.0:
                raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "artifact_id": self.artifact_id,
            "evidence_ids": self.evidence_ids,
            "state": self.state.value,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "provenance": dict(self.provenance),
            "truth_guaranteed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }


@dataclass(frozen=True)
class ReliabilityRecord:
    """Immutable lifecycle record preserving the learned artifact's history."""

    record_id: str
    artifact_id: str
    state: ReliabilityState
    assessment_id: str
    predecessor_id: str | None = None
    resolution_reference: str | None = None
    supersession_reference: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("record_id", "artifact_id", "assessment_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.state, ReliabilityState):
            try:
                object.__setattr__(self, "state", ReliabilityState(self.state))
            except (TypeError, ValueError) as exc:
                raise TypeError("state must be a ReliabilityState") from exc
        if self.state in {ReliabilityState.REVERSED, ReliabilityState.SUPERSEDED}:
            if not isinstance(self.resolution_reference, str) or not self.resolution_reference.strip():
                raise ValueError("terminal reliability states require a resolution reference")
        if self.state == ReliabilityState.SUPERSEDED:
            if not isinstance(self.supersession_reference, str) or not self.supersession_reference.strip():
                raise ValueError("superseded records require a supersession reference")
        if self.predecessor_id is not None and (
            not isinstance(self.predecessor_id, str) or not self.predecessor_id.strip()
        ):
            raise ValueError("predecessor_id must be a non-empty string or None")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "artifact_id": self.artifact_id,
            "state": self.state.value,
            "assessment_id": self.assessment_id,
            "predecessor_id": self.predecessor_id,
            "resolution_reference": self.resolution_reference,
            "supersession_reference": self.supersession_reference,
            "provenance": dict(self.provenance),
            "truth_guaranteed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }


class LearningReliabilityController:
    """Assess reliability and create explicit lifecycle transitions."""

    _ALLOWED_TRANSITIONS = {
        ReliabilityState.RETAINED: {
            ReliabilityState.WATCH,
            ReliabilityState.CONFLICTED,
            ReliabilityState.SUSPENDED,
            ReliabilityState.REVERSED,
            ReliabilityState.SUPERSEDED,
        },
        ReliabilityState.WATCH: {
            ReliabilityState.RETAINED,
            ReliabilityState.CONFLICTED,
            ReliabilityState.SUSPENDED,
            ReliabilityState.REVERSED,
            ReliabilityState.SUPERSEDED,
        },
        ReliabilityState.CONFLICTED: {
            ReliabilityState.SUSPENDED,
            ReliabilityState.RETAINED,
            ReliabilityState.REVERSED,
            ReliabilityState.SUPERSEDED,
        },
        ReliabilityState.SUSPENDED: {
            ReliabilityState.RETAINED,
            ReliabilityState.REVERSED,
            ReliabilityState.SUPERSEDED,
        },
        ReliabilityState.REVERSED: set(),
        ReliabilityState.SUPERSEDED: set(),
    }

    def assess(
        self,
        *,
        artifact_id: str,
        evidence: tuple[ReliabilityEvidence, ...],
        assessment_id: str | None = None,
        confidence: float | None = None,
        provenance: Mapping[str, Any] | None = None,
    ) -> ReliabilityAssessment:
        if not isinstance(artifact_id, str) or not artifact_id.strip():
            raise ValueError("artifact_id must be a non-empty string")
        if not isinstance(evidence, tuple):
            raise TypeError("evidence must be a tuple")
        if not evidence:
            raise ValueError("at least one evidence item is required")
        if not all(isinstance(item, ReliabilityEvidence) for item in evidence):
            raise TypeError("evidence must contain ReliabilityEvidence values")
        ids = [item.evidence_id for item in evidence]
        if len(set(ids)) != len(ids):
            raise ValueError("evidence identities must be unique")
        signals = {item.supports_reliability for item in evidence}
        if True in signals and False in signals:
            state = ReliabilityState.CONFLICTED
            rationale = "explicit evidence contains conflicting reliability signals"
        elif False in signals:
            state = ReliabilityState.SUSPENDED
            rationale = "explicit evidence weakens reliability"
        elif True in signals:
            state = ReliabilityState.RETAINED
            rationale = "explicit evidence supports continued reliability"
        else:
            state = ReliabilityState.WATCH
            rationale = "evidence is directionless; reliability should be monitored"
        return ReliabilityAssessment(
            assessment_id=assessment_id or f"{artifact_id}:reliability",
            artifact_id=artifact_id,
            evidence_ids=tuple(ids),
            state=state,
            confidence=confidence,
            rationale=rationale,
            provenance=provenance or {"source": "m10.6", "artifact_id": artifact_id},
        )

    def initialize(self, assessment: ReliabilityAssessment) -> ReliabilityRecord:
        if not isinstance(assessment, ReliabilityAssessment):
            raise TypeError("assessment must be a ReliabilityAssessment")
        if assessment.state in {ReliabilityState.REVERSED, ReliabilityState.SUPERSEDED}:
            raise ValueError("initial reliability cannot be terminal")
        return ReliabilityRecord(
            record_id=f"{assessment.artifact_id}:reliability:1",
            artifact_id=assessment.artifact_id,
            state=assessment.state,
            assessment_id=assessment.assessment_id,
            provenance=assessment.provenance,
        )

    def transition(
        self,
        record: ReliabilityRecord,
        assessment: ReliabilityAssessment,
        *,
        state: ReliabilityState,
        reference: str | None = None,
        supersession_reference: str | None = None,
    ) -> ReliabilityRecord:
        if not isinstance(record, ReliabilityRecord):
            raise TypeError("record must be a ReliabilityRecord")
        if not isinstance(assessment, ReliabilityAssessment):
            raise TypeError("assessment must be a ReliabilityAssessment")
        if assessment.artifact_id != record.artifact_id:
            raise ValueError("assessment must reference the same artifact")
        if not isinstance(state, ReliabilityState):
            try:
                state = ReliabilityState(state)
            except (TypeError, ValueError) as exc:
                raise TypeError("state must be a ReliabilityState") from exc
        if state not in self._ALLOWED_TRANSITIONS[record.state]:
            raise ValueError(f"transition {record.state.value} -> {state.value} is not allowed")
        if state in {ReliabilityState.REVERSED, ReliabilityState.SUPERSEDED}:
            if not isinstance(reference, str) or not reference.strip():
                raise ValueError("terminal transitions require an explicit reference")
        if state == ReliabilityState.SUPERSEDED:
            if not isinstance(supersession_reference, str) or not supersession_reference.strip():
                raise ValueError("supersession requires an explicit supersession reference")
        return ReliabilityRecord(
            record_id=f"{record.artifact_id}:reliability:{record.record_id.rsplit(':', 1)[-1]}->{state.value.lower()}",
            artifact_id=record.artifact_id,
            state=state,
            assessment_id=assessment.assessment_id,
            predecessor_id=record.record_id,
            resolution_reference=reference.strip() if isinstance(reference, str) else None,
            supersession_reference=(
                supersession_reference.strip()
                if isinstance(supersession_reference, str)
                else None
            ),
            provenance=assessment.provenance,
        )


@dataclass(frozen=True)
class ReliabilityStore:
    """Immutable reliability history; current state never erases prior records."""

    records: tuple[ReliabilityRecord, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.records, tuple):
            raise TypeError("records must be a tuple")
        ids: set[str] = set()
        for record in self.records:
            if not isinstance(record, ReliabilityRecord):
                raise TypeError("records must contain ReliabilityRecord values")
            if record.record_id in ids:
                raise ReliabilityConflictError(f"reliability record '{record.record_id}' is already stored")
            ids.add(record.record_id)
            if record.predecessor_id is not None and record.predecessor_id not in ids:
                raise ReliabilityConflictError("reliability predecessor must already exist in history")

    def append(self, record: ReliabilityRecord) -> "ReliabilityStore":
        if not isinstance(record, ReliabilityRecord):
            raise TypeError("record must be a ReliabilityRecord")
        if any(item.record_id == record.record_id for item in self.records):
            raise ReliabilityConflictError(f"reliability record '{record.record_id}' is already stored")
        if record.predecessor_id is not None and not any(
            item.record_id == record.predecessor_id for item in self.records
        ):
            raise ReliabilityConflictError("reliability predecessor must exist in history")
        return ReliabilityStore(self.records + (record,))

    def history(self, artifact_id: str) -> tuple[ReliabilityRecord, ...]:
        return tuple(item for item in self.records if item.artifact_id == artifact_id)

    def current(self, artifact_id: str) -> ReliabilityRecord | None:
        history = self.history(artifact_id)
        return history[-1] if history else None

    def to_json(self) -> str:
        return json.dumps(
            {"records": [item.to_dict() for item in self.records]},
            sort_keys=True,
            default=str,
        )
