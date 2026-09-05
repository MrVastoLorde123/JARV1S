"""M23.46: observational feedback derived from rollback-repair retry outcome."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_outcome import (
    EnvironmentWorldModelRollbackRepairRetryOutcome,
    EnvironmentWorldModelRollbackRepairRetryOutcomeStatus,
)


class EnvironmentWorldModelRollbackRepairRetryFeedbackError(RuntimeError):
    """Raised when retry feedback cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryFeedbackStatus(str, Enum):
    SUCCESS_SIGNAL = "SUCCESS_SIGNAL"
    FAILURE_SIGNAL = "FAILURE_SIGNAL"


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
class EnvironmentWorldModelRollbackRepairRetryFeedback:
    """Immutable observational feedback derived from one verified outcome."""

    feedback_id: str
    outcome_id: str
    execution_id: str
    preparation_id: str
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    outcome_status: str
    feedback_status: EnvironmentWorldModelRollbackRepairRetryFeedbackStatus
    result_fingerprint: str | None = None
    failure_reason: str | None = None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "feedback_id",
            "outcome_id",
            "execution_id",
            "preparation_id",
            "environment_id",
            "expected_model_id",
            "observed_model_id",
            "outcome_status",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.feedback_status, EnvironmentWorldModelRollbackRepairRetryFeedbackStatus):
            raise TypeError("feedback_status must be a retry feedback status")
        if self.outcome_status not in {"SUCCESS", "FAILURE"}:
            raise ValueError("outcome_status must be SUCCESS or FAILURE")
        if self.feedback_status is EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.SUCCESS_SIGNAL:
            if self.outcome_status != "SUCCESS":
                raise ValueError("SUCCESS_SIGNAL requires SUCCESS outcome")
            if not self.result_fingerprint or self.failure_reason is not None:
                raise ValueError("SUCCESS_SIGNAL requires fingerprint and no failure reason")
        else:
            if self.outcome_status != "FAILURE":
                raise ValueError("FAILURE_SIGNAL requires FAILURE outcome")
            if self.failure_reason is None or not self.failure_reason.strip():
                raise ValueError("FAILURE_SIGNAL requires failure reason")
            if self.result_fingerprint is not None:
                raise ValueError("FAILURE_SIGNAL cannot contain result fingerprint")
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
    def recommends_retry(self) -> bool:
        return False

    @property
    def requests_retry(self) -> bool:
        return False

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryFeedbackService:
    """Convert one verified retry outcome into inert feedback evidence."""

    def record(
        self,
        outcome: EnvironmentWorldModelRollbackRepairRetryOutcome,
        *,
        feedback_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryFeedback:
        if type(outcome) is not EnvironmentWorldModelRollbackRepairRetryOutcome:
            raise TypeError(
                "outcome must be EnvironmentWorldModelRollbackRepairRetryOutcome"
            )
        if not isinstance(feedback_id, str) or not feedback_id.strip():
            raise ValueError("feedback_id must be a non-empty string")
        if not isinstance(outcome.status, EnvironmentWorldModelRollbackRepairRetryOutcomeStatus):
            raise EnvironmentWorldModelRollbackRepairRetryFeedbackError(
                "unsupported outcome status"
            )
        if outcome.status is EnvironmentWorldModelRollbackRepairRetryOutcomeStatus.SUCCESS:
            feedback_status = EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.SUCCESS_SIGNAL
            outcome_status = "SUCCESS"
            default_reason = "verified retry success recorded as observational feedback"
        elif outcome.status is EnvironmentWorldModelRollbackRepairRetryOutcomeStatus.FAILURE:
            feedback_status = EnvironmentWorldModelRollbackRepairRetryFeedbackStatus.FAILURE_SIGNAL
            outcome_status = "FAILURE"
            default_reason = "verified retry failure recorded as observational feedback"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryFeedbackError(
                "unsupported outcome status"
            )

        return EnvironmentWorldModelRollbackRepairRetryFeedback(
            feedback_id=feedback_id,
            outcome_id=outcome.outcome_id,
            execution_id=outcome.execution_id,
            preparation_id=outcome.preparation_id,
            environment_id=outcome.environment_id,
            expected_model_id=outcome.expected_model_id,
            observed_model_id=outcome.observed_model_id,
            outcome_status=outcome_status,
            feedback_status=feedback_status,
            result_fingerprint=outcome.result_fingerprint,
            failure_reason=outcome.failure_reason,
            reasons=reasons or {"status": default_reason},
            lineage=lineage or {
                "outcome_id": outcome.outcome_id,
                "execution_id": outcome.execution_id,
                "preparation_id": outcome.preparation_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryFeedback",
    "EnvironmentWorldModelRollbackRepairRetryFeedbackError",
    "EnvironmentWorldModelRollbackRepairRetryFeedbackStatus",
    "EnvironmentWorldModelRollbackRepairRetryFeedbackService",
]
