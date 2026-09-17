"""M45: bounded reasoning and uncertainty substrate.

This module defines the contract between current context and downstream
reasoning. It records hypotheses and uncertainty without establishing truth,
inferring intent, granting authority, requesting execution, or selecting a
provider/model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .current_context import CurrentContext


@dataclass(frozen=True)
class ReasoningHypothesis:
    """One explicitly represented reasoning hypothesis."""

    hypothesis_id: str
    statement: str
    confidence: float
    supporting_fact_ids: tuple[str, ...] = ()
    contradicting_fact_ids: tuple[str, ...] = ()
    uncertainty_reasons: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.hypothesis_id, str) or not self.hypothesis_id.strip():
            raise ValueError("hypothesis_id must be a non-empty string")
        if not isinstance(self.statement, str) or not self.statement.strip():
            raise ValueError("statement must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise TypeError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        for name, values in (
            ("supporting_fact_ids", self.supporting_fact_ids),
            ("contradicting_fact_ids", self.contradicting_fact_ids),
            ("uncertainty_reasons", self.uncertainty_reasons),
        ):
            if not isinstance(values, tuple):
                raise TypeError(f"{name} must be a tuple")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must contain unique values")
            if any(not isinstance(item, str) or not item.strip() for item in values):
                raise ValueError(f"{name} must contain non-empty strings")
        if not set(self.supporting_fact_ids).isdisjoint(self.contradicting_fact_ids):
            raise ValueError("a fact cannot both support and contradict one hypothesis")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "confidence", float(self.confidence))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "statement": self.statement,
            "confidence": self.confidence,
            "supporting_fact_ids": self.supporting_fact_ids,
            "contradicting_fact_ids": self.contradicting_fact_ids,
            "uncertainty_reasons": self.uncertainty_reasons,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "authority_granted": False,
            "intent_established": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class ReasoningResult:
    """Immutable reasoning output bounded to one CurrentContext identity."""

    reasoning_id: str
    context_id: str
    hypotheses: tuple[ReasoningHypothesis, ...] = ()
    unresolved_uncertainties: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("reasoning_id", "context_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.hypotheses, tuple) or any(
            not isinstance(item, ReasoningHypothesis) for item in self.hypotheses
        ):
            raise TypeError("hypotheses must be a tuple of ReasoningHypothesis values")
        hypothesis_ids = tuple(item.hypothesis_id for item in self.hypotheses)
        if len(set(hypothesis_ids)) != len(hypothesis_ids):
            raise ValueError("hypothesis IDs must be unique")
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
    def hypothesis_count(self) -> int:
        return len(self.hypotheses)

    def to_context(self) -> dict[str, Any]:
        return {
            "reasoning_id": self.reasoning_id,
            "context_id": self.context_id,
            "hypotheses": tuple(item.to_context() for item in self.hypotheses),
            "hypothesis_count": self.hypothesis_count,
            "unresolved_uncertainties": self.unresolved_uncertainties,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "authority_granted": False,
            "permissions_granted": False,
            "intent_established": False,
            "execution_requested": False,
        }


def build_reasoning_result(
    context: CurrentContext,
    *,
    reasoning_id: str,
    hypotheses: tuple[ReasoningHypothesis, ...] = (),
    unresolved_uncertainties: tuple[str, ...] = (),
    metadata: Mapping[str, Any] | None = None,
) -> ReasoningResult:
    """Validate reasoning output against the exact CurrentContext fact set."""
    if not isinstance(context, CurrentContext):
        raise TypeError("context must be a CurrentContext")
    if not isinstance(reasoning_id, str) or not reasoning_id.strip():
        raise ValueError("reasoning_id must be a non-empty string")
    if not isinstance(hypotheses, tuple) or any(
        not isinstance(item, ReasoningHypothesis) for item in hypotheses
    ):
        raise TypeError("hypotheses must be a tuple of ReasoningHypothesis values")
    if not isinstance(unresolved_uncertainties, tuple):
        raise TypeError("unresolved_uncertainties must be a tuple")

    context_fact_ids = {item.fact.fact_id for item in context.facts}
    referenced_ids = {
        fact_id
        for hypothesis in hypotheses
        for fact_id in hypothesis.supporting_fact_ids + hypothesis.contradicting_fact_ids
    }
    if not referenced_ids.issubset(context_fact_ids):
        raise ValueError("reasoning may only reference facts admitted into CurrentContext")

    return ReasoningResult(
        reasoning_id=reasoning_id.strip(),
        context_id=context.context_id,
        hypotheses=hypotheses,
        unresolved_uncertainties=unresolved_uncertainties,
        metadata={"source": "M45", **dict(metadata or {})},
    )


__all__ = ["ReasoningHypothesis", "ReasoningResult", "build_reasoning_result"]
