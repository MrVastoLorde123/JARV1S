"""M22.1 bounded capability/plugin contract and registry boundary.

This module describes and discovers plugin capabilities without invoking them.
Registration is metadata management, not trust, permission, authorization, or
execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


class PluginRegistryError(ValueError):
    """Raised when a plugin/capability registry contract is invalid."""


@dataclass(frozen=True)
class CapabilityDescriptor:
    """Immutable, metadata-only description of one plugin capability."""

    capability_id: str
    name: str
    version: str
    description: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in ("capability_id", "name", "version", "description"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise PluginRegistryError(f"{field_name} must be a non-empty string")
        if not isinstance(self.metadata, Mapping):
            raise PluginRegistryError("metadata must be a mapping")
        object.__setattr__(self, "metadata", dict(self.metadata))

    def to_context(self) -> dict[str, object]:
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


class CapabilityRegistry:
    """Conflict-aware metadata registry; never invokes registered plugins."""

    def __init__(self) -> None:
        self._descriptors: dict[str, CapabilityDescriptor] = {}

    @staticmethod
    def _key(capability_id: str) -> str:
        if not isinstance(capability_id, str) or not capability_id.strip():
            raise PluginRegistryError("capability_id must be a non-empty string")
        return capability_id.strip().lower()

    def register(self, descriptor: CapabilityDescriptor, *, replace: bool = False) -> CapabilityDescriptor:
        if not isinstance(descriptor, CapabilityDescriptor):
            raise TypeError("descriptor must be a CapabilityDescriptor")
        key = self._key(descriptor.capability_id)
        if key in self._descriptors and not replace:
            raise PluginRegistryError(
                f"capability '{descriptor.capability_id}' is already registered"
            )
        self._descriptors[key] = descriptor
        return descriptor

    def unregister(self, capability_id: str) -> None:
        key = self._key(capability_id)
        if key not in self._descriptors:
            raise PluginRegistryError(f"capability '{capability_id}' is not registered")
        del self._descriptors[key]

    def get(self, capability_id: str) -> CapabilityDescriptor | None:
        return self._descriptors.get(self._key(capability_id))

    def discover(self) -> tuple[CapabilityDescriptor, ...]:
        return tuple(
            self._descriptors[key] for key in sorted(self._descriptors)
        )

    def __len__(self) -> int:
        return len(self._descriptors)
