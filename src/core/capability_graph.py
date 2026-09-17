"""M68: provider-neutral graph of declared capability relationships.

The graph is an inspectable systems-intelligence substrate. It describes
capability relationships but never selects, authorizes, invokes, or executes
a capability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from src.core.capability_registry import CapabilityDefinition


class CapabilityRelationKind(str, Enum):
    """Declared relationship types used by the capability graph."""

    DEPENDS_ON = "DEPENDS_ON"
    ENABLES = "ENABLES"
    COMPOSES_WITH = "COMPOSES_WITH"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class CapabilityRelation:
    """One immutable directed relationship between declared capabilities."""

    source_capability_id: str
    target_capability_id: str
    kind: CapabilityRelationKind
    rationale: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "source_capability_id",
            _text(self.source_capability_id, "source_capability_id"),
        )
        object.__setattr__(
            self,
            "target_capability_id",
            _text(self.target_capability_id, "target_capability_id"),
        )
        if self.source_capability_id == self.target_capability_id:
            raise ValueError("a capability relation cannot connect a capability to itself")
        if not isinstance(self.kind, CapabilityRelationKind):
            raise TypeError("kind must be a CapabilityRelationKind")
        object.__setattr__(self, "rationale", _text(self.rationale, "rationale"))
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", _freeze(self.metadata))


@dataclass(frozen=True)
class CapabilityGraph:
    """Immutable graph over registered capability definitions."""

    capabilities: Mapping[str, CapabilityDefinition]
    relations: tuple[CapabilityRelation, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.capabilities, Mapping):
            raise TypeError("capabilities must be a mapping")
        normalized = dict(self.capabilities)
        for capability_id, definition in normalized.items():
            if not isinstance(capability_id, str) or not capability_id.strip():
                raise ValueError("capability identifiers must be non-empty strings")
            if not isinstance(definition, CapabilityDefinition):
                raise TypeError("capabilities must contain CapabilityDefinition values")
            if definition.capability_id != capability_id:
                raise ValueError("capability mapping key must match definition capability_id")
        object.__setattr__(self, "capabilities", MappingProxyType(normalized))
        if not isinstance(self.relations, tuple):
            raise TypeError("relations must be a tuple")
        if not all(isinstance(item, CapabilityRelation) for item in self.relations):
            raise TypeError("relations must contain only CapabilityRelation values")
        seen: set[tuple[str, str, CapabilityRelationKind]] = set()
        for relation in self.relations:
            if relation.source_capability_id not in normalized:
                raise ValueError(f"unknown source capability: {relation.source_capability_id}")
            if relation.target_capability_id not in normalized:
                raise ValueError(f"unknown target capability: {relation.target_capability_id}")
            key = (
                relation.source_capability_id,
                relation.target_capability_id,
                relation.kind,
            )
            if key in seen:
                raise ValueError("duplicate capability relation")
            seen.add(key)

    @property
    def capability_ids(self) -> tuple[str, ...]:
        return tuple(self.capabilities)

    def has_capability(self, capability_id: str) -> bool:
        return isinstance(capability_id, str) and capability_id in self.capabilities

    def relations_from(
        self,
        capability_id: str,
        *,
        kind: CapabilityRelationKind | None = None,
    ) -> tuple[CapabilityRelation, ...]:
        _text(capability_id, "capability_id")
        return tuple(
            relation
            for relation in self.relations
            if relation.source_capability_id == capability_id
            and (kind is None or relation.kind is kind)
        )

    def relations_to(
        self,
        capability_id: str,
        *,
        kind: CapabilityRelationKind | None = None,
    ) -> tuple[CapabilityRelation, ...]:
        _text(capability_id, "capability_id")
        return tuple(
            relation
            for relation in self.relations
            if relation.target_capability_id == capability_id
            and (kind is None or relation.kind is kind)
        )

    def to_context(self) -> dict[str, Any]:
        return {
            "capability_ids": self.capability_ids,
            "relations": tuple(
                {
                    "source_capability_id": relation.source_capability_id,
                    "target_capability_id": relation.target_capability_id,
                    "kind": relation.kind.value,
                    "rationale": relation.rationale,
                    "metadata": dict(relation.metadata),
                }
                for relation in self.relations
            ),
            "authority_granted": False,
            "execution_requested": False,
        }


def build_capability_graph(
    capabilities: Sequence[CapabilityDefinition],
    relations: Sequence[CapabilityRelation] = (),
) -> CapabilityGraph:
    """Build one immutable graph from declared capabilities and relationships."""

    definitions = tuple(capabilities)
    if any(not isinstance(item, CapabilityDefinition) for item in definitions):
        raise TypeError("capabilities must contain only CapabilityDefinition values")
    if len({item.capability_id for item in definitions}) != len(definitions):
        raise ValueError("capabilities must have unique capability identifiers")
    if not isinstance(relations, (tuple, list)):
        raise TypeError("relations must be a sequence")
    return CapabilityGraph(
        capabilities={item.capability_id: item for item in definitions},
        relations=tuple(relations),
    )


__all__ = [
    "CapabilityGraph",
    "CapabilityRelation",
    "CapabilityRelationKind",
    "build_capability_graph",
]
