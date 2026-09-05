"""M23.35: explicit decision evidence for rollback-repair follow-up proposals.

This boundary converts an advisory follow-up proposal into deterministic,
non-mutating decision evidence. It does not retry repair or authorize action.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_follow_up_proposal import (
    EnvironmentWorldModelRollbackRepairFollowUpProposal,
)


class EnvironmentWorldModelRollbackRepairFollowUpDecisionError(RuntimeError):
    """Raised when a follow-up decision cannot be formed safely."""


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
class EnvironmentWorldModelRollbackRepairFollowUpDecision:
    """Immutable decision evidence derived from one follow-up proposal."""

    decision_id: str
    environment_id: str
    proposal_id: str
    verification_decision_id: str
    expected_model_id: str
    observed_model_id: str
    decision: str
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "decision_id",
            "environment_id",
            "proposal_id",
            "verification_decision_id",
            "expected_model_id",
            "observed_model_id",
            "decision",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.decision not in {"ACCEPT", "REJECT", "DEFER"}:
            raise ValueError("decision must be ACCEPT, REJECT, or DEFER")
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


class EnvironmentWorldModelRollbackRepairFollowUpDecisionService:
    """Convert follow-up proposal evidence into deterministic decision evidence."""

    def decide(
        self,
        proposal: EnvironmentWorldModelRollbackRepairFollowUpProposal,
        *,
        decision_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairFollowUpDecision:
        if type(proposal) is not EnvironmentWorldModelRollbackRepairFollowUpProposal:
            raise TypeError(
                "proposal must be EnvironmentWorldModelRollbackRepairFollowUpProposal"
            )

        if proposal.recommendation == "FOLLOW_UP":
            decision = "ACCEPT"
            default_reason = "validated follow-up proposal is accepted for separate action selection"
        elif proposal.recommendation == "NO_FOLLOW_UP":
            decision = "REJECT"
            default_reason = "validated follow-up proposal does not require additional action"
        else:
            raise EnvironmentWorldModelRollbackRepairFollowUpDecisionError(
                "follow-up proposal recommendation is not supported by the decision contract"
            )

        return EnvironmentWorldModelRollbackRepairFollowUpDecision(
            decision_id=decision_id,
            environment_id=proposal.environment_id,
            proposal_id=proposal.proposal_id,
            verification_decision_id=proposal.verification_decision_id,
            expected_model_id=proposal.expected_model_id,
            observed_model_id=proposal.observed_model_id,
            decision=decision,
            reasons=reasons or {"status": default_reason},
            lineage=lineage
            or {
                "proposal_id": proposal.proposal_id,
                "verification_decision_id": proposal.verification_decision_id,
                "expected_model_id": proposal.expected_model_id,
                "observed_model_id": proposal.observed_model_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairFollowUpDecision",
    "EnvironmentWorldModelRollbackRepairFollowUpDecisionError",
    "EnvironmentWorldModelRollbackRepairFollowUpDecisionService",
]
