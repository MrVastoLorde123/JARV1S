"""M23.41: integrity verification for rollback-repair retry authorization evidence.

This boundary verifies that retry authorization decision evidence is internally
consistent with its originating authorization proposal. It does not grant
execution authority, prepare execution, or execute retry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_authorization_decision import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision,
)
from src.core.environment_world_model_rollback_repair_retry_authorization_proposal import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal,
)


class EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrityError(RuntimeError):
    """Raised when authorization integrity cannot be established safely."""


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
class EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrity:
    """Immutable evidence describing whether authorization decision evidence is internally consistent."""

    integrity_id: str
    environment_id: str
    authorization_decision_id: str
    proposal_id: str
    eligibility_id: str
    action_decision_id: str
    requested_action: str
    decision: str
    proposal_eligible: bool
    integrity_status: str
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "integrity_id",
            "environment_id",
            "authorization_decision_id",
            "proposal_id",
            "eligibility_id",
            "action_decision_id",
            "requested_action",
            "decision",
            "integrity_status",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.requested_action not in {"RETRY_REPAIR", "NO_AUTHORIZATION"}:
            raise ValueError("requested_action must be RETRY_REPAIR or NO_AUTHORIZATION")
        if self.decision not in {"ACCEPT", "REJECT", "DEFER"}:
            raise ValueError("decision must be ACCEPT, REJECT, or DEFER")
        if self.integrity_status not in {"VALID", "INVALID", "DEFER"}:
            raise ValueError("integrity_status must be VALID, INVALID, or DEFER")
        if not isinstance(self.proposal_eligible, bool):
            raise TypeError("proposal_eligible must be a boolean")
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
    def grants_execution_authority(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrityService:
    """Verify retry authorization decision consistency without granting authority."""

    def verify(
        self,
        proposal: EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal,
        decision: EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision,
        *,
        integrity_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrity:
        if type(proposal) is not EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal:
            raise TypeError(
                "proposal must be EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal"
            )
        if type(decision) is not EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision:
            raise TypeError(
                "decision must be EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision"
            )
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")

        identities_match = (
            decision.proposal_id == proposal.proposal_id
            and decision.eligibility_id == proposal.eligibility_id
            and decision.action_decision_id == proposal.action_decision_id
            and decision.environment_id == proposal.environment_id
        )
        action_matches = decision.requested_action == proposal.requested_action

        if proposal.requested_action == "RETRY_REPAIR":
            expected_decision = "ACCEPT" if proposal.eligible else "REJECT"
        elif proposal.requested_action == "NO_AUTHORIZATION":
            expected_decision = "REJECT"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrityError(
                "requested action is not supported by the authorization integrity contract"
            )

        if decision.decision == "DEFER":
            integrity_status = "DEFER"
            default_reason = "authorization decision is deferred and cannot be integrity-validated as executable authority"
        elif identities_match and action_matches and decision.decision == expected_decision:
            integrity_status = "VALID"
            default_reason = "authorization decision is consistent with its originating proposal and eligibility"
        else:
            integrity_status = "INVALID"
            default_reason = "authorization decision conflicts with proposal identity, requested action, or eligibility"

        return EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrity(
            integrity_id=integrity_id,
            environment_id=proposal.environment_id,
            authorization_decision_id=decision.decision_id,
            proposal_id=proposal.proposal_id,
            eligibility_id=proposal.eligibility_id,
            action_decision_id=proposal.action_decision_id,
            requested_action=proposal.requested_action,
            decision=decision.decision,
            proposal_eligible=proposal.eligible,
            integrity_status=integrity_status,
            reasons=reasons or {"status": default_reason},
            lineage=lineage
            or {
                "proposal_id": proposal.proposal_id,
                "eligibility_id": proposal.eligibility_id,
                "action_decision_id": proposal.action_decision_id,
                "authorization_decision_id": decision.decision_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrity",
    "EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrityError",
    "EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrityService",
]
