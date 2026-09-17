"""M47: bounded evaluation of initiative candidates.

This module evaluates initiative candidates using explicit descriptive dimensions
without selecting a winner, inferring user intent as fact, scheduling, notifying,
authorizing, or executing anything.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .initiative_candidate import InitiativeCandidate, InitiativeCandidateSet


@dataclass(frozen=True)
class InitiativeEvaluation:
    """Immutable descriptive evaluation of one initiative candidate."""

    candidate_id: str
    candidate_set_id: str
    value: float
    feasibility: float
    urgency: float
    rationale: str
    uncertainty_reasons: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("candidate_id", "candidate_set_id", "rationale"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("value", "feasibility", "urgency"):
            score = getattr(self, name)
            if isinstance(score, bool) or not isinstance(score, (int, float)):
                raise TypeError(f"{name} must be numeric")
            if not 0.0 <= float(score) <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0")
            object.__setattr__(self, name, float(score))
        if not isinstance(self.uncertainty_reasons, tuple):
            raise TypeError("uncertainty_reasons must be a tuple")
        if len(set(self.uncertainty_reasons)) != len(self.uncertainty_reasons):
            raise ValueError("uncertainty_reasons must contain unique values")
        if any(not isinstance(item, str) or not item.strip() for item in self.uncertainty_reasons):
            raise ValueError("uncertainty_reasons must contain non-empty strings")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "candidate_set_id": self.candidate_set_id,
            "value": self.value,
            "feasibility": self.feasibility,
            "urgency": self.urgency,
            "rationale": self.rationale,
            "uncertainty_reasons": self.uncertainty_reasons,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "intent_established": False,
            "authority_granted": False,
            "scheduling_requested": False,
            "notification_requested": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class InitiativeEvaluationSet:
    """Immutable evaluations tied to one initiative-candidate set."""

    evaluation_set_id: str
    candidate_set_id: str
    evaluations: tuple[InitiativeEvaluation, ...] = ()
    unresolved_uncertainties: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("evaluation_set_id", "candidate_set_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.evaluations, tuple) or any(
            not isinstance(item, InitiativeEvaluation) for item in self.evaluations
        ):
            raise TypeError("evaluations must be a tuple of InitiativeEvaluation values")
        ids = tuple(item.candidate_id for item in self.evaluations)
        if len(set(ids)) != len(ids):
            raise ValueError("evaluation candidate IDs must be unique")
        if any(item.candidate_set_id != self.candidate_set_id for item in self.evaluations):
            raise ValueError("evaluation candidate-set identity mismatch")
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
    def evaluation_count(self) -> int:
        return len(self.evaluations)

    def to_context(self) -> dict[str, Any]:
        return {
            "evaluation_set_id": self.evaluation_set_id,
            "candidate_set_id": self.candidate_set_id,
            "evaluations": tuple(item.to_context() for item in self.evaluations),
            "evaluation_count": self.evaluation_count,
            "unresolved_uncertainties": self.unresolved_uncertainties,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "intent_established": False,
            "authority_granted": False,
            "scheduling_requested": False,
            "notification_requested": False,
            "execution_requested": False,
        }


def build_initiative_evaluation_set(
    candidate_set: InitiativeCandidateSet,
    *,
    evaluation_set_id: str,
    evaluations: tuple[InitiativeEvaluation, ...] = (),
    metadata: Mapping[str, Any] | None = None,
) -> InitiativeEvaluationSet:
    """Validate descriptive evaluations against the exact candidate-set identity."""
    if not isinstance(candidate_set, InitiativeCandidateSet):
        raise TypeError("candidate_set must be an InitiativeCandidateSet")
    if not isinstance(evaluation_set_id, str) or not evaluation_set_id.strip():
        raise ValueError("evaluation_set_id must be a non-empty string")
    if not isinstance(evaluations, tuple) or any(
        not isinstance(item, InitiativeEvaluation) for item in evaluations
    ):
        raise TypeError("evaluations must be a tuple of InitiativeEvaluation values")

    candidate_ids = {item.candidate_id for item in candidate_set.candidates}
    for evaluation in evaluations:
        if evaluation.candidate_set_id != candidate_set.candidate_set_id:
            raise ValueError("evaluation candidate-set identity mismatch")
        if evaluation.candidate_id not in candidate_ids:
            raise ValueError("evaluation may only reference candidates from the supplied candidate set")

    return InitiativeEvaluationSet(
        evaluation_set_id=evaluation_set_id.strip(),
        candidate_set_id=candidate_set.candidate_set_id,
        evaluations=evaluations,
        unresolved_uncertainties=candidate_set.unresolved_uncertainties,
        metadata={"source": "M47", **dict(metadata or {})},
    )


__all__ = ["InitiativeEvaluation", "InitiativeEvaluationSet", "build_initiative_evaluation_set"]
