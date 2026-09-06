"""M23.57: observational evaluation of v2 rollback-repair retry feedback."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_feedback_v2 import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackV2,
    EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status,
)


class EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Error(RuntimeError):
    """Raised when v2 retry-feedback evaluation evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status(str, Enum):
    SUCCESS_EVALUATION = "SUCCESS_EVALUATION"
    FAILURE_EVALUATION = "FAILURE_EVALUATION"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2:
    """Immutable observational evaluation derived from one v2 feedback artifact."""

    evaluation_id: str
    feedback_id: str
    outcome_id: str
    integrity_id: str
    execution_id: str
    preparation_id: str
    decision_id: str
    integrity_decision_id: str | None
    proposal_id: str
    assessment_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    feedback_status: EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status
    evaluation_status: EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status
    confidence: float
    result_fingerprint: str | None = None
    failure_reason: str | None = None
    worker_id: str | None = None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "evaluation_id", "feedback_id", "outcome_id", "integrity_id", "execution_id",
            "preparation_id", "decision_id", "proposal_id", "environment_id",
            "expected_model_id", "observed_model_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("integrity_decision_id", "assessment_id", "worker_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if not isinstance(self.feedback_status, EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status):
            raise TypeError("feedback_status must be a retry feedback v2 status")
        if not isinstance(self.evaluation_status, EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status):
            raise TypeError("evaluation_status must be a feedback-evaluation v2 status")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        feedback_status = self.feedback_status.value
        evaluation_status = self.evaluation_status.value
        if evaluation_status == EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.SUCCESS_EVALUATION.value:
            if feedback_status != EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.SUCCESS_SIGNAL.value:
                raise ValueError("SUCCESS_EVALUATION requires SUCCESS_SIGNAL")
            if not self.result_fingerprint or self.failure_reason is not None:
                raise ValueError("SUCCESS_EVALUATION requires fingerprint and no failure reason")
        elif evaluation_status == EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.FAILURE_EVALUATION.value:
            if feedback_status != EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.FAILURE_SIGNAL.value:
                raise ValueError("FAILURE_EVALUATION requires FAILURE_SIGNAL")
            if self.failure_reason is None or not self.failure_reason.strip():
                raise ValueError("FAILURE_EVALUATION requires failure reason")
            if self.result_fingerprint is not None:
                raise ValueError("FAILURE_EVALUATION cannot contain a result fingerprint")
        else:
            raise ValueError("unsupported evaluation status")

        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_observational(self) -> bool:
        return True

    @property
    def recommends_retry(self) -> bool:
        return False

    @property
    def requests_retry(self) -> bool:
        return False

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Service:
    """Evaluate one immutable v2 feedback artifact without changing authority or policy."""

    def evaluate(
        self,
        feedback: EnvironmentWorldModelRollbackRepairRetryFeedbackV2,
        *,
        evaluation_id: str,
        confidence: float | None = None,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2:
        if type(feedback) is not EnvironmentWorldModelRollbackRepairRetryFeedbackV2:
            raise TypeError("feedback must be EnvironmentWorldModelRollbackRepairRetryFeedbackV2")
        if not isinstance(evaluation_id, str) or not evaluation_id.strip():
            raise ValueError("evaluation_id must be a non-empty string")

        feedback_status = feedback.feedback_status.value
        if feedback_status == EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.SUCCESS_SIGNAL.value:
            evaluation_status = EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.SUCCESS_EVALUATION
            default_reason = "verified v2 success feedback evaluated as a positive observational signal"
        elif feedback_status == EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.FAILURE_SIGNAL.value:
            evaluation_status = EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.FAILURE_EVALUATION
            default_reason = "verified v2 failure feedback evaluated as an observed negative operational signal"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Error("unsupported feedback status")

        resolved_confidence = 1.0 if confidence is None else confidence
        if isinstance(resolved_confidence, bool) or not isinstance(resolved_confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(resolved_confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        return EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2(
            evaluation_id=evaluation_id,
            feedback_id=feedback.feedback_id,
            outcome_id=feedback.outcome_id,
            integrity_id=feedback.integrity_id,
            execution_id=feedback.execution_id,
            preparation_id=feedback.preparation_id,
            decision_id=feedback.decision_id,
            integrity_decision_id=feedback.integrity_decision_id,
            proposal_id=feedback.proposal_id,
            assessment_id=feedback.assessment_id,
            environment_id=feedback.environment_id,
            expected_model_id=feedback.expected_model_id,
            observed_model_id=feedback.observed_model_id,
            feedback_status=feedback.feedback_status,
            evaluation_status=evaluation_status,
            confidence=float(resolved_confidence),
            result_fingerprint=feedback.result_fingerprint,
            failure_reason=feedback.failure_reason,
            worker_id=feedback.worker_id,
            reasons=reasons or {"status": default_reason},
            lineage=lineage or {
                "feedback_id": feedback.feedback_id,
                "outcome_id": feedback.outcome_id,
                "integrity_id": feedback.integrity_id,
                "execution_id": feedback.execution_id,
                "preparation_id": feedback.preparation_id,
                "decision_id": feedback.decision_id,
                "integrity_decision_id": feedback.integrity_decision_id,
                "proposal_id": feedback.proposal_id,
                "assessment_id": feedback.assessment_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Error",
    "EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status",
    "EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2",
    "EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Service",
]
