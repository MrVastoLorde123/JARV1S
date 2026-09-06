"""M23.72: deterministic eligibility evidence for v3 learning signals."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_signal_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Error(RuntimeError):
    """Raised when v3 learning eligibility evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status(str, Enum):
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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3:
    """Immutable advisory eligibility evidence over one v3 learning-signal integrity artifact."""

    eligibility_id: str
    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    classification_id: str
    execution_id: str
    handoff_id: str
    authorization_id: str
    validation_id: str
    proposal_id: str
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
    evaluation_status: Any
    signal_status: Any
    confidence: float
    signal_fingerprint: str
    proposal_fingerprint: str
    handoff_fingerprint: str
    result_fingerprint: str
    authority_principal_id: str | None
    executor_id: str | None
    failure_reason: str | None
    integrity_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status
    status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id",
            "classification_id", "execution_id", "handoff_id", "authorization_id", "validation_id",
            "proposal_id", "source_signal_id", "outcome_id", "preparation_id", "decision_id",
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
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or not self.failure_reason.strip()):
            raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(self.integrity_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status):
            raise TypeError("integrity_status must be a learning-signal integrity v3 status")
        if not isinstance(self.status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status):
            raise TypeError("status must be a learning-eligibility v3 status")
        expected = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.ELIGIBLE,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.INVALID:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.INELIGIBLE,
        }[self.integrity_status]
        if self.status != expected:
            raise ValueError("eligibility status does not match integrity status")
        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def is_learning(self) -> bool:
        return False

    @property
    def permits_learning(self) -> bool:
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


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Service:
    """Assess v3 learning eligibility without performing learning or adaptation."""

    def assess(
        self,
        integrity: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3,
        *,
        eligibility_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3:
        if type(integrity) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3:
            raise TypeError(
                "integrity must be EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3"
            )
        if not isinstance(eligibility_id, str) or not eligibility_id.strip():
            raise ValueError("eligibility_id must be a non-empty string")

        status = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.ELIGIBLE,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.INVALID:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.INELIGIBLE,
        }[integrity.status]

        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3(
            eligibility_id=eligibility_id,
            integrity_id=integrity.integrity_id,
            signal_id=integrity.signal_id,
            evaluation_id=integrity.evaluation_id,
            feedback_id=integrity.feedback_id,
            classification_id=integrity.classification_id,
            execution_id=integrity.execution_id,
            handoff_id=integrity.handoff_id,
            authorization_id=integrity.authorization_id,
            validation_id=integrity.validation_id,
            proposal_id=integrity.proposal_id,
            source_signal_id=integrity.source_signal_id,
            outcome_id=integrity.outcome_id,
            preparation_id=integrity.preparation_id,
            decision_id=integrity.decision_id,
            source_proposal_id=integrity.source_proposal_id,
            source_integrity_id=integrity.source_integrity_id,
            assessment_id=integrity.assessment_id,
            environment_id=integrity.environment_id,
            expected_model_id=integrity.expected_model_id,
            observed_model_id=integrity.observed_model_id,
            execution_status=integrity.execution_status,
            feedback_status=integrity.feedback_status,
            evaluation_status=integrity.evaluation_status,
            signal_status=integrity.signal_status,
            confidence=integrity.confidence,
            signal_fingerprint=integrity.signal_fingerprint,
            proposal_fingerprint=integrity.proposal_fingerprint,
            handoff_fingerprint=integrity.handoff_fingerprint,
            result_fingerprint=integrity.result_fingerprint,
            authority_principal_id=integrity.authority_principal_id,
            executor_id=integrity.executor_id,
            failure_reason=integrity.failure_reason,
            integrity_status=integrity.status,
            status=status,
            reasons=reasons if reasons is not None else {
                "status": f"learning signal integrity {integrity.status.value.lower()} yields {status.value.lower()} eligibility"
            },
            lineage=lineage if lineage is not None else {
                "integrity_id": integrity.integrity_id,
                "signal_id": integrity.signal_id,
                "evaluation_id": integrity.evaluation_id,
                "feedback_id": integrity.feedback_id,
                "classification_id": integrity.classification_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Service",
]