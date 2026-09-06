"""M23.89: bounded evaluation of one application outcome feedback artifact."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_outcome_classification_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_outcome_feedback_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3Error(RuntimeError):
    """Raised when safe feedback evaluation cannot be formed."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3Status(str, Enum):
    INFORMATIVE = "INFORMATIVE"
    AMBIGUOUS = "AMBIGUOUS"
    NON_INFORMATIVE = "NON_INFORMATIVE"


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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3:
    """Immutable advisory evaluation derived from one M23.88 feedback artifact."""

    evaluation_id: str
    feedback_id: str
    feedback_source_id: str
    classification_id: str
    integrity_id: str
    application_id: str
    decision_id: str
    proposal_id: str
    outcome_id: str
    outcome_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status
    feedback_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status
    confidence: float
    signal_fingerprint: str
    result_fingerprint: str
    application_fingerprint: str
    failure_reason: str | None
    evaluation_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3Status
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "evaluation_id", "feedback_id", "feedback_source_id", "classification_id", "integrity_id", "application_id",
            "decision_id", "proposal_id", "outcome_id", "signal_fingerprint", "result_fingerprint", "application_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.outcome_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status):
            raise TypeError("outcome_status has invalid enum type")
        if not isinstance(self.feedback_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status):
            raise TypeError("feedback_status has invalid enum type")
        if not isinstance(self.evaluation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3Status):
            raise TypeError("evaluation_status has invalid enum type")
        expected_feedback = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.SUCCESS: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.SUCCESS_FEEDBACK,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.FAILURE_FEEDBACK,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.REJECTED: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.REJECTION_FEEDBACK,
        }[self.outcome_status]
        if self.feedback_status != expected_feedback:
            raise ValueError("feedback status does not match outcome classification")
        if self.feedback_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.FAILURE_FEEDBACK:
            if self.failure_reason is None:
                raise ValueError("failure feedback evaluation requires failure evidence")
        elif self.failure_reason is not None:
            raise ValueError("non-failure feedback evaluation cannot carry failure evidence")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def creates_learning_signal(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def executes(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False

    @property
    def mutates_memory(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3Service:
    """Record one bounded evaluation of a validated M23.88 feedback artifact."""

    def evaluate(
        self,
        feedback: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3,
        *,
        evaluation_id: str,
        evaluation_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3Status,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3:
        if type(feedback) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3:
            raise TypeError("feedback must be an application outcome feedback v3 artifact")
        if not isinstance(evaluation_id, str) or not evaluation_id.strip():
            raise ValueError("evaluation_id must be a non-empty string")
        if not isinstance(evaluation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3Status):
            raise TypeError("evaluation_status has invalid enum type")
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3(
            evaluation_id=evaluation_id,
            feedback_id=feedback.feedback_id,
            feedback_source_id=feedback.feedback_source_id,
            classification_id=feedback.classification_id,
            integrity_id=feedback.integrity_id,
            application_id=feedback.application_id,
            decision_id=feedback.decision_id,
            proposal_id=feedback.proposal_id,
            outcome_id=feedback.outcome_id,
            outcome_status=feedback.outcome_status,
            feedback_status=feedback.feedback_status,
            confidence=feedback.confidence,
            signal_fingerprint=feedback.signal_fingerprint,
            result_fingerprint=feedback.result_fingerprint,
            application_fingerprint=feedback.application_fingerprint,
            failure_reason=feedback.failure_reason,
            evaluation_status=evaluation_status,
            reasons=reasons if reasons is not None else {"evaluation": evaluation_status.value},
            lineage=lineage if lineage is not None else {
                "evaluation_id": evaluation_id,
                "feedback_id": feedback.feedback_id,
                "feedback_source_id": feedback.feedback_source_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackEvaluationV3Service",
]
