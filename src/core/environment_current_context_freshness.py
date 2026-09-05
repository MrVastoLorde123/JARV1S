"""M23.11: deterministic freshness assessment for current-context evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_context_composition import EnvironmentCurrentContextBundle
from src.core.environment_evidence_current_context import EnvironmentCurrentContext


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


class CurrentContextFreshness(str, Enum):
    """Deterministic temporal classification for current-context evidence."""

    CURRENT = "CURRENT"
    STALE = "STALE"
    FUTURE = "FUTURE"
    INVALID = "INVALID"


@dataclass(frozen=True)
class EnvironmentCurrentContextValidity:
    """Immutable temporal validity evidence for one context artifact."""

    context_id: str
    environment_id: str
    domain: str
    observed_at: datetime
    assessed_at: datetime
    max_age_seconds: float
    freshness: CurrentContextFreshness
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("context_id", "environment_id", "domain"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        object.__setattr__(self, "observed_at", _require_aware_utc(self.observed_at, "observed_at"))
        object.__setattr__(self, "assessed_at", _require_aware_utc(self.assessed_at, "assessed_at"))
        if not isinstance(self.max_age_seconds, (int, float)) or isinstance(self.max_age_seconds, bool):
            raise TypeError("max_age_seconds must be numeric")
        if self.max_age_seconds < 0:
            raise ValueError("max_age_seconds must be >= 0")
        if not isinstance(self.freshness, CurrentContextFreshness):
            raise TypeError("freshness must be a CurrentContextFreshness")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def age_seconds(self) -> float:
        return (self.assessed_at - self.observed_at).total_seconds()

    @property
    def usable_as_current(self) -> bool:
        return self.freshness is CurrentContextFreshness.CURRENT


@dataclass(frozen=True)
class EnvironmentCurrentContextBundleValidity:
    """Immutable temporal validity evidence for a composed context bundle."""

    bundle_id: str
    environment_id: str
    context_ids: tuple[str, ...]
    observed_at: tuple[datetime, ...]
    assessed_at: datetime
    max_age_seconds: float
    freshness: CurrentContextFreshness
    current_context_validities: tuple[EnvironmentCurrentContextValidity, ...]
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.bundle_id, str) or not self.bundle_id.strip():
            raise ValueError("bundle_id must be a non-empty string")
        if not isinstance(self.environment_id, str) or not self.environment_id.strip():
            raise ValueError("environment_id must be a non-empty string")
        if not isinstance(self.context_ids, tuple) or not self.context_ids:
            raise ValueError("context_ids must be a non-empty tuple")
        if len(set(self.context_ids)) != len(self.context_ids):
            raise ValueError("context_ids must be unique")
        if not isinstance(self.observed_at, tuple) or len(self.observed_at) != len(self.context_ids):
            raise ValueError("observed_at must align with context_ids")
        object.__setattr__(self, "observed_at", tuple(_require_aware_utc(item, "observed_at") for item in self.observed_at))
        object.__setattr__(self, "assessed_at", _require_aware_utc(self.assessed_at, "assessed_at"))
        if not isinstance(self.max_age_seconds, (int, float)) or isinstance(self.max_age_seconds, bool):
            raise TypeError("max_age_seconds must be numeric")
        if self.max_age_seconds < 0:
            raise ValueError("max_age_seconds must be >= 0")
        if not isinstance(self.freshness, CurrentContextFreshness):
            raise TypeError("freshness must be a CurrentContextFreshness")
        if not isinstance(self.current_context_validities, tuple):
            raise TypeError("current_context_validities must be a tuple")
        if tuple(item.context_id for item in self.current_context_validities) != self.context_ids:
            raise ValueError("current_context_validities must preserve context order")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def usable_as_current(self) -> bool:
        return self.freshness is CurrentContextFreshness.CURRENT and all(
            item.usable_as_current for item in self.current_context_validities
        )


class EnvironmentCurrentContextFreshnessError(RuntimeError):
    """Raised when current-context temporal evidence violates the contract."""


class EnvironmentCurrentContextFreshnessService:
    """Assess context freshness without mutating upstream context evidence."""

    @staticmethod
    def _validate_policy(max_age_seconds: float) -> float:
        if not isinstance(max_age_seconds, (int, float)) or isinstance(max_age_seconds, bool):
            raise TypeError("max_age_seconds must be numeric")
        if max_age_seconds < 0:
            raise ValueError("max_age_seconds must be >= 0")
        return float(max_age_seconds)

    def assess_context(
        self,
        context: EnvironmentCurrentContext,
        *,
        observed_at: datetime,
        assessed_at: datetime,
        max_age_seconds: float,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentCurrentContextValidity:
        if type(context) is not EnvironmentCurrentContext:
            raise TypeError("context must be EnvironmentCurrentContext")
        normalized_observed_at = _require_aware_utc(observed_at, "observed_at")
        normalized_assessed_at = _require_aware_utc(assessed_at, "assessed_at")
        age_policy = self._validate_policy(max_age_seconds)
        age_seconds = (normalized_assessed_at - normalized_observed_at).total_seconds()
        if age_seconds < 0:
            freshness = CurrentContextFreshness.FUTURE
        elif age_seconds <= age_policy:
            freshness = CurrentContextFreshness.CURRENT
        else:
            freshness = CurrentContextFreshness.STALE
        return EnvironmentCurrentContextValidity(
            context_id=context.context_id,
            environment_id=context.environment_id,
            domain=context.domain,
            observed_at=normalized_observed_at,
            assessed_at=normalized_assessed_at,
            max_age_seconds=age_policy,
            freshness=freshness,
            lineage=lineage or {"source_context_id": context.context_id},
        )

    def assess_bundle(
        self,
        bundle: EnvironmentCurrentContextBundle,
        observed_at: tuple[datetime, ...] | list[datetime],
        *,
        assessed_at: datetime,
        max_age_seconds: float,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentCurrentContextBundleValidity:
        if type(bundle) is not EnvironmentCurrentContextBundle:
            raise TypeError("bundle must be EnvironmentCurrentContextBundle")
        normalized_times = tuple(observed_at)
        if len(normalized_times) != len(bundle.contexts):
            raise EnvironmentCurrentContextFreshnessError("observed_at must align with bundle contexts")
        normalized_assessed_at = _require_aware_utc(assessed_at, "assessed_at")
        age_policy = self._validate_policy(max_age_seconds)
        validities = tuple(
            self.assess_context(
                context,
                observed_at=observed_time,
                assessed_at=normalized_assessed_at,
                max_age_seconds=age_policy,
                lineage={"bundle_id": bundle.bundle_id, "context_id": context.context_id},
            )
            for context, observed_time in zip(bundle.contexts, normalized_times)
        )
        states = tuple(item.freshness for item in validities)
        if any(item is CurrentContextFreshness.FUTURE for item in states):
            freshness = CurrentContextFreshness.FUTURE
        elif any(item is CurrentContextFreshness.STALE for item in states):
            freshness = CurrentContextFreshness.STALE
        elif all(item is CurrentContextFreshness.CURRENT for item in states):
            freshness = CurrentContextFreshness.CURRENT
        else:
            freshness = CurrentContextFreshness.INVALID
        return EnvironmentCurrentContextBundleValidity(
            bundle_id=bundle.bundle_id,
            environment_id=bundle.environment_id,
            context_ids=bundle.context_ids,
            observed_at=tuple(item.observed_at for item in validities),
            assessed_at=normalized_assessed_at,
            max_age_seconds=age_policy,
            freshness=freshness,
            current_context_validities=validities,
            lineage=lineage or {"bundle_id": bundle.bundle_id},
        )
