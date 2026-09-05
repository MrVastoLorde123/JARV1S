"""Bounded value assessment for proactive proposals.

M21.3 estimates relative user value for already-formed proactive proposals.
The assessment is advisory only: it cannot schedule, authorize, or execute work.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


class ValueAssessmentError(ValueError):
    """Raised when a proactive value assessment is invalid."""



def _bounded(value: float, field: str) -> float:
    """Validate and normalize a finite [0, 1] factor."""
    if isinstance(value, bool):
        raise ValueAssessmentError(f"{field} must be numeric")
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueAssessmentError(f"{field} must be numeric") from exc
    if numeric < 0.0 or numeric > 1.0:
        raise ValueAssessmentError(f"{field} must be between 0 and 1")
    return numeric


@dataclass(frozen=True)
class ProposalValueFactors:
    """Bounded normalized factors used to estimate proposal value."""

    importance: float
    urgency: float
    expected_benefit: float
    confidence: float
    effort_cost: float
    risk: float

    def __post_init__(self) -> None:
        for name, value in (
            ("importance", self.importance),
            ("urgency", self.urgency),
            ("expected_benefit", self.expected_benefit),
            ("confidence", self.confidence),
            ("effort_cost", self.effort_cost),
            ("risk", self.risk),
        ):
            object.__setattr__(self, name, _bounded(value, name))


@dataclass(frozen=True)
class ProposalValueAssessment:
    """Deterministic advisory value estimate for one proposal."""

    proposal_id: str
    score: float
    factors: ProposalValueFactors
    formula_version: str = "linear-v1"
    authority_granted: bool = False
    authorization_granted: bool = False
    execution_requested: bool = False

    def __post_init__(self) -> None:
        if not self.proposal_id:
            raise ValueAssessmentError("proposal_id must not be empty")
        score = _bounded(self.score, "score")
        object.__setattr__(self, "score", score)
        if self.authority_granted or self.authorization_granted or self.execution_requested:
            raise ValueAssessmentError("value assessment cannot grant authority or request execution")

    def to_context(self) -> dict[str, object]:
        """Expose advisory context without authority semantics."""
        return {
            "proposal_id": self.proposal_id,
            "score": self.score,
            "formula_version": self.formula_version,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "factors": {
                "importance": self.factors.importance,
                "urgency": self.factors.urgency,
                "expected_benefit": self.factors.expected_benefit,
                "confidence": self.factors.confidence,
                "effort_cost": self.factors.effort_cost,
                "risk": self.factors.risk,
            },
        }


def assess_proposal_value(
    proposal_id: str,
    factors: ProposalValueFactors,
) -> ProposalValueAssessment:
    """Return a deterministic advisory value score.

    Score = 0.25*importance + 0.20*urgency + 0.25*benefit
            + 0.10*confidence - 0.10*cost - 0.10*risk.

    The result is clamped to [0, 1]. This is a prioritization input, not a
    permission decision and does not imply that the proposal should execute.
    """
    score = (
        0.25 * factors.importance
        + 0.20 * factors.urgency
        + 0.25 * factors.expected_benefit
        + 0.10 * factors.confidence
        - 0.10 * factors.effort_cost
        - 0.10 * factors.risk
    )
    score = max(0.0, min(1.0, score))
    return ProposalValueAssessment(proposal_id=proposal_id, score=score, factors=factors)


def rank_assessments(
    assessments: Mapping[str, ProposalValueAssessment],
) -> tuple[ProposalValueAssessment, ...]:
    """Return deterministic advisory ordering: score descending, id ascending."""
    values = tuple(assessments.values())
    if any(key != value.proposal_id for key, value in assessments.items()):
        raise ValueAssessmentError("assessment mapping key must match proposal_id")
    return tuple(sorted(values, key=lambda item: (-item.score, item.proposal_id)))
