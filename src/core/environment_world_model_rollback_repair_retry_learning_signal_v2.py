"""M23.58: observational learning signal derived from v2 feedback evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_feedback_evaluation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2,
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status,
)


class EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Error(RuntimeError):
    """Raised when a v2 learning signal cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status(str, Enum):
    POSITIVE_SIGNAL = "POSITIVE_SIGNAL"
    NEGATIVE_SIGNAL = "NEGATIVE_SIGNAL"


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
class EnvironmentWorldModelRollbackRepairRetryLearningSignalV2:
    """Immutable advisory learning signal derived from one v2 evaluation artifact."""

    signal_id: str
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
    evaluation_status: EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status
    signal_status: EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status
    confidence: float
    result_fingerprint: str | None = None
    failure_reason: str | None = None
    worker_id: str | None = None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "signal_id", "evaluation_id", "feedback_id", "outcome_id", "integrity_id",
            "execution_id", "preparation_id", "decision_id", "proposal_id", "environment_id",
            "expected_model_id", "observed_model_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("integrity_decision_id", "assessment_id", "worker_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if not isinstance(
            self.evaluation_status,
            EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status,
        ):
            raise TypeError("evaluation_status must be a feedback-evaluation v2 status")
        if not isinstance(
            self.signal_status,
            EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status,
        ):
            raise TypeError("signal_status must be a learning-signal v2 status")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        evaluation_status = self.evaluation_status.value
        signal_status = self.signal_status.value
        if evaluation_status == EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.SUCCESS_EVALUATION.value:
            if signal_status != EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.POSITIVE_SIGNAL.value:
                raise ValueError("POSITIVE_SIGNAL requires SUCCESS_EVALUATION")
            if not self.result_fingerprint or self.failure_reason is not None:
                raise ValueError("POSITIVE_SIGNAL requires fingerprint and no failure reason")
        elif evaluation_status == EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.FAILURE_EVALUATION.value:
            if signal_status != EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.NEGATIVE_SIGNAL.value:
                raise ValueError("NEGATIVE_SIGNAL requires FAILURE_EVALUATION")
            if self.failure_reason is None or not self.failure_reason.strip():
                raise ValueError("NEGATIVE_SIGNAL requires failure reason")
            if self.result_fingerprint is not None:
                raise ValueError("NEGATIVE_SIGNAL cannot contain a result fingerprint")
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

    @property
    def updates_model(self) -> bool:
        return False

    @property
    def mutates_memory(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Service:
    """Derive one immutable learning signal without updating models, memory, policy, or authority."""

    def emit(
        self,
        evaluation: EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2,
        *,
        signal_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryLearningSignalV2:
        if type(evaluation) is not EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2:
            raise TypeError(
                "evaluation must be EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2"
            )
        if not isinstance(signal_id, str) or not signal_id.strip():
            raise ValueError("signal_id must be a non-empty string")

        evaluation_status = evaluation.evaluation_status.value
        if (
            evaluation_status
            == EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.SUCCESS_EVALUATION.value
        ):
            signal_status = EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.POSITIVE_SIGNAL
            default_reason = "verified v2 success evaluation emitted as a positive observational learning signal"
        elif (
            evaluation_status
            == EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.FAILURE_EVALUATION.value
        ):
            signal_status = EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.NEGATIVE_SIGNAL
            default_reason = "verified v2 failure evaluation emitted as a negative observational learning signal"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Error(
                "unsupported evaluation status"
            )

        return EnvironmentWorldModelRollbackRepairRetryLearningSignalV2(
            signal_id=signal_id,
            evaluation_id=evaluation.evaluation_id,
            feedback_id=evaluation.feedback_id,
            outcome_id=evaluation.outcome_id,
            integrity_id=evaluation.integrity_id,
            execution_id=evaluation.execution_id,
            preparation_id=evaluation.preparation_id,
            decision_id=evaluation.decision_id,
            integrity_decision_id=evaluation.integrity_decision_id,
            proposal_id=evaluation.proposal_id,
            assessment_id=evaluation.assessment_id,
            environment_id=evaluation.environment_id,
            expected_model_id=evaluation.expected_model_id,
            observed_model_id=evaluation.observed_model_id,
            evaluation_status=evaluation.evaluation_status,
            signal_status=signal_status,
            confidence=evaluation.confidence,
            result_fingerprint=evaluation.result_fingerprint,
            failure_reason=evaluation.failure_reason,
            worker_id=evaluation.worker_id,
            reasons=reasons or {"status": default_reason},
            lineage=lineage or {
                "evaluation_id": evaluation.evaluation_id,
                "feedback_id": evaluation.feedback_id,
                "outcome_id": evaluation.outcome_id,
                "integrity_id": evaluation.integrity_id,
                "execution_id": evaluation.execution_id,
                "preparation_id": evaluation.preparation_id,
                "decision_id": evaluation.decision_id,
                "integrity_decision_id": evaluation.integrity_decision_id,
                "proposal_id": evaluation.proposal_id,
                "assessment_id": evaluation.assessment_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Error",
    "EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status",
    "EnvironmentWorldModelRollbackRepairRetryLearningSignalV2",
    "EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Service",
]
