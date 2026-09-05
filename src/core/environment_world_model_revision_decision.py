"""M23.17: explicit decision evidence for a world-model revision proposal.

This boundary converts a validated advisory revision proposal into a deterministic
non-mutating decision artifact. It does not apply revision or establish truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_revision_proposal import (
    EnvironmentWorldModelRevisionProposal,
)


class EnvironmentWorldModelRevisionDecisionError(RuntimeError):
    """Raised when a world-model revision decision cannot be formed safely."""


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
class EnvironmentWorldModelRevisionDecision:
    """Immutable decision evidence derived from one advisory revision proposal."""

    decision_id: str
    environment_id: str
    baseline_model_id: str
    candidate_model_id: str
    proposal_id: str
    assessment_id: str
    decision: str
    changed_domains: tuple[str, ...]
    unchanged_domains: tuple[str, ...]
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "decision_id",
            "environment_id",
            "baseline_model_id",
            "candidate_model_id",
            "proposal_id",
            "assessment_id",
            "decision",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.baseline_model_id == self.candidate_model_id:
            raise ValueError("baseline and candidate model identities must differ")
        if self.decision not in {"ACCEPT", "DEFER", "REJECT"}:
            raise ValueError("decision must be ACCEPT, DEFER, or REJECT")
        if not isinstance(self.changed_domains, tuple):
            raise TypeError("changed_domains must be a tuple")
        if not isinstance(self.unchanged_domains, tuple):
            raise TypeError("unchanged_domains must be a tuple")
        if set(self.changed_domains) & set(self.unchanged_domains):
            raise ValueError("changed and unchanged domains must be disjoint")
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
    def applies_revision(self) -> bool:
        return False


class EnvironmentWorldModelRevisionDecisionService:
    """Convert one validated revision proposal into deterministic decision evidence."""

    def decide(
        self,
        proposal: EnvironmentWorldModelRevisionProposal,
        *,
        decision_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRevisionDecision:
        if type(proposal) is not EnvironmentWorldModelRevisionProposal:
            raise TypeError("proposal must be EnvironmentWorldModelRevisionProposal")

        if proposal.recommendation == "CONSIDER_REVISION":
            decision = "ACCEPT"
            default_reasons = {
                "status": "validated proposal contains one or more detected model changes"
            }
        elif proposal.recommendation == "NO_CHANGE":
            decision = "REJECT"
            default_reasons = {"status": "validated proposal contains no detected model changes"}
        else:
            raise EnvironmentWorldModelRevisionDecisionError(
                "proposal recommendation is not supported by the decision contract"
            )

        return EnvironmentWorldModelRevisionDecision(
            decision_id=decision_id,
            environment_id=proposal.environment_id,
            baseline_model_id=proposal.baseline_model_id,
            candidate_model_id=proposal.candidate_model_id,
            proposal_id=proposal.proposal_id,
            assessment_id=proposal.assessment_id,
            decision=decision,
            changed_domains=proposal.changed_domains,
            unchanged_domains=proposal.unchanged_domains,
            reasons=reasons or default_reasons,
            lineage=lineage
            or {
                "proposal_id": proposal.proposal_id,
                "assessment_id": proposal.assessment_id,
            },
        )
