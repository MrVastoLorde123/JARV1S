"""M23.78: observational feedback from verified adaptation application outcome."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_outcome_classification_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Error(RuntimeError):
    """Raised when safe application feedback cannot be formed."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status(str, Enum):
    SUCCESS_SIGNAL = "SUCCESS_SIGNAL"
    FAILURE_SIGNAL = "FAILURE_SIGNAL"
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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3:
    """Immutable observational feedback derived from one M23.77 classification."""

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
    evaluation_id: str
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
    failure_reason: str | None
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (
            "feedback_id", "classification_id", "integrity_id", "application_id", "decision_id", "proposal_id",
            "source_proposal_id", "eligibility_id", "source_integrity_id", "signal_id", "evaluation_id",
            "feedback_source_id", "execution_id", "handoff_id", "authorization_id", "validation_id",
            "source_signal_id", "outcome_id", "preparation_id", "environment_id", "expected_model_id",
            "observed_model_id", "signal_fingerprint", "upstream_proposal_fingerprint", "handoff_fingerprint",
            "result_fingerprint", "application_fingerprint", "proposal_kind",
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
        ):
            if not isinstance(getattr(self, name), enum_type):
                raise TypeError(f"{name} has invalid enum type")
        if self.integrity_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status.VALID:
            raise ValueError("feedback requires VALID application-integrity evidence")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or not self.failure_reason.strip()):
            raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")

        expected = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status.SUCCESS:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.SUCCESS_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.FAILURE_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status.REJECTED:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.REJECTION_SIGNAL,
        }[self.outcome_status]
        if self.feedback_status != expected:
            raise ValueError("feedback status does not match outcome classification")

        if self.outcome_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE:
            if self.application_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.NOT_APPLIED or self.decision_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.ACCEPTED:
                raise ValueError("FAILURE_SIGNAL requires an accepted, not-applied application")
            if self.failure_reason is None:
                raise ValueError("FAILURE_SIGNAL requires failure evidence")
        elif self.failure_reason is not None:
            raise ValueError("non-FAILURE feedback cannot carry failure evidence")

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


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Service:
    """Convert one validated v3 outcome classification into inert observational feedback."""

    def record(
        self,
        classification: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3,
        *,
        feedback_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3:
        if type(classification) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3:
            raise TypeError("classification must be an adaptation-application outcome-classification v3 artifact")
        if not isinstance(feedback_id, str) or not feedback_id.strip():
            raise ValueError("feedback_id must be a non-empty string")

        feedback_status = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status.SUCCESS:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.SUCCESS_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.FAILURE_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status.REJECTED:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.REJECTION_SIGNAL,
        }.get(classification.outcome_status)
        if feedback_status is None:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Error("unsupported outcome classification status")

        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3(
            feedback_id=feedback_id,
            classification_id=classification.classification_id,
            integrity_id=classification.integrity_id,
            application_id=classification.application_id,
            decision_id=classification.decision_id,
            proposal_id=classification.proposal_id,
            source_proposal_id=classification.source_proposal_id,
            eligibility_id=classification.eligibility_id,
            source_integrity_id=classification.source_integrity_id,
            signal_id=classification.signal_id,
            evaluation_id=classification.evaluation_id,
            feedback_source_id=classification.classification_id,
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
            lineage=lineage if lineage is not None else {"feedback_id": feedback_id, "classification_id": classification.classification_id, "integrity_id": classification.integrity_id, "application_id": classification.application_id},
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Service",
]
