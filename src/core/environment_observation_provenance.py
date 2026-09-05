"""M23.7: immutable provenance for environment observation evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_observation import EnvironmentObservation
from src.core.environment_observation_aggregation import EnvironmentObservationAggregate


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


def _require_aware_utc(value: datetime, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class EnvironmentObservationProvenance:
    """Immutable provenance describing where observation evidence came from."""

    provenance_id: str
    observation_ids: tuple[str, ...]
    adapter_ids: tuple[str, ...]
    environment_id: str
    domain: str
    observed_at: tuple[datetime, ...]
    recorded_at: datetime
    assessment_id: str | None = None
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("provenance_id", "environment_id", "domain"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.observation_ids, tuple) or not self.observation_ids:
            raise ValueError("observation_ids must be a non-empty tuple")
        if not isinstance(self.adapter_ids, tuple) or len(self.adapter_ids) != len(self.observation_ids):
            raise ValueError("adapter_ids must align with observation_ids")
        if len(set(self.observation_ids)) != len(self.observation_ids):
            raise ValueError("observation_ids must be unique")
        if len(set(self.adapter_ids)) != len(self.adapter_ids):
            raise ValueError("adapter_ids must be unique")
        if not isinstance(self.observed_at, tuple) or len(self.observed_at) != len(self.observation_ids):
            raise ValueError("observed_at must align with observation_ids")
        object.__setattr__(self, "observed_at", tuple(_require_aware_utc(item, "observed_at") for item in self.observed_at))
        object.__setattr__(self, "recorded_at", _require_aware_utc(self.recorded_at, "recorded_at"))
        if self.assessment_id is not None and (not isinstance(self.assessment_id, str) or not self.assessment_id.strip()):
            raise ValueError("assessment_id must be a non-empty string or None")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "lineage", _freeze(self.lineage))


class EnvironmentObservationProvenanceService:
    """Create provenance without changing evidence or assigning truth."""

    def from_observation(
        self,
        observation: EnvironmentObservation,
        *,
        observed_at: datetime,
        recorded_at: datetime,
        provenance_id: str,
        assessment_id: str | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentObservationProvenance:
        if type(observation) is not EnvironmentObservation:
            raise TypeError("observation must be EnvironmentObservation")
        return EnvironmentObservationProvenance(
            provenance_id=provenance_id,
            observation_ids=(observation.observation_id,),
            adapter_ids=(observation.adapter_id,),
            environment_id=observation.environment_id,
            domain=observation.domain,
            observed_at=(_require_aware_utc(observed_at, "observed_at"),),
            recorded_at=recorded_at,
            assessment_id=assessment_id,
            lineage=lineage or {},
        )

    def from_aggregate(
        self,
        aggregate: EnvironmentObservationAggregate,
        *,
        recorded_at: datetime,
        provenance_id: str,
        assessment_id: str | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentObservationProvenance:
        if type(aggregate) is not EnvironmentObservationAggregate:
            raise TypeError("aggregate must be EnvironmentObservationAggregate")
        return EnvironmentObservationProvenance(
            provenance_id=provenance_id,
            observation_ids=aggregate.observation_ids,
            adapter_ids=aggregate.adapter_ids,
            environment_id=aggregate.environment_id,
            domain=aggregate.domain,
            observed_at=tuple(item for item in aggregate.observed_at),
            recorded_at=recorded_at,
            assessment_id=assessment_id,
            lineage=lineage or {},
        )
