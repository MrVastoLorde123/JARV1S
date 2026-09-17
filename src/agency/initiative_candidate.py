"""M46: bounded initiative candidates derived from reasoning and uncertainty.

An initiative candidate records a possible objective worth evaluating downstream.
It is descriptive/propositive only: it does not authorize, schedule, execute,
select capabilities/providers, infer intent as fact, or establish truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .reasoning import ReasoningResult


@dataclass(frozen=True)
class InitiativeCandidate:
    """Immutable candidate for downstream initiative evaluation."""

    candidate_id: str
    reasoning_id: str
    statement: str
    supporting_hypothesis_ids: tuple[str, ...] = ()
    uncertainty_reasons: tuple[str, ...] = ()
    rationale: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("candidate_id", "reasoning_id", "statement", "rationale"):
            value = getattr(self, name)
            if not isinstance(value, str) or (name != "rationale" and not value.strip()):
                raise ValueError(f"{name} must be a non-empty string")
        for name, values in (
            ("supporting_hypothesis_ids", self.supporting_hypothesis_ids),
            ("uncertainty_reasons", self.uncertainty_reasons),
        ):
            if not isinstance(values, tuple):
                raise TypeError(f"{name} must be a tuple")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must contain unique values")
            if any(not isinstance(item, str) or not item.strip() for item in values):
                raise ValueError(f"{name} must contain non-empty strings")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "reasoning_id": self.reasoning_id,
            "statement": self.statement,
            "supporting_hypothesis_ids": self.supporting_hypothesis_ids,
            "uncertainty_reasons": self.uncertainty_reasons,
            "rationale": self.rationale,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "intent_established": False,
            "authority_granted": False,
            "permissions_granted": False,
            "scheduling_requested": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class InitiativeCandidateSet:
    """Immutable bounded set of candidates tied to one reasoning result."""

    candidate_set_id: str
    reasoning_id: str
    candidates: tuple[InitiativeCandidate, ...] = ()
    unresolved_uncertainties: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("candidate_set_id", "reasoning_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.candidates, tuple) or any(
            not isinstance(item, InitiativeCandidate) for item in self.candidates
        ):
            raise TypeError("candidates must be a tuple of InitiativeCandidate values")
        ids = tuple(item.candidate_id for item in self.candidates)
        if len(set(ids)) != len(ids):
            raise ValueError("candidate IDs must be unique")
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
    def candidate_count(self) -> int:
        return len(self.candidates)

    def to_context(self) -> dict[str, Any]:
        return {
            "candidate_set_id": self.candidate_set_id,
            "reasoning_id": self.reasoning_id,
            "candidates": tuple(item.to_context() for item in self.candidates),
            "candidate_count": self.candidate_count,
            "unresolved_uncertainties": self.unresolved_uncertainties,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "intent_established": False,
            "authority_granted": False,
            "permissions_granted": False,
            "scheduling_requested": False,
            "execution_requested": False,
        }


def build_initiative_candidate_set(
    reasoning: ReasoningResult,
    *,
    candidate_set_id: str,
    candidates: tuple[InitiativeCandidate, ...] = (),
    metadata: Mapping[str, Any] | None = None,
) -> InitiativeCandidateSet:
    """Build candidates whose supporting hypotheses belong to the exact reasoning result."""
    if not isinstance(reasoning, ReasoningResult):
        raise TypeError("reasoning must be a ReasoningResult")
    if not isinstance(candidate_set_id, str) or not candidate_set_id.strip():
        raise ValueError("candidate_set_id must be a non-empty string")
    if not isinstance(candidates, tuple) or any(
        not isinstance(item, InitiativeCandidate) for item in candidates
    ):
        raise TypeError("candidates must be a tuple of InitiativeCandidate values")

    hypothesis_ids = {item.hypothesis_id for item in reasoning.hypotheses}
    for candidate in candidates:
        if candidate.reasoning_id != reasoning.reasoning_id:
            raise ValueError("candidate reasoning identity mismatch")
        if not set(candidate.supporting_hypothesis_ids).issubset(hypothesis_ids):
            raise ValueError("candidate may only reference hypotheses from the supplied reasoning result")

    return InitiativeCandidateSet(
        candidate_set_id=candidate_set_id.strip(),
        reasoning_id=reasoning.reasoning_id,
        candidates=candidates,
        unresolved_uncertainties=reasoning.unresolved_uncertainties,
        metadata={"source": "M46", **dict(metadata or {})},
    )


__all__ = ["InitiativeCandidate", "InitiativeCandidateSet", "build_initiative_candidate_set"]
