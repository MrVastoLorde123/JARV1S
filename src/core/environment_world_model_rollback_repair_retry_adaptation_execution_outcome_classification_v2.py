"""M23.67: classify one integrity-validated adaptation execution result."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_result_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Error(RuntimeError):
    """Raised when a valid outcome classification cannot be established safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status(str, Enum):
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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2:
    """Immutable advisory classification for one integrity-validated adaptation execution."""

    classification_id: str
    integrity_id: str
    execution_id: str
    handoff_id: str
    authorization_id: str
    validation_id: str
    proposal_id: str
    eligibility_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    preparation_id: str
    decision_id: str
    source_proposal_id: str
    source_integrity_id: str
    assessment_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    execution_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status
    integrity_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status
    classification_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status
    confidence: float
    signal_fingerprint: str
    proposal_kind: str
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
            "classification_id", "integrity_id", "execution_id", "handoff_id", "authorization_id",
            "validation_id", "proposal_id", "eligibility_id", "signal_id", "evaluation_id", "feedback_id",
            "outcome_id", "preparation_id", "decision_id", "source_proposal_id", "source_integrity_id",
            "environment_id", "expected_model_id", "observed_model_id", "signal_fingerprint", "proposal_kind",
            "proposal_fingerprint", "handoff_fingerprint", "result_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.assessment_id is not None and (not isinstance(self.assessment_id, str) or not self.assessment_id.strip()):
            raise ValueError("assessment_id must be None or a non-empty string")
        if not isinstance(self.execution_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status):
            raise TypeError("execution_status has invalid enum type")
        if not isinstance(self.integrity_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status):
            raise TypeError("integrity_status has invalid enum type")
        if not isinstance(self.classification_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status):
            raise TypeError("classification_status has invalid enum type")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.authority_principal_id is not None and (not isinstance(self.authority_principal_id, str) or not self.authority_principal_id.strip()):
            raise ValueError("authority_principal_id must be None or a non-empty string")
        if self.executor_id is not None and (not isinstance(self.executor_id, str) or not self.executor_id.strip()):
            raise ValueError("executor_id must be None or a non-empty string")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or not self.failure_reason.strip()):
            raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        if self.integrity_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.VALID:
            raise ValueError("outcome classification requires VALID integrity evidence")

        expected = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.FAILED:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.FAILURE,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.REJECTED:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.REJECTED,
        }[self.execution_status]
        if self.classification_status != expected:
            raise ValueError("classification status does not match execution status")

        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def creates_learning_signal(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
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


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Service:
    """Classify one valid M23.66 integrity artifact without causing side effects."""

    def classify(
        self,
        integrity: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2,
        *,
        classification_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2:
        if type(integrity) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2:
            raise TypeError(
                "integrity must be EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2"
            )
        if not isinstance(classification_id, str) or not classification_id.strip():
            raise ValueError("classification_id must be a non-empty string")
        if integrity.integrity_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.VALID:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Error(
                "cannot classify INVALID execution-result integrity evidence"
            )

        classification_status = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.FAILED:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.FAILURE,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.REJECTED:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.REJECTED,
        }[integrity.execution_status]

        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2(
            classification_id=classification_id,
            integrity_id=integrity.integrity_id,
            execution_id=integrity.execution_id,
            handoff_id=integrity.handoff_id,
            authorization_id=integrity.authorization_id,
            validation_id=integrity.validation_id,
            proposal_id=integrity.proposal_id,
            eligibility_id=integrity.eligibility_id,
            signal_id=integrity.signal_id,
            evaluation_id=integrity.evaluation_id,
            feedback_id=integrity.feedback_id,
            outcome_id=integrity.outcome_id,
            preparation_id=integrity.preparation_id,
            decision_id=integrity.decision_id,
            source_proposal_id=integrity.source_proposal_id,
            source_integrity_id=integrity.integrity_id,
            assessment_id=integrity.assessment_id,
            environment_id=integrity.environment_id,
            expected_model_id=integrity.expected_model_id,
            observed_model_id=integrity.observed_model_id,
            execution_status=integrity.execution_status,
            integrity_status=integrity.integrity_status,
            classification_status=classification_status,
            confidence=integrity.confidence,
            signal_fingerprint=integrity.signal_fingerprint,
            proposal_kind=integrity.proposal_kind,
            proposal_fingerprint=integrity.proposal_fingerprint,
            handoff_fingerprint=integrity.handoff_fingerprint,
            result_fingerprint=integrity.result_fingerprint,
            authority_principal_id=integrity.authority_principal_id,
            executor_id=integrity.executor_id,
            failure_reason=integrity.failure_reason,
            reasons=reasons or {"classification": classification_status.value.lower()},
            lineage=lineage or {"integrity_id": integrity.integrity_id, "execution_id": integrity.execution_id},
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Service",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status",
]
