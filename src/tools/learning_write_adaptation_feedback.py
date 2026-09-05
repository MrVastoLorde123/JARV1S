"""Feedback boundary after learning-write adaptation outcome integrity.

This module converts a verified adaptation outcome into immutable feedback
that can later be evaluated. It does not mutate memory, authorize, retry,
revoke, or execute tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_adaptation_outcome import (
    LearningWriteAdaptationOutcome,
    LearningWriteAdaptationOutcomeStatus,
)


class LearningWriteAdaptationFeedbackError(ValueError):
    """Raised when the adaptation-feedback contract is invalid."""


class LearningWriteAdaptationFeedbackKind(str, Enum):
    """Normalized feedback classification for an adaptation outcome."""

    ADAPTATION_SUCCESS = "adaptation_success"
    ADAPTATION_FAILURE = "adaptation_failure"


def _freeze(value: Any) -> Any:
    """Recursively freeze common mutable containers into immutable snapshots."""
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class LearningWriteAdaptationFeedbackEvent:
    """Immutable feedback evidence derived from one adaptation outcome."""

    feedback_id: str
    execution_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    candidate_id: str
    source_feedback_id: str
    source_candidate_id: str
    domain: str
    kind: LearningWriteAdaptationFeedbackKind
    payload: Mapping[str, Any]
    provenance: Mapping[str, str]
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("feedback_id", self.feedback_id),
            ("execution_id", self.execution_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("candidate_id", self.candidate_id),
            ("source_feedback_id", self.source_feedback_id),
            ("source_candidate_id", self.source_candidate_id),
            ("domain", self.domain),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationFeedbackError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.kind, LearningWriteAdaptationFeedbackKind):
            raise LearningWriteAdaptationFeedbackError(
                "kind must be a LearningWriteAdaptationFeedbackKind member"
            )
        if not isinstance(self.payload, Mapping):
            raise LearningWriteAdaptationFeedbackError("payload must be a mapping")
        if not isinstance(self.provenance, Mapping):
            raise LearningWriteAdaptationFeedbackError("provenance must be a mapping")
        if not all(
            isinstance(key, str)
            and key.strip()
            and isinstance(value, str)
            and value.strip()
            for key, value in self.provenance.items()
        ):
            raise LearningWriteAdaptationFeedbackError(
                "provenance must contain non-empty string keys and values"
            )

        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_feedback_id": self.feedback_id,
            "learning_write_adaptation_execution_id": self.execution_id,
            "learning_write_adaptation_admission_id": self.admission_id,
            "learning_write_adaptation_proposal_id": self.proposal_id,
            "learning_write_adaptation_decision_id": self.decision_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_write_feedback_id": self.source_feedback_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_feedback_kind": self.kind.value,
            "payload": dict(self.payload),
            "provenance": dict(self.provenance),
            "learning_write_adaptation_feedback_reason": self.reason,
            "adaptation_applied": self.kind
            is LearningWriteAdaptationFeedbackKind.ADAPTATION_SUCCESS,
            "learning_written": False,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteAdaptationFeedbackService:
    """Convert an adaptation outcome into inert feedback evidence."""

    def from_outcome(
        self, outcome: LearningWriteAdaptationOutcome
    ) -> LearningWriteAdaptationFeedbackEvent:
        if not isinstance(outcome, LearningWriteAdaptationOutcome):
            raise TypeError("outcome must be a LearningWriteAdaptationOutcome")

        if outcome.status is LearningWriteAdaptationOutcomeStatus.SUCCEEDED:
            kind = LearningWriteAdaptationFeedbackKind.ADAPTATION_SUCCESS
            payload = {
                "outcome_status": outcome.status.value,
                "adaptation_result": outcome.adaptation_result,
                "result_fingerprint": outcome.result_fingerprint,
            }
            reason = "successful adaptation outcome provides observable positive feedback"
        elif outcome.status is LearningWriteAdaptationOutcomeStatus.FAILED:
            kind = LearningWriteAdaptationFeedbackKind.ADAPTATION_FAILURE
            payload = {
                "outcome_status": outcome.status.value,
                "reason": outcome.reason,
            }
            reason = "failed adaptation outcome provides observable operational feedback"
        else:
            raise LearningWriteAdaptationFeedbackError("unsupported adaptation outcome status")

        provenance = {
            "source": "learning_write_adaptation_outcome",
            "feedback_id": outcome.feedback_id,
            "execution_id": outcome.execution_id,
            "admission_id": outcome.admission_id,
            "proposal_id": outcome.proposal_id,
            "decision_id": outcome.decision_id,
            "candidate_id": outcome.candidate_id,
            "source_candidate_id": outcome.source_candidate_id,
        }
        feedback_id = self._feedback_id(outcome, kind, payload)
        return LearningWriteAdaptationFeedbackEvent(
            feedback_id=feedback_id,
            execution_id=outcome.execution_id,
            admission_id=outcome.admission_id,
            proposal_id=outcome.proposal_id,
            decision_id=outcome.decision_id,
            candidate_id=outcome.candidate_id,
            source_feedback_id=outcome.feedback_id,
            source_candidate_id=outcome.source_candidate_id,
            domain=outcome.domain,
            kind=kind,
            payload=payload,
            provenance=provenance,
            reason=reason,
        )

    @staticmethod
    def _feedback_id(
        outcome: LearningWriteAdaptationOutcome,
        kind: LearningWriteAdaptationFeedbackKind,
        payload: Mapping[str, Any],
    ) -> str:
        serialized = json.dumps(
            {
                "source_feedback_id": outcome.feedback_id,
                "execution_id": outcome.execution_id,
                "admission_id": outcome.admission_id,
                "proposal_id": outcome.proposal_id,
                "decision_id": outcome.decision_id,
                "candidate_id": outcome.candidate_id,
                "source_candidate_id": outcome.source_candidate_id,
                "domain": outcome.domain,
                "kind": kind.value,
                "payload": payload,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"adaptation-feedback-{hashlib.sha256(serialized).hexdigest()[:24]}"
