"""M23.44: result-integrity boundary for rollback-repair retry execution attempts."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_execution_attempt import (
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult,
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus,
)
from src.core.environment_world_model_rollback_repair_retry_execution_preparation import (
    EnvironmentWorldModelRollbackRepairRetryExecutionPreparation,
)


class EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityError(RuntimeError):
    """Raised when execution-attempt result integrity cannot be established safely."""


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


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonicalize(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, (set, frozenset)):
        normalized = [_canonicalize(item) for item in value]
        return sorted(normalized, key=lambda item: json.dumps(item, sort_keys=True, default=repr, separators=(",", ":")))
    return value


def _fingerprint(value: Any) -> str:
    payload = json.dumps(
        _canonicalize(value),
        sort_keys=True,
        default=repr,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrity:
    """Immutable evidence describing whether one retry execution result is structurally integral."""

    integrity_id: str
    execution_id: str
    preparation_id: str
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    attempt_status: EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus
    integrity_status: str
    result_fingerprint: str | None = None
    failure_reason: str | None = None
    worker_id: str | None = None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "integrity_id",
            "execution_id",
            "preparation_id",
            "environment_id",
            "expected_model_id",
            "observed_model_id",
            "integrity_status",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.attempt_status, EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus):
            raise TypeError("attempt_status must be an execution-attempt status")
        if self.integrity_status not in {"VALID", "INVALID"}:
            raise ValueError("integrity_status must be VALID or INVALID")
        if self.worker_id is not None and (not isinstance(self.worker_id, str) or not self.worker_id.strip()):
            raise ValueError("worker_id must be a non-empty string or None")
        if self.result_fingerprint is not None and (
            not isinstance(self.result_fingerprint, str) or not self.result_fingerprint.strip()
        ):
            raise ValueError("result_fingerprint must be a non-empty string or None")
        if self.failure_reason is not None and not isinstance(self.failure_reason, str):
            raise TypeError("failure_reason must be a string or None")
        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def observed_result_integrity(self) -> bool:
        return self.integrity_status == "VALID"

    @property
    def is_advisory_only(self) -> bool:
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


class EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityService:
    """Validate one retry execution attempt against the exact preparation that produced it."""

    def verify(
        self,
        preparation: EnvironmentWorldModelRollbackRepairRetryExecutionPreparation,
        attempt: EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult,
        *,
        integrity_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrity:
        if type(preparation) is not EnvironmentWorldModelRollbackRepairRetryExecutionPreparation:
            raise TypeError(
                "preparation must be EnvironmentWorldModelRollbackRepairRetryExecutionPreparation"
            )
        if type(attempt) is not EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult:
            raise TypeError(
                "attempt must be EnvironmentWorldModelRollbackRepairRetryExecutionAttemptResult"
            )
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")

        lineage_match = (
            attempt.preparation_id == preparation.preparation_id
            and attempt.environment_id == preparation.environment_id
            and attempt.expected_model_id == preparation.expected_model_id
            and attempt.observed_model_id == preparation.observed_model_id
        )

        if not lineage_match:
            status = "INVALID"
            result_fingerprint = None
            failure_reason = attempt.reason
            default_reason = "execution attempt conflicts with its exact preparation identity or model lineage"
        elif attempt.status is EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.COMPLETED:
            if attempt.reason is not None:
                status = "INVALID"
                result_fingerprint = None
                failure_reason = attempt.reason
                default_reason = "completed execution attempt contains a failure reason"
            else:
                status = "VALID"
                result_fingerprint = _fingerprint(attempt.observed_result)
                failure_reason = None
                default_reason = "completed execution result is structurally consistent with its preparation"
        elif attempt.status is EnvironmentWorldModelRollbackRepairRetryExecutionAttemptStatus.FAILED:
            if attempt.reason is None or not attempt.reason.strip():
                status = "INVALID"
                result_fingerprint = None
                failure_reason = attempt.reason
                default_reason = "failed execution attempt is missing its required failure reason"
            else:
                status = "VALID"
                result_fingerprint = None
                failure_reason = attempt.reason
                default_reason = "failed execution result is structurally consistent with its preparation"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityError(
                "unsupported execution-attempt status"
            )

        return EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrity(
            integrity_id=integrity_id,
            execution_id=attempt.execution_id,
            preparation_id=preparation.preparation_id,
            environment_id=preparation.environment_id,
            expected_model_id=preparation.expected_model_id,
            observed_model_id=preparation.observed_model_id,
            attempt_status=attempt.status,
            integrity_status=status,
            result_fingerprint=result_fingerprint,
            failure_reason=failure_reason,
            worker_id=attempt.worker_id,
            reasons=reasons or {"status": default_reason},
            lineage=lineage
            or {
                "execution_id": attempt.execution_id,
                "preparation_id": preparation.preparation_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrity",
    "EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityError",
    "EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityService",
]
