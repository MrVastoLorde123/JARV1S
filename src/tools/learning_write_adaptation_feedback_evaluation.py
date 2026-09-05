"""Evaluation boundary after adaptation feedback.

This module interprets immutable adaptation feedback into an inert evaluation
signal/candidate. It does not authorize, mutate memory, retry, revoke, or
execute tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_adaptation_feedback import (
    LearningWriteAdaptationFeedbackEvent,
    LearningWriteAdaptationFeedbackKind,
)


class LearningWriteAdaptationFeedbackEvaluationError(ValueError):
    """Raised when the adaptation-feedback evaluation contract is invalid."""


class LearningWriteAdaptationFeedbackSignalKind(str, Enum):
    """Normalized evaluation signal derived from adaptation feedback."""

    ADAPTATION_SUCCESS_SIGNAL = "adaptation_success_signal"
    ADAPTATION_FAILURE_SIGNAL = "adaptation_failure_signal"


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
class LearningWriteAdaptationFeedbackEvaluationCandidate:
    """Immutable evaluation evidence derived from one adaptation feedback event."""

    evaluation_id: str
    feedback_id: str
    source_feedback_id: str
    candidate_id: str
    execution_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    source_candidate_id: str
    domain: str
    signal: LearningWriteAdaptationFeedbackSignalKind
    confidence: float
    evidence: Mapping[str, Any]
    provenance: Mapping[str, str]
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("evaluation_id", self.evaluation_id),
            ("feedback_id", self.feedback_id),
            ("source_feedback_id", self.source_feedback_id),
            ("candidate_id", self.candidate_id),
            ("execution_id", self.execution_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("source_candidate_id", self.source_candidate_id),
            ("domain", self.domain),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationFeedbackEvaluationError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.signal, LearningWriteAdaptationFeedbackSignalKind):
            raise LearningWriteAdaptationFeedbackEvaluationError(
                "signal must be a LearningWriteAdaptationFeedbackSignalKind member"
            )
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise LearningWriteAdaptationFeedbackEvaluationError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdaptationFeedbackEvaluationError(
                "confidence must be between 0.0 and 1.0"
            )
        if not isinstance(self.evidence, Mapping):
            raise LearningWriteAdaptationFeedbackEvaluationError("evidence must be a mapping")
        if not isinstance(self.provenance, Mapping):
            raise LearningWriteAdaptationFeedbackEvaluationError("provenance must be a mapping")
        if not all(
            isinstance(key, str)
            and key.strip()
            and isinstance(value, str)
            and value.strip()
            for key, value in self.provenance.items()
        ):
            raise LearningWriteAdaptationFeedbackEvaluationError(
                "provenance must contain non-empty string keys and values"
            )

        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_feedback_id": self.feedback_id,
            "learning_write_adaptation_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_write_adaptation_execution_id": self.execution_id,
            "learning_write_adaptation_admission_id": self.admission_id,
            "learning_write_adaptation_proposal_id": self.proposal_id,
            "learning_write_adaptation_decision_id": self.decision_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_feedback_signal": self.signal.value,
            "confidence": float(self.confidence),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
            "learning_write_adaptation_feedback_evaluation_reason": self.reason,
            "adaptation_evaluation": True,
            "learning_written": False,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteAdaptationFeedbackEvaluationService:
    """Evaluate adaptation feedback into an inert evaluation candidate."""

    _DEFAULT_CONFIDENCE = 0.5

    def evaluate(
        self, feedback: LearningWriteAdaptationFeedbackEvent
    ) -> LearningWriteAdaptationFeedbackEvaluationCandidate:
        if not isinstance(feedback, LearningWriteAdaptationFeedbackEvent):
            raise TypeError("feedback must be a LearningWriteAdaptationFeedbackEvent")

        if feedback.kind is LearningWriteAdaptationFeedbackKind.ADAPTATION_SUCCESS:
            signal = LearningWriteAdaptationFeedbackSignalKind.ADAPTATION_SUCCESS_SIGNAL
            reason = "successful adaptation feedback provides an observed positive evaluation signal"
        elif feedback.kind is LearningWriteAdaptationFeedbackKind.ADAPTATION_FAILURE:
            signal = LearningWriteAdaptationFeedbackSignalKind.ADAPTATION_FAILURE_SIGNAL
            reason = "failed adaptation feedback provides an observed operational evaluation signal"
        else:
            raise LearningWriteAdaptationFeedbackEvaluationError(
                "unsupported adaptation feedback kind"
            )

        evidence = {
            "feedback_kind": feedback.kind.value,
            "payload": dict(feedback.payload),
            "feedback_reason": feedback.reason,
        }
        provenance = {
            "source": "learning_write_adaptation_feedback",
            "feedback_id": feedback.feedback_id,
            "source_feedback_id": feedback.source_feedback_id,
            "candidate_id": feedback.candidate_id,
            "execution_id": feedback.execution_id,
            "admission_id": feedback.admission_id,
            "proposal_id": feedback.proposal_id,
            "decision_id": feedback.decision_id,
            "source_candidate_id": feedback.source_candidate_id,
        }
        evaluation_id = self._evaluation_id(
            feedback.feedback_id,
            feedback.source_feedback_id,
            feedback.execution_id,
            signal,
            evidence,
        )

        return LearningWriteAdaptationFeedbackEvaluationCandidate(
            evaluation_id=evaluation_id,
            feedback_id=feedback.feedback_id,
            source_feedback_id=feedback.source_feedback_id,
            candidate_id=feedback.candidate_id,
            execution_id=feedback.execution_id,
            admission_id=feedback.admission_id,
            proposal_id=feedback.proposal_id,
            decision_id=feedback.decision_id,
            source_candidate_id=feedback.source_candidate_id,
            domain=feedback.domain,
            signal=signal,
            confidence=self._DEFAULT_CONFIDENCE,
            evidence=evidence,
            provenance=provenance,
            reason=reason,
        )

    @staticmethod
    def _evaluation_id(
        feedback_id: str,
        source_feedback_id: str,
        execution_id: str,
        signal: LearningWriteAdaptationFeedbackSignalKind,
        evidence: Mapping[str, Any],
    ) -> str:
        payload = json.dumps(
            {
                "feedback_id": feedback_id,
                "source_feedback_id": source_feedback_id,
                "execution_id": execution_id,
                "signal": signal.value,
                "evidence": evidence,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"adaptation-feedback-evaluation-{hashlib.sha256(payload).hexdigest()[:24]}"
