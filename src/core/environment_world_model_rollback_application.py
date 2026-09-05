"""M23.25: explicit application boundary for world-model rollback decisions.

This boundary applies an accepted rollback decision by selecting a historical
model as the resulting immutable current state. It never mutates model objects
or history in place and does not itself persist the resulting state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_history import EnvironmentWorldModelHistory
from src.core.environment_world_model_rollback_decision import (
    EnvironmentWorldModelRollbackDecision,
)


class EnvironmentWorldModelRollbackApplicationError(RuntimeError):
    """Raised when an accepted rollback cannot be applied safely."""


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
class EnvironmentWorldModelRollbackApplication:
    """Immutable record of one rollback state transition."""

    application_id: str
    environment_id: str
    previous_model_id: str
    target_model_id: str
    decision_id: str
    applied: bool
    resulting_model_id: str
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "application_id",
            "environment_id",
            "previous_model_id",
            "target_model_id",
            "decision_id",
            "resulting_model_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.applied and self.resulting_model_id != self.target_model_id:
            raise ValueError("applied rollback must result in target model")
        if not self.applied and self.resulting_model_id != self.previous_model_id:
            raise ValueError("unapplied rollback must retain previous model")
        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_mutation_of_source_objects(self) -> bool:
        return False


class EnvironmentWorldModelRollbackApplicationService:
    """Apply an explicit rollback decision as an immutable state transition."""

    def apply(
        self,
        history: EnvironmentWorldModelHistory,
        decision: EnvironmentWorldModelRollbackDecision,
        *,
        application_id: str,
        current_model: EnvironmentWorldModel | None = None,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> tuple[EnvironmentWorldModel, EnvironmentWorldModelRollbackApplication]:
        if type(history) is not EnvironmentWorldModelHistory:
            raise TypeError("history must be EnvironmentWorldModelHistory")
        if type(decision) is not EnvironmentWorldModelRollbackDecision:
            raise TypeError("decision must be EnvironmentWorldModelRollbackDecision")
        if current_model is not None and type(current_model) is not EnvironmentWorldModel:
            raise TypeError("current_model must be EnvironmentWorldModel or None")

        current = current_model if current_model is not None else history.latest
        if current is None:
            raise EnvironmentWorldModelRollbackApplicationError(
                "history has no current/latest model"
            )
        if current.environment_id != history.environment_id:
            raise EnvironmentWorldModelRollbackApplicationError(
                "current model environment does not match history"
            )
        if decision.environment_id != history.environment_id:
            raise EnvironmentWorldModelRollbackApplicationError(
                "decision environment does not match history"
            )
        if decision.current_model_id != current.model_id:
            raise EnvironmentWorldModelRollbackApplicationError(
                "decision current identity does not match current model"
            )
        if decision.target_model_id not in history.model_ids:
            raise EnvironmentWorldModelRollbackApplicationError(
                "decision target model must exist in history"
            )

        target = next(model for model in history.models if model.model_id == decision.target_model_id)
        if decision.decision == "ACCEPT":
            resulting = target
            applied = True
            default_reason = "accepted rollback decision selected historical target as resulting state"
        elif decision.decision in {"REJECT", "DEFER"}:
            resulting = current
            applied = False
            default_reason = "rollback decision did not authorize application; current state retained"
        else:
            raise EnvironmentWorldModelRollbackApplicationError(
                "decision value is unsupported by rollback application contract"
            )

        application = EnvironmentWorldModelRollbackApplication(
            application_id=application_id,
            environment_id=history.environment_id,
            previous_model_id=current.model_id,
            target_model_id=decision.target_model_id,
            decision_id=decision.decision_id,
            applied=applied,
            resulting_model_id=resulting.model_id,
            reasons=reasons or {"status": default_reason},
            lineage=lineage
            or {
                "decision_id": decision.decision_id,
                "previous_model_id": current.model_id,
                "target_model_id": decision.target_model_id,
            },
        )
        return resulting, application
