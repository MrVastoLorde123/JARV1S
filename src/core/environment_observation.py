"""M23.3: provider-neutral observation adapters for environment state.

Observation adapters collect descriptive environment facts. They do not grant
authority, infer executability, authorize actions, or mutate environment state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, runtime_checkable

from src.core.environment_model import EnvironmentSnapshot, EnvironmentSnapshotService


ENVIRONMENT_DOMAINS = (
    "hardware",
    "software",
    "network",
    "models",
    "capabilities",
    "permissions",
    "performance",
    "costs",
    "resources",
    "metadata",
)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _freeze(item) for key, item in value.items()}
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class EnvironmentObservation:
    """Immutable descriptive observation produced by one environment adapter."""

    observation_id: str
    adapter_id: str
    environment_id: str
    domain: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("observation_id", "adapter_id", "environment_id", "domain"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.domain not in ENVIRONMENT_DOMAINS:
            raise ValueError(f"unsupported environment observation domain: {self.domain}")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "metadata", _freeze(self.metadata))


@runtime_checkable
class EnvironmentObservationAdapter(Protocol):
    """Replaceable provider-neutral adapter for one environment domain."""

    adapter_id: str
    domain: str

    def observe(self, environment_id: str) -> EnvironmentObservation:
        """Return exactly one descriptive observation for the requested environment."""
        ...


class EnvironmentObservationError(RuntimeError):
    """Raised when an observation adapter violates its contract or fails."""


class EnvironmentObservationService:
    """Compose independent observations into one immutable environment snapshot."""

    def __init__(self, snapshot_service: EnvironmentSnapshotService | None = None) -> None:
        self._snapshot_service = snapshot_service or EnvironmentSnapshotService()

    def snapshot(
        self,
        environment_id: str,
        adapters: tuple[EnvironmentObservationAdapter, ...] | list[EnvironmentObservationAdapter] = (),
    ) -> EnvironmentSnapshot:
        if not isinstance(environment_id, str) or not environment_id.strip():
            raise ValueError("environment_id must be a non-empty string")

        observations: dict[str, EnvironmentObservation] = {}
        adapter_ids: set[str] = set()

        for adapter in adapters:
            adapter_id = getattr(adapter, "adapter_id", None)
            domain = getattr(adapter, "domain", None)
            if not isinstance(adapter_id, str) or not adapter_id.strip():
                raise EnvironmentObservationError("adapter_id must be a non-empty string")
            if adapter_id in adapter_ids:
                raise EnvironmentObservationError(f"duplicate adapter_id: {adapter_id}")
            adapter_ids.add(adapter_id)

            if domain not in ENVIRONMENT_DOMAINS:
                raise EnvironmentObservationError(f"unsupported adapter domain: {domain}")
            if domain in observations:
                raise EnvironmentObservationError(f"duplicate observation domain: {domain}")

            try:
                observation = adapter.observe(environment_id)
            except Exception as exc:
                raise EnvironmentObservationError(
                    f"environment observation failed for adapter {adapter_id}"
                ) from exc

            if type(observation) is not EnvironmentObservation:
                raise EnvironmentObservationError(
                    f"adapter {adapter_id} must return EnvironmentObservation"
                )
            if observation.adapter_id != adapter_id:
                raise EnvironmentObservationError(
                    f"adapter {adapter_id} returned observation for adapter {observation.adapter_id}"
                )
            if observation.domain != domain:
                raise EnvironmentObservationError(
                    f"adapter {adapter_id} returned domain {observation.domain} instead of {domain}"
                )
            if observation.environment_id != environment_id:
                raise EnvironmentObservationError(
                    f"adapter {adapter_id} returned environment {observation.environment_id}"
                )

            observations[domain] = observation

        domains: dict[str, Mapping[str, Any]] = {domain: {} for domain in ENVIRONMENT_DOMAINS}
        for domain, observation in observations.items():
            domains[domain] = observation.payload

        provenance = {
            domain: {
                "adapter_id": observation.adapter_id,
                "observation_id": observation.observation_id,
            }
            for domain, observation in observations.items()
        }
        metadata = {"observation_sources": provenance}

        return self._snapshot_service.snapshot(
            environment_id,
            hardware=domains["hardware"],
            software=domains["software"],
            network=domains["network"],
            models=domains["models"],
            capabilities=domains["capabilities"],
            permissions=domains["permissions"],
            performance=domains["performance"],
            costs=domains["costs"],
            resources=domains["resources"],
            metadata=metadata,
        )
