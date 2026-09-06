"""M23.55: bounded outcome classification for rollback-repair retry execution v2."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_execution_attempt_v2 import (
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_execution_result_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2,
)


class EnvironmentWorldModelRollbackRepairRetryOutcomeV2Error(RuntimeError):
    """Raised when v2 retry outcome evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


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
class EnvironmentWorldModelRollbackRepairRetryOutcomeV2:
    """Immutable observational outcome derived from valid v2 result-integrity evidence."""

    outcome_id: str
    integrity_id: str
    execution_id: str
    preparation_id: str
    decision_id: str
    integrity_decision_id: str | None
    proposal_id: str
    assessment_id: str | None
    evaluation_id: str | None
    feedback_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    attempt_status: EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status
    status: EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status
    result_fingerprint: str | None = None
    failure_reason: str | None = None
    worker_id: str | None = None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "outcome_id", "integrity_id", "execution_id", "preparation_id",
            "decision_id", "proposal_id", "environment_id", "expected_model_id",
            "observed_model_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in (
            "integrity_decision_id", "assessment_id", "evaluation_id",
            "feedback_id", "worker_id",
        ):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if not isinstance(self.attempt_status, EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status):
            raise TypeError("attempt_status must be an execution-attempt v2 status")
        if not isinstance(self.status, EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status):
            raise TypeError("status must be an outcome v2 status")
        if self.status is EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.SUCCESS:
            if self.attempt_status is not EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.COMPLETED:
                raise ValueError("SUCCESS outcome requires a COMPLETED attempt")
            if not self.result_fingerprint or self.failure_reason is not None:
                raise ValueError("SUCCESS outcome requires a fingerprint and no failure reason")
        elif self.status is EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.FAILURE:
            if self.attempt_status is not EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.FAILED:
                raise ValueError("FAILURE outcome requires a FAILED attempt")
            if self.failure_reason is None or not self.failure_reason.strip():
                raise ValueError("FAILURE outcome requires a non-empty failure reason")
            if self.result_fingerprint is not None:
                raise ValueError("FAILURE outcome cannot contain a result fingerprint")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_observational(self) -> bool:
        return True

    @property
    def grants_execution_authority(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def schedules_retry(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryOutcomeV2Service:
    """Classify valid v2 result-integrity evidence without asserting world-model truth."""

    def classify(
        self,
        integrity: EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2,
        *,
        outcome_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryOutcomeV2:
        if type(integrity) is not EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2:
            raise TypeError(
                "integrity must be EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2"
            )
        if not isinstance(outcome_id, str) or not outcome_id.strip():
            raise ValueError("outcome_id must be a non-empty string")
        if integrity.integrity_status != "VALID":
            raise EnvironmentWorldModelRollbackRepairRetryOutcomeV2Error(
                "outcome classification requires VALID v2 result-integrity evidence"
            )

        if integrity.attempt_status is EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.COMPLETED:
            status = EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.SUCCESS
            default_reason = "verified completed v2 retry attempt classified as an observational success outcome"
        elif integrity.attempt_status is EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.FAILED:
            status = EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.FAILURE
            default_reason = "verified failed v2 retry attempt classified as an observational failure outcome"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryOutcomeV2Error(
                "unsupported execution-attempt v2 status for outcome classification"
            )

        return EnvironmentWorldModelRollbackRepairRetryOutcomeV2(
            outcome_id=outcome_id,
            integrity_id=integrity.integrity_id,
            execution_id=integrity.execution_id,
            preparation_id=integrity.preparation_id,
            decision_id=integrity.decision_id,
            integrity_decision_id=integrity.integrity_decision_id,
            proposal_id=integrity.proposal_id,
            assessment_id=integrity.assessment_id,
            evaluation_id=integrity.evaluation_id,
            feedback_id=integrity.feedback_id,
            environment_id=integrity.environment_id,
            expected_model_id=integrity.expected_model_id,
            observed_model_id=integrity.observed_model_id,
            attempt_status=integrity.attempt_status,
            status=status,
            result_fingerprint=integrity.result_fingerprint,
            failure_reason=integrity.failure_reason,
            worker_id=integrity.worker_id,
            reasons=reasons or {"status": default_reason},
            lineage=lineage or {
                "integrity_id": integrity.integrity_id,
                "execution_id": integrity.execution_id,
                "preparation_id": integrity.preparation_id,
                "decision_id": integrity.decision_id,
                "integrity_decision_id": integrity.integrity_decision_id,
                "proposal_id": integrity.proposal_id,
                "assessment_id": integrity.assessment_id,
                "evaluation_id": integrity.evaluation_id,
                "feedback_id": integrity.feedback_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryOutcomeV2Error",
    "EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status",
    "EnvironmentWorldModelRollbackRepairRetryOutcomeV2",
    "EnvironmentWorldModelRollbackRepairRetryOutcomeV2Service",
]
