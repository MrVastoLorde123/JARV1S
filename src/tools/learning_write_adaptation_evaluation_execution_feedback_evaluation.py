"""Evaluation boundary for future adaptation execution feedback.

The module accepts both the original M22.36 execution-feedback contract and
M22.44 result-integrity feedback. Evaluation is observational only: it does
not authorize, execute, retry, revoke, mutate memory, or establish adaptation
truth.
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
from .learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError(ValueError):
    """Raised when the feedback-evaluation contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationSignalKind(str, Enum):
    """Normalized evaluation signal across feedback variants."""

    EXECUTION_SUCCESS_SIGNAL = "execution_success_signal"
    EXECUTION_FAILURE_SIGNAL = "execution_failure_signal"
    INTEGRITY_SUCCESS_SIGNAL = "integrity_success_signal"
    INTEGRITY_FAILURE_SIGNAL = "integrity_failure_signal"


# Compatibility alias retained for callers of the earlier M22.37 name.
LearningWriteAdaptationEvaluationExecutionFeedbackSignalKind = (
    LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationSignalKind
)


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
    """Immutable evaluation evidence preserving the complete known lineage."""

    evaluation_id: str
    feedback_id: str
    outcome_id: str | None = None
    execution_id: str = ""
    preparation_id: str = ""
    admission_id: str = ""
    proposal_id: str = ""
    decision_id: str = ""
    evaluation_id_from_feedback: str = ""
    decision_source_evaluation_id: str | None = None
    source_feedback_id: str = ""
    candidate_id: str = ""
    source_candidate_id: str = ""
    execution_source_id: str | None = None
    source_execution_id: str = ""
    source_admission_id: str | None = None
    proposal_source_id: str | None = None
    domain: str = ""
    source_policy_id: str | None = None
    policy_id: str = ""
    signal: LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationSignalKind | str = ""
    confidence: float = 0.5
    evidence: Mapping[str, Any] = None  # type: ignore[assignment]
    provenance: Mapping[str, str] = None  # type: ignore[assignment]
    reason: str = ""

    def __post_init__(self) -> None:
        required_strings = (
            ("evaluation_id", self.evaluation_id),
            ("feedback_id", self.feedback_id),
            ("execution_id", self.execution_id),
            ("preparation_id", self.preparation_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("evaluation_id_from_feedback", self.evaluation_id_from_feedback),
            ("source_feedback_id", self.source_feedback_id),
            ("candidate_id", self.candidate_id),
            ("source_candidate_id", self.source_candidate_id),
            ("source_execution_id", self.source_execution_id),
            ("domain", self.domain),
            ("policy_id", self.policy_id),
            ("reason", self.reason),
        )
        for field_name, value in required_strings:
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError(
                    f"{field_name} must be a non-empty string"
                )

        optional_strings = (
            ("outcome_id", self.outcome_id),
            ("decision_source_evaluation_id", self.decision_source_evaluation_id),
            ("execution_source_id", self.execution_source_id),
            ("source_admission_id", self.source_admission_id),
            ("proposal_source_id", self.proposal_source_id),
            ("source_policy_id", self.source_policy_id),
        )
        for field_name, value in optional_strings:
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError(
                    f"{field_name} must be a non-empty string when provided"
                )

        if not isinstance(self.signal, LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationSignalKind):
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
        if not all(
            isinstance(key, str) and key.strip() and isinstance(value, str) and value.strip()
            for key, value in self.provenance.items()
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError(
                "provenance must contain non-empty string keys and values"
            )
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_id": self.feedback_id,
            "learning_write_adaptation_evaluation_execution_feedback_outcome_id": self.outcome_id,
            "learning_write_adaptation_evaluation_execution_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_decision_id": self.decision_id,
            "learning_write_adaptation_feedback_evaluation_id": self.evaluation_id_from_feedback,
            "learning_write_adaptation_feedback_evaluation_decision_source_id": self.decision_source_evaluation_id,
            "learning_write_adaptation_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_evaluation_execution_source_id": self.execution_source_id,
            "learning_write_adaptation_source_execution_id": self.source_execution_id,
            "learning_write_adaptation_evaluation_execution_source_admission_id": self.source_admission_id,
            "learning_write_adaptation_evaluation_proposal_source_id": self.proposal_source_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_source_policy_id": self.source_policy_id,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "learning_write_adaptation_evaluation_execution_feedback_signal": self.signal.value,
            "confidence": float(self.confidence),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
            "learning_write_adaptation_evaluation_execution_feedback_evaluation_reason": self.reason,
            "feedback_evaluation_observed": True,
            "adaptation_evaluation": True,
            "learning_written": False,
            "memory_mutated": False,
            "memory_mutation_allowed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "adaptation_truth_proven": False,
        }


class LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationService:
    """Evaluate exactly one supported feedback event into inert evidence."""

    _DEFAULT_CONFIDENCE = 0.5

    def evaluate(
        self,
        feedback: (
            LearningWriteAdaptationEvaluationExecutionFeedback
            | LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback
        ),
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation:
        if isinstance(feedback, LearningWriteAdaptationEvaluationExecutionFeedback):
            return self._evaluate_execution_feedback(feedback)
        if isinstance(feedback, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback):
            return self._evaluate_integrity_feedback(feedback)
        raise TypeError("feedback must be a supported adaptation execution feedback type")

    def _evaluate_execution_feedback(
        self, feedback: LearningWriteAdaptationEvaluationExecutionFeedback
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation:
        if feedback.kind is LearningWriteAdaptationEvaluationExecutionFeedbackKind.EXECUTION_SUCCESS:
            signal = LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationSignalKind.EXECUTION_SUCCESS_SIGNAL
            reason = "successful future adaptation execution feedback provides an observed positive evaluation signal"
        elif feedback.kind is LearningWriteAdaptationEvaluationExecutionFeedbackKind.EXECUTION_FAILURE:
            signal = LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationSignalKind.EXECUTION_FAILURE_SIGNAL
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
        return self._build(
            feedback_id=feedback.feedback_id,
            outcome_id=None,
            execution_id=feedback.execution_id,
            preparation_id=feedback.preparation_id,
            admission_id=feedback.admission_id,
            proposal_id=feedback.proposal_id,
            decision_id=feedback.decision_id,
            evaluation_id_from_feedback=feedback.evaluation_id,
            decision_source_evaluation_id=None,
            source_feedback_id=feedback.source_feedback_id,
            candidate_id=feedback.candidate_id,
            source_candidate_id=feedback.source_candidate_id,
            execution_source_id=None,
            source_execution_id=feedback.source_execution_id,
            source_admission_id=None,
            proposal_source_id=None,
            domain=feedback.domain,
            source_policy_id=None,
            policy_id=feedback.policy_id,
            signal=signal,
            evidence=evidence,
            provenance=provenance,
            reason=reason,
        )

    def _evaluate_integrity_feedback(
        self, feedback: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation:
        if feedback.kind is LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_SUCCESS:
            signal = LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationSignalKind.INTEGRITY_SUCCESS_SIGNAL
            reason = "successful result-integrity evidence provides an observed positive evaluation signal"
        elif feedback.kind is LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_FAILURE:
            signal = LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationSignalKind.INTEGRITY_FAILURE_SIGNAL
            reason = "failed result-integrity evidence provides an observed operational evaluation signal"
        else:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackEvaluationError("unsupported feedback kind")

        evidence = {
            "feedback_kind": feedback.kind.value,
            "payload": dict(feedback.payload),
            "feedback_reason": feedback.reason,
            "result_fingerprint": feedback.payload.get("result_fingerprint"),
        }
        provenance = dict(feedback.provenance)
        provenance.update(
            {
                "feedback_id": feedback.feedback_id,
                "outcome_id": feedback.outcome_id,
                "execution_id": feedback.execution_id,
                "preparation_id": feedback.preparation_id,
                "admission_id": feedback.admission_id,
                "proposal_id": feedback.proposal_id,
                "decision_id": feedback.decision_id,
                "evaluation_id": feedback.evaluation_id,
                "decision_source_evaluation_id": feedback.decision_source_evaluation_id,
                "source_feedback_id": feedback.source_feedback_id,
                "candidate_id": feedback.candidate_id,
                "source_candidate_id": feedback.source_candidate_id,
                "execution_source_id": feedback.execution_source_id,
                "source_execution_id": feedback.source_execution_id,
                "source_admission_id": feedback.source_admission_id,
                "proposal_source_id": feedback.proposal_source_id,
                "domain": feedback.domain,
                "source_policy_id": feedback.source_policy_id,
                "policy_id": feedback.policy_id,
            }
        )
        return self._build(
            feedback_id=feedback.feedback_id,
            outcome_id=feedback.outcome_id,
            execution_id=feedback.execution_id,
            preparation_id=feedback.preparation_id,
            admission_id=feedback.admission_id,
            proposal_id=feedback.proposal_id,
            decision_id=feedback.decision_id,
            evaluation_id_from_feedback=feedback.evaluation_id,
            decision_source_evaluation_id=feedback.decision_source_evaluation_id,
            source_feedback_id=feedback.source_feedback_id,
            candidate_id=feedback.candidate_id,
            source_candidate_id=feedback.source_candidate_id,
            execution_source_id=feedback.execution_source_id,
            source_execution_id=feedback.source_execution_id,
            source_admission_id=feedback.source_admission_id,
            proposal_source_id=feedback.proposal_source_id,
            domain=feedback.domain,
            source_policy_id=feedback.source_policy_id,
            policy_id=feedback.policy_id,
            signal=signal,
            evidence=evidence,
            provenance=provenance,
            reason=reason,
        )

    def _build(self, **kwargs: Any) -> LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation:
        evaluation_id = self._evaluation_id(kwargs)
        return LearningWriteAdaptationEvaluationExecutionFeedbackEvaluation(
            evaluation_id=evaluation_id,
            confidence=self._DEFAULT_CONFIDENCE,
            **kwargs,
        )

    @staticmethod
    def _evaluation_id(values: Mapping[str, Any]) -> str:
        serialized = json.dumps(
            {
                "feedback_id": values["feedback_id"],
                "outcome_id": values.get("outcome_id"),
                "preparation_id": values["preparation_id"],
                "admission_id": values["admission_id"],
                "proposal_id": values["proposal_id"],
                "decision_id": values["decision_id"],
                "evaluation_id_from_feedback": values["evaluation_id_from_feedback"],
                "execution_id": values["execution_id"],
                "signal": values["signal"].value,
                "evidence": values["evidence"],
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return (
            "adaptation-evaluation-execution-feedback-evaluation-"
            f"{hashlib.sha256(serialized).hexdigest()[:24]}"
        )
