"""Evaluation boundary after future adaptation execution feedback.

This module converts one M22.36 feedback event into immutable evaluation
evidence. Evaluation is observational only: it does not establish truth,
authorize execution, request retry, revoke execution, or mutate memory.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_adaptation_evaluation_execution_feedback import (
    LearningWriteAdaptationEvaluationExecutionFeedback,
    LearningWriteAdaptationEvaluationExecutionFeedbackKind,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError(ValueError):
    """Raised when the M22.37 feedback-evaluation contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionFeedbackSignalKind(str, Enum):
    """Normalized evaluation signal derived from future-execution feedback."""

    EXECUTION_SUCCESS_SIGNAL = "execution_success_signal"
    EXECUTION_FAILURE_SIGNAL = "execution_failure_signal"


def _freeze(value: Any) -> Any:
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
class LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation:
    """Immutable evaluation evidence preserving full M22.34 lineage."""

    evaluation_id: str
    feedback_id: str
    preparation_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    evaluation_id_from_feedback: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    execution_id: str
    source_execution_id: str
    domain: str
    policy_id: str
    signal: LearningWriteAdaptationEvaluationExecutionFeedbackSignalKind
    confidence: float
    evidence: Mapping[str, Any]
    provenance: Mapping[str, str]
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("evaluation_id", self.evaluation_id), ("feedback_id", self.feedback_id),
            ("preparation_id", self.preparation_id), ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id), ("decision_id", self.decision_id),
            ("evaluation_id_from_feedback", self.evaluation_id_from_feedback),
            ("source_feedback_id", self.source_feedback_id), ("candidate_id", self.candidate_id),
            ("source_candidate_id", self.source_candidate_id), ("execution_id", self.execution_id),
            ("source_execution_id", self.source_execution_id), ("domain", self.domain),
            ("policy_id", self.policy_id), ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.signal, LearningWriteAdaptationEvaluationExecutionFeedbackSignalKind):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError("invalid signal")
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError(
                "confidence must be between 0.0 and 1.0"
            )
        if not isinstance(self.evidence, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError("evidence must be a mapping")
        if not isinstance(self.provenance, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError("provenance must be a mapping")
        if not all(isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip() for k, v in self.provenance.items()):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError(
                "provenance must contain non-empty string keys and values"
            )
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_id": self.feedback_id,
            "learning_write_adaptation_evaluation_execution_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_decision_id": self.decision_id,
            "learning_write_adaptation_feedback_evaluation_id": self.evaluation_id_from_feedback,
            "learning_write_adaptation_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_evaluation_execution_id": self.execution_id,
            "learning_write_adaptation_source_execution_id": self.source_execution_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "learning_write_adaptation_evaluation_execution_feedback_signal": self.signal.value,
            "confidence": float(self.confidence),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
            "learning_write_adaptation_evaluation_execution_feedback_evaluation_reason": self.reason,
            "adaptation_evaluation": True,
            "learning_written": False,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "adaptation_truth_proven": False,
        }


class LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationService:
    """Evaluate exactly one M22.36 feedback event into inert evidence."""

    _DEFAULT_CONFIDENCE = 0.5

    def evaluate(
        self, feedback: LearningWriteAdaptationEvaluationExecutionFeedback
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation:
        if not isinstance(feedback, LearningWriteAdaptationEvaluationExecutionFeedback):
            raise TypeError(
                "feedback must be a LearningWriteAdaptationEvaluationExecutionFeedback"
            )
        if feedback.kind is LearningWriteAdaptationEvaluationExecutionFeedbackKind.EXECUTION_SUCCESS:
            signal = LearningWriteAdaptationEvaluationExecutionFeedbackSignalKind.EXECUTION_SUCCESS_SIGNAL
            reason = "successful future adaptation execution feedback provides an observed positive evaluation signal"
        elif feedback.kind is LearningWriteAdaptationEvaluationExecutionFeedbackKind.EXECUTION_FAILURE:
            signal = LearningWriteAdaptationEvaluationExecutionFeedbackSignalKind.EXECUTION_FAILURE_SIGNAL
            reason = "failed future adaptation execution feedback provides an observed operational evaluation signal"
        else:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError("unsupported feedback kind")

        evidence = {
            "feedback_kind": feedback.kind.value,
            "payload": dict(feedback.payload),
            "feedback_reason": feedback.reason,
            "result_fingerprint": feedback.payload.get("result_fingerprint"),
        }
        provenance = {
            "source": "learning_write_adaptation_evaluation_execution_feedback",
            "feedback_id": feedback.feedback_id,
            "execution_id": feedback.execution_id,
            "preparation_id": feedback.preparation_id,
            "admission_id": feedback.admission_id,
            "proposal_id": feedback.proposal_id,
            "decision_id": feedback.decision_id,
            "evaluation_id": feedback.evaluation_id,
            "source_feedback_id": feedback.source_feedback_id,
            "candidate_id": feedback.candidate_id,
            "source_candidate_id": feedback.source_candidate_id,
            "source_execution_id": feedback.source_execution_id,
            "domain": feedback.domain,
            "policy_id": feedback.policy_id,
        }
        evaluation_id = self._evaluation_id(feedback, signal, evidence)
        return LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation(
            evaluation_id=evaluation_id,
            feedback_id=feedback.feedback_id,
            preparation_id=feedback.preparation_id,
            admission_id=feedback.admission_id,
            proposal_id=feedback.proposal_id,
            decision_id=feedback.decision_id,
            evaluation_id_from_feedback=feedback.evaluation_id,
            source_feedback_id=feedback.source_feedback_id,
            candidate_id=feedback.candidate_id,
            source_candidate_id=feedback.source_candidate_id,
            execution_id=feedback.execution_id,
            source_execution_id=feedback.source_execution_id,
            domain=feedback.domain,
            policy_id=feedback.policy_id,
            signal=signal,
            confidence=self._DEFAULT_CONFIDENCE,
            evidence=evidence,
            provenance=provenance,
            reason=reason,
        )

    @staticmethod
    def _evaluation_id(feedback: Any, signal: Any, evidence: Mapping[str, Any]) -> str:
        serialized = json.dumps(
            {
                "feedback_id": feedback.feedback_id,
                "preparation_id": feedback.preparation_id,
                "evaluation_id": feedback.evaluation_id,
                "execution_id": feedback.execution_id,
                "signal": signal.value,
                "evidence": evidence,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"adaptation-evaluation-execution-feedback-{hashlib.sha256(serialized).hexdigest()[:24]}"
