"""M23.34: explicit follow-up proposal evidence for unverified repair."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_verification_decision import (
    EnvironmentWorldModelRollbackRepairVerificationDecision,
)


class EnvironmentWorldModelRollbackRepairFollowUpProposalError(RuntimeError):
    """Raised when a repair follow-up proposal cannot be formed safely."""


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
class EnvironmentWorldModelRollbackRepairFollowUpProposal:
    """Immutable advisory evidence for follow-up after an unresolved repair."""

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
        if self.recommendation not in {"FOLLOW_UP", "NO_FOLLOW_UP"}:
            raise ValueError("recommendation must be FOLLOW_UP or NO_FOLLOW_UP")
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
    def applies_follow_up(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairFollowUpProposalService:
    """Convert repair-verification decision evidence into follow-up proposal evidence."""

    def propose(
        self,
        decision: EnvironmentWorldModelRollbackRepairVerificationDecision,
        *,
        proposal_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairFollowUpProposal:
        if type(decision) is not EnvironmentWorldModelRollbackRepairVerificationDecision:
            raise TypeError(
                "decision must be EnvironmentWorldModelRollbackRepairVerificationDecision"
            )

        if decision.decision == "REJECT":
            recommendation = "FOLLOW_UP"
            default_reason = "repair verification was rejected; follow-up is proposed for separate evaluation"
        elif decision.decision == "ACCEPT":
            recommendation = "NO_FOLLOW_UP"
            default_reason = "repair verification was accepted; no follow-up is proposed"
        else:
            raise EnvironmentWorldModelRollbackRepairFollowUpProposalError(
                "repair verification decision is not supported by the follow-up proposal contract"
            )

        return EnvironmentWorldModelRollbackRepairFollowUpProposal(
            proposal_id=proposal_id,
            environment_id=decision.environment_id,
            verification_decision_id=decision.verification_id,
            expected_model_id=decision.expected_model_id,
            observed_model_id=decision.observed_model_id,
            recommendation=recommendation,
            reasons=reasons or {"status": default_reason},
            lineage=lineage or {
                "verification_decision_id": decision.decision_id,
                "expected_model_id": decision.expected_model_id,
                "observed_model_id": decision.observed_model_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairFollowUpProposal",
    "EnvironmentWorldModelRollbackRepairFollowUpProposalError",
    "EnvironmentWorldModelRollbackRepairFollowUpProposalService",
]
