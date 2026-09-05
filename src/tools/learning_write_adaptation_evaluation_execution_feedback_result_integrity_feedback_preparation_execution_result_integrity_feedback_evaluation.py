"""Evaluation boundary after the M22.52 future execution result-integrity feedback artifact.

M22.53 converts exactly one M22.52 feedback artifact into immutable
observational evaluation evidence. The historical M22.45 evaluation namespace
remains untouched. Evaluation does not establish adaptation truth or grant
execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_preparation_execution_result_integrity_feedback import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationError(ValueError):
    """Raised when the dedicated M22.53 evaluation contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind(str, Enum):
    """Normalized evaluation signal derived from one exact M22.52 feedback artifact."""

    INTEGRITY_SUCCESS_SIGNAL = "integrity_success_signal"
    INTEGRITY_FAILURE_SIGNAL = "integrity_failure_signal"


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
class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation:
    """Immutable evaluation evidence derived from one exact M22.52 feedback artifact."""

    evaluation_id: str
    feedback_id: str
    integrity_id: str
    execution_id: str
    preparation_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    evaluation_id_from_feedback: str
    decision_source_evaluation_id: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    execution_source_id: str
    source_execution_id: str
    source_admission_id: str
    proposal_source_id: str
    domain: str
    source_policy_id: str
    policy_id: str
    signal: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind
    confidence: float
    evidence: Mapping[str, Any]
    provenance: Mapping[str, str]
    reason: str

    def __post_init__(self) -> None:
        for field_name in (
            "evaluation_id", "feedback_id", "integrity_id", "execution_id", "preparation_id",
            "admission_id", "proposal_id", "decision_id", "evaluation_id_from_feedback",
            "decision_source_evaluation_id", "source_feedback_id", "candidate_id",
            "source_candidate_id", "execution_source_id", "source_execution_id",
            "source_admission_id", "proposal_source_id", "domain", "source_policy_id",
            "policy_id", "reason",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(
            self.signal,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind,
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationError(
                "invalid evaluation signal"
            )
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationError(
                "confidence must be numeric"
            )
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationError(
                "confidence must be between 0.0 and 1.0"
            )
        if not isinstance(self.evidence, Mapping) or not self.evidence:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationError(
                "evidence must be a non-empty mapping"
            )
        if not isinstance(self.provenance, Mapping) or not self.provenance:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationError(
                "provenance must be a non-empty mapping"
            )
        if not all(
            isinstance(key, str) and key.strip() and isinstance(value, str) and value.strip()
            for key, value in self.provenance.items()
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationError(
                "provenance must contain non-empty string keys and values"
            )
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_id": self.feedback_id,
            "learning_write_adaptation_evaluation_execution_result_integrity_id": self.integrity_id,
            "learning_write_adaptation_evaluation_execution_id": self.execution_id,
            "learning_write_adaptation_evaluation_execution_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_execution_feedback_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_execution_feedback_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_execution_feedback_decision_id": self.decision_id,
            "learning_write_adaptation_evaluation_feedback_evaluation_id_from_feedback": self.evaluation_id_from_feedback,
            "learning_write_adaptation_evaluation_feedback_decision_source_evaluation_id": self.decision_source_evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_evaluation_execution_source_id": self.execution_source_id,
            "learning_write_adaptation_source_execution_id": self.source_execution_id,
            "learning_write_adaptation_evaluation_execution_source_admission_id": self.source_admission_id,
            "learning_write_adaptation_evaluation_proposal_id": self.proposal_source_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_source_policy_id": self.source_policy_id,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "learning_write_adaptation_evaluation_signal": self.signal.value,
            "confidence": float(self.confidence),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
            "learning_write_adaptation_evaluation_reason": self.reason,
            "feedback_evaluation_observed": True,
            "adaptation_truth_proven": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "memory_mutation_allowed": False,
        }


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationService:
    """Evaluate exactly one M22.52 future execution result-integrity feedback artifact."""

    _DEFAULT_CONFIDENCE = 0.5

    def evaluate(
        self,
        feedback: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation:
        if not isinstance(
            feedback,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback,
        ):
            raise TypeError(
                "feedback must be a LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback"
            )

        if feedback.kind is LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_SUCCESS:
            signal = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_SUCCESS_SIGNAL
            reason = "successful result-integrity feedback provides an observed positive evaluation signal"
        elif feedback.kind is LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_FAILURE:
            signal = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind.INTEGRITY_FAILURE_SIGNAL
            reason = "failed result-integrity feedback provides an observed operational evaluation signal"
        else:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationError(
                "unsupported result-integrity feedback kind"
            )

        evidence = {
            "feedback_kind": feedback.kind.value,
            "payload": dict(feedback.payload),
            "feedback_reason": feedback.reason,
        }
        provenance = dict(feedback.provenance)
        provenance["source"] = "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback"
        evaluation_id = self._evaluation_id(feedback, signal, evidence)

        return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluation(
            evaluation_id=evaluation_id,
            feedback_id=feedback.feedback_id,
            integrity_id=feedback.integrity_id,
            execution_id=feedback.execution_id,
            preparation_id=feedback.preparation_id,
            admission_id=feedback.admission_id,
            proposal_id=feedback.proposal_id,
            decision_id=feedback.decision_id,
            evaluation_id_from_feedback=feedback.evaluation_id_from_feedback,
            decision_source_evaluation_id=feedback.decision_source_evaluation_id,
            source_feedback_id=feedback.source_feedback_id,
            candidate_id=feedback.candidate_id,
            source_candidate_id=feedback.source_candidate_id,
            execution_source_id=feedback.execution_source_id,
            source_execution_id=feedback.source_execution_id,
            source_admission_id=feedback.source_admission_id,
            proposal_source_id=feedback.source_proposal_id,
            domain=feedback.domain,
            source_policy_id=feedback.source_policy_id,
            policy_id=feedback.policy_id,
            signal=signal,
            confidence=self._DEFAULT_CONFIDENCE,
            evidence=evidence,
            provenance=provenance,
            reason=reason,
        )

    @staticmethod
    def _evaluation_id(
        feedback: Any,
        signal: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationSignalKind,
        evidence: Mapping[str, Any],
    ) -> str:
        serialized = json.dumps(
            {
                "feedback_id": feedback.feedback_id,
                "integrity_id": feedback.integrity_id,
                "execution_id": feedback.execution_id,
                "preparation_id": feedback.preparation_id,
                "admission_id": feedback.admission_id,
                "proposal_id": feedback.proposal_id,
                "decision_id": feedback.decision_id,
                "evaluation_id_from_feedback": feedback.evaluation_id_from_feedback,
                "decision_source_evaluation_id": feedback.decision_source_evaluation_id,
                "source_feedback_id": feedback.source_feedback_id,
                "candidate_id": feedback.candidate_id,
                "source_candidate_id": feedback.source_candidate_id,
                "execution_source_id": feedback.execution_source_id,
                "source_execution_id": feedback.source_execution_id,
                "source_admission_id": feedback.source_admission_id,
                "source_proposal_id": feedback.source_proposal_id,
                "domain": feedback.domain,
                "source_policy_id": feedback.source_policy_id,
                "policy_id": feedback.policy_id,
                "signal": signal.value,
                "evidence": evidence,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return "adaptation-evaluation-execution-feedback-result-integrity-feedback-evaluation-preparation-execution-result-integrity-feedback-evaluation-" + hashlib.sha256(serialized).hexdigest()[:24]
