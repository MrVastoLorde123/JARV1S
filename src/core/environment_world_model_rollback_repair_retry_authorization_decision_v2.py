"""M23.50: assessment-bound retry authorization decision evidence.

This boundary consumes exactly one M23.49 authorization proposal and produces
immutable decision evidence. It remains non-executing: decision evidence is
not execution, scheduling, or persistence mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_authorization_proposal import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal,
)


class EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2Error(RuntimeError):
    """Raised when an M23.50 authorization decision cannot be formed safely."""


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
class EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2:
    """Immutable M23.50 decision evidence derived from one M23.49 proposal."""

    decision_id: str
    proposal_id: str
    assessment_id: str | None
    evaluation_id: str | None
    feedback_id: str | None
    outcome_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    requested_action: str
    assessment_status: str | None
    eligible: bool | None
    retry_count: int | None
    max_retries: int | None
    evaluated_at: datetime
    next_eligible_at: datetime | None
    decision: str
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "decision_id",
            "proposal_id",
            "environment_id",
            "expected_model_id",
            "observed_model_id",
            "requested_action",
            "decision",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("assessment_id", "evaluation_id", "feedback_id", "outcome_id", "assessment_status"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if self.requested_action not in {"RETRY_REPAIR", "NO_AUTHORIZATION"}:
            raise ValueError("requested_action must be RETRY_REPAIR or NO_AUTHORIZATION")
        if self.eligible is not None and not isinstance(self.eligible, bool):
            raise TypeError("eligible must be a boolean or None")
        for name in ("retry_count", "max_retries"):
            value = getattr(self, name)
            if value is not None:
                if isinstance(value, bool) or not isinstance(value, int):
                    raise TypeError(f"{name} must be an integer or None")
                if value < 0:
                    raise ValueError(f"{name} must be >= 0")
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
    def is_decision_evidence(self) -> bool:
        return True

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def executes_retry(self) -> bool:
        return False

    @property
    def schedules_retry(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2Service:
    """Convert one M23.49 proposal into deterministic non-executing decision evidence."""

    def decide(
        self,
        proposal: EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal,
        *,
        decision_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2:
        if type(proposal) is not EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal:
            raise TypeError(
                "proposal must be EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal"
            )
        if not isinstance(decision_id, str) or not decision_id.strip():
            raise ValueError("decision_id must be a non-empty string")

        if proposal.requested_action == "RETRY_REPAIR":
            if proposal.eligible is not True:
                raise EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2Error(
                    "RETRY_REPAIR requires eligible proposal evidence"
                )
            decision = "ACCEPT"
            default_reason = "eligible retry proposal accepted as non-executing authorization decision evidence"
        elif proposal.requested_action == "NO_AUTHORIZATION":
            decision = "REJECT"
            default_reason = "proposal does not request retry authorization"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2Error(
                "unsupported proposal action"
            )

        return EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2(
            decision_id=decision_id,
            proposal_id=proposal.proposal_id,
            assessment_id=proposal.assessment_id,
            evaluation_id=proposal.evaluation_id,
            feedback_id=proposal.feedback_id,
            outcome_id=proposal.outcome_id,
            environment_id=proposal.environment_id,
            expected_model_id=proposal.expected_model_id,
            observed_model_id=proposal.observed_model_id,
            requested_action=proposal.requested_action,
            assessment_status=proposal.assessment_status.value if proposal.assessment_status is not None else None,
            eligible=proposal.eligible,
            retry_count=proposal.retry_count,
            max_retries=proposal.max_retries,
            evaluated_at=proposal.evaluated_at,
            next_eligible_at=proposal.next_eligible_at,
            decision=decision,
            reasons=reasons or {"status": default_reason},
            lineage=lineage or {
                "proposal_id": proposal.proposal_id,
                "assessment_id": proposal.assessment_id,
                "evaluation_id": proposal.evaluation_id,
                "feedback_id": proposal.feedback_id,
                "outcome_id": proposal.outcome_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2Error",
    "EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2",
    "EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2Service",
]
