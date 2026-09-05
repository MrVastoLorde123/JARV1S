"""M23.30: explicit decision evidence for world-model rollback repair proposals.

This boundary converts an advisory rollback repair proposal into deterministic,
non-mutating decision evidence. It does not apply repair or alter persistence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_proposal import (
    EnvironmentWorldModelRollbackRepairProposal,
)


class EnvironmentWorldModelRollbackRepairDecisionError(RuntimeError):
    """Raised when a rollback repair decision cannot be formed safely."""


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
class EnvironmentWorldModelRollbackRepairDecision:
    """Immutable decision evidence derived from one repair proposal."""

    decision_id: str
    environment_id: str
    proposal_id: str
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
    def applies_repair(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairDecisionService:
    """Convert one repair proposal into deterministic decision evidence."""

    def decide(
        self,
        proposal: EnvironmentWorldModelRollbackRepairProposal,
        *,
        decision_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairDecision:
        if type(proposal) is not EnvironmentWorldModelRollbackRepairProposal:
            raise TypeError(
                "proposal must be EnvironmentWorldModelRollbackRepairProposal"
            )

        if proposal.recommendation == "REPAIR":
            decision = "ACCEPT"
            default_reason = "validated rollback repair proposal is accepted for separate application"
        elif proposal.recommendation == "NO_REPAIR":
            decision = "REJECT"
            default_reason = "validated rollback repair proposal does not require repair"
        else:
            raise EnvironmentWorldModelRollbackRepairDecisionError(
                "repair proposal recommendation is not supported by the rollback repair decision contract"
            )

        return EnvironmentWorldModelRollbackRepairDecision(
            decision_id=decision_id,
            environment_id=proposal.environment_id,
            proposal_id=proposal.proposal_id,
            expected_model_id=proposal.expected_model_id,
            observed_model_id=proposal.observed_model_id,
            decision=decision,
            reasons=reasons or {"status": default_reason},
            lineage=lineage
            or {
                "proposal_id": proposal.proposal_id,
                "expected_model_id": proposal.expected_model_id,
                "observed_model_id": proposal.observed_model_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairDecision",
    "EnvironmentWorldModelRollbackRepairDecisionError",
    "EnvironmentWorldModelRollbackRepairDecisionService",
]
