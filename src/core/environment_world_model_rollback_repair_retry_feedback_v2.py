"""M23.56: observational feedback derived from v2 rollback-repair retry outcome."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_outcome_v2 import (
    EnvironmentWorldModelRollbackRepairRetryOutcomeV2,
    EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status,
)


class EnvironmentWorldModelRollbackRepairRetryFeedbackV2Error(RuntimeError):
    """Raised when v2 retry feedback cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status(str, Enum):
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
class EnvironmentWorldModelRollbackRepairRetryFeedbackV2:
    """Immutable observational feedback derived from one verified v2 outcome."""

    feedback_id: str
    outcome_id: str
    integrity_id: str
    execution_id: str
    preparation_id: str
    decision_id: str
    integrity_decision_id: str | None
    proposal_id: str
    assessment_id: str | None
    evaluation_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    outcome_status: EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status
    feedback_status: EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status
    result_fingerprint: str | None = None
    failure_reason: str | None = None
    worker_id: str | None = None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "feedback_id", "outcome_id", "integrity_id", "execution_id", "preparation_id",
            "decision_id", "proposal_id", "environment_id", "expected_model_id", "observed_model_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("integrity_decision_id", "assessment_id", "evaluation_id", "worker_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if not isinstance(self.outcome_status, EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status):
            raise TypeError("outcome_status must be an outcome v2 status")
        if not isinstance(self.feedback_status, EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status):
            raise TypeError("feedback_status must be a retry feedback v2 status")
        if self.feedback_status is EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.SUCCESS_SIGNAL:
            if self.outcome_status is not EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.SUCCESS:
                raise ValueError("SUCCESS_SIGNAL requires SUCCESS outcome")
            if not self.result_fingerprint or self.failure_reason is not None:
                raise ValueError("SUCCESS_SIGNAL requires fingerprint and no failure reason")
        else:
            if self.outcome_status is not EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.FAILURE:
                if self.failure_reason is None or not self.failure_reason.strip():
                    raise ValueError("FAILURE_SIGNAL requires failure reason")
                if self.result_fingerprint is not None:
                    raise ValueError("FAILURE_SIGNAL cannot contain result fingerprint")
            else:
                raise ValueError("FAILURE_SIGNAL requires FAILURE outcome")
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
    def mutates_policy(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryFeedbackV2Service:
    """Convert one verified v2 retry outcome into inert feedback evidence."""

    def record(
        self,
        outcome: EnvironmentWorldModelRollbackRepairRetryOutcomeV2,
        *,
        feedback_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryFeedbackV2:
        if type(outcome) is not EnvironmentWorldModelRollbackRepairRetryOutcomeV2:
            raise TypeError("outcome must be EnvironmentWorldModelRollbackRepairRetryOutcomeV2")
        if not isinstance(feedback_id, str) or not feedback_id.strip():
            raise ValueError("feedback_id must be a non-empty string")
        if outcome.status is EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.SUCCESS:
            feedback_status = EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.SUCCESS_SIGNAL
            default_reason = "verified retry success recorded as observational v2 feedback"
        elif outcome.status is EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.FAILURE:
            feedback_status = EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.FAILURE_SIGNAL
            default_reason = "verified retry failure recorded as observational v2 feedback"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryFeedbackV2Error("unsupported outcome status")

        return EnvironmentWorldModelRollbackRepairRetryFeedbackV2(
            feedback_id=feedback_id,
            outcome_id=outcome.outcome_id,
            integrity_id=outcome.integrity_id,
            execution_id=outcome.execution_id,
            preparation_id=outcome.preparation_id,
            decision_id=outcome.decision_id,
            integrity_decision_id=outcome.integrity_decision_id,
            proposal_id=outcome.proposal_id,
            assessment_id=outcome.assessment_id,
            evaluation_id=outcome.evaluation_id,
            environment_id=outcome.environment_id,
            expected_model_id=outcome.expected_model_id,
            observed_model_id=outcome.observed_model_id,
            outcome_status=outcome.status,
            feedback_status=feedback_status,
            result_fingerprint=outcome.result_fingerprint,
            failure_reason=outcome.failure_reason,
            worker_id=outcome.worker_id,
            reasons=reasons or {"status": default_reason},
            lineage=lineage or {
                "outcome_id": outcome.outcome_id,
                "integrity_id": outcome.integrity_id,
                "execution_id": outcome.execution_id,
                "preparation_id": outcome.preparation_id,
                "decision_id": outcome.decision_id,
                "integrity_decision_id": outcome.integrity_decision_id,
                "proposal_id": outcome.proposal_id,
                "assessment_id": outcome.assessment_id,
                "evaluation_id": outcome.evaluation_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryFeedbackV2",
    "EnvironmentWorldModelRollbackRepairRetryFeedbackV2Error",
    "EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status",
    "EnvironmentWorldModelRollbackRepairRetryFeedbackV2Service",
]
