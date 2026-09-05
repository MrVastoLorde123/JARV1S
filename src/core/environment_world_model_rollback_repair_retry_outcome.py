"""M23.45: bounded outcome classification for rollback-repair retry execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_execution_result_integrity import (
    EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrity,
)
from src.core.environment_world_model_rollback_repair_retry_execution_attempt import (
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus,
)


class EnvironmentWorldModelRollbackRepairRetryOutcomeError(RuntimeError):
    """Raised when retry outcome evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryOutcomeStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"


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
class EnvironmentWorldModelRollbackRepairRetryOutcome:
    """Immutable observational outcome derived from verified retry result-integrity evidence."""

    outcome_id: str
    integrity_id: str
    execution_id: str
    preparation_id: str
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    attempt_status: EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus
    status: EnvironmentWorldModelRollbackRepairRetryOutcomeStatus
    result_fingerprint: str | None = None
    failure_reason: str | None = None
    worker_id: str | None = None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "outcome_id", "integrity_id", "execution_id", "preparation_id",
            "environment_id", "expected_model_id", "observed_model_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.attempt_status, EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus):
            raise TypeError("attempt_status must be an execution-attempt status")
        if not isinstance(self.status, EnvironmentWorldModelRollbackRepairRetryOutcomeStatus):
            raise TypeError("status must be an outcome status")
        if self.worker_id is not None and (not isinstance(self.worker_id, str) or not self.worker_id.strip()):
            raise ValueError("worker_id must be a non-empty string or None")
        if self.status is EnvironmentWorldModelRollbackRepairRetryOutcomeStatus.SUCCESS:
            if self.attempt_status is not EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED:
                raise ValueError("SUCCESS outcome requires a COMPLETED attempt")
            if not self.result_fingerprint or self.failure_reason is not None:
                raise ValueError("SUCCESS outcome requires a fingerprint and no failure reason")
        elif self.status is EnvironmentWorldModelRollbackRepairRetryOutcomeStatus.FAILURE:
            if self.attempt_status is not EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.FAILED:
                raise ValueError("FAILURE outcome requires a FAILED attempt")
            if self.failure_reason is None or not self.failure_reason.strip():
                raise ValueError("FAILURE outcome requires a non-empty failure reason")
            if self.result_fingerprint is not None:
                raise ValueError("FAILURE outcome cannot contain a result fingerprint")
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
    def mutates_persistence(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryOutcomeService:
    """Classify verified retry result-integrity evidence without asserting world-model truth."""

    def classify(
        self,
        integrity: EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrity,
        *,
        outcome_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryOutcome:
        if type(integrity) is not EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrity:
            raise TypeError(
                "integrity must be EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrity"
            )
        if not isinstance(outcome_id, str) or not outcome_id.strip():
            raise ValueError("outcome_id must be a non-empty string")
        if integrity.integrity_status != "VALID":
            raise EnvironmentWorldModelRollbackRepairRetryOutcomeError(
                "outcome classification requires VALID result-integrity evidence"
            )

        if integrity.attempt_status is EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED:
            status = EnvironmentWorldModelRollbackRepairRetryOutcomeStatus.SUCCESS
            default_reason = "verified completed retry attempt classified as an observational success outcome"
        elif integrity.attempt_status is EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.FAILED:
            status = EnvironmentWorldModelRollbackRepairRetryOutcomeStatus.FAILURE
            default_reason = "verified failed retry attempt classified as an observational failure outcome"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryOutcomeError(
                "unsupported execution-attempt status for outcome classification"
            )

        return EnvironmentWorldModelRollbackRepairRetryOutcome(
            outcome_id=outcome_id,
            integrity_id=integrity.integrity_id,
            execution_id=integrity.execution_id,
            preparation_id=integrity.preparation_id,
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
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryOutcomeError",
    "EnvironmentWorldModelRollbackRepairRetryOutcomeStatus",
    "EnvironmentWorldModelRollbackRepairRetryOutcome",
    "EnvironmentWorldModelRollbackRepairRetryOutcomeService",
]
