"""M23.38: bounded retry-policy and eligibility evidence for rollback repair.

This boundary evaluates whether an accepted retry-action decision is eligible
for a later retry, using an explicit immutable policy and supplied retry state.
It does not execute retry, mutate persistence, or authorize capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_follow_up_action_decision import (
    EnvironmentWorldModelRollbackRepairFollowUpActionDecision,
)


class EnvironmentWorldModelRollbackRepairRetryEligibilityError(RuntimeError):
    """Raised when retry eligibility cannot be evaluated safely."""


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


def _validate_aware_datetime(value: datetime, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryPolicy:
    """Immutable bounded policy describing retry-count and backoff limits."""

    max_retries: int
    base_backoff_seconds: float = 0.0
    backoff_multiplier: float = 2.0
    max_backoff_seconds: float = 3600.0

    def __post_init__(self) -> None:
        if isinstance(self.max_retries, bool) or not isinstance(self.max_retries, int):
            raise TypeError("max_retries must be an integer")
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        for name in (
            "base_backoff_seconds",
            "backoff_multiplier",
            "max_backoff_seconds",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number")
            if value < 0:
                raise ValueError(f"{name} must be >= 0")
        if self.backoff_multiplier < 1.0:
            raise ValueError("backoff_multiplier must be >= 1")
        if self.max_backoff_seconds < self.base_backoff_seconds:
            raise ValueError("max_backoff_seconds must be >= base_backoff_seconds")

    def backoff_seconds_for_retry(self, retry_count: int) -> float:
        """Return the deterministic backoff before the next retry."""
        if isinstance(retry_count, bool) or not isinstance(retry_count, int):
            raise TypeError("retry_count must be an integer")
        if retry_count < 0:
            raise ValueError("retry_count must be >= 0")
        delay = self.base_backoff_seconds * (self.backoff_multiplier ** retry_count)
        return min(delay, self.max_backoff_seconds)


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryEligibility:
    """Immutable advisory evidence describing whether another repair retry is eligible."""

    eligibility_id: str
    environment_id: str
    action_decision_id: str
    expected_model_id: str
    observed_model_id: str
    retry_count: int
    max_retries: int
    backoff_seconds: float
    evaluated_at: datetime
    next_eligible_at: datetime | None
    eligible: bool
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "eligibility_id",
            "environment_id",
            "action_decision_id",
            "expected_model_id",
            "observed_model_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.retry_count, bool) or not isinstance(self.retry_count, int):
            raise TypeError("retry_count must be an integer")
        if self.retry_count < 0:
            raise ValueError("retry_count must be >= 0")
        if isinstance(self.max_retries, bool) or not isinstance(self.max_retries, int):
            raise TypeError("max_retries must be an integer")
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if isinstance(self.backoff_seconds, bool) or not isinstance(
            self.backoff_seconds, (int, float)
        ):
            raise TypeError("backoff_seconds must be a number")
        if self.backoff_seconds < 0:
            raise ValueError("backoff_seconds must be >= 0")
        if not isinstance(self.eligible, bool):
            raise TypeError("eligible must be a boolean")
        _validate_aware_datetime(self.evaluated_at, "evaluated_at")
        if self.next_eligible_at is not None:
            _validate_aware_datetime(self.next_eligible_at, "next_eligible_at")
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
    def authorizes_retry(self) -> bool:
        return False

    @property
    def executes_retry(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryEligibilityService:
    """Evaluate retry eligibility without executing or authorizing retry."""

    def evaluate(
        self,
        decision: EnvironmentWorldModelRollbackRepairFollowUpActionDecision,
        policy: EnvironmentWorldModelRollbackRepairRetryPolicy,
        *,
        eligibility_id: str,
        retry_count: int,
        evaluated_at: datetime,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryEligibility:
        if type(decision) is not EnvironmentWorldModelRollbackRepairFollowUpActionDecision:
            raise TypeError(
                "decision must be EnvironmentWorldModelRollbackRepairFollowUpActionDecision"
            )
        if type(policy) is not EnvironmentWorldModelRollbackRepairRetryPolicy:
            raise TypeError("policy must be EnvironmentWorldModelRollbackRepairRetryPolicy")
        if not isinstance(eligibility_id, str) or not eligibility_id.strip():
            raise ValueError("eligibility_id must be a non-empty string")
        if isinstance(retry_count, bool) or not isinstance(retry_count, int):
            raise TypeError("retry_count must be an integer")
        if retry_count < 0:
            raise ValueError("retry_count must be >= 0")
        _validate_aware_datetime(evaluated_at, "evaluated_at")

        if decision.decision == "ACCEPT" and retry_count < policy.max_retries:
            backoff_seconds = policy.backoff_seconds_for_retry(retry_count)
            eligible = True
            next_eligible_at = evaluated_at + timedelta(seconds=backoff_seconds)
            default_reason = "accepted retry action is within the configured retry limit"
        elif decision.decision == "ACCEPT":
            backoff_seconds = 0.0
            eligible = False
            next_eligible_at = None
            default_reason = "accepted retry action exhausted the configured retry limit"
        elif decision.decision == "REJECT":
            backoff_seconds = 0.0
            eligible = False
            next_eligible_at = None
            default_reason = "retry action decision was rejected"
        elif decision.decision == "DEFER":
            backoff_seconds = 0.0
            eligible = False
            next_eligible_at = None
            default_reason = "retry action decision was deferred and is not eligible"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryEligibilityError(
                "action decision is not supported by the retry eligibility contract"
            )

        return EnvironmentWorldModelRollbackRepairRetryEligibility(
            eligibility_id=eligibility_id,
            environment_id=decision.environment_id,
            action_decision_id=decision.decision_id,
            expected_model_id=decision.expected_model_id,
            observed_model_id=decision.observed_model_id,
            retry_count=retry_count,
            max_retries=policy.max_retries,
            backoff_seconds=backoff_seconds,
            evaluated_at=evaluated_at,
            next_eligible_at=next_eligible_at,
            eligible=eligible,
            reasons=reasons or {"status": default_reason},
            lineage=lineage
            or {
                "action_decision_id": decision.decision_id,
                "proposal_id": decision.proposal_id,
                "follow_up_decision_id": decision.follow_up_decision_id,
                "expected_model_id": decision.expected_model_id,
                "observed_model_id": decision.observed_model_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryEligibility",
    "EnvironmentWorldModelRollbackRepairRetryEligibilityError",
    "EnvironmentWorldModelRollbackRepairRetryEligibilityService",
    "EnvironmentWorldModelRollbackRepairRetryPolicy",
]
