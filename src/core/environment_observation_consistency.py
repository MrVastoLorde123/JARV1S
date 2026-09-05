"""M23.5: deterministic consistency assessment for environment observations.

This boundary compares independent observations without selecting a winner,
establishing truth, or merging evidence. Conflicts remain explicit so a later
policy or reasoning layer can decide what to do with them.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.core.environment_observation import EnvironmentObservation


class ObservationConsistency(str, Enum):
    """Deterministic relationship between two observations."""

    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"


def _canonical(value: Any) -> Any:
    """Produce a deterministic, recursively comparable representation."""
    if isinstance(value, dict):
        return tuple(sorted((str(key), _canonical(item)) for key, item in value.items()))
    if isinstance(value, tuple):
        return tuple(_canonical(item) for item in value)
    if isinstance(value, list):
        return tuple(_canonical(item) for item in value)
    if isinstance(value, set):
        return frozenset(_canonical(item) for item in value)
    return value


@dataclass(frozen=True)
class EnvironmentObservationConsistency:
    """Immutable pairwise consistency evidence for two observations."""

    left_observation_id: str
    right_observation_id: str
    left_adapter_id: str
    right_adapter_id: str
    environment_id: str
    domain: str
    consistency: ObservationConsistency

    def __post_init__(self) -> None:
        for name in (
            "left_observation_id",
            "right_observation_id",
            "left_adapter_id",
            "right_adapter_id",
            "environment_id",
            "domain",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.left_observation_id == self.right_observation_id:
            raise ValueError("left and right observations must be distinct")
        if not isinstance(self.consistency, ObservationConsistency):
            raise TypeError("consistency must be an ObservationConsistency")

    @property
    def is_conflict(self) -> bool:
        return self.consistency is ObservationConsistency.CONFLICTING


class EnvironmentObservationConsistencyService:
    """Compare observations without merging or selecting authoritative truth."""

    def compare(
        self,
        left: EnvironmentObservation,
        right: EnvironmentObservation,
    ) -> EnvironmentObservationConsistency:
        self._validate_pair(left, right)
        relationship = (
            ObservationConsistency.CONSISTENT
            if _canonical(left.payload) == _canonical(right.payload)
            else ObservationConsistency.CONFLICTING
        )
        return EnvironmentObservationConsistency(
            left_observation_id=left.observation_id,
            right_observation_id=right.observation_id,
            left_adapter_id=left.adapter_id,
            right_adapter_id=right.adapter_id,
            environment_id=left.environment_id,
            domain=left.domain,
            consistency=relationship,
        )

    def compare_many(
        self,
        observations: tuple[EnvironmentObservation, ...] | list[EnvironmentObservation],
    ) -> tuple[EnvironmentObservationConsistency, ...]:
        normalized = tuple(observations)
        for observation in normalized:
            if type(observation) is not EnvironmentObservation:
                raise TypeError("observations must contain EnvironmentObservation values")

        results: list[EnvironmentObservationConsistency] = []
        for index, left in enumerate(normalized):
            for right in normalized[index + 1 :]:
                if left.domain != right.domain or left.environment_id != right.environment_id:
                    continue
                results.append(self.compare(left, right))
        return tuple(results)

    @staticmethod
    def _validate_pair(
        left: EnvironmentObservation,
        right: EnvironmentObservation,
    ) -> None:
        if type(left) is not EnvironmentObservation or type(right) is not EnvironmentObservation:
            raise TypeError("left and right must be EnvironmentObservation")
        if left.environment_id != right.environment_id:
            raise ValueError("observations must belong to the same environment")
        if left.domain != right.domain:
            raise ValueError("observations must belong to the same domain")
        if left.observation_id == right.observation_id:
            raise ValueError("observations must have distinct observation IDs")
