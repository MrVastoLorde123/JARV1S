"""M26.2: provider-neutral registry of declared JARVIS capabilities."""
from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from types import MappingProxyType
from typing import Any, Mapping


class CapabilityRegistryError(RuntimeError):
    """Raised when capability registration violates the registry contract."""


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
class CapabilityDefinition:
    """Immutable declaration of one capability; contains no executable handler."""

    capability_id: str
    name: str
    description: str
    category: str
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        for field in ("capability_id", "name", "description", "category"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be a non-empty string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @property
    def normalized_name(self) -> str:
        return self.name.strip().lower()


class CapabilityRegistry:
    """Thread-safe registry for declared capabilities without execution semantics."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._definitions: dict[str, CapabilityDefinition] = {}
        self._names: dict[str, str] = {}

    def register(self, definition: CapabilityDefinition) -> CapabilityDefinition:
        if type(definition) is not CapabilityDefinition:
            raise TypeError("definition must be a capability definition")
        with self._lock:
            if definition.capability_id in self._definitions:
                raise CapabilityRegistryError(
                    f"capability id already registered: {definition.capability_id}"
                )
            normalized_name = definition.normalized_name
            if normalized_name in self._names:
                raise CapabilityRegistryError(
                    f"capability name already registered: {definition.name}"
                )
            self._definitions[definition.capability_id] = definition
            self._names[normalized_name] = definition.capability_id
            return definition

    def remove(self, capability_id: str) -> CapabilityDefinition:
        if not isinstance(capability_id, str) or not capability_id.strip():
            raise ValueError("capability_id must be a non-empty string")
        with self._lock:
            definition = self._definitions.pop(capability_id, None)
            if definition is None:
                raise KeyError(capability_id)
            self._names.pop(definition.normalized_name, None)
            return definition

    def get(self, capability_id: str) -> CapabilityDefinition | None:
        if not isinstance(capability_id, str):
            return None
        with self._lock:
            return self._definitions.get(capability_id)

    def find_by_name(self, name: str) -> CapabilityDefinition | None:
        if not isinstance(name, str):
            return None
        with self._lock:
            capability_id = self._names.get(name.strip().lower())
            if capability_id is None:
                return None
            return self._definitions[capability_id]

    def snapshot(self) -> tuple[CapabilityDefinition, ...]:
        with self._lock:
            return tuple(self._definitions.values())

    def __len__(self) -> int:
        with self._lock:
            return len(self._definitions)


__all__ = ["CapabilityRegistryError", "CapabilityDefinition", "CapabilityRegistry"]
