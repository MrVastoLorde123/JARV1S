"""M23.40: explicit decision evidence for rollback-repair retry authorization.

This boundary converts a bounded retry-authorization proposal into deterministic,
non-executing authorization decision evidence. It does not execute retry or
mutate persistence/history.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_authorization_proposal import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal,
)


class EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionError(RuntimeError):
    """Raised when a retry authorization decision cannot be formed safely."""


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
class EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision:
    """Immutable authorization decision evidence derived from one proposal."""

    decision_id: str
    environment_id: str
    proposal_id: str
    eligibility_id: str
    action_decision_id: str
    expected_model_id: str
    observed_model_id: str
    requested_action: str
    eligible: bool
    evaluated_at: datetime
    next_eligible_at: datetime | None
    decision: str
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "decision_id",
            "environment_id",
            "proposal_id",
            "eligibility_id",
            "action_decision_id",
            "expected_model_id",
            "observed_model_id",
            "requested_action",
            "decision",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.requested_action not in {"RETRY_REPAIR", "NO_AUTHORIZATION"}:
            raise ValueError("requested_action must be RETRY_REPAIR or NO_AUTHORIZATION")
        if not isinstance(self.eligible, bool):
            raise TypeError("eligible must be a boolean")
        if self.decision not in {"ACCEPT", "REJECT", "DEFER"}:
            raise ValueError("decision must be ACCEPT, REJECT, or DEFER")
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


class EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionService:
    """Convert retry authorization proposal evidence into deterministic decision evidence."""

    def decide(
        self,
        proposal: EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal,
        *,
        decision_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision:
        if type(proposal) is not EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal:
            raise TypeError(
                "proposal must be EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal"
            )

        if proposal.requested_action == "RETRY_REPAIR":
            decision = "ACCEPT"
            default_reason = "eligible retry-repair authorization proposal is accepted as non-executing decision evidence"
        elif proposal.requested_action == "NO_AUTHORIZATION":
            decision = "REJECT"
            default_reason = "retry authorization proposal contains no requested authorization"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionError(
                "requested action is not supported by the retry authorization decision contract"
            )

        return EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision(
            decision_id=decision_id,
            environment_id=proposal.environment_id,
            proposal_id=proposal.proposal_id,
            eligibility_id=proposal.eligibility_id,
            action_decision_id=proposal.action_decision_id,
            expected_model_id=proposal.expected_model_id,
            observed_model_id=proposal.observed_model_id,
            requested_action=proposal.requested_action,
            eligible=proposal.eligible,
            evaluated_at=proposal.evaluated_at,
            next_eligible_at=proposal.next_eligible_at,
            decision=decision,
            reasons=reasons or {"status": default_reason},
            lineage=lineage
            or {
                "proposal_id": proposal.proposal_id,
                "eligibility_id": proposal.eligibility_id,
                "action_decision_id": proposal.action_decision_id,
                "expected_model_id": proposal.expected_model_id,
                "observed_model_id": proposal.observed_model_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision",
    "EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionError",
    "EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionService",
]
