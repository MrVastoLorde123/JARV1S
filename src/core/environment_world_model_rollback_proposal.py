"""M23.23: advisory rollback proposal for descriptive world-model history."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_history import EnvironmentWorldModelHistory


class EnvironmentWorldModelRollbackProposalError(RuntimeError):
    """Raised when a rollback proposal cannot be formed safely."""


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
class EnvironmentWorldModelRollbackProposal:
    """Immutable advisory proposal to restore a historical model as current state."""

    proposal_id: str
    environment_id: str
    current_model_id: str
    target_model_id: str
    recommendation: str
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "proposal_id", "environment_id", "current_model_id", "target_model_id", "recommendation"
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.recommendation not in {"ROLLBACK", "NO_ROLLBACK"}:
            raise ValueError("recommendation must be ROLLBACK or NO_ROLLBACK")
        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.recommendation == "ROLLBACK" and self.current_model_id == self.target_model_id:
            raise ValueError("rollback recommendation requires different current and target model identities")
        if self.recommendation == "NO_ROLLBACK" and self.current_model_id != self.target_model_id:
            raise ValueError("no-rollback recommendation requires identical current and target model identities")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def applies_rollback(self) -> bool:
        return False


class EnvironmentWorldModelRollbackProposalService:
    """Produce a bounded rollback proposal without changing stored or current state."""

    def propose(
        self,
        history: EnvironmentWorldModelHistory,
        *,
        proposal_id: str,
        target_model_id: str,
        current_model: EnvironmentWorldModel | None = None,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackProposal:
        if type(history) is not EnvironmentWorldModelHistory:
            raise TypeError("history must be EnvironmentWorldModelHistory")
        if current_model is not None and type(current_model) is not EnvironmentWorldModel:
            raise TypeError("current_model must be EnvironmentWorldModel or None")
        if not isinstance(target_model_id, str) or not target_model_id.strip():
            raise ValueError("target_model_id must be a non-empty string")
        if current_model is None:
            current = history.latest
            if current is None:
                raise EnvironmentWorldModelRollbackProposalError("history has no current/latest model")
        else:
            current = current_model
        if current.environment_id != history.environment_id:
            raise EnvironmentWorldModelRollbackProposalError("current model environment does not match history")
        if target_model_id not in history.model_ids:
            raise EnvironmentWorldModelRollbackProposalError("target model must exist in history")
        if target_model_id == current.model_id:
            recommendation = "NO_ROLLBACK"
            default_reason = "target model is already current"
        else:
            recommendation = "ROLLBACK"
            default_reason = "historical target differs from current model"
        return EnvironmentWorldModelRollbackProposal(
            proposal_id=proposal_id,
            environment_id=history.environment_id,
            current_model_id=current.model_id,
            target_model_id=target_model_id,
            recommendation=recommendation,
            reasons=reasons or {"status": default_reason},
            lineage=lineage or {
                "history_environment_id": history.environment_id,
                "current_model_id": current.model_id,
                "target_model_id": target_model_id,
            },
        )
