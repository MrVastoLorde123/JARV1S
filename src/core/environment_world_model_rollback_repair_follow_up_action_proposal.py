"""M23.36: explicit action proposal evidence for rollback-repair follow-up.

This boundary converts accepted follow-up decision evidence into a bounded,
non-mutating action proposal. It does not retry repair or authorize execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_follow_up_decision import (
    EnvironmentWorldModelRollbackRepairFollowUpDecision,
)


class EnvironmentWorldModelRollbackRepairFollowUpActionProposalError(RuntimeError):
    """Raised when a follow-up action proposal cannot be formed safely."""


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
class EnvironmentWorldModelRollbackRepairFollowUpActionProposal:
    """Immutable advisory evidence describing one proposed follow-up action."""

    proposal_id: str
    environment_id: str
    follow_up_decision_id: str
    expected_model_id: str
    observed_model_id: str
    action: str
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "proposal_id",
            "environment_id",
            "follow_up_decision_id",
            "expected_model_id",
            "observed_model_id",
            "action",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.action not in {"RETRY_REPAIR", "NO_ACTION"}:
            raise ValueError("action must be RETRY_REPAIR or NO_ACTION")
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
    def executes_action(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairFollowUpActionProposalService:
    """Convert follow-up decision evidence into bounded action proposal evidence."""

    def propose(
        self,
        decision: EnvironmentWorldModelRollbackRepairFollowUpDecision,
        *,
        proposal_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairFollowUpActionProposal:
        if type(decision) is not EnvironmentWorldModelRollbackRepairFollowUpDecision:
            raise TypeError(
                "decision must be EnvironmentWorldModelRollbackRepairFollowUpDecision"
            )

        if decision.decision == "ACCEPT":
            action = "RETRY_REPAIR"
            default_reason = "accepted follow-up decision proposes a bounded repair retry for separate execution"
        elif decision.decision == "REJECT":
            action = "NO_ACTION"
            default_reason = "follow-up decision rejected additional action"
        else:
            raise EnvironmentWorldModelRollbackRepairFollowUpActionProposalError(
                "follow-up decision is not supported by the action proposal contract"
            )

        return EnvironmentWorldModelRollbackRepairFollowUpActionProposal(
            proposal_id=proposal_id,
            environment_id=decision.environment_id,
            follow_up_decision_id=decision.decision_id,
            expected_model_id=decision.expected_model_id,
            observed_model_id=decision.observed_model_id,
            action=action,
            reasons=reasons or {"status": default_reason},
            lineage=lineage
            or {
                "follow_up_decision_id": decision.decision_id,
                "expected_model_id": decision.expected_model_id,
                "observed_model_id": decision.observed_model_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairFollowUpActionProposal",
    "EnvironmentWorldModelRollbackRepairFollowUpActionProposalError",
    "EnvironmentWorldModelRollbackRepairFollowUpActionProposalService",
]
