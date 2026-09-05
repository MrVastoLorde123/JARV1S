"""M23.4: deterministic freshness and validity assessment for observations.

Freshness is a separate assessment of observation evidence. It never mutates
or replaces the underlying observation and it does not grant authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from src.core.environment_observation import EnvironmentObservation


class ObservationFreshness(str, Enum):
    """Deterministic temporal classification for one observation."""

    CURRENT = "CURRENT"
    STALE = "STALE"
    FUTURE = "FUTURE"
    INVALID = "INVALID"


def _require_aware_utc(value: datetime, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class EnvironmentObservationValidity:
    """Immutable assessment of one observation's temporal validity."""

    observation_id: str
    environment_id: str
    domain: str
    observed_at: datetime
    assessed_at: datetime
    max_age_seconds: float
    freshness: ObservationFreshness

    def __post_init__(self) -> None:
        if not isinstance(self.observation_id, str) or not self.observation_id.strip():
            raise ValueError("observation_id must be a non-empty string")
        if not isinstance(self.environment_id, str) or not self.environment_id.strip():
            raise ValueError("environment_id must be a non-empty string")
        if not isinstance(self.domain, str) or not self.domain.strip():
            raise ValueError("domain must be a non-empty string")
        object.__setattr__(self, "observed_at", _require_aware_utc(self.observed_at, "observed_at"))
        object.__setattr__(self, "assessed_at", _require_aware_utc(self.assessed_at, "assessed_at"))
        if not isinstance(self.max_age_seconds, (int, float)) or isinstance(self.max_age_seconds, bool):
            raise TypeError("max_age_seconds must be numeric")
        if self.max_age_seconds < 0:
            raise ValueError("max_age_seconds must be >= 0")
        if not isinstance(self.freshness, ObservationFreshness):
            raise TypeError("freshness must be an ObservationFreshness")

    @property
    def age_seconds(self) -> float:
        return (self.assessed_at - self.observed_at).total_seconds()

    @property
    def usable_as_current(self) -> bool:
        return self.freshness is ObservationFreshness.CURRENT


class EnvironmentObservationFreshnessService:
    """Assess observation freshness without mutating the source evidence."""

    def assess(
        self,
        observation: EnvironmentObservation,
        *,
        observed_at: datetime,
        assessed_at: datetime,
        max_age_seconds: float,
    ) -> EnvironmentObservationValidity:
        if type(observation) is not EnvironmentObservation:
            raise TypeError("observation must be EnvironmentObservation")
        normalized_observed_at = _require_aware_utc(observed_at, "observed_at")
        normalized_assessed_at = _require_aware_utc(assessed_at, "assessed_at")

        if not isinstance(max_age_seconds, (int, float)) or isinstance(max_age_seconds, bool):
            raise TypeError("max_age_seconds must be numeric")
        if max_age_seconds < 0:
            raise ValueError("max_age_seconds must be >= 0")

        age_seconds = (normalized_assessed_at - normalized_observed_at).total_seconds()
        if age_seconds < 0:
            freshness = ObservationFreshness.FUTURE
        elif age_seconds <= float(max_age_seconds):
            freshness = ObservationFreshness.CURRENT
        else:
            freshness = ObservationFreshness.STALE

        return EnvironmentObservationValidity(
            observation_id=observation.observation_id,
            environment_id=observation.environment_id,
            domain=observation.domain,
            observed_at=normalized_observed_at,
            assessed_at=normalized_assessed_at,
            max_age_seconds=float(max_age_seconds),
            freshness=freshness,
        )

    def assess_many(
        self,
        observations: tuple[tuple[EnvironmentObservation, datetime], ...] | list[tuple[EnvironmentObservation, datetime]],
        *,
        assessed_at: datetime,
        max_age_seconds: float,
    ) -> tuple[EnvironmentObservationValidity, ...]:
        normalized_assessed_at = _require_aware_utc(assessed_at, "assessed_at")
        results = []
        seen_ids: set[str] = set()
        for observation, observed_at in observations:
            if type(observation) is not EnvironmentObservation:
                raise TypeError("observations must contain EnvironmentObservation values")
            if observation.observation_id in seen_ids:
                raise ValueError(f"duplicate observation_id: {observation.observation_id}")
            seen_ids.add(observation.observation_id)
            results.append(
                self.assess(
                    observation,
                    observed_at=observed_at,
                    assessed_at=normalized_assessed_at,
                    max_age_seconds=max_age_seconds,
                )
            )
        return tuple(results)
