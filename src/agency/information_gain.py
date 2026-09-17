"""M48: bounded information-gain and uncertainty-reduction substrate.

This module identifies explicit uncertainty-reduction opportunities from an
initiative evaluation set. It does not schedule, notify, authorize, execute,
select a provider/tool, or declare a value judgment as authoritative.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .initiative_evaluation import InitiativeEvaluationSet


@dataclass(frozen=True)
class InformationGainOpportunity:
    """One bounded opportunity to reduce a named unresolved uncertainty."""

    opportunity_id: str
    evaluation_set_id: str
    uncertainty: str
    expected_information_gain: float
    rationale: str
    candidate_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("opportunity_id", "evaluation_set_id", "uncertainty", "rationale"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.candidate_id is not None and (not isinstance(self.candidate_id, str) or not self.candidate_id.strip()):
            raise ValueError("candidate_id must be a non-empty string when supplied")
        if isinstance(self.expected_information_gain, bool) or not isinstance(self.expected_information_gain, (int, float)):
            raise TypeError("expected_information_gain must be numeric")
        if not 0.0 <= float(self.expected_information_gain) <= 1.0:
            raise ValueError("expected_information_gain must be between 0.0 and 1.0")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "expected_information_gain", float(self.expected_information_gain))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "evaluation_set_id": self.evaluation_set_id,
            "uncertainty": self.uncertainty,
            "expected_information_gain": self.expected_information_gain,
            "rationale": self.rationale,
            "candidate_id": self.candidate_id,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "intent_established": False,
            "authority_granted": False,
            "scheduling_requested": False,
            "notification_requested": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class InformationGainAssessment:
    """Immutable set of uncertainty-reduction opportunities."""

    assessment_id: str
    evaluation_set_id: str
    opportunities: tuple[InformationGainOpportunity, ...] = ()
    unresolved_uncertainties: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("assessment_id", "evaluation_set_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.opportunities, tuple) or any(
            not isinstance(item, InformationGainOpportunity) for item in self.opportunities
        ):
            raise TypeError("opportunities must be a tuple of InformationGainOpportunity values")
        ids = tuple(item.opportunity_id for item in self.opportunities)
        if len(set(ids)) != len(ids):
            raise ValueError("opportunity IDs must be unique")
        if any(item.evaluation_set_id != self.evaluation_set_id for item in self.opportunities):
            raise ValueError("opportunity evaluation-set identity mismatch")
        if not isinstance(self.unresolved_uncertainties, tuple):
            raise TypeError("unresolved_uncertainties must be a tuple")
        if len(set(self.unresolved_uncertainties)) != len(self.unresolved_uncertainties):
            raise ValueError("unresolved_uncertainties must contain unique values")
        if any(not isinstance(item, str) or not item.strip() for item in self.unresolved_uncertainties):
            raise ValueError("unresolved_uncertainties must contain non-empty strings")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def opportunity_count(self) -> int:
        return len(self.opportunities)

    def to_context(self) -> dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "evaluation_set_id": self.evaluation_set_id,
            "opportunities": tuple(item.to_context() for item in self.opportunities),
            "opportunity_count": self.opportunity_count,
            "unresolved_uncertainties": self.unresolved_uncertainties,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "intent_established": False,
            "authority_granted": False,
            "scheduling_requested": False,
            "notification_requested": False,
            "execution_requested": False,
        }


def build_information_gain_assessment(
    evaluation_set: InitiativeEvaluationSet,
    *,
    assessment_id: str,
    opportunities: tuple[InformationGainOpportunity, ...] = (),
    metadata: Mapping[str, Any] | None = None,
) -> InformationGainAssessment:
    """Build uncertainty-reduction opportunities against one exact evaluation set."""
    if not isinstance(evaluation_set, InitiativeEvaluationSet):
        raise TypeError("evaluation_set must be an InitiativeEvaluationSet")
    if not isinstance(assessment_id, str) or not assessment_id.strip():
        raise ValueError("assessment_id must be a non-empty string")
    if not isinstance(opportunities, tuple) or any(
        not isinstance(item, InformationGainOpportunity) for item in opportunities
    ):
        raise TypeError("opportunities must be a tuple of InformationGainOpportunity values")

    known_candidate_ids = {item.candidate_id for item in evaluation_set.evaluations}
    known_uncertainties = set(evaluation_set.unresolved_uncertainties)
    for opportunity in opportunities:
        if opportunity.evaluation_set_id != evaluation_set.evaluation_set_id:
            raise ValueError("opportunity evaluation-set identity mismatch")
        if opportunity.uncertainty not in known_uncertainties:
            raise ValueError("opportunity may only reference an unresolved uncertainty from the supplied evaluation set")
        if opportunity.candidate_id is not None and opportunity.candidate_id not in known_candidate_ids:
            raise ValueError("opportunity may only reference candidates from the supplied evaluation set")

    return InformationGainAssessment(
        assessment_id=assessment_id.strip(),
        evaluation_set_id=evaluation_set.evaluation_set_id,
        opportunities=opportunities,
        unresolved_uncertainties=evaluation_set.unresolved_uncertainties,
        metadata={"source": "M48", **dict(metadata or {})},
    )


__all__ = ["InformationGainAssessment", "InformationGainOpportunity", "build_information_gain_assessment"]
