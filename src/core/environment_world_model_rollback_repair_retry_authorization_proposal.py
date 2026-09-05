"""M23.39: advisory authorization proposal for rollback-repair retry eligibility.

This boundary converts retry-eligibility evidence into a bounded proposal for a
separate authorization decision. It does not grant authorization or execute retry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_eligibility import (
    EnvironmentWorldModelRollbackRepairRetryEligibility,
)


class EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalError(RuntimeError):
    """Raised when a retry authorization proposal cannot be formed safely."""


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
class EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal:
    """Immutable advisory evidence proposing a separate retry authorization decision."""

    proposal_id: str
    environment_id: str
    eligibility_id: str
    action_decision_id: str
    expected_model_id: str
    observed_model_id: str
    requested_action: str
    eligible: bool
    evaluated_at: datetime
    next_eligible_at: datetime | None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "proposal_id",
            "environment_id",
            "eligibility_id",
            "action_decision_id",
            "expected_model_id",
            "observed_model_id",
            "requested_action",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.requested_action not in {"RETRY_REPAIR", "NO_AUTHORIZATION"}:
            raise ValueError("requested_action must be RETRY_REPAIR or NO_AUTHORIZATION")
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


class EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalService:
    """Convert retry eligibility evidence into non-authorizing proposal evidence."""

    def propose(
        self,
        eligibility: EnvironmentWorldModelRollbackRepairRetryEligibility,
        *,
        proposal_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal:
        if type(eligibility) is not EnvironmentWorldModelRollbackRepairRetryEligibility:
            raise TypeError(
                "eligibility must be EnvironmentWorldModelRollbackRepairRetryEligibility"
            )
        if not isinstance(proposal_id, str) or not proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string")

        if eligibility.eligible:
            requested_action = "RETRY_REPAIR"
            default_reason = "eligible retry evidence requests a separate authorization decision"
        else:
            requested_action = "NO_AUTHORIZATION"
            default_reason = "retry eligibility evidence does not support requesting authorization"

        return EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal(
            proposal_id=proposal_id,
            environment_id=eligibility.environment_id,
            eligibility_id=eligibility.eligibility_id,
            action_decision_id=eligibility.action_decision_id,
            expected_model_id=eligibility.expected_model_id,
            observed_model_id=eligibility.observed_model_id,
            requested_action=requested_action,
            eligible=eligibility.eligible,
            evaluated_at=eligibility.evaluated_at,
            next_eligible_at=eligibility.next_eligible_at,
            reasons=reasons or {"status": default_reason},
            lineage=lineage
            or {
                "eligibility_id": eligibility.eligibility_id,
                "action_decision_id": eligibility.action_decision_id,
                "expected_model_id": eligibility.expected_model_id,
                "observed_model_id": eligibility.observed_model_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal",
    "EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalError",
    "EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalService",
]
