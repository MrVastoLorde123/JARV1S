"""M23.6: deterministic aggregation of fresh, consistent environment observations."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_observation import EnvironmentObservation
from src.core.environment_observation_consistency import (
    EnvironmentObservationConsistencyService,
    ObservationConsistency,
)
from src.core.environment_observation_freshness import (
    EnvironmentObservationValidity,
    ObservationFreshness,
)


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
class EnvironmentObservationAggregate:
    """Immutable derived evidence from mutually consistent current observations."""

    environment_id: str
    domain: str
    payload: Mapping[str, Any]
    observation_ids: tuple[str, ...]
    adapter_ids: tuple[str, ...]
    observed_at: tuple[object, ...]

    def __post_init__(self) -> None:
        for name in ("environment_id", "domain"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")
        if not isinstance(self.observation_ids, tuple) or len(self.observation_ids) < 2:
            raise ValueError("observation_ids must contain at least two IDs")
        if not isinstance(self.adapter_ids, tuple) or len(self.adapter_ids) != len(self.observation_ids):
            raise ValueError("adapter_ids must align with observation_ids")
        if not isinstance(self.observed_at, tuple) or len(self.observed_at) != len(self.observation_ids):
            raise ValueError("observed_at must align with observation_ids")
        if len(set(self.observation_ids)) != len(self.observation_ids):
            raise ValueError("observation_ids must be unique")
        if len(set(self.adapter_ids)) != len(self.adapter_ids):
            raise ValueError("adapter_ids must be unique")
        object.__setattr__(self, "payload", _freeze(self.payload))


class EnvironmentObservationAggregationError(RuntimeError):
    """Raised when observations cannot be safely aggregated."""


class EnvironmentObservationAggregationService:
    """Aggregate observations only when freshness and consistency gates pass."""

    def __init__(
        self,
        consistency_service: EnvironmentObservationConsistencyService | None = None,
    ) -> None:
        self._consistency_service = consistency_service or EnvironmentObservationConsistencyService()

    def aggregate(
        self,
        observations: tuple[EnvironmentObservation, ...] | list[EnvironmentObservation],
        validities: tuple[EnvironmentObservationValidity, ...] | list[EnvironmentObservationValidity],
    ) -> EnvironmentObservationAggregate:
        normalized_observations = tuple(observations)
        normalized_validities = tuple(validities)
        if len(normalized_observations) < 2:
            raise EnvironmentObservationAggregationError("at least two observations are required")
        if len(normalized_observations) != len(normalized_validities):
            raise EnvironmentObservationAggregationError("observations and validities must have equal length")

        for observation in normalized_observations:
            if type(observation) is not EnvironmentObservation:
                raise TypeError("observations must contain EnvironmentObservation values")
        for validity in normalized_validities:
            if type(validity) is not EnvironmentObservationValidity:
                raise TypeError("validities must contain EnvironmentObservationValidity values")
            if validity.freshness is not ObservationFreshness.CURRENT:
                raise EnvironmentObservationAggregationError("all observations must be CURRENT")

        observation_ids = tuple(item.observation_id for item in normalized_observations)
        if len(set(observation_ids)) != len(observation_ids):
            raise EnvironmentObservationAggregationError("duplicate observation_id")

        first = normalized_observations[0]
        if any(
            item.environment_id != first.environment_id or item.domain != first.domain
            for item in normalized_observations
        ):
            raise EnvironmentObservationAggregationError(
                "all observations must belong to the same environment and domain"
            )

        validity_by_id = {item.observation_id: item for item in normalized_validities}
        if set(validity_by_id) != set(observation_ids):
            raise EnvironmentObservationAggregationError("validities must match observations by identity")
        if any(
            validity.environment_id != first.environment_id or validity.domain != first.domain
            for validity in normalized_validities
        ):
            raise EnvironmentObservationAggregationError("validity scope must match observation scope")

        consistency_results = self._consistency_service.compare_many(normalized_observations)
        expected_pairs = len(normalized_observations) * (len(normalized_observations) - 1) // 2
        if len(consistency_results) != expected_pairs:
            raise EnvironmentObservationAggregationError("consistency evidence is incomplete")
        if any(item.consistency is not ObservationConsistency.CONSISTENT for item in consistency_results):
            raise EnvironmentObservationAggregationError("conflicting observations cannot be aggregated")

        return EnvironmentObservationAggregate(
            environment_id=first.environment_id,
            domain=first.domain,
            payload=first.payload,
            observation_ids=observation_ids,
            adapter_ids=tuple(item.adapter_id for item in normalized_observations),
            observed_at=tuple(validity_by_id[item.observation_id].observed_at for item in normalized_observations),
        )
