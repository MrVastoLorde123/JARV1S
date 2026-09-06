"""M23.87: classify one integrity-validated learning-adaptation application outcome."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3Status as IntegrityStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status as ApplicationStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status as DecisionStatus,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Error(RuntimeError):
    """Raised when a safe application outcome classification cannot be formed."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    REJECTED = "REJECTED"


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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3:
    """Immutable advisory outcome classification for one valid M23.86 application integrity artifact."""

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
    feedback_id: str
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
    decision_status: DecisionStatus
    application_status: ApplicationStatus
    integrity_status: IntegrityStatus
    outcome_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status
    failure_reason: str | None
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (
            "classification_id", "integrity_id", "application_id", "decision_id", "proposal_id", "source_proposal_id",
            "eligibility_id", "eligibility_source_id", "integrity_source_id", "signal_id", "evaluation_id", "feedback_id",
            "classification_source_id", "application_source_id", "source_integrity_id", "feedback_signal_id", "feedback_source_id",
            "source_evaluation_id", "execution_id", "handoff_id", "authorization_id", "validation_id", "source_signal_id",
            "outcome_id", "preparation_id", "environment_id", "expected_model_id", "observed_model_id", "signal_fingerprint",
            "upstream_proposal_fingerprint", "handoff_fingerprint", "result_fingerprint", "source_application_fingerprint",
            "application_fingerprint", "proposal_kind",
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
            ("decision_status", DecisionStatus),
            ("application_status", ApplicationStatus),
            ("integrity_status", IntegrityStatus),
            ("outcome_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status),
        ):
            if not isinstance(getattr(self, name), enum_type):
                raise TypeError(f"{name} has invalid enum type")
        if self.integrity_status != IntegrityStatus.VALID:
            raise ValueError("outcome classification requires VALID application integrity evidence")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or not self.failure_reason.strip()):
            raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")

        if self.application_status == ApplicationStatus.APPLIED:
            expected_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.SUCCESS
        elif self.application_status == ApplicationStatus.BLOCKED:
            expected_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.REJECTED
        elif self.application_status == ApplicationStatus.NOT_APPLIED:
            if self.decision_status == DecisionStatus.ACCEPTED:
                expected_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE
            elif self.decision_status == DecisionStatus.REJECTED:
                expected_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.REJECTED
            else:
                raise ValueError("unsupported decision/application state")
        else:
            raise ValueError("unsupported application status")

        if self.outcome_status != expected_status:
            raise ValueError("outcome status does not match application/decision state")
        if self.outcome_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE and not self.failure_reason:
            raise ValueError("FAILURE outcome requires failure evidence")
        if self.outcome_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE and self.failure_reason is not None:
            raise ValueError("non-FAILURE outcome cannot carry failure evidence")

        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def creates_feedback(self) -> bool:
        return False

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


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Service:
    """Classify one valid M23.86 application-integrity artifact without side effects."""

    def classify(
        self,
        integrity: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3,
        *,
        classification_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3:
        if type(integrity) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV3:
            raise TypeError("integrity must be an application-learning adaptation application-integrity v3 artifact")
        if not isinstance(classification_id, str) or not classification_id.strip():
            raise ValueError("classification_id must be a non-empty string")
        if integrity.integrity_status != IntegrityStatus.VALID:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Error(
                "cannot classify INVALID application-integrity evidence"
            )

        if integrity.application_status == ApplicationStatus.APPLIED:
            outcome_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.SUCCESS
        elif integrity.application_status == ApplicationStatus.BLOCKED:
            outcome_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.REJECTED
        elif integrity.decision_status == DecisionStatus.ACCEPTED:
            outcome_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.FAILURE
        elif integrity.decision_status == DecisionStatus.REJECTED:
            outcome_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status.REJECTED
        else:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Error(
                "unsupported decision/application state"
            )

        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3(
            classification_id=classification_id,
            integrity_id=integrity.integrity_id,
            application_id=integrity.application_id,
            decision_id=integrity.decision_id,
            proposal_id=integrity.proposal_id,
            source_proposal_id=integrity.source_proposal_id,
            eligibility_id=integrity.eligibility_id,
            eligibility_source_id=integrity.eligibility_source_id,
            integrity_source_id=integrity.integrity_source_id,
            signal_id=integrity.signal_id,
            evaluation_id=integrity.evaluation_id,
            feedback_id=integrity.feedback_id,
            classification_source_id=integrity.integrity_id,
            application_source_id=integrity.application_source_id,
            source_integrity_id=integrity.source_integrity_id,
            feedback_signal_id=integrity.feedback_signal_id,
            feedback_source_id=integrity.feedback_source_id,
            source_evaluation_id=integrity.source_evaluation_id,
            execution_id=integrity.execution_id,
            handoff_id=integrity.handoff_id,
            authorization_id=integrity.authorization_id,
            validation_id=integrity.validation_id,
            source_signal_id=integrity.source_signal_id,
            outcome_id=integrity.outcome_id,
            preparation_id=integrity.preparation_id,
            assessment_id=integrity.assessment_id,
            environment_id=integrity.environment_id,
            expected_model_id=integrity.expected_model_id,
            observed_model_id=integrity.observed_model_id,
            confidence=integrity.confidence,
            signal_fingerprint=integrity.signal_fingerprint,
            upstream_proposal_fingerprint=integrity.upstream_proposal_fingerprint,
            handoff_fingerprint=integrity.handoff_fingerprint,
            result_fingerprint=integrity.result_fingerprint,
            source_application_fingerprint=integrity.source_application_fingerprint,
            application_fingerprint=integrity.application_fingerprint,
            authority_principal_id=integrity.authority_principal_id,
            executor_id=integrity.executor_id,
            proposal_kind=integrity.proposal_kind,
            proposal_status=integrity.proposal_status,
            decision_status=integrity.decision_status,
            application_status=integrity.application_status,
            integrity_status=integrity.integrity_status,
            outcome_status=outcome_status,
            failure_reason=integrity.failure_reason,
            reasons=reasons if reasons is not None else {"outcome": outcome_status.value},
            lineage=lineage if lineage is not None else {
                "classification_id": classification_id,
                "integrity_id": integrity.integrity_id,
                "application_id": integrity.application_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationOutcomeClassificationV3Service",
]
