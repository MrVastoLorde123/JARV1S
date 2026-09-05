"""M23.29: explicit repair proposal evidence for failed rollback verification.

This boundary converts deterministic rollback-verification decision evidence into
an advisory repair proposal. It does not repair state, authorize execution, or
mutate persistence/history.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_verification_decision import (
    EnvironmentWorldModelRollbackVerificationDecision,
)


class EnvironmentWorldModelRollbackRepairProposalError(RuntimeError):
    """Raised when a rollback repair proposal cannot be formed safely."""


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
class EnvironmentWorldModelRollbackRepairProposal:
    """Immutable advisory proposal for correcting a failed rollback verification."""

    proposal_id: str
    environment_id: str
    verification_decision_id: str
    expected_model_id: str
    observed_model_id: str
    recommendation: str
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "proposal_id",
            "environment_id",
            "verification_decision_id",
            "expected_model_id",
            "observed_model_id",
            "recommendation",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.recommendation not in {"REPAIR", "NO_REPAIR"}:
            raise ValueError("recommendation must be REPAIR or NO_REPAIR")
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


class EnvironmentWorldModelRollbackRepairProposalService:
    """Convert verification decision evidence into deterministic repair proposal evidence."""

    def propose(
        self,
        decision: EnvironmentWorldModelRollbackVerificationDecision,
        *,
        proposal_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairProposal:
        if type(decision) is not EnvironmentWorldModelRollbackVerificationDecision:
            raise TypeError(
                "decision must be EnvironmentWorldModelRollbackVerificationDecision"
            )

        if decision.decision == "ACCEPT":
            recommendation = "NO_REPAIR"
            default_reason = "rollback verification was accepted; no repair is proposed"
        elif decision.decision == "REJECT":
            recommendation = "REPAIR"
            default_reason = "rollback verification was rejected; repair is proposed for separate evaluation"
        else:
            raise EnvironmentWorldModelRollbackRepairProposalError(
                "verification decision is not supported by the rollback repair proposal contract"
            )

        return EnvironmentWorldModelRollbackRepairProposal(
            proposal_id=proposal_id,
            environment_id=decision.environment_id,
            verification_decision_id=decision.decision_id,
            expected_model_id=decision.expected_model_id,
            observed_model_id=decision.observed_model_id,
            recommendation=recommendation,
            reasons=reasons or {"status": default_reason},
            lineage=lineage
            or {
                "verification_decision_id": decision.decision_id,
                "expected_model_id": decision.expected_model_id,
                "observed_model_id": decision.observed_model_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairProposal",
    "EnvironmentWorldModelRollbackRepairProposalError",
    "EnvironmentWorldModelRollbackRepairProposalService",
]
