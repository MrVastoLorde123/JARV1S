"""M23.16: non-mutating revision proposal evidence for descriptive world models.

This boundary turns explicit model-change evidence into an advisory proposal.
It never applies a revision, establishes truth, or grants execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_change_assessment import (
    EnvironmentWorldModelChangeAssessment,
)


class EnvironmentWorldModelRevisionProposalError(RuntimeError):
    """Raised when a world-model revision proposal cannot be formed safely."""


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
class EnvironmentWorldModelRevisionProposal:
    """Immutable advisory proposal to consider a candidate model as a revision."""

    proposal_id: str
    environment_id: str
    baseline_model_id: str
    candidate_model_id: str
    assessment_id: str
    recommendation: str
    changed_domains: tuple[str, ...]
    unchanged_domains: tuple[str, ...]
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "proposal_id",
            "environment_id",
            "baseline_model_id",
            "candidate_model_id",
            "assessment_id",
            "recommendation",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.baseline_model_id == self.candidate_model_id:
            raise ValueError("baseline and candidate model identities must differ")
        if self.recommendation not in {"NO_CHANGE", "CONSIDER_REVISION"}:
            raise ValueError("recommendation must be NO_CHANGE or CONSIDER_REVISION")
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


class EnvironmentWorldModelRevisionProposalService:
    """Convert validated change evidence into a non-mutating revision proposal."""

    def propose(
        self,
        baseline: EnvironmentWorldModel,
        candidate: EnvironmentWorldModel,
        assessment: EnvironmentWorldModelChangeAssessment,
        *,
        proposal_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRevisionProposal:
        if type(baseline) is not EnvironmentWorldModel:
            raise TypeError("baseline must be EnvironmentWorldModel")
        if type(candidate) is not EnvironmentWorldModel:
            raise TypeError("candidate must be EnvironmentWorldModel")
        if type(assessment) is not EnvironmentWorldModelChangeAssessment:
            raise TypeError("assessment must be EnvironmentWorldModelChangeAssessment")
        if assessment.environment_id != baseline.environment_id or assessment.environment_id != candidate.environment_id:
            raise EnvironmentWorldModelRevisionProposalError(
                "baseline, candidate, and assessment must share an environment"
            )
        if assessment.baseline_model_id != baseline.model_id:
            raise EnvironmentWorldModelRevisionProposalError(
                "assessment baseline identity does not match baseline model"
            )
        if assessment.candidate_model_id != candidate.model_id:
            raise EnvironmentWorldModelRevisionProposalError(
                "assessment candidate identity does not match candidate model"
            )

        recommendation = "CONSIDER_REVISION" if assessment.changed_domains else "NO_CHANGE"
        default_reasons = {
            "status": (
                "candidate differs from baseline in one or more represented domains"
                if assessment.changed_domains
                else "candidate contains no detected domain changes"
            )
        }
        return EnvironmentWorldModelRevisionProposal(
            proposal_id=proposal_id,
            environment_id=baseline.environment_id,
            baseline_model_id=baseline.model_id,
            candidate_model_id=candidate.model_id,
            assessment_id=assessment.assessment_id,
            recommendation=recommendation,
            changed_domains=assessment.changed_domains,
            unchanged_domains=assessment.unchanged_domains,
            reasons=reasons or default_reasons,
            lineage=lineage
            or {
                "assessment_id": assessment.assessment_id,
                "baseline_model_id": baseline.model_id,
                "candidate_model_id": candidate.model_id,
            },
        )
