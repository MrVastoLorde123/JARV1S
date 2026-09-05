"""M23.47: bounded evaluation of rollback-repair retry feedback."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_feedback import (
    EnvironmentWorldModelRollbackRepairRetryFeedback,
    EnvironmentWorldModelRollbackRepairRetryFeedbackStatus,
)


class EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationError(RuntimeError):
    """Raised when retry-feedback evaluation evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus(str, Enum):
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
class EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluation:
    """Immutable observational evaluation derived from one M23.46 feedback artifact."""

    evaluation_id: str
    feedback_id: str
    outcome_id: str
    execution_id: str
    preparation_id: str
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    feedback_status: EnvironmentWorldModelRollbackRepairRetryFeedbackStatus
    evaluation_status: EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus
    confidence: float
    result_fingerprint: str | None = None
    failure_reason: str | None = None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "evaluation_id",
            "feedback_id",
            "outcome_id",
            "execution_id",
            "preparation_id",
            "environment_id",
            "expected_model_id",
            "observed_model_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.feedback_status, EnvironmentWorldModelRollbackRepairRetryFeedbackStatus):
            raise TypeError("feedback_status must be a retry feedback status")
        if not isinstance(self.evaluation_status, EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus):
            raise TypeError("evaluation_status must be a feedback-evaluation status")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.evaluation_status is EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus.SUCCESS_EVALUATION:
            if self.feedback_status is not EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.SUCCESS_SIGNAL:
                raise ValueError("SUCCESS_EVALUATION requires SUCCESS_SIGNAL")
            if not self.result_fingerprint or self.failure_reason is not None:
                raise ValueError("SUCCESS_EVALUATION requires fingerprint and no failure reason")
        elif self.evaluation_status is EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus.FAILURE_EVALUATION:
            if self.feedback_status is not EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.FAILURE_SIGNAL:
                raise ValueError("FAILURE_EVALUATION requires FAILURE_SIGNAL")
            if self.failure_reason is None or not self.failure_reason.strip():
                raise ValueError("FAILURE_EVALUATION requires failure reason")
            if self.result_fingerprint is not None:
                raise ValueError("FAILURE_EVALUATION cannot contain a result fingerprint")
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
    def mutates_persistence(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationService:
    """Evaluate one immutable retry feedback artifact without changing policy or authority."""

    def evaluate(
        self,
        feedback: EnvironmentWorldModelRollbackRepairRetryFeedback,
        *,
        evaluation_id: str,
        confidence: float | None = None,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluation:
        if type(feedback) is not EnvironmentWorldModelRollbackRepairRetryFeedback:
            raise TypeError(
                "feedback must be EnvironmentWorldModelRollbackRepairRetryFeedback"
            )
        if not isinstance(evaluation_id, str) or not evaluation_id.strip():
            raise ValueError("evaluation_id must be a non-empty string")

        if feedback.feedback_status is EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.SUCCESS_SIGNAL:
            evaluation_status = EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus.SUCCESS_EVALUATION
            default_confidence = 1.0
            default_reason = "verified success feedback evaluated as a positive observational signal"
        elif feedback.feedback_status is EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.FAILURE_SIGNAL:
            evaluation_status = EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus.FAILURE_EVALUATION
            default_confidence = 1.0
            default_reason = "verified failure feedback evaluated as an observed negative operational signal"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationError(
                "unsupported feedback status"
            )

        resolved_confidence = default_confidence if confidence is None else confidence
        if isinstance(resolved_confidence, bool) or not isinstance(resolved_confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(resolved_confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        return EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluation(
            evaluation_id=evaluation_id,
            feedback_id=feedback.feedback_id,
            outcome_id=feedback.outcome_id,
            execution_id=feedback.execution_id,
            preparation_id=feedback.preparation_id,
            environment_id=feedback.environment_id,
            expected_model_id=feedback.expected_model_id,
            observed_model_id=feedback.observed_model_id,
            feedback_status=feedback.feedback_status,
            evaluation_status=evaluation_status,
            confidence=float(resolved_confidence),
            result_fingerprint=feedback.result_fingerprint,
            failure_reason=feedback.failure_reason,
            reasons=reasons or {"status": default_reason},
            lineage=lineage or {
                "feedback_id": feedback.feedback_id,
                "outcome_id": feedback.outcome_id,
                "execution_id": feedback.execution_id,
                "preparation_id": feedback.preparation_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationError",
    "EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus",
    "EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluation",
    "EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationService",
]
