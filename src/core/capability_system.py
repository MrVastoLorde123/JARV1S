"""M73: compose graph, dependencies, utility, composition, and leverage.

``CapabilitySystem`` is an immutable analysis boundary over declared
capabilities. It makes relationships and measurable leverage inspectable as a
system without introducing execution, authorization, provider selection, or
persistence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from src.core.capability_compounding import (
    CapabilityCompoundingLink,
    CapabilityCompoundingModel,
)
from src.core.capability_composition import (
    CapabilityComposition,
    CapabilityCompositionModel,
    CapabilityCompositionReadiness,
)
from src.core.capability_dependency import (
    CapabilityDependencyModel,
    build_capability_dependency_model,
)
from src.core.capability_graph import (
    CapabilityGraph,
    CapabilityRelation,
    build_capability_graph,
)
from src.core.capability_registry import CapabilityRegistry
from src.core.capability_utility import (
    CapabilityUtilityModel,
    CapabilityUtilityProfile,
    CapabilityUtilityWeights,
)


@dataclass(frozen=True)
class CapabilitySystemAssessment:
    """Cross-model systems-intelligence assessment for one capability."""

    capability_id: str
    dependency_count: int
    dependency_depth: int
    utility_score: float | None
    composition_count: int
    outgoing_compounding_link_count: int
    incoming_compounding_link_count: int
    total_weighted_compounding_gain: float
    leveraged_utility: float | None

    def to_context(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "dependency_count": self.dependency_count,
            "dependency_depth": self.dependency_depth,
            "utility_score": self.utility_score,
            "composition_count": self.composition_count,
            "outgoing_compounding_link_count": self.outgoing_compounding_link_count,
            "incoming_compounding_link_count": self.incoming_compounding_link_count,
            "total_weighted_compounding_gain": self.total_weighted_compounding_gain,
            "leveraged_utility": self.leveraged_utility,
            "authority_granted": False,
            "execution_requested": False,
        }


class CapabilitySystem:
    """Immutable composition root for capability systems intelligence."""

    def __init__(
        self,
        graph: CapabilityGraph,
        *,
        dependency_model: CapabilityDependencyModel | None = None,
        utility_model: CapabilityUtilityModel | None = None,
        compositions: Sequence[CapabilityComposition] = (),
        compounding_links: Sequence[CapabilityCompoundingLink] = (),
        utility_weights: CapabilityUtilityWeights | None = None,
    ) -> None:
        if not isinstance(graph, CapabilityGraph):
            raise TypeError("graph must be a CapabilityGraph")
        dependency_model = dependency_model or build_capability_dependency_model(graph)
        if dependency_model.graph is not graph:
            raise ValueError("dependency_model must be derived from graph")
        if utility_model is None:
            utility_model = CapabilityUtilityModel(weights=utility_weights)
        elif utility_weights is not None and utility_model.weights != utility_weights:
            raise ValueError("utility_weights conflicts with supplied utility_model")
        unknown_profiles = tuple(
            profile.capability_id
            for profile in utility_model.snapshot()
            if not graph.has_capability(profile.capability_id)
        )
        if unknown_profiles:
            raise KeyError(
                f"utility profiles reference unknown capabilities: {unknown_profiles}"
            )
        composition_model = CapabilityCompositionModel(
            graph,
            dependency_model,
            compositions,
        )
        compounding_model = CapabilityCompoundingModel(
            graph,
            compounding_links,
            utility_model=utility_model,
        )
        self._graph = graph
        self._dependency_model = dependency_model
        self._utility_model = utility_model
        self._composition_model = composition_model
        self._compounding_model = compounding_model

    @classmethod
    def from_registry(
        cls,
        registry: CapabilityRegistry,
        *,
        relations: Sequence[CapabilityRelation] = (),
        utility_profiles: Sequence[CapabilityUtilityProfile] = (),
        compositions: Sequence[CapabilityComposition] = (),
        compounding_links: Sequence[CapabilityCompoundingLink] = (),
        utility_weights: CapabilityUtilityWeights | None = None,
    ) -> "CapabilitySystem":
        """Build a systems-intelligence snapshot from the current registry."""
        if type(registry) is not CapabilityRegistry:
            raise TypeError("registry must be a CapabilityRegistry")
        graph = build_capability_graph(registry.snapshot(), relations)
        utility_model = CapabilityUtilityModel(utility_profiles, weights=utility_weights)
        return cls(
            graph,
            utility_model=utility_model,
            compositions=compositions,
            compounding_links=compounding_links,
        )

    @property
    def graph(self) -> CapabilityGraph:
        return self._graph

    @property
    def dependency_model(self) -> CapabilityDependencyModel:
        return self._dependency_model

    @property
    def utility_model(self) -> CapabilityUtilityModel:
        return self._utility_model

    @property
    def composition_model(self) -> CapabilityCompositionModel:
        return self._composition_model

    @property
    def compounding_model(self) -> CapabilityCompoundingModel:
        return self._compounding_model

    @property
    def capability_ids(self) -> tuple[str, ...]:
        return self._graph.capability_ids

    def assess(self, capability_id: str) -> CapabilitySystemAssessment:
        if not self._graph.has_capability(capability_id):
            raise KeyError(capability_id)
        try:
            utility_score = self._utility_model.utility_score(capability_id)
        except KeyError:
            utility_score = None
        compounding = self._compounding_model.assess(capability_id)
        composition_count = sum(
            capability_id in composition.capability_ids
            for composition in self._composition_model.snapshot()
        )
        return CapabilitySystemAssessment(
            capability_id=capability_id,
            dependency_count=len(self._dependency_model.transitive_dependencies(capability_id)),
            dependency_depth=self._dependency_model.dependency_depth(capability_id),
            utility_score=utility_score,
            composition_count=composition_count,
            outgoing_compounding_link_count=len(compounding.outgoing_links),
            incoming_compounding_link_count=len(self._compounding_model.incoming(capability_id)),
            total_weighted_compounding_gain=compounding.total_weighted_gain,
            leveraged_utility=compounding.leveraged_utility,
        )

    def assess_all(self) -> tuple[CapabilitySystemAssessment, ...]:
        return tuple(self.assess(capability_id) for capability_id in self.capability_ids)

    def assess_composition_readiness(
        self,
        composition_id: str,
        *,
        available_capabilities: Iterable[str],
    ) -> CapabilityCompositionReadiness:
        """Assess prerequisites without invoking or authorizing the composition."""
        return self._composition_model.assess_readiness(
            composition_id,
            available_capabilities=available_capabilities,
        )

    def summary(self) -> Mapping[str, Any]:
        assessments = self.assess_all()
        utility_values = tuple(item.utility_score for item in assessments if item.utility_score is not None)
        return {
            "capability_count": len(self._graph.capability_ids),
            "relationship_count": len(self._graph.relations),
            "dependency_relationship_count": sum(
                relation.kind.value == "DEPENDS_ON" for relation in self._graph.relations
            ),
            "composition_count": len(self._composition_model.snapshot()),
            "compounding_link_count": len(self._compounding_model.snapshot()),
            "average_utility_score": (
                0.0 if not utility_values else sum(utility_values) / len(utility_values)
            ),
            "total_weighted_compounding_gain": sum(
                item.total_weighted_compounding_gain for item in assessments
            ),
            "authority_granted": False,
            "execution_requested": False,
        }

    def to_context(self) -> dict[str, Any]:
        return {
            "summary": dict(self.summary()),
            "graph": self._graph.to_context(),
            "utility": self._utility_model.to_context(),
            "assessments": tuple(item.to_context() for item in self.assess_all()),
            "compositions": tuple(
                item.to_context() for item in self._composition_model.snapshot()
            ),
            "compounding_links": tuple(
                item.to_context() for item in self._compounding_model.snapshot()
            ),
            "authority_granted": False,
            "execution_requested": False,
        }


__all__ = ["CapabilitySystem", "CapabilitySystemAssessment"]
