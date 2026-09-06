"""M23.54: result-integrity boundary for v2 retry execution attempts."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_execution_attempt_v2 import (
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Result,
    EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status,
)


class EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2Error(RuntimeError):
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
class EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2:
    """Immutable evidence describing integrity of one v2 execution result."""

    integrity_id: str
    execution_id: str
    preparation_id: str
    decision_id: str
    integrity_decision_id: str | None
    proposal_id: str
    assessment_id: str | None
    evaluation_id: str | None
    feedback_id: str | None
    outcome_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    attempt_status: EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status
    integrity_status: str
    result_fingerprint: str | None = None
    failure_reason: str | None = None
    worker_id: str | None = None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "integrity_id", "execution_id", "preparation_id", "decision_id",
            "proposal_id", "environment_id", "expected_model_id",
            "observed_model_id", "integrity_status",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("integrity_decision_id", "assessment_id", "evaluation_id", "feedback_id", "outcome_id", "worker_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if not isinstance(self.attempt_status, EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status):
            raise TypeError("attempt_status must be an execution-attempt v2 status")
        if self.integrity_status not in {"VALID", "INVALID"}:
            raise ValueError("integrity_status must be VALID or INVALID")
        if self.result_fingerprint is not None and (not isinstance(self.result_fingerprint, str) or not self.result_fingerprint.strip()):
            raise ValueError("result_fingerprint must be a non-empty string or None")
        if self.failure_reason is not None and not isinstance(self.failure_reason, str):
            raise TypeError("failure_reason must be a string or None")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
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
    def schedules_retry(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2Service:
    """Validate one v2 execution attempt as immutable result evidence."""

    def verify(
        self,
        attempt: EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Result,
        *,
        integrity_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2:
        if type(attempt) is not EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Result:
            raise TypeError(
                "attempt must be EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Result"
            )
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")

        status = "VALID"
        result_fingerprint = None
        failure_reason = attempt.failure_reason
        if attempt.status is EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.COMPLETED:
            if attempt.failure_reason is not None:
                status = "INVALID"
            else:
                result_fingerprint = _fingerprint(attempt.observed_result)
        elif attempt.status is EnvironmentWorldModelRollbackRepairRetryExecutionAttemptV2Status.FAILED:
            if attempt.failure_reason is None or not attempt.failure_reason.strip():
                status = "INVALID"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2Error(
                "unsupported execution-attempt status"
            )

        return EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2(
            integrity_id=integrity_id,
            execution_id=attempt.execution_id,
            preparation_id=attempt.preparation_id,
            decision_id=attempt.decision_id,
            integrity_decision_id=attempt.integrity_id,
            proposal_id=attempt.proposal_id,
            assessment_id=attempt.assessment_id,
            evaluation_id=attempt.evaluation_id,
            feedback_id=attempt.feedback_id,
            outcome_id=attempt.outcome_id,
            environment_id=attempt.environment_id,
            expected_model_id=attempt.expected_model_id,
            observed_model_id=attempt.observed_model_id,
            attempt_status=attempt.status,
            integrity_status=status,
            result_fingerprint=result_fingerprint,
            failure_reason=failure_reason,
            worker_id=attempt.worker_id,
            reasons=reasons or {
                "status": "execution result is structurally integral" if status == "VALID" else "execution result evidence is invalid"
            },
            lineage=lineage or {
                "execution_id": attempt.execution_id,
                "preparation_id": attempt.preparation_id,
                "decision_id": attempt.decision_id,
                "integrity_id": attempt.integrity_id,
                "proposal_id": attempt.proposal_id,
                "assessment_id": attempt.assessment_id,
                "evaluation_id": attempt.evaluation_id,
                "feedback_id": attempt.feedback_id,
                "outcome_id": attempt.outcome_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2",
    "EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2Error",
    "EnvironmentWorldModelRollbackRepairRetryExecutionResultIntegrityV2Service",
]
