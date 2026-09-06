"""M23.69: observational evaluation of v2 adaptation-execution feedback."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_feedback_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_outcome_classification_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Error(RuntimeError):
    """Raised when adaptation-execution feedback evaluation evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status(str, Enum):
    SUCCESS_EVALUATION = "SUCCESS_EVALUATION"
    FAILURE_EVALUATION = "FAILURE_EVALUATION"
    REJECTION_EVALUATION = "REJECTION_EVALUATION"


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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2:
    """Immutable observational evaluation derived from one M23.68 feedback artifact."""

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
    signal_id: str
    outcome_id: str
    preparation_id: str
    decision_id: str
    source_proposal_id: str
    source_integrity_id: str
    assessment_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    execution_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status
    feedback_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status
    evaluation_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status
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
            "evaluation_id", "feedback_id", "classification_id", "integrity_id", "execution_id",
            "handoff_id", "authorization_id", "validation_id", "proposal_id", "eligibility_id",
            "signal_id", "outcome_id", "preparation_id", "decision_id", "source_proposal_id",
            "source_integrity_id", "environment_id", "expected_model_id", "observed_model_id",
            "signal_fingerprint", "proposal_fingerprint", "handoff_fingerprint", "result_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("assessment_id", "authority_principal_id", "executor_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if not isinstance(self.execution_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status):
            raise TypeError("execution_status must be an outcome-classification v2 status")
        if not isinstance(self.feedback_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status):
            raise TypeError("feedback_status must be an adaptation-execution feedback v2 status")
        if not isinstance(self.evaluation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status):
            raise TypeError("evaluation_status must be a feedback-evaluation v2 status")
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
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.FAILURE_SIGNAL:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.FAILURE_EVALUATION,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.REJECTION_SIGNAL:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.REJECTION_EVALUATION,
        }[self.feedback_status]
        if self.evaluation_status != expected:
            raise ValueError("evaluation status does not match feedback status")

        if self.evaluation_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION:
            if len(self.result_fingerprint) != 64 or self.result_fingerprint == "0" * 64 or self.failure_reason is not None:
                raise ValueError("SUCCESS_EVALUATION requires successful result evidence")
        elif self.evaluation_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.FAILURE_EVALUATION:
            if self.failure_reason is None or self.result_fingerprint != "0" * 64:
                raise ValueError("FAILURE_EVALUATION requires failure evidence and zero result fingerprint")
        else:
            if self.authority_principal_id is not None or self.executor_id is not None:
                raise ValueError("REJECTION_EVALUATION cannot carry authority or executor evidence")
            if self.result_fingerprint != "0" * 64 or self.handoff_fingerprint != "0" * 64:
                raise ValueError("REJECTION_EVALUATION requires zero action fingerprints")
            if self.failure_reason is None or not self.failure_reason.strip():
                raise ValueError("REJECTION_EVALUATION requires rejection evidence")

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
    def executes_action(self) -> bool:
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


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Service:
    """Evaluate one immutable v2 adaptation-execution feedback artifact inertly."""

    def evaluate(
        self,
        feedback: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2,
        *,
        evaluation_id: str,
        confidence: float | None = None,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2:
        if type(feedback) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2:
            raise TypeError("feedback must be EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2")
        if not isinstance(evaluation_id, str) or not evaluation_id.strip():
            raise ValueError("evaluation_id must be a non-empty string")

        evaluation_status = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.FAILURE_SIGNAL:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.FAILURE_EVALUATION,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.REJECTION_SIGNAL:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.REJECTION_EVALUATION,
        }.get(feedback.feedback_status)
        if evaluation_status is None:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Error("unsupported feedback status")

        resolved_confidence = 1.0 if confidence is None else confidence
        if isinstance(resolved_confidence, bool) or not isinstance(resolved_confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(resolved_confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2(
            evaluation_id=evaluation_id,
            feedback_id=feedback.feedback_id,
            classification_id=feedback.classification_id,
            integrity_id=feedback.integrity_id,
            execution_id=feedback.execution_id,
            handoff_id=feedback.handoff_id,
            authorization_id=feedback.authorization_id,
            validation_id=feedback.validation_id,
            proposal_id=feedback.proposal_id,
            eligibility_id=feedback.eligibility_id,
            signal_id=feedback.signal_id,
            outcome_id=feedback.outcome_id,
            preparation_id=feedback.preparation_id,
            decision_id=feedback.decision_id,
            source_proposal_id=feedback.source_proposal_id,
            source_integrity_id=feedback.source_integrity_id,
            assessment_id=feedback.assessment_id,
            environment_id=feedback.environment_id,
            expected_model_id=feedback.expected_model_id,
            observed_model_id=feedback.observed_model_id,
            execution_status=feedback.execution_status,
            feedback_status=feedback.feedback_status,
            evaluation_status=evaluation_status,
            confidence=float(resolved_confidence),
            signal_fingerprint=feedback.signal_fingerprint,
            proposal_fingerprint=feedback.proposal_fingerprint,
            handoff_fingerprint=feedback.handoff_fingerprint,
            result_fingerprint=feedback.result_fingerprint,
            authority_principal_id=feedback.authority_principal_id,
            executor_id=feedback.executor_id,
            failure_reason=feedback.failure_reason,
            reasons=reasons if reasons is not None else {"status": f"{evaluation_status.value.lower()} recorded as observational evaluation"},
            lineage=lineage if lineage is not None else {
                "feedback_id": feedback.feedback_id,
                "classification_id": feedback.classification_id,
                "integrity_id": feedback.integrity_id,
                "execution_id": feedback.execution_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Service",
]
