"""M23.88: observational feedback from one outcome classification."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_outcome_classification_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Error(RuntimeError):
    """Raised when safe outcome feedback cannot be formed."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status(str, Enum):
    SUCCESS_FEEDBACK = "SUCCESS_FEEDBACK"
    FAILURE_FEEDBACK = "FAILURE_FEEDBACK"
    REJECTION_FEEDBACK = "REJECTION_FEEDBACK"


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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3:
    """Immutable observational feedback derived from one M23.87 outcome classification."""

    feedback_id: str
    classification_id: str
    integrity_id: str
    application_id: str
    decision_id: str
    proposal_id: str
    source_proposal_id: str
    eligibility_id: str
    eligibility_source_id: str
    integrity_source_id: str
    signal_id: str
    evaluation_id: str
    classification_source_id: str
    application_source_id: str
    source_integrity_id: str
    feedback_signal_id: str
    feedback_source_id: str
    source_evaluation_id: str
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
    source_application_fingerprint: str
    application_fingerprint: str
    authority_principal_id: str | None
    executor_id: str | None
    proposal_kind: str
    proposal_status: Any
    decision_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status
    application_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status
    integrity_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3Status
    outcome_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status
    feedback_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status
    failure_reason: str | None
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (
            "feedback_id", "classification_id", "integrity_id", "application_id", "decision_id", "proposal_id", "source_proposal_id",
            "eligibility_id", "eligibility_source_id", "integrity_source_id", "signal_id", "evaluation_id", "classification_source_id",
            "application_source_id", "source_integrity_id", "feedback_signal_id", "feedback_source_id", "source_evaluation_id",
            "execution_id", "handoff_id", "authorization_id", "validation_id", "source_signal_id", "outcome_id", "preparation_id",
            "environment_id", "expected_model_id", "observed_model_id", "signal_fingerprint", "upstream_proposal_fingerprint",
            "handoff_fingerprint", "result_fingerprint", "source_application_fingerprint", "application_fingerprint", "proposal_kind",
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
            ("decision_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status),
            ("application_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status),
            ("integrity_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3Status),
            ("outcome_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status),
            ("feedback_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status),
        ):
            if not isinstance(getattr(self, name), enum_type):
                raise TypeError(f"{name} has invalid enum type")
        if self.integrity_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3Status.VALID:
            raise ValueError("feedback requires VALID application-integrity evidence")
        expected = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.SUCCESS: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.SUCCESS_FEEDBACK,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.FAILURE_FEEDBACK,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.REJECTED: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.REJECTION_FEEDBACK,
        }[self.outcome_status]
        if self.feedback_status != expected:
            raise ValueError("feedback status does not match outcome classification")
        if self.outcome_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE:
            if self.application_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.NOT_APPLIED:
                raise ValueError("FAILURE_FEEDBACK requires NOT_APPLIED application evidence")
            if self.decision_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.ACCEPTED:
                raise ValueError("FAILURE_FEEDBACK requires ACCEPTED decision evidence")
            if self.failure_reason is None:
                raise ValueError("FAILURE_FEEDBACK requires failure evidence")
        elif self.failure_reason is not None:
            raise ValueError("non-failure feedback cannot carry failure evidence")
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


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Service:
    """Convert one validated M23.87 outcome classification into inert feedback evidence."""

    def record(
        self,
        classification: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3,
        *,
        feedback_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3:
        if type(classification) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3:
            raise TypeError("classification must be an application-learning adaptation application outcome-classification v3 artifact")
        if not isinstance(feedback_id, str) or not feedback_id.strip():
            raise ValueError("feedback_id must be a non-empty string")
        if classification.outcome_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.SUCCESS:
            feedback_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.SUCCESS_FEEDBACK
        elif classification.outcome_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE:
            feedback_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.FAILURE_FEEDBACK
        elif classification.outcome_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.REJECTED:
            feedback_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status.REJECTION_FEEDBACK
        else:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Error("unsupported outcome classification status")
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3(
            feedback_id=feedback_id,
            classification_id=classification.classification_id,
            integrity_id=classification.integrity_id,
            application_id=classification.application_id,
            decision_id=classification.decision_id,
            proposal_id=classification.proposal_id,
            source_proposal_id=classification.source_proposal_id,
            eligibility_id=classification.eligibility_id,
            eligibility_source_id=classification.eligibility_source_id,
            integrity_source_id=classification.integrity_source_id,
            signal_id=classification.signal_id,
            evaluation_id=classification.evaluation_id,
            classification_source_id=classification.classification_source_id,
            application_source_id=classification.application_source_id,
            source_integrity_id=classification.source_integrity_id,
            feedback_signal_id=classification.feedback_signal_id,
            feedback_source_id=classification.classification_id,
            source_evaluation_id=classification.source_evaluation_id,
            execution_id=classification.execution_id,
            handoff_id=classification.handoff_id,
            authorization_id=classification.authorization_id,
            validation_id=classification.validation_id,
            source_signal_id=classification.source_signal_id,
            outcome_id=classification.outcome_id,
            preparation_id=classification.preparation_id,
            assessment_id=classification.assessment_id,
            environment_id=classification.environment_id,
            expected_model_id=classification.expected_model_id,
            observed_model_id=classification.observed_model_id,
            confidence=classification.confidence,
            signal_fingerprint=classification.signal_fingerprint,
            upstream_proposal_fingerprint=classification.upstream_proposal_fingerprint,
            handoff_fingerprint=classification.handoff_fingerprint,
            result_fingerprint=classification.result_fingerprint,
            source_application_fingerprint=classification.source_application_fingerprint,
            application_fingerprint=classification.application_fingerprint,
            authority_principal_id=classification.authority_principal_id,
            executor_id=classification.executor_id,
            proposal_kind=classification.proposal_kind,
            proposal_status=classification.proposal_status,
            decision_status=classification.decision_status,
            application_status=classification.application_status,
            integrity_status=classification.integrity_status,
            outcome_status=classification.outcome_status,
            feedback_status=feedback_status,
            failure_reason=classification.failure_reason,
            reasons=reasons if reasons is not None else {"feedback": feedback_status.value},
            lineage=lineage if lineage is not None else {
                "feedback_id": feedback_id,
                "classification_id": classification.classification_id,
                "integrity_id": classification.integrity_id,
                "application_id": classification.application_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeFeedbackV3Service",
]
