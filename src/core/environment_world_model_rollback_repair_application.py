"""M23.31: explicit repair application boundary for failed rollback verification.

This boundary applies an accepted repair decision by replacing an observed
incorrect current model with the expected model, guarded by compare-and-swap.
It does not invent repair targets, mutate source artifacts in place, or imply
truth/authorization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_rollback_repair_decision import (
    EnvironmentWorldModelRollbackRepairDecision,
)
from src.core.environment_world_model_rollback_repair_proposal import (
    EnvironmentWorldModelRollbackRepairProposal,
)
from src.core.environment_world_model_store import EnvironmentWorldModelStore


class EnvironmentWorldModelRollbackRepairApplicationError(RuntimeError):
    """Raised when a rollback repair cannot be applied safely."""


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
class EnvironmentWorldModelRollbackRepairApplication:
    """Immutable record of one repair state transition."""

    application_id: str
    environment_id: str
    previous_model_id: str
    expected_model_id: str
    resulting_model_id: str
    decision_id: str
    applied: bool
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "application_id",
            "environment_id",
            "previous_model_id",
            "expected_model_id",
            "resulting_model_id",
            "decision_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.applied and self.resulting_model_id != self.expected_model_id:
            raise ValueError("applied repair must result in expected model")
        if not self.applied and self.resulting_model_id != self.previous_model_id:
            raise ValueError("unapplied repair must retain previous model")
        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def mutates_source_objects(self) -> bool:
        return False

    @property
    def establishes_truth(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairApplicationService:
    """Apply an accepted repair decision through a guarded current-model store update."""

    def apply(
        self,
        proposal: EnvironmentWorldModelRollbackRepairProposal,
        decision: EnvironmentWorldModelRollbackRepairDecision,
        expected_model: EnvironmentWorldModel,
        store: EnvironmentWorldModelStore,
        *,
        application_id: str,
        current_model: EnvironmentWorldModel | None = None,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> tuple[EnvironmentWorldModel, EnvironmentWorldModelRollbackRepairApplication]:
        if type(proposal) is not EnvironmentWorldModelRollbackRepairProposal:
            raise TypeError("proposal must be EnvironmentWorldModelRollbackRepairProposal")
        if type(decision) is not EnvironmentWorldModelRollbackRepairDecision:
            raise TypeError("decision must be EnvironmentWorldModelRollbackRepairDecision")
        if type(expected_model) is not EnvironmentWorldModel:
            raise TypeError("expected_model must be EnvironmentWorldModel")
        if not hasattr(store, "get") or not hasattr(store, "put"):
            raise TypeError("store must implement the EnvironmentWorldModelStore contract")

        if proposal.environment_id != decision.environment_id:
            raise EnvironmentWorldModelRollbackRepairApplicationError(
                "proposal and decision environments must match"
            )
        if proposal.proposal_id != decision.proposal_id:
            raise EnvironmentWorldModelRollbackRepairApplicationError(
                "decision identity does not match repair proposal"
            )
        if proposal.expected_model_id != decision.expected_model_id:
            raise EnvironmentWorldModelRollbackRepairApplicationError(
                "proposal and decision expected identities must match"
            )
        if proposal.observed_model_id != decision.observed_model_id:
            raise EnvironmentWorldModelRollbackRepairApplicationError(
                "proposal and decision observed identities must match"
            )
        if proposal.expected_model_id != expected_model.model_id:
            raise EnvironmentWorldModelRollbackRepairApplicationError(
                "proposal expected identity does not match expected model"
            )
        if proposal.environment_id != expected_model.environment_id:
            raise EnvironmentWorldModelRollbackRepairApplicationError(
                "proposal and expected model environments must match"
            )

        current = current_model if current_model is not None else store.get(proposal.environment_id)
        if current is None:
            raise EnvironmentWorldModelRollbackRepairApplicationError(
                "current model is absent from store"
            )
        if current.environment_id != proposal.environment_id:
            raise EnvironmentWorldModelRollbackRepairApplicationError(
                "current model environment does not match repair proposal"
            )
        if proposal.observed_model_id != current.model_id:
            raise EnvironmentWorldModelRollbackRepairApplicationError(
                "current model identity does not match observed repair-proposal identity"
            )

        if decision.decision == "ACCEPT":
            try:
                store.put(expected_model, expected_model_id=current.model_id)
            except Exception as exc:
                raise EnvironmentWorldModelRollbackRepairApplicationError(
                    "repair could not be persisted with expected current-model identity"
                ) from exc
            resulting = expected_model
            applied = True
            default_reason = "accepted repair decision replaced observed current model with expected model"
        elif decision.decision == "REJECT":
            resulting = current
            applied = False
            default_reason = "repair decision rejected application; current model retained"
        else:
            raise EnvironmentWorldModelRollbackRepairApplicationError(
                "repair decision is unsupported by the repair application contract"
            )

        application = EnvironmentWorldModelRollbackRepairApplication(
            application_id=application_id,
            environment_id=proposal.environment_id,
            previous_model_id=current.model_id,
            expected_model_id=expected_model.model_id,
            resulting_model_id=resulting.model_id,
            decision_id=decision.decision_id,
            applied=applied,
            reasons=reasons or {"status": default_reason},
            lineage=lineage or {
                "proposal_id": proposal.proposal_id,
                "decision_id": decision.decision_id,
                "previous_model_id": current.model_id,
                "expected_model_id": expected_model.model_id,
            },
        )
        return resulting, application


__all__ = [
    "EnvironmentWorldModelRollbackRepairApplication",
    "EnvironmentWorldModelRollbackRepairApplicationError",
    "EnvironmentWorldModelRollbackRepairApplicationService",
]
