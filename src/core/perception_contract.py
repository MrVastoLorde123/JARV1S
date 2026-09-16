"""M29 perception contract for provider-neutral environment sensing.

Perception is observation only. It records what JARVIS can observe about
filesystem, processes, network, services, logs, and hardware without granting
authority, executing tools, or treating observations as truth beyond their
provenance and freshness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class PerceptionDomain(str, Enum):
    FILESYSTEM = "FILESYSTEM"
    PROCESSES = "PROCESSES"
    NETWORK = "NETWORK"
    SERVICES = "SERVICES"
    LOGS = "LOGS"
    HARDWARE = "HARDWARE"


class PerceptionAvailability(str, Enum):
    READY = "READY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


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


def _utc(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class PerceptionObservation:
    """One immutable observation from one perception source."""

    observation_id: str
    source_id: str
    environment_id: str
    domain: PerceptionDomain
    availability: PerceptionAvailability
    observed_at: datetime
    payload: Mapping[str, Any] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("observation_id", "source_id", "environment_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.domain, PerceptionDomain):
            raise TypeError("domain must be a PerceptionDomain")
        if not isinstance(self.availability, PerceptionAvailability):
            raise TypeError("availability must be a PerceptionAvailability")
        object.__setattr__(self, "observed_at", _utc(self.observed_at, "observed_at"))
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping")
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "provenance", _freeze(self.provenance))


@dataclass(frozen=True)
class PerceptionSnapshot:
    """Bounded immutable collection of observations for one environment."""

    snapshot_id: str
    environment_id: str
    generated_at: datetime
    observations: tuple[PerceptionObservation, ...]
    authority_granted: bool = False
    execution_requested: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.snapshot_id, str) or not self.snapshot_id.strip():
            raise ValueError("snapshot_id must be a non-empty string")
        if not isinstance(self.environment_id, str) or not self.environment_id.strip():
            raise ValueError("environment_id must be a non-empty string")
        object.__setattr__(self, "generated_at", _utc(self.generated_at, "generated_at"))
        if not isinstance(self.observations, tuple):
            raise TypeError("observations must be a tuple")
        ids: set[str] = set()
        for observation in self.observations:
            if type(observation) is not PerceptionObservation:
                raise TypeError("observations must contain PerceptionObservation values")
            if observation.environment_id != self.environment_id:
                raise ValueError("all observations must belong to the snapshot environment")
            if observation.observation_id in ids:
                raise ValueError("observation_id values must be unique")
            ids.add(observation.observation_id)
        if not isinstance(self.authority_granted, bool):
            raise TypeError("authority_granted must be a bool")
        if not isinstance(self.execution_requested, bool):
            raise TypeError("execution_requested must be a bool")

    @property
    def domains(self) -> tuple[PerceptionDomain, ...]:
        return tuple(observation.domain for observation in self.observations)


__all__ = ["PerceptionAvailability", "PerceptionDomain", "PerceptionObservation", "PerceptionSnapshot"]
