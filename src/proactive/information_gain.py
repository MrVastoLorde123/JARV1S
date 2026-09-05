"""M21.4 bounded information-gain and uncertainty-reduction boundary.

This module produces advisory estimates about how much additional information
could reduce uncertainty around a proactive proposal. It does not establish
truth or certainty, and it cannot authorize, schedule, notify, assign, or
execute anything.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


class InformationGainError(ValueError):
    """Raised when an information-gain contract is invalid."""


def _bounded(value: float, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field} must be a number")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{field} must be between 0 and 1")
    return value


@dataclass(frozen=True)
class InformationGainFactors:
    """Bounded advisory factors for expected uncertainty reduction."""

    current_uncertainty: float
    expected_reduction: float
    evidence_quality: float
    relevance: float

    def __post_init__(self) -> None:
        for field in ("current_uncertainty", "expected_reduction", "evidence_quality", "relevance"):
            object.__setattr__(self, field, _bounded(getattr(self, field), field))


@dataclass(frozen=True)
class InformationGainAssessment:
    """Immutable advisory information-gain estimate for one proposal."""

    proposal_id: str
    score: float
    factors: InformationGainFactors
    formula_version: str = "multiplicative-v1"
    authority_granted: bool = False
    authorization_granted: bool = False
    execution_requested: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.proposal_id, str) or not self.proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string")
        object.__setattr__(self, "score", _bounded(self.score, "score"))
        if not isinstance(self.factors, InformationGainFactors):
            raise TypeError("factors must be InformationGainFactors")
        if not isinstance(self.formula_version, str) or not self.formula_version.strip():
            raise ValueError("formula_version must be a non-empty string")
        for field in ("authority_granted", "authorization_granted", "execution_requested"):
            if not isinstance(getattr(self, field), bool):
                raise TypeError(f"{field} must be a bool")
            if getattr(self, field):
                raise InformationGainError(f"information-gain assessments cannot set {field} to true")

    def to_context(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "score": self.score,
            "formula_version": self.formula_version,
            "factors": {
                "current_uncertainty": self.factors.current_uncertainty,
                "expected_reduction": self.factors.expected_reduction,
                "evidence_quality": self.factors.evidence_quality,
                "relevance": self.factors.relevance,
            },
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


def assess_information_gain(proposal_id: str, factors: InformationGainFactors) -> InformationGainAssessment:
    """Estimate bounded expected uncertainty reduction for a proposal."""
    if not isinstance(factors, InformationGainFactors):
        raise TypeError("factors must be InformationGainFactors")
    score = (
        factors.current_uncertainty
        * factors.expected_reduction
        * factors.evidence_quality
        * factors.relevance
    )
    return InformationGainAssessment(proposal_id=proposal_id, score=max(0.0, min(1.0, score)), factors=factors)


def rank_information_gain(
    assessments: Mapping[str, InformationGainAssessment],
) -> tuple[InformationGainAssessment, ...]:
    """Rank advisory estimates deterministically without scheduling them."""
    for proposal_id, assessment in assessments.items():
        if assessment.proposal_id != proposal_id:
            raise ValueError("mapping key must match assessment.proposal_id")
    return tuple(sorted(assessments.values(), key=lambda item: (-item.score, item.proposal_id)))
