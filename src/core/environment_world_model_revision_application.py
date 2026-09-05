"""M23.18: explicit application boundary for accepted world-model revisions.

This boundary validates an accepted revision decision and returns the immutable
candidate model as the applied state transition. It never mutates either source
model object or introduces persistence/authorization on its own.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_revision_decision import (
    EnvironmentWorldModelRevisionDecision,
)


class EnvironmentWorldModelRevisionApplicationError(RuntimeError):
    """Raised when an accepted world-model revision cannot be applied safely."""


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
class EnvironmentWorldModelRevisionApplication:
    """Immutable record of one accepted world-model state transition."""

    application_id: str
    environment_id: str
    baseline_model_id: str
    candidate_model_id: str
    decision_id: str
    applied: bool
    resulting_model_id: str
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "application_id",
            "environment_id",
            "baseline_model_id",
            "candidate_model_id",
            "decision_id",
            "resulting_model_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.baseline_model_id == self.candidate_model_id:
            raise ValueError("baseline and candidate model identities must differ")
        if not isinstance(self.applied, bool):
            raise TypeError("applied must be a bool")
        if self.applied and self.resulting_model_id != self.candidate_model_id:
            raise ValueError("applied revision must result in candidate model")
        if not self.applied and self.resulting_model_id != self.baseline_model_id:
            raise ValueError("unapplied revision must preserve baseline model")
        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_mutation_of_source_objects(self) -> bool:
        return False


class EnvironmentWorldModelRevisionApplicationService:
    """Apply an explicit revision decision as an immutable state transition."""

    def apply(
        self,
        baseline: EnvironmentWorldModel,
        candidate: EnvironmentWorldModel,
        decision: EnvironmentWorldModelRevisionDecision,
        *,
        application_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> tuple[EnvironmentWorldModel, EnvironmentWorldModelRevisionApplication]:
        if type(baseline) is not EnvironmentWorldModel:
            raise TypeError("baseline must be EnvironmentWorldModel")
        if type(candidate) is not EnvironmentWorldModel:
            raise TypeError("candidate must be EnvironmentWorldModel")
        if type(decision) is not EnvironmentWorldModelRevisionDecision:
            raise TypeError("decision must be EnvironmentWorldModelRevisionDecision")
        if baseline.environment_id != candidate.environment_id != decision.environment_id:
            raise EnvironmentWorldModelRevisionApplicationError(
                "baseline, candidate, and decision must share an environment"
            )
        if decision.baseline_model_id != baseline.model_id:
            raise EnvironmentWorldModelRevisionApplicationError(
                "decision baseline identity does not match baseline model"
            )
        if decision.candidate_model_id != candidate.model_id:
            raise EnvironmentWorldModelRevisionApplicationError(
                "decision candidate identity does not match candidate model"
            )
        if decision.decision == "ACCEPT":
            resulting = candidate
            applied = True
            default_reasons = {"status": "accepted revision decision applied as candidate state"}
        elif decision.decision in {"REJECT", "DEFER"}:
            resulting = baseline
            applied = False
            default_reasons = {
                "status": "revision decision did not authorize application; baseline state retained"
            }
        else:
            raise EnvironmentWorldModelRevisionApplicationError(
                "decision value is unsupported by application contract"
            )

        application = EnvironmentWorldModelRevisionApplication(
            application_id=application_id,
            environment_id=baseline.environment_id,
            baseline_model_id=baseline.model_id,
            candidate_model_id=candidate.model_id,
            decision_id=decision.decision_id,
            applied=applied,
            resulting_model_id=resulting.model_id,
            reasons=reasons or default_reasons,
            lineage=lineage
            or {
                "decision_id": decision.decision_id,
                "baseline_model_id": baseline.model_id,
                "candidate_model_id": candidate.model_id,
            },
        )
        return resulting, application
