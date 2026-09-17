"""M70: measurable, provider-neutral capability utility model.

Utility is an assessment signal for systems intelligence. It can inform
prioritization and composition analysis but never grants authority or
permission.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from types import MappingProxyType
from typing import Any, Mapping, Sequence


def _unit_interval(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    if not math.isfinite(result) or result < 0.0 or result > 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return result


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True)
class CapabilityUtilityWeights:
    """Weights for the normalized utility dimensions."""

    frequency: float = 1 / 6
    impact: float = 1 / 6
    reliability: float = 1 / 6
    scalability: float = 1 / 6
    cost: float = 1 / 6
    failure_rate: float = 1 / 6

    def __post_init__(self) -> None:
        fields = (
            "frequency",
            "impact",
            "reliability",
            "scalability",
            "cost",
            "failure_rate",
        )
        values = {field_name: _unit_interval(getattr(self, field_name), field_name) for field_name in fields}
        if not math.isclose(sum(values.values()), 1.0, rel_tol=0.0, abs_tol=1e-9):
            raise ValueError("utility weights must sum to 1")
        for field_name, value in values.items():
            object.__setattr__(self, field_name, value)


@dataclass(frozen=True)
class CapabilityUtilityProfile:
    """Immutable utility evidence for one capability."""

    capability_id: str
    frequency: float
    impact: float
    reliability: float
    scalability: float
    cost: float
    failure_rate: float
    evidence_count: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "capability_id", _text(self.capability_id, "capability_id"))
        for field_name in (
            "frequency",
            "impact",
            "reliability",
            "scalability",
            "cost",
            "failure_rate",
        ):
            object.__setattr__(self, field_name, _unit_interval(getattr(self, field_name), field_name))
        if not isinstance(self.evidence_count, int) or isinstance(self.evidence_count, bool) or self.evidence_count < 0:
            raise ValueError("evidence_count must be a non-negative integer")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def score(self, weights: CapabilityUtilityWeights | None = None) -> float:
        """Return normalized utility where higher means more useful under the weights."""
        weights = weights or CapabilityUtilityWeights()
        return (
            self.frequency * weights.frequency
            + self.impact * weights.impact
            + self.reliability * weights.reliability
            + self.scalability * weights.scalability
            + (1.0 - self.cost) * weights.cost
            + (1.0 - self.failure_rate) * weights.failure_rate
        )

    def to_context(self, weights: CapabilityUtilityWeights | None = None) -> dict[str, Any]:
        weights = weights or CapabilityUtilityWeights()
        return {
            "capability_id": self.capability_id,
            "frequency": self.frequency,
            "impact": self.impact,
            "reliability": self.reliability,
            "scalability": self.scalability,
            "cost": self.cost,
            "failure_rate": self.failure_rate,
            "evidence_count": self.evidence_count,
            "utility_score": self.score(weights),
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "execution_requested": False,
        }


class CapabilityUtilityModel:
    """Immutable collection of capability utility profiles."""

    def __init__(
        self,
        profiles: Sequence[CapabilityUtilityProfile] = (),
        *,
        weights: CapabilityUtilityWeights | None = None,
    ) -> None:
        values = tuple(profiles)
        if any(not isinstance(item, CapabilityUtilityProfile) for item in values):
            raise TypeError("profiles must contain only CapabilityUtilityProfile values")
        if len({item.capability_id for item in values}) != len(values):
            raise ValueError("utility profiles must have unique capability identifiers")
        self._profiles = MappingProxyType({item.capability_id: item for item in values})
        self._weights = weights or CapabilityUtilityWeights()

    @property
    def weights(self) -> CapabilityUtilityWeights:
        return self._weights

    def profile(self, capability_id: str) -> CapabilityUtilityProfile:
        normalized = _text(capability_id, "capability_id")
        try:
            return self._profiles[normalized]
        except KeyError as exc:
            raise KeyError(normalized) from exc

    def utility_score(self, capability_id: str) -> float:
        return self.profile(capability_id).score(self._weights)

    def snapshot(self) -> tuple[CapabilityUtilityProfile, ...]:
        return tuple(self._profiles.values())

    def average_score(self) -> float:
        values = tuple(self._profiles.values())
        return 0.0 if not values else sum(item.score(self._weights) for item in values) / len(values)

    def to_context(self) -> dict[str, Any]:
        return {
            "weights": self._weights.__dict__.copy(),
            "profiles": tuple(item.to_context(self._weights) for item in self._profiles.values()),
            "average_score": self.average_score(),
            "authority_granted": False,
            "execution_requested": False,
        }


__all__ = [
    "CapabilityUtilityModel",
    "CapabilityUtilityProfile",
    "CapabilityUtilityWeights",
]
