"""M23.82: deterministic eligibility evidence for v3 application learning signals."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_signal_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Error(RuntimeError):
    """Raised when application-learning eligibility evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Status(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"


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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3:
    """Immutable advisory eligibility evidence over one M23.81 integrity artifact."""

    eligibility_id: str
    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    classification_id: str
    source_integrity_id: str
    application_id: str
    decision_id: str
    proposal_id: str
    source_proposal_id: str
    feedback_signal_id: str
    feedback_source_id: str
    source_evaluation_id: str
    eligibility_source_id: str
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
    proposal_kind: str
    proposal_status: Any
    decision_status: Any
    application_status: Any
    integrity_status: Any
    outcome_status: Any
    feedback_status: Any
    evaluation_status: Any
    signal_status: Any
    confidence: float
    signal_fingerprint: str
    upstream_proposal_fingerprint: str
    handoff_fingerprint: str
    result_fingerprint: str
    application_fingerprint: str
    authority_principal_id: str | None
    executor_id: str | None
    failure_reason: str | None
    status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Status
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id", "classification_id",
            "source_integrity_id", "application_id", "decision_id", "proposal_id", "source_proposal_id",
            "feedback_signal_id", "feedback_source_id", "source_evaluation_id", "eligibility_source_id",
            "execution_id", "handoff_id", "authorization_id", "validation_id", "source_signal_id", "outcome_id",
            "preparation_id", "environment_id", "expected_model_id", "observed_model_id", "proposal_kind",
            "signal_fingerprint", "upstream_proposal_fingerprint", "handoff_fingerprint", "result_fingerprint",
            "application_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("assessment_id", "authority_principal_id", "executor_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or not self.failure_reason.strip()):
            raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(self.integrity_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status):
            raise TypeError("integrity_status must be an application learning-signal integrity v3 status")
        if not isinstance(self.status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Status):
            raise TypeError("status must be an application-learning eligibility v3 status")
        expected = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status.VALID: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Status.ELIGIBLE,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status.INVALID: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Status.INELIGIBLE,
        }[self.integrity_status]
        if self.status != expected:
            raise ValueError("eligibility status does not match integrity status")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool: return True
    @property
    def is_learning(self) -> bool: return False
    @property
    def permits_learning(self) -> bool: return False
    @property
    def grants_authority(self) -> bool: return False
    @property
    def updates_model(self) -> bool: return False
    @property
    def mutates_memory(self) -> bool: return False
    @property
    def mutates_policy(self) -> bool: return False
    @property
    def mutates_persistence(self) -> bool: return False
    @property
    def schedules_work(self) -> bool: return False
    @property
    def executes_action(self) -> bool: return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Service:
    """Assess application-learning eligibility without performing learning or adaptation."""

    def assess(
        self,
        integrity: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3,
        *,
        eligibility_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3:
        if type(integrity) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3:
            raise TypeError("integrity must be an adaptation-application learning-signal integrity v3 artifact")
        if not isinstance(eligibility_id, str) or not eligibility_id.strip():
            raise ValueError("eligibility_id must be a non-empty string")
        status = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status.VALID: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Status.ELIGIBLE,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status.INVALID: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Status.INELIGIBLE,
        }[integrity.status]
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3(
            eligibility_id=eligibility_id,
            integrity_id=integrity.integrity_id,
            signal_id=integrity.signal_id,
            evaluation_id=integrity.evaluation_id,
            feedback_id=integrity.feedback_id,
            classification_id=integrity.classification_id,
            source_integrity_id=integrity.source_integrity_id,
            application_id=integrity.application_id,
            decision_id=integrity.decision_id,
            proposal_id=integrity.proposal_id,
            source_proposal_id=integrity.source_proposal_id,
            feedback_signal_id=integrity.feedback_signal_id,
            feedback_source_id=integrity.feedback_source_id,
            source_evaluation_id=integrity.source_evaluation_id,
            eligibility_source_id=integrity.integrity_id,
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
            proposal_kind=integrity.proposal_kind,
            proposal_status=integrity.proposal_status,
            decision_status=integrity.decision_status,
            application_status=integrity.application_status,
            integrity_status=integrity.status,
            outcome_status=integrity.outcome_status,
            feedback_status=integrity.feedback_status,
            evaluation_status=integrity.evaluation_status,
            signal_status=integrity.signal_status,
            confidence=integrity.confidence,
            signal_fingerprint=integrity.signal_fingerprint,
            upstream_proposal_fingerprint=integrity.upstream_proposal_fingerprint,
            handoff_fingerprint=integrity.handoff_fingerprint,
            result_fingerprint=integrity.result_fingerprint,
            application_fingerprint=integrity.application_fingerprint,
            authority_principal_id=integrity.authority_principal_id,
            executor_id=integrity.executor_id,
            failure_reason=integrity.failure_reason,
            status=status,
            reasons=reasons if reasons is not None else {"status": f"application learning signal integrity {integrity.status.value.lower()} yields {status.value.lower()} eligibility"},
            lineage=lineage if lineage is not None else {
                "integrity_id": integrity.integrity_id,
                "signal_id": integrity.signal_id,
                "evaluation_id": integrity.evaluation_id,
                "feedback_id": integrity.feedback_id,
                "application_id": integrity.application_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Service",
]
