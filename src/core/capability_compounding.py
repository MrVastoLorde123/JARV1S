"""M72: model how one capability increases the usefulness of another.

Compounding is a measurable systems-intelligence signal. It describes expected
or observed leverage between capabilities without granting authority, access,
or execution rights.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from src.core.capability_graph import CapabilityGraph
from src.core.capability_utility import CapabilityUtilityModel


class CapabilityCompoundingEvidence(str, Enum):
    """Epistemic status of a capability-compounding claim."""

    HYPOTHESIZED = "HYPOTHESIZED"
    OBSERVED = "OBSERVED"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _unit_interval(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    if not math.isfinite(result) or result < 0.0 or result > 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return result


@dataclass(frozen=True)
class CapabilityCompoundingLink:
    """One directed leverage relationship between two capabilities."""

    source_capability_id: str
    target_capability_id: str
    mechanism: str
    utility_gain: float
    confidence: float
    evidence: CapabilityCompoundingEvidence = CapabilityCompoundingEvidence.HYPOTHESIZED
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_capability_id", _text(self.source_capability_id, "source_capability_id"))
        object.__setattr__(self, "target_capability_id", _text(self.target_capability_id, "target_capability_id"))
        if self.source_capability_id == self.target_capability_id:
            raise ValueError("a compounding link cannot target the same capability")
        object.__setattr__(self, "mechanism", _text(self.mechanism, "mechanism"))
        object.__setattr__(self, "utility_gain", _unit_interval(self.utility_gain, "utility_gain"))
        object.__setattr__(self, "confidence", _unit_interval(self.confidence, "confidence"))
        if not isinstance(self.evidence, CapabilityCompoundingEvidence):
            raise TypeError("evidence must be a CapabilityCompoundingEvidence value")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def weighted_gain(self) -> float:
        """Return utility gain discounted by confidence."""
        return self.utility_gain * self.confidence

    def to_context(self) -> dict[str, Any]:
        return {
            "source_capability_id": self.source_capability_id,
            "target_capability_id": self.target_capability_id,
            "mechanism": self.mechanism,
            "utility_gain": self.utility_gain,
            "confidence": self.confidence,
            "weighted_gain": self.weighted_gain,
            "evidence": self.evidence.value,
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class CapabilityCompoundingAssessment:
    """Aggregated leverage signals for one source capability."""

    capability_id: str
    base_utility: float | None
    outgoing_links: tuple[CapabilityCompoundingLink, ...]
    total_weighted_gain: float
    leveraged_utility: float | None

    def to_context(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "base_utility": self.base_utility,
            "outgoing_link_count": len(self.outgoing_links),
            "total_weighted_gain": self.total_weighted_gain,
            "leveraged_utility": self.leveraged_utility,
            "authority_granted": False,
            "execution_requested": False,
        }


class CapabilityCompoundingModel:
    """Immutable leverage relationships over a capability graph."""

    def __init__(
        self,
        graph: CapabilityGraph,
        links: Sequence[CapabilityCompoundingLink] = (),
        *,
        utility_model: CapabilityUtilityModel | None = None,
    ) -> None:
        if not isinstance(graph, CapabilityGraph):
            raise TypeError("graph must be a CapabilityGraph")
        if utility_model is not None and not isinstance(utility_model, CapabilityUtilityModel):
            raise TypeError("utility_model must be a CapabilityUtilityModel or None")
        values = tuple(links)
        if any(not isinstance(item, CapabilityCompoundingLink) for item in values):
            raise TypeError("links must contain only CapabilityCompoundingLink values")
        seen: set[tuple[str, str]] = set()
        for link in values:
            if not graph.has_capability(link.source_capability_id):
                raise KeyError(link.source_capability_id)
            if not graph.has_capability(link.target_capability_id):
                raise KeyError(link.target_capability_id)
            key = (link.source_capability_id, link.target_capability_id)
            if key in seen:
                raise ValueError("duplicate compounding link")
            seen.add(key)
        self._graph = graph
        self._links = values
        self._utility_model = utility_model

    @property
    def graph(self) -> CapabilityGraph:
        return self._graph

    @property
    def utility_model(self) -> CapabilityUtilityModel | None:
        return self._utility_model

    def snapshot(self) -> tuple[CapabilityCompoundingLink, ...]:
        return self._links

    def outgoing(self, capability_id: str) -> tuple[CapabilityCompoundingLink, ...]:
        self._require_capability(capability_id)
        return tuple(item for item in self._links if item.source_capability_id == capability_id)

    def incoming(self, capability_id: str) -> tuple[CapabilityCompoundingLink, ...]:
        self._require_capability(capability_id)
        return tuple(item for item in self._links if item.target_capability_id == capability_id)

    def assess(self, capability_id: str) -> CapabilityCompoundingAssessment:
        self._require_capability(capability_id)
        outgoing = self.outgoing(capability_id)
        total_gain = sum(item.weighted_gain for item in outgoing)
        base_utility = None
        leveraged_utility = None
        if self._utility_model is not None:
            try:
                base_utility = self._utility_model.utility_score(capability_id)
            except KeyError:
                base_utility = None
            if base_utility is not None:
                leveraged_utility = min(1.0, base_utility + total_gain)
        return CapabilityCompoundingAssessment(
            capability_id=capability_id,
            base_utility=base_utility,
            outgoing_links=outgoing,
            total_weighted_gain=total_gain,
            leveraged_utility=leveraged_utility,
        )

    def _require_capability(self, capability_id: str) -> None:
        if not isinstance(capability_id, str) or not capability_id.strip():
            raise ValueError("capability_id must be a non-empty string")
        if not self._graph.has_capability(capability_id):
            raise KeyError(capability_id)


__all__ = [
    "CapabilityCompoundingAssessment",
    "CapabilityCompoundingEvidence",
    "CapabilityCompoundingLink",
    "CapabilityCompoundingModel",
]
