"""M69: explicit capability dependency analysis.

Dependencies describe prerequisites between capabilities. They are a
planning and systems-intelligence concern only; dependency satisfaction never
grants permission or authority to use a capability.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from src.core.capability_graph import CapabilityGraph, CapabilityRelationKind


@dataclass(frozen=True)
class CapabilityDependencyAssessment:
    """Dependency closure and readiness information for one capability."""

    capability_id: str
    direct_dependencies: tuple[str, ...]
    transitive_dependencies: tuple[str, ...]
    missing_dependencies: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return not self.missing_dependencies

    def to_context(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "direct_dependencies": self.direct_dependencies,
            "transitive_dependencies": self.transitive_dependencies,
            "missing_dependencies": self.missing_dependencies,
            "ready": self.ready,
            "authority_granted": False,
            "execution_requested": False,
        }


class CapabilityDependencyModel:
    """Read-only dependency view derived from a capability graph."""

    def __init__(self, graph: CapabilityGraph) -> None:
        if not isinstance(graph, CapabilityGraph):
            raise TypeError("graph must be a CapabilityGraph")
        self._graph = graph
        self._dependencies: Mapping[str, tuple[str, ...]] = MappingProxyType(
            {
                capability_id: tuple(
                    relation.target_capability_id
                    for relation in graph.relations_from(
                        capability_id,
                        kind=CapabilityRelationKind.DEPENDS_ON,
                    )
                )
                for capability_id in graph.capability_ids
            }
        )
        for capability_id in graph.capability_ids:
            self._closure(capability_id)

    @property
    def graph(self) -> CapabilityGraph:
        return self._graph

    def direct_dependencies(self, capability_id: str) -> tuple[str, ...]:
        self._require_capability(capability_id)
        return self._dependencies[capability_id]

    def transitive_dependencies(self, capability_id: str) -> tuple[str, ...]:
        self._require_capability(capability_id)
        return self._closure(capability_id)

    def dependency_depth(self, capability_id: str) -> int:
        dependencies = self.transitive_dependencies(capability_id)
        return 0 if not dependencies else self._max_depth(capability_id)

    def assess(
        self,
        capability_id: str,
        *,
        available_capabilities: Iterable[str] = (),
    ) -> CapabilityDependencyAssessment:
        self._require_capability(capability_id)
        available = set(available_capabilities)
        if any(not isinstance(item, str) or not item.strip() for item in available):
            raise ValueError("available_capabilities must contain non-empty strings")
        dependencies = self.transitive_dependencies(capability_id)
        missing = tuple(item for item in dependencies if item not in available)
        return CapabilityDependencyAssessment(
            capability_id=capability_id,
            direct_dependencies=self.direct_dependencies(capability_id),
            transitive_dependencies=dependencies,
            missing_dependencies=missing,
        )

    def dependency_map(self) -> Mapping[str, tuple[str, ...]]:
        return self._dependencies

    def _closure(self, capability_id: str) -> tuple[str, ...]:
        visiting: set[str] = set()
        visited: set[str] = set()
        result: list[str] = []

        def visit(current: str) -> None:
            if current in visiting:
                raise ValueError(f"capability dependency cycle detected at {current}")
            if current in visited:
                return
            visiting.add(current)
            for dependency in self._dependencies[current]:
                visit(dependency)
                if dependency not in result:
                    result.append(dependency)
            visiting.remove(current)
            visited.add(current)

        visit(capability_id)
        return tuple(result)

    def _max_depth(self, capability_id: str) -> int:
        def depth(current: str, visiting: set[str]) -> int:
            if current in visiting:
                raise ValueError(f"capability dependency cycle detected at {current}")
            visiting.add(current)
            dependencies = self._dependencies[current]
            value = 0 if not dependencies else 1 + max(
                depth(dependency, visiting) for dependency in dependencies
            )
            visiting.remove(current)
            return value

        return depth(capability_id, set())

    def _require_capability(self, capability_id: str) -> None:
        if not isinstance(capability_id, str) or not capability_id.strip():
            raise ValueError("capability_id must be a non-empty string")
        if not self._graph.has_capability(capability_id):
            raise KeyError(capability_id)


def build_capability_dependency_model(graph: CapabilityGraph) -> CapabilityDependencyModel:
    """Validate and expose the dependency model for a capability graph."""
    return CapabilityDependencyModel(graph)


__all__ = [
    "CapabilityDependencyAssessment",
    "CapabilityDependencyModel",
    "build_capability_dependency_model",
]
