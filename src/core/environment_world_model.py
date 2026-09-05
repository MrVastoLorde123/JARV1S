"""M23.13: descriptive environment world model derived from ready context."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_context_composition import EnvironmentCurrentContextBundle
from src.core.environment_current_context_freshness import CurrentContextFreshness
from src.core.environment_current_context_freshness import EnvironmentCurrentContextBundleValidity


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
class EnvironmentWorldModel:
    """Immutable descriptive model of current environment evidence."""

    model_id: str
    environment_id: str
    state_by_domain: Mapping[str, Mapping[str, Any]]
    represented_domains: tuple[str, ...]
    missing_domains: tuple[str, ...]
    context_ids: tuple[str, ...]
    qualification_ids: tuple[str, ...]
    provenance_ids: tuple[str, ...]
    readiness_id: str
    source_bundle_id: str
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("model_id", "environment_id", "readiness_id", "source_bundle_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.state_by_domain, Mapping):
            raise TypeError("state_by_domain must be a mapping")
        if not isinstance(self.represented_domains, tuple):
            raise TypeError("represented_domains must be a tuple")
        if not isinstance(self.missing_domains, tuple):
            raise TypeError("missing_domains must be a tuple")
        if set(self.represented_domains) & set(self.missing_domains):
            raise ValueError("represented and missing domains must be disjoint")
        if len(set(self.context_ids)) != len(self.context_ids):
            raise ValueError("context_ids must be unique")
        if len(self.context_ids) != len(self.qualification_ids) or len(self.context_ids) != len(self.provenance_ids):
            raise ValueError("source identity tuples must align")
        if tuple(self.state_by_domain.keys()) != self.represented_domains:
            raise ValueError("state_by_domain must preserve represented domain order")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "state_by_domain", _freeze(self.state_by_domain))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_descriptive_only(self) -> bool:
        return True


class EnvironmentWorldModelError(RuntimeError):
    """Raised when ready context cannot form a world model."""


class EnvironmentWorldModelService:
    """Construct a world model only from explicitly READY current context."""

    def build(
        self,
        bundle: EnvironmentCurrentContextBundle,
        validity: EnvironmentCurrentContextBundleValidity,
        *,
        readiness_id: str,
        model_id: str,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModel:
        if type(bundle) is not EnvironmentCurrentContextBundle:
            raise TypeError("bundle must be EnvironmentCurrentContextBundle")
        if type(validity) is not EnvironmentCurrentContextBundleValidity:
            raise TypeError("validity must be EnvironmentCurrentContextBundleValidity")
        if bundle.bundle_id != validity.bundle_id or bundle.environment_id != validity.environment_id:
            raise EnvironmentWorldModelError("bundle and validity identity mismatch")
        if bundle.context_ids != validity.context_ids:
            raise EnvironmentWorldModelError("bundle and validity context identities mismatch")
        if validity.freshness is not CurrentContextFreshness.CURRENT:
            raise EnvironmentWorldModelError("bundle must have CURRENT temporal validity")
        if any(item.freshness is not CurrentContextFreshness.CURRENT for item in validity.current_context_validities):
            raise EnvironmentWorldModelError("all contained contexts must be CURRENT")
        represented = bundle.represented_domains
        return EnvironmentWorldModel(
            model_id=model_id,
            environment_id=bundle.environment_id,
            state_by_domain={domain: bundle.data_by_domain[domain] for domain in represented},
            represented_domains=represented,
            missing_domains=bundle.missing_domains,
            context_ids=bundle.context_ids,
            qualification_ids=bundle.qualification_ids,
            provenance_ids=bundle.provenance_ids,
            readiness_id=readiness_id,
            source_bundle_id=bundle.bundle_id,
            lineage=lineage or {"bundle_id": bundle.bundle_id, "readiness_id": readiness_id},
        )
