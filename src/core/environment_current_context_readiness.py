"""M23.12: deterministic readiness qualification for current-context evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_context_composition import EnvironmentCurrentContextBundle
from src.core.environment_current_context_freshness import (
    CurrentContextFreshness,
    EnvironmentCurrentContextBundleValidity,
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


class CurrentContextReadiness(str, Enum):
    """Deterministic readiness state for downstream world-model consumption."""

    READY = "READY"
    STALE = "STALE"
    FUTURE = "FUTURE"
    INVALID = "INVALID"


@dataclass(frozen=True)
class EnvironmentCurrentContextReadiness:
    """Immutable readiness evidence binding one bundle to its temporal validity."""

    readiness_id: str
    bundle_id: str
    environment_id: str
    context_ids: tuple[str, ...]
    freshness: CurrentContextFreshness
    current_context_freshness: tuple[CurrentContextFreshness, ...]
    readiness: CurrentContextReadiness
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("readiness_id", "bundle_id", "environment_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.context_ids, tuple) or not self.context_ids:
            raise ValueError("context_ids must be a non-empty tuple")
        if len(set(self.context_ids)) != len(self.context_ids):
            raise ValueError("context_ids must be unique")
        if not isinstance(self.freshness, CurrentContextFreshness):
            raise TypeError("freshness must be a CurrentContextFreshness")
        if not isinstance(self.current_context_freshness, tuple):
            raise TypeError("current_context_freshness must be a tuple")
        if len(self.current_context_freshness) != len(self.context_ids):
            raise ValueError("current_context_freshness must align with context_ids")
        if not all(isinstance(item, CurrentContextFreshness) for item in self.current_context_freshness):
            raise TypeError("current_context_freshness must contain CurrentContextFreshness values")
        if not isinstance(self.readiness, CurrentContextReadiness):
            raise TypeError("readiness must be a CurrentContextReadiness")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def usable_for_world_model(self) -> bool:
        return self.readiness is CurrentContextReadiness.READY


class EnvironmentCurrentContextReadinessError(RuntimeError):
    """Raised when context readiness inputs violate the contract."""


class EnvironmentCurrentContextReadinessService:
    """Bind a composed context bundle to its temporal validity without changing it."""

    def qualify(
        self,
        bundle: EnvironmentCurrentContextBundle,
        validity: EnvironmentCurrentContextBundleValidity,
        *,
        readiness_id: str,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentCurrentContextReadiness:
        if type(bundle) is not EnvironmentCurrentContextBundle:
            raise TypeError("bundle must be EnvironmentCurrentContextBundle")
        if type(validity) is not EnvironmentCurrentContextBundleValidity:
            raise TypeError("validity must be EnvironmentCurrentContextBundleValidity")
        if validity.bundle_id != bundle.bundle_id:
            raise EnvironmentCurrentContextReadinessError("validity bundle identity mismatch")
        if validity.environment_id != bundle.environment_id:
            raise EnvironmentCurrentContextReadinessError("validity environment identity mismatch")
        if validity.context_ids != bundle.context_ids:
            raise EnvironmentCurrentContextReadinessError("validity context identities mismatch")
        if len(validity.current_context_validities) != len(bundle.contexts):
            raise EnvironmentCurrentContextReadinessError("validity context count mismatch")

        state = validity.freshness
        if state is CurrentContextFreshness.CURRENT and validity.usable_as_current:
            readiness = CurrentContextReadiness.READY
        elif state is CurrentContextFreshness.FUTURE:
            readiness = CurrentContextReadiness.FUTURE
        elif state is CurrentContextFreshness.STALE:
            readiness = CurrentContextReadiness.STALE
        else:
            readiness = CurrentContextReadiness.INVALID

        return EnvironmentCurrentContextReadiness(
            readiness_id=readiness_id,
            bundle_id=bundle.bundle_id,
            environment_id=bundle.environment_id,
            context_ids=bundle.context_ids,
            freshness=validity.freshness,
            current_context_freshness=tuple(item.freshness for item in validity.current_context_validities),
            readiness=readiness,
            lineage=lineage or {"bundle_id": bundle.bundle_id},
        )
