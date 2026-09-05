"""M23.37: explicit decision evidence for rollback-repair follow-up actions.

This boundary converts a proposed follow-up action into deterministic,
non-mutating decision evidence. It does not execute retry or authorize effects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_follow_up_action_proposal import (
    EnvironmentWorldModelRollbackRepairFollowUpActionProposal,
)


class EnvironmentWorldModelRollbackRepairFollowUpActionDecisionError(RuntimeError):
    """Raised when a follow-up action decision cannot be formed safely."""


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
class EnvironmentWorldModelRollbackRepairFollowUpActionDecision:
    """Immutable decision evidence derived from one follow-up action proposal."""

    decision_id: str
    environment_id: str
    proposal_id: str
    follow_up_decision_id: str
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
            "follow_up_decision_id",
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
    def authorizes_execution(self) -> bool:
        return False

    @property
    def executes_action(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairFollowUpActionDecisionService:
    """Convert a follow-up action proposal into deterministic decision evidence."""

    def decide(
        self,
        proposal: EnvironmentWorldModelRollbackRepairFollowUpActionProposal,
        *,
        decision_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairFollowUpActionDecision:
        if type(proposal) is not EnvironmentWorldModelRollbackRepairFollowUpActionProposal:
            raise TypeError(
                "proposal must be EnvironmentWorldModelRollbackRepairFollowUpActionProposal"
            )

        if proposal.action == "RETRY_REPAIR":
            decision = "ACCEPT"
            default_reason = "validated retry-repair action proposal is accepted for separate execution"
        elif proposal.action == "NO_ACTION":
            decision = "REJECT"
            default_reason = "validated action proposal requests no follow-up action"
        else:
            raise EnvironmentWorldModelRollbackRepairFollowUpActionDecisionError(
                "follow-up action is not supported by the action decision contract"
            )

        return EnvironmentWorldModelRollbackRepairFollowUpActionDecision(
            decision_id=decision_id,
            environment_id=proposal.environment_id,
            proposal_id=proposal.proposal_id,
            follow_up_decision_id=proposal.follow_up_decision_id,
            expected_model_id=proposal.expected_model_id,
            observed_model_id=proposal.observed_model_id,
            decision=decision,
            reasons=reasons or {"status": default_reason},
            lineage=lineage
            or {
                "proposal_id": proposal.proposal_id,
                "follow_up_decision_id": proposal.follow_up_decision_id,
                "expected_model_id": proposal.expected_model_id,
                "observed_model_id": proposal.observed_model_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairFollowUpActionDecision",
    "EnvironmentWorldModelRollbackRepairFollowUpActionDecisionError",
    "EnvironmentWorldModelRollbackRepairFollowUpActionDecisionService",
]
