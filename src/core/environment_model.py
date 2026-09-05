"""M23.2: provider-neutral model of JARVIS's operating environment.

The environment model is descriptive state, not authority. It records the
hardware, software, network, models, capabilities, permissions, performance,
cost, and resource observations that can influence later routing or planning.
It never grants permission or implies that a capability is executable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


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
class EnvironmentSnapshot:
    """Immutable descriptive snapshot of the environment known to JARVIS."""

    environment_id: str
    hardware: Mapping[str, Any] = field(default_factory=dict)
    software: Mapping[str, Any] = field(default_factory=dict)
    network: Mapping[str, Any] = field(default_factory=dict)
    models: Mapping[str, Any] = field(default_factory=dict)
    capabilities: Mapping[str, Any] = field(default_factory=dict)
    permissions: Mapping[str, Any] = field(default_factory=dict)
    performance: Mapping[str, Any] = field(default_factory=dict)
    costs: Mapping[str, Any] = field(default_factory=dict)
    resources: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.environment_id, str) or not self.environment_id.strip():
            raise ValueError("environment_id must be a non-empty string")
        for field_name in (
            "hardware", "software", "network", "models", "capabilities",
            "permissions", "performance", "costs", "resources", "metadata",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Mapping):
                raise TypeError(f"{field_name} must be a mapping")
            object.__setattr__(self, field_name, _freeze(value))

    def to_context(self) -> dict[str, object]:
        return {
            "environment_id": self.environment_id,
            "hardware": dict(self.hardware),
            "software": dict(self.software),
            "network": dict(self.network),
            "models": dict(self.models),
            "capabilities": dict(self.capabilities),
            "permissions": dict(self.permissions),
            "performance": dict(self.performance),
            "costs": dict(self.costs),
            "resources": dict(self.resources),
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "adaptation_truth_proven": False,
        }


class EnvironmentSnapshotService:
    """Construct validated immutable environment snapshots from observations."""

    def snapshot(
        self,
        environment_id: str,
        *,
        hardware: Mapping[str, Any] | None = None,
        software: Mapping[str, Any] | None = None,
        network: Mapping[str, Any] | None = None,
        models: Mapping[str, Any] | None = None,
        capabilities: Mapping[str, Any] | None = None,
        permissions: Mapping[str, Any] | None = None,
        performance: Mapping[str, Any] | None = None,
        costs: Mapping[str, Any] | None = None,
        resources: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> EnvironmentSnapshot:
        return EnvironmentSnapshot(
            environment_id=environment_id,
            hardware=hardware or {},
            software=software or {},
            network=network or {},
            models=models or {},
            capabilities=capabilities or {},
            permissions=permissions or {},
            performance=performance or {},
            costs=costs or {},
            resources=resources or {},
            metadata=metadata or {},
        )
