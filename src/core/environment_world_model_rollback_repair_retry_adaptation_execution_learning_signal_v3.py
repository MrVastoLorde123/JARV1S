"""M23.70: advisory learning signal derived from v3 adaptation-execution feedback evaluation."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_feedback_evaluation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Error(RuntimeError):
    """Raised when a v3 learning signal cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status(str, Enum):
    POSITIVE_SIGNAL = "POSITIVE_SIGNAL"
    NEGATIVE_SIGNAL = "NEGATIVE_SIGNAL"
    REJECTION_SIGNAL = "REJECTION_SIGNAL"


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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3:
    """Immutable advisory learning signal derived from one M23.69 evaluation artifact."""

    signal_id: str
    evaluation_id: str
    feedback_id: str
    classification_id: str
    integrity_id: str
    execution_id: str
    handoff_id: str
    authorization_id: str
    validation_id: str
    proposal_id: str
    eligibility_id: str
    source_signal_id: str
    outcome_id: str
    preparation_id: str
    decision_id: str
    source_proposal_id: str
    source_integrity_id: str
    assessment_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    execution_status: Any
    feedback_status: Any
    evaluation_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status
    signal_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status
    confidence: float
    signal_fingerprint: str
    proposal_fingerprint: str
    handoff_fingerprint: str
    result_fingerprint: str
    authority_principal_id: str | None
    executor_id: str | None
    failure_reason: str | None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "signal_id", "evaluation_id", "feedback_id", "classification_id", "integrity_id",
            "execution_id", "handoff_id", "authorization_id", "validation_id", "proposal_id",
            "eligibility_id", "source_signal_id", "outcome_id", "preparation_id", "decision_id",
            "source_proposal_id", "source_integrity_id", "environment_id", "expected_model_id",
            "observed_model_id", "signal_fingerprint", "proposal_fingerprint", "handoff_fingerprint",
            "result_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("assessment_id", "authority_principal_id", "executor_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if not isinstance(self.evaluation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status):
            raise TypeError("evaluation_status must be a feedback-evaluation v2 status")
        if not isinstance(self.signal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status):
            raise TypeError("signal_status must be a learning-signal v3 status")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or not self.failure_reason.strip()):
            raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")

        expected = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.FAILURE_EVALUATION:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.NEGATIVE_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.REJECTION_EVALUATION:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.REJECTION_SIGNAL,
        }[self.evaluation_status]
        if self.signal_status != expected:
            raise ValueError("signal status does not match evaluation status")

        if self.evaluation_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION:
            if len(self.result_fingerprint) != 64 or self.result_fingerprint == "0" * 64 or self.failure_reason is not None:
                raise ValueError("POSITIVE_SIGNAL requires successful result evidence")
        elif self.evaluation_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.FAILURE_EVALUATION:
            if self.failure_reason is None or self.result_fingerprint != "0" * 64:
                raise ValueError("NEGATIVE_SIGNAL requires failure evidence and zero result fingerprint")
        else:
            if self.authority_principal_id is not None or self.executor_id is not None:
                raise ValueError("REJECTION_SIGNAL cannot carry authority or executor evidence")
            if self.result_fingerprint != "0" * 64 or self.handoff_fingerprint != "0" * 64:
                raise ValueError("REJECTION_SIGNAL requires zero action fingerprints")
            if self.failure_reason is None or not self.failure_reason.strip():
                raise ValueError("REJECTION_SIGNAL requires rejection evidence")

        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_observational(self) -> bool:
        return True

    @property
    def is_advisory_only(self) -> bool:
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
    def updates_model(self) -> bool:
        return False

    @property
    def mutates_memory(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def executes_action(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Service:
    """Emit one immutable v3 learning signal without performing learning or adaptation."""

    def emit(
        self,
        evaluation: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2,
        *,
        signal_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3:
        if type(evaluation) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2:
            raise TypeError(
                "evaluation must be EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2"
            )
        if not isinstance(signal_id, str) or not signal_id.strip():
            raise ValueError("signal_id must be a non-empty string")

        signal_status = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.FAILURE_EVALUATION:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.NEGATIVE_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.REJECTION_EVALUATION:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.REJECTION_SIGNAL,
        }.get(evaluation.evaluation_status)
        if signal_status is None:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Error("unsupported evaluation status")

        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3(
            signal_id=signal_id,
            evaluation_id=evaluation.evaluation_id,
            feedback_id=evaluation.feedback_id,
            classification_id=evaluation.classification_id,
            integrity_id=evaluation.integrity_id,
            execution_id=evaluation.execution_id,
            handoff_id=evaluation.handoff_id,
            authorization_id=evaluation.authorization_id,
            validation_id=evaluation.validation_id,
            proposal_id=evaluation.proposal_id,
            eligibility_id=evaluation.eligibility_id,
            source_signal_id=evaluation.signal_id,
            outcome_id=evaluation.outcome_id,
            preparation_id=evaluation.preparation_id,
            decision_id=evaluation.decision_id,
            source_proposal_id=evaluation.source_proposal_id,
            source_integrity_id=evaluation.source_integrity_id,
            assessment_id=evaluation.assessment_id,
            environment_id=evaluation.environment_id,
            expected_model_id=evaluation.expected_model_id,
            observed_model_id=evaluation.observed_model_id,
            execution_status=evaluation.execution_status,
            feedback_status=evaluation.feedback_status,
            evaluation_status=evaluation.evaluation_status,
            signal_status=signal_status,
            confidence=evaluation.confidence,
            signal_fingerprint=evaluation.signal_fingerprint,
            proposal_fingerprint=evaluation.proposal_fingerprint,
            handoff_fingerprint=evaluation.handoff_fingerprint,
            result_fingerprint=evaluation.result_fingerprint,
            authority_principal_id=evaluation.authority_principal_id,
            executor_id=evaluation.executor_id,
            failure_reason=evaluation.failure_reason,
            reasons=reasons if reasons is not None else {"status": f"{signal_status.value.lower()} emitted as advisory learning signal"},
            lineage=lineage if lineage is not None else {
                "evaluation_id": evaluation.evaluation_id,
                "feedback_id": evaluation.feedback_id,
                "classification_id": evaluation.classification_id,
                "integrity_id": evaluation.integrity_id,
                "execution_id": evaluation.execution_id,
                "handoff_id": evaluation.handoff_id,
                "proposal_id": evaluation.proposal_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Service",
]
