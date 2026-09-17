"""M49: bounded proactive proposal substrate.

This module turns evaluated initiatives and uncertainty-reduction opportunities
into descriptive proactive proposals. A proposal is an advisory candidate for
user-facing consideration; it does not infer intent, schedule, notify,
authorize, execute, or select providers/tools.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .information_gain import InformationGainAssessment
from .initiative_evaluation import InitiativeEvaluationSet


@dataclass(frozen=True)
class ProactiveProposal:
    """Immutable descriptive proposal for downstream user consideration."""

    proposal_id: str
    evaluation_set_id: str
    statement: str
    rationale: str
    candidate_id: str | None = None
    information_gain_opportunity_ids: tuple[str, ...] = ()
    unresolved_uncertainties: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("proposal_id", "evaluation_set_id", "statement", "rationale"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.candidate_id is not None and (not isinstance(self.candidate_id, str) or not self.candidate_id.strip()):
            raise ValueError("candidate_id must be a non-empty string when supplied")
        if not isinstance(self.information_gain_opportunity_ids, tuple):
            raise TypeError("information_gain_opportunity_ids must be a tuple")
        if len(set(self.information_gain_opportunity_ids)) != len(self.information_gain_opportunity_ids):
            raise ValueError("information_gain_opportunity_ids must contain unique values")
        if any(not isinstance(item, str) or not item.strip() for item in self.information_gain_opportunity_ids):
            raise ValueError("information_gain_opportunity_ids must contain non-empty strings")
        if not isinstance(self.unresolved_uncertainties, tuple):
            raise TypeError("unresolved_uncertainties must be a tuple")
        if len(set(self.unresolved_uncertainties)) != len(self.unresolved_uncertainties):
            raise ValueError("unresolved_uncertainties must contain unique values")
        if any(not isinstance(item, str) or not item.strip() for item in self.unresolved_uncertainties):
            raise ValueError("unresolved_uncertainties must contain non-empty strings")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "evaluation_set_id": self.evaluation_set_id,
            "statement": self.statement,
            "rationale": self.rationale,
            "candidate_id": self.candidate_id,
            "information_gain_opportunity_ids": self.information_gain_opportunity_ids,
            "unresolved_uncertainties": self.unresolved_uncertainties,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "intent_established": False,
            "authority_granted": False,
            "scheduling_requested": False,
            "notification_requested": False,
            "authorization_requested": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class ProactiveProposalSet:
    """Immutable bounded collection of proactive proposals."""

    proposal_set_id: str
    evaluation_set_id: str
    proposals: tuple[ProactiveProposal, ...] = ()
    unresolved_uncertainties: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("proposal_set_id", "evaluation_set_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.proposals, tuple) or any(
            not isinstance(item, ProactiveProposal) for item in self.proposals
        ):
            raise TypeError("proposals must be a tuple of ProactiveProposal values")
        ids = tuple(item.proposal_id for item in self.proposals)
        if len(set(ids)) != len(ids):
            raise ValueError("proposal IDs must be unique")
        if any(item.evaluation_set_id != self.evaluation_set_id for item in self.proposals):
            raise ValueError("proposal evaluation-set identity mismatch")
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
    def proposal_count(self) -> int:
        return len(self.proposals)

    def to_context(self) -> dict[str, Any]:
        return {
            "proposal_set_id": self.proposal_set_id,
            "evaluation_set_id": self.evaluation_set_id,
            "proposals": tuple(item.to_context() for item in self.proposals),
            "proposal_count": self.proposal_count,
            "unresolved_uncertainties": self.unresolved_uncertainties,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "intent_established": False,
            "authority_granted": False,
            "scheduling_requested": False,
            "notification_requested": False,
            "authorization_requested": False,
            "execution_requested": False,
        }


def build_proactive_proposal_set(
    evaluation_set: InitiativeEvaluationSet,
    information_gain: InformationGainAssessment,
    *,
    proposal_set_id: str,
    proposals: tuple[ProactiveProposal, ...] = (),
    metadata: Mapping[str, Any] | None = None,
) -> ProactiveProposalSet:
    """Build proposals against exact evaluation and information-gain identities."""
    if not isinstance(evaluation_set, InitiativeEvaluationSet):
        raise TypeError("evaluation_set must be an InitiativeEvaluationSet")
    if not isinstance(information_gain, InformationGainAssessment):
        raise TypeError("information_gain must be an InformationGainAssessment")
    if information_gain.evaluation_set_id != evaluation_set.evaluation_set_id:
        raise ValueError("evaluation-set identity mismatch")
    if not isinstance(proposal_set_id, str) or not proposal_set_id.strip():
        raise ValueError("proposal_set_id must be a non-empty string")
    if not isinstance(proposals, tuple) or any(not isinstance(item, ProactiveProposal) for item in proposals):
        raise TypeError("proposals must be a tuple of ProactiveProposal values")

    candidate_ids = {item.candidate_id for item in evaluation_set.evaluations}
    opportunity_ids = {item.opportunity_id for item in information_gain.opportunities}
    uncertainties = set(information_gain.unresolved_uncertainties)

    for proposal in proposals:
        if proposal.evaluation_set_id != evaluation_set.evaluation_set_id:
            raise ValueError("proposal evaluation-set identity mismatch")
        if proposal.candidate_id is not None and proposal.candidate_id not in candidate_ids:
            raise ValueError("proposal may only reference candidates from the supplied evaluation set")
        if not set(proposal.information_gain_opportunity_ids).issubset(opportunity_ids):
            raise ValueError("proposal may only reference supplied information-gain opportunities")
        if not set(proposal.unresolved_uncertainties).issubset(uncertainties):
            raise ValueError("proposal may only carry unresolved uncertainties from the supplied information-gain assessment")

    return ProactiveProposalSet(
        proposal_set_id=proposal_set_id.strip(),
        evaluation_set_id=evaluation_set.evaluation_set_id,
        proposals=proposals,
        unresolved_uncertainties=information_gain.unresolved_uncertainties,
        metadata={"source": "M49", **dict(metadata or {})},
    )


__all__ = ["ProactiveProposal", "ProactiveProposalSet", "build_proactive_proposal_set"]
