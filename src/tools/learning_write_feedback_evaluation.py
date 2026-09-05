"""Evaluation boundary after learning-write feedback.

This module converts immutable learning-write feedback into an inert
adaptation candidate. It does not mutate memory or learning state, authorize,
retry, revoke, or execute tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_feedback import (
    LearningWriteFeedbackEvent,
    LearningWriteFeedbackKind,
)


class LearningWriteFeedbackEvaluationError(ValueError):
    """Raised when the feedback-evaluation contract is invalid."""


class LearningWriteFeedbackSignalKind(str, Enum):
    """Normalized adaptation signal derived from learning-write feedback."""

    WRITE_SUCCESS_SIGNAL = "write_success_signal"
    WRITE_FAILURE_SIGNAL = "write_failure_signal"


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
class LearningWriteAdaptationCandidate:
    """Immutable adaptation candidate derived from one learning-write feedback event."""

    candidate_id: str
    feedback_id: str
    execution_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    source_candidate_id: str
    domain: str
    signal: LearningWriteFeedbackSignalKind
    confidence: float
    evidence: Mapping[str, Any]
    provenance: Mapping[str, str]
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("candidate_id", self.candidate_id),
            ("feedback_id", self.feedback_id),
            ("execution_id", self.execution_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("source_candidate_id", self.source_candidate_id),
            ("domain", self.domain),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteFeedbackEvaluationError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.signal, LearningWriteFeedbackSignalKind):
            raise LearningWriteFeedbackEvaluationError(
                "signal must be a LearningWriteFeedbackSignalKind member"
            )
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise LearningWriteFeedbackEvaluationError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteFeedbackEvaluationError(
                "confidence must be between 0.0 and 1.0"
            )
        if not isinstance(self.evidence, Mapping):
            raise LearningWriteFeedbackEvaluationError("evidence must be a mapping")
        if not isinstance(self.provenance, Mapping):
            raise LearningWriteFeedbackEvaluationError("provenance must be a mapping")
        if not all(
            isinstance(key, str) and key.strip()
            and isinstance(value, str) and value.strip()
            for key, value in self.provenance.items()
        ):
            raise LearningWriteFeedbackEvaluationError(
                "provenance must contain non-empty string keys and values"
            )

        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_write_feedback_id": self.feedback_id,
            "learning_write_execution_id": self.execution_id,
            "learning_write_admission_id": self.admission_id,
            "learning_write_proposal_id": self.proposal_id,
            "learning_decision_id": self.decision_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_domain": self.domain,
            "learning_write_signal": self.signal.value,
            "confidence": float(self.confidence),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
            "learning_write_adaptation_reason": self.reason,
            "adaptation_candidate": True,
            "learning_written": self.signal is LearningWriteFeedbackSignalKind.WRITE_SUCCESS_SIGNAL,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteFeedbackEvaluationService:
    """Evaluate learning-write feedback into an inert adaptation candidate."""

    _DEFAULT_CONFIDENCE = 0.5

    def evaluate(
        self, feedback: LearningWriteFeedbackEvent
    ) -> LearningWriteAdaptationCandidate:
        if not isinstance(feedback, LearningWriteFeedbackEvent):
            raise TypeError("feedback must be a LearningWriteFeedbackEvent")

        if feedback.kind is LearningWriteFeedbackKind.WRITE_SUCCESS:
            signal = LearningWriteFeedbackSignalKind.WRITE_SUCCESS_SIGNAL
            reason = "successful learning write provides an observed positive adaptation signal"
        elif feedback.kind is LearningWriteFeedbackKind.WRITE_FAILURE:
            signal = LearningWriteFeedbackSignalKind.WRITE_FAILURE_SIGNAL
            reason = "failed learning write provides an observed operational signal requiring evaluation"
        else:
            raise LearningWriteFeedbackEvaluationError("unsupported learning-write feedback kind")

        evidence = {
            "feedback_kind": feedback.kind.value,
            "payload": dict(feedback.payload),
            "feedback_reason": feedback.reason,
        }
        provenance = {
            "source": "learning_write_feedback",
            "feedback_id": feedback.feedback_id,
            "execution_id": feedback.execution_id,
            "admission_id": feedback.admission_id,
            "proposal_id": feedback.proposal_id,
            "decision_id": feedback.decision_id,
            "candidate_id": feedback.candidate_id,
        }
        candidate_id = self._candidate_id(
            feedback.feedback_id,
            feedback.execution_id,
            signal,
            evidence,
        )

        return LearningWriteAdaptationCandidate(
            candidate_id=candidate_id,
            feedback_id=feedback.feedback_id,
            execution_id=feedback.execution_id,
            admission_id=feedback.admission_id,
            proposal_id=feedback.proposal_id,
            decision_id=feedback.decision_id,
            source_candidate_id=feedback.candidate_id,
            domain=feedback.domain,
            signal=signal,
            confidence=self._DEFAULT_CONFIDENCE,
            evidence=evidence,
            provenance=provenance,
            reason=reason,
        )

    @staticmethod
    def _candidate_id(
        feedback_id: str,
        execution_id: str,
        signal: LearningWriteFeedbackSignalKind,
        evidence: Mapping[str, Any],
    ) -> str:
        payload = json.dumps(
            {
                "feedback_id": feedback_id,
                "execution_id": execution_id,
                "signal": signal.value,
                "evidence": evidence,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"learn-write-adaptation-{hashlib.sha256(payload).hexdigest()[:24]}"
