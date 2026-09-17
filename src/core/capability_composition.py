"""M71: declarative composition of multiple capabilities into higher-order work."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from src.core.capability_dependency import CapabilityDependencyModel
from src.core.capability_graph import CapabilityGraph


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True)
class CapabilityCompositionStep:
    """One ordered declarative step in a higher-order capability."""

    order: int
    capability_id: str
    purpose: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.order, int) or isinstance(self.order, bool) or self.order < 0:
            raise ValueError("order must be a non-negative integer")
        object.__setattr__(self, "capability_id", _text(self.capability_id, "capability_id"))
        object.__setattr__(self, "purpose", _text(self.purpose, "purpose"))
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class CapabilityComposition:
    """Immutable recipe describing how existing capabilities form a compound capability."""

    composition_id: str
    output_capability_id: str
    steps: tuple[CapabilityCompositionStep, ...]
    rationale: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "composition_id", _text(self.composition_id, "composition_id"))
        object.__setattr__(
            self,
            "output_capability_id",
            _text(self.output_capability_id, "output_capability_id"),
        )
        if not isinstance(self.steps, tuple) or not self.steps:
            raise ValueError("steps must be a non-empty tuple")
        if not all(isinstance(item, CapabilityCompositionStep) for item in self.steps):
            raise TypeError("steps must contain CapabilityCompositionStep values")
        orders = tuple(item.order for item in self.steps)
        if orders != tuple(range(len(self.steps))):
            raise ValueError("composition step orders must be contiguous starting at zero")
        capability_ids = tuple(item.capability_id for item in self.steps)
        if len(set(capability_ids)) != len(capability_ids):
            raise ValueError("a composition cannot repeat a capability")
        if self.output_capability_id in capability_ids:
            raise ValueError("output capability must differ from every input capability")
        object.__setattr__(self, "rationale", _text(self.rationale, "rationale"))
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def capability_ids(self) -> tuple[str, ...]:
        return tuple(step.capability_id for step in self.steps)

    def to_context(self) -> dict[str, Any]:
        return {
            "composition_id": self.composition_id,
            "output_capability_id": self.output_capability_id,
            "capability_ids": self.capability_ids,
            "steps": tuple(
                {
                    "order": step.order,
                    "capability_id": step.capability_id,
                    "purpose": step.purpose,
                    "metadata": dict(step.metadata),
                }
                for step in self.steps
            ),
            "rationale": self.rationale,
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class CapabilityCompositionReadiness:
    """Deterministic readiness assessment for a composition."""

    composition_id: str
    required_capabilities: tuple[str, ...]
    missing_capabilities: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return not self.missing_capabilities

    def to_context(self) -> dict[str, Any]:
        return {
            "composition_id": self.composition_id,
            "required_capabilities": self.required_capabilities,
            "missing_capabilities": self.missing_capabilities,
            "ready": self.ready,
            "authority_granted": False,
            "execution_requested": False,
        }


class CapabilityCompositionModel:
    """Read-only set of declarative capability compositions."""

    def __init__(
        self,
        graph: CapabilityGraph,
        dependency_model: CapabilityDependencyModel,
        compositions: Sequence[CapabilityComposition] = (),
    ) -> None:
        if not isinstance(graph, CapabilityGraph):
            raise TypeError("graph must be a CapabilityGraph")
        if not isinstance(dependency_model, CapabilityDependencyModel):
            raise TypeError("dependency_model must be a CapabilityDependencyModel")
        if dependency_model.graph is not graph:
            raise ValueError("dependency_model must be derived from the supplied graph")
        values = tuple(compositions)
        if any(not isinstance(item, CapabilityComposition) for item in values):
            raise TypeError("compositions must contain only CapabilityComposition values")
        if len({item.composition_id for item in values}) != len(values):
            raise ValueError("composition identifiers must be unique")
        for composition in values:
            for capability_id in composition.capability_ids:
                if not graph.has_capability(capability_id):
                    raise KeyError(capability_id)
        self._graph = graph
        self._dependency_model = dependency_model
        self._compositions = MappingProxyType({item.composition_id: item for item in values})

    @property
    def graph(self) -> CapabilityGraph:
        return self._graph

    @property
    def dependency_model(self) -> CapabilityDependencyModel:
        return self._dependency_model

    def snapshot(self) -> tuple[CapabilityComposition, ...]:
        return tuple(self._compositions.values())

    def get(self, composition_id: str) -> CapabilityComposition | None:
        normalized = _text(composition_id, "composition_id")
        return self._compositions.get(normalized)

    def required_capabilities(self, composition_id: str) -> tuple[str, ...]:
        composition = self._require(composition_id)
        required: list[str] = []
        for capability_id in composition.capability_ids:
            for dependency in self._dependency_model.transitive_dependencies(capability_id):
                if dependency not in required:
                    required.append(dependency)
            if capability_id not in required:
                required.append(capability_id)
        return tuple(required)

    def assess_readiness(
        self,
        composition_id: str,
        *,
        available_capabilities: Iterable[str] = (),
    ) -> CapabilityCompositionReadiness:
        composition = self._require(composition_id)
        available = set(available_capabilities)
        required = self.required_capabilities(composition.composition_id)
        missing = tuple(item for item in required if item not in available)
        return CapabilityCompositionReadiness(
            composition_id=composition.composition_id,
            required_capabilities=required,
            missing_capabilities=missing,
        )

    def _require(self, composition_id: str) -> CapabilityComposition:
        normalized = _text(composition_id, "composition_id")
        try:
            return self._compositions[normalized]
        except KeyError as exc:
            raise KeyError(normalized) from exc


def build_capability_composition(
    *,
    composition_id: str,
    output_capability_id: str,
    steps: Sequence[CapabilityCompositionStep],
    rationale: str,
    metadata: Mapping[str, Any] | None = None,
) -> CapabilityComposition:
    """Create one validated declarative composition recipe."""
    return CapabilityComposition(
        composition_id=composition_id,
        output_capability_id=output_capability_id,
        steps=tuple(steps),
        rationale=rationale,
        metadata=metadata or {},
    )


__all__ = [
    "CapabilityComposition",
    "CapabilityCompositionModel",
    "CapabilityCompositionReadiness",
    "CapabilityCompositionStep",
    "build_capability_composition",
]
