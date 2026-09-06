"""M23.51: integrity verification for M23.49 proposal and M23.50 decision."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from src.core.environment_world_model_rollback_repair_retry_authorization_proposal import EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal
    from src.core.environment_world_model_rollback_repair_retry_authorization_decision_v2 import EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list): return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple): return tuple(_freeze(item) for item in value)
    if isinstance(value, set): return frozenset(_freeze(item) for item in value)
    return value


class EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2:
    integrity_id: str
    proposal_id: str
    decision_id: str
    status: EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("integrity_id", "proposal_id", "decision_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip(): raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status): raise TypeError("status must be an integrity status")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping): raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool: return True
    @property
    def authorizes_retry(self) -> bool: return False
    @property
    def executes_retry(self) -> bool: return False


class EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Service:
    def verify(self, proposal: "EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal", decision: "EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2", *, integrity_id: str, reasons: Mapping[str, str] | None = None, lineage: Mapping[str, Any] | None = None) -> EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2:
        from src.core.environment_world_model_rollback_repair_retry_authorization_proposal import EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal
        from src.core.environment_world_model_rollback_repair_retry_authorization_decision_v2 import EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2
        if type(proposal) is not EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal: raise TypeError("proposal must be EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal")
        if type(decision) is not EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2: raise TypeError("decision must be EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2")
        if not isinstance(integrity_id, str) or not integrity_id.strip(): raise ValueError("integrity_id must be a non-empty string")

        common = (
            proposal.proposal_id == decision.proposal_id
            and proposal.environment_id == decision.environment_id
            and proposal.expected_model_id == decision.expected_model_id
            and proposal.observed_model_id == decision.observed_model_id
            and proposal.requested_action == decision.requested_action
            and proposal.eligible == decision.eligible
            and proposal.evaluated_at == decision.evaluated_at
            and proposal.next_eligible_at == decision.next_eligible_at
            and proposal.assessment_id == decision.assessment_id
            and proposal.evaluation_id == decision.evaluation_id
            and proposal.feedback_id == decision.feedback_id
            and proposal.outcome_id == decision.outcome_id
            and proposal.retry_count == decision.retry_count
            and proposal.max_retries == decision.max_retries
        )
        action_consistency = (
            (proposal.requested_action == "RETRY_REPAIR" and proposal.eligible is True and decision.decision == "ACCEPT")
            or (proposal.requested_action == "NO_AUTHORIZATION" and proposal.eligible is False and decision.decision == "REJECT")
        )
        valid = common and action_consistency
        status = EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status.VALID if valid else EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status.INVALID
        return EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2(
            integrity_id=integrity_id,
            proposal_id=proposal.proposal_id,
            decision_id=decision.decision_id,
            status=status,
            reasons=reasons or {"status": "proposal and decision identities and semantics are consistent" if valid else "proposal and decision evidence are inconsistent"},
            lineage=lineage or {"proposal_id": proposal.proposal_id, "decision_id": decision.decision_id},
        )


__all__ = ["EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status", "EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2", "EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Service"]
