"""M23.79: observational evaluation of v3 adaptation application feedback."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_feedback_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_outcome_classification_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Error(RuntimeError):
    """Raised when safe application-feedback evaluation cannot be formed."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status(str, Enum):
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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3:
    """Immutable observational evaluation derived from one M23.78 feedback artifact."""

    evaluation_id: str
    feedback_id: str
    classification_id: str
    integrity_id: str
    application_id: str
    decision_id: str
    proposal_id: str
    source_proposal_id: str
    eligibility_id: str
    source_integrity_id: str
    signal_id: str
    source_evaluation_id: str
    feedback_source_id: str
    execution_id: str
    handoff_id: str
    authorization_id: str
    validation_id: str
    source_signal_id: str
    outcome_id: str
    preparation_id: str
    assessment_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    confidence: float
    signal_fingerprint: str
    upstream_proposal_fingerprint: str
    handoff_fingerprint: str
    result_fingerprint: str
    application_fingerprint: str
    authority_principal_id: str | None
    executor_id: str | None
    proposal_kind: str
    proposal_status: Any
    decision_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status
    application_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status
    integrity_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status
    outcome_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status
    feedback_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status
    evaluation_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status
    failure_reason: str | None
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (
            "evaluation_id", "feedback_id", "classification_id", "integrity_id", "application_id", "decision_id",
            "proposal_id", "source_proposal_id", "eligibility_id", "source_integrity_id", "signal_id",
            "source_evaluation_id", "feedback_source_id", "execution_id", "handoff_id", "authorization_id",
            "validation_id", "source_signal_id", "outcome_id", "preparation_id", "environment_id",
            "expected_model_id", "observed_model_id", "signal_fingerprint", "upstream_proposal_fingerprint",
            "handoff_fingerprint", "result_fingerprint", "application_fingerprint", "proposal_kind",
        )
        for name in required:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("assessment_id", "authority_principal_id", "executor_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        for name, enum_type in (
            ("decision_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status),
            ("application_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status),
            ("integrity_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status),
            ("outcome_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status),
            ("feedback_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status),
            ("evaluation_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status),
        ):
            if not isinstance(getattr(self, name), enum_type):
                raise TypeError(f"{name} has invalid enum type")
        if self.integrity_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status.VALID:
            raise ValueError("evaluation requires VALID application-integrity-backed evidence")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or not self.failure_reason.strip()):
            raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")

        expected_evaluation = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.SUCCESS_SIGNAL: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.SUCCESS_EVALUATION,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.FAILURE_SIGNAL: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.FAILURE_EVALUATION,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.REJECTION_SIGNAL: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.REJECTION_EVALUATION,
        }[self.feedback_status]
        if self.evaluation_status != expected_evaluation:
            raise ValueError("evaluation status does not match feedback status")

        expected_outcome_feedback = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status.SUCCESS: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.SUCCESS_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.FAILURE_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status.REJECTED: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.REJECTION_SIGNAL,
        }[self.outcome_status]
        if self.feedback_status != expected_outcome_feedback:
            raise ValueError("feedback status does not match outcome status")

        if self.evaluation_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.SUCCESS_EVALUATION:
            if self.application_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.APPLIED or self.failure_reason is not None:
                raise ValueError("SUCCESS_EVALUATION requires an applied application with no failure evidence")
        elif self.evaluation_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.FAILURE_EVALUATION:
            if self.application_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.NOT_APPLIED or self.decision_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.ACCEPTED or self.failure_reason is None:
                raise ValueError("FAILURE_EVALUATION requires accepted, not-applied failure evidence")
        else:
            if self.authority_principal_id is not None or self.executor_id is not None:
                raise ValueError("REJECTION_EVALUATION cannot carry authority or executor evidence")
            if self.application_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.NOT_APPLIED and self.decision_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.REJECTED:
                raise ValueError("REJECTION_EVALUATION for NOT_APPLIED requires rejected decision evidence")
            if self.application_status not in (
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.NOT_APPLIED,
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.BLOCKED,
            ):
                raise ValueError("REJECTION_EVALUATION requires a non-applied or blocked application")
            if self.failure_reason is not None:
                raise ValueError("REJECTION_EVALUATION cannot carry failure evidence")

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


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Service:
    """Evaluate one immutable v3 adaptation-application feedback artifact inertly."""

    def evaluate(
        self,
        feedback: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3,
        *,
        evaluation_id: str,
        confidence: float | None = None,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3:
        if type(feedback) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3:
            raise TypeError("feedback must be an adaptation-application feedback v3 artifact")
        if not isinstance(evaluation_id, str) or not evaluation_id.strip():
            raise ValueError("evaluation_id must be a non-empty string")

        evaluation_status = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.SUCCESS_SIGNAL: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.SUCCESS_EVALUATION,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.FAILURE_SIGNAL: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.FAILURE_EVALUATION,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.REJECTION_SIGNAL: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status.REJECTION_EVALUATION,
        }.get(feedback.feedback_status)
        if evaluation_status is None:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Error("unsupported feedback status")

        if feedback.integrity_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status.VALID:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Error("cannot evaluate feedback backed by INVALID application integrity")

        resolved_confidence = feedback.confidence if confidence is None else confidence
        if isinstance(resolved_confidence, bool) or not isinstance(resolved_confidence, (int, float)) or not 0.0 <= float(resolved_confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3(
            evaluation_id=evaluation_id,
            feedback_id=feedback.feedback_id,
            classification_id=feedback.classification_id,
            integrity_id=feedback.integrity_id,
            application_id=feedback.application_id,
            decision_id=feedback.decision_id,
            proposal_id=feedback.proposal_id,
            source_proposal_id=feedback.source_proposal_id,
            eligibility_id=feedback.eligibility_id,
            source_integrity_id=feedback.source_integrity_id,
            signal_id=feedback.signal_id,
            source_evaluation_id=feedback.evaluation_id,
            feedback_source_id=feedback.feedback_source_id,
            execution_id=feedback.execution_id,
            handoff_id=feedback.handoff_id,
            authorization_id=feedback.authorization_id,
            validation_id=feedback.validation_id,
            source_signal_id=feedback.source_signal_id,
            outcome_id=feedback.outcome_id,
            preparation_id=feedback.preparation_id,
            assessment_id=feedback.assessment_id,
            environment_id=feedback.environment_id,
            expected_model_id=feedback.expected_model_id,
            observed_model_id=feedback.observed_model_id,
            confidence=float(resolved_confidence),
            signal_fingerprint=feedback.signal_fingerprint,
            upstream_proposal_fingerprint=feedback.upstream_proposal_fingerprint,
            handoff_fingerprint=feedback.handoff_fingerprint,
            result_fingerprint=feedback.result_fingerprint,
            application_fingerprint=feedback.application_fingerprint,
            authority_principal_id=feedback.authority_principal_id,
            executor_id=feedback.executor_id,
            proposal_kind=feedback.proposal_kind,
            proposal_status=feedback.proposal_status,
            decision_status=feedback.decision_status,
            application_status=feedback.application_status,
            integrity_status=feedback.integrity_status,
            outcome_status=feedback.outcome_status,
            feedback_status=feedback.feedback_status,
            evaluation_status=evaluation_status,
            failure_reason=feedback.failure_reason,
            reasons=reasons if reasons is not None else {"evaluation": evaluation_status.value},
            lineage=lineage if lineage is not None else {
                "evaluation_id": evaluation_id,
                "feedback_id": feedback.feedback_id,
                "classification_id": feedback.classification_id,
                "integrity_id": feedback.integrity_id,
                "application_id": feedback.application_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Service",
]
