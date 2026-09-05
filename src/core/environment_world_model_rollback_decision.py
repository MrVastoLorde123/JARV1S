"""M23.24: explicit decision evidence for a world-model rollback proposal.

This boundary converts a validated advisory rollback proposal into deterministic,
non-mutating decision evidence. It does not apply rollback or alter persistence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_proposal import (
    EnvironmentWorldModelRollbackProposal,
)


class EnvironmentWorldModelRollbackDecisionError(RuntimeError):
    """Raised when a rollback decision cannot be formed safely."""


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
class EnvironmentWorldModelRollbackDecision:
    """Immutable decision evidence derived from one rollback proposal."""

    decision_id: str
    environment_id: str
    current_model_id: str
    target_model_id: str
    proposal_id: str
    decision: str
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "decision_id",
            "environment_id",
            "current_model_id",
            "target_model_id",
            "proposal_id",
            "decision",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.decision not in {"ACCEPT", "DEFER", "REJECT"}:
            raise ValueError("decision must be ACCEPT, DEFER, or REJECT")
        if self.decision == "ACCEPT" and self.current_model_id == self.target_model_id:
            raise ValueError("accepted rollback requires different current and target models")
        if self.decision == "REJECT" and self.current_model_id != self.target_model_id:
            raise ValueError("rejected rollback requires identical current and target models")
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
    def applies_rollback(self) -> bool:
        return False


class EnvironmentWorldModelRollbackDecisionService:
    """Convert one rollback proposal into deterministic decision evidence."""

    def decide(
        self,
        proposal: EnvironmentWorldModelRollbackProposal,
        *,
        decision_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackDecision:
        if type(proposal) is not EnvironmentWorldModelRollbackProposal:
            raise TypeError("proposal must be EnvironmentWorldModelRollbackProposal")

        if proposal.recommendation == "ROLLBACK":
            decision = "ACCEPT"
            default_reason = "validated rollback proposal targets a different historical model"
        elif proposal.recommendation == "NO_ROLLBACK":
            decision = "REJECT"
            default_reason = "validated rollback proposal already targets the current model"
        else:
            raise EnvironmentWorldModelRollbackDecisionError(
                "proposal recommendation is not supported by the rollback decision contract"
            )

        return EnvironmentWorldModelRollbackDecision(
            decision_id=decision_id,
            environment_id=proposal.environment_id,
            current_model_id=proposal.current_model_id,
            target_model_id=proposal.target_model_id,
            proposal_id=proposal.proposal_id,
            decision=decision,
            reasons=reasons or {"status": default_reason},
            lineage=lineage
            or {
                "proposal_id": proposal.proposal_id,
                "current_model_id": proposal.current_model_id,
                "target_model_id": proposal.target_model_id,
            },
        )
