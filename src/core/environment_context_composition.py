"""M23.10: deterministic composition of environment current-context evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_observation import ENVIRONMENT_DOMAINS
from src.core.environment_observation_evidence_qualification import EvidenceQualification
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


@dataclass(frozen=True)
class EnvironmentCurrentContextBundle:
    """Immutable bundle of independent per-domain current-context evidence."""

    bundle_id: str
    environment_id: str
    contexts: tuple[EnvironmentCurrentContext, ...]
    represented_domains: tuple[str, ...]
    missing_domains: tuple[str, ...]
    data_by_domain: Mapping[str, Mapping[str, Any]]
    context_ids: tuple[str, ...]
    qualification_ids: tuple[str, ...]
    provenance_ids: tuple[str, ...]
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.bundle_id, str) or not self.bundle_id.strip():
            raise ValueError("bundle_id must be a non-empty string")
        if not isinstance(self.environment_id, str) or not self.environment_id.strip():
            raise ValueError("environment_id must be a non-empty string")
        if not isinstance(self.contexts, tuple) or not self.contexts:
            raise ValueError("contexts must be a non-empty tuple")
        if not all(type(item) is EnvironmentCurrentContext for item in self.contexts):
            raise TypeError("contexts must contain EnvironmentCurrentContext values")
        if any(item.environment_id != self.environment_id for item in self.contexts):
            raise ValueError("all contexts must belong to the same environment")
        if any(item.evidence_status is not EvidenceQualification.USABLE for item in self.contexts):
            raise ValueError("all contexts must be USABLE")
        if len(set(item.context_id for item in self.contexts)) != len(self.contexts):
            raise ValueError("context IDs must be unique")
        if len(set(item.domain for item in self.contexts)) != len(self.contexts):
            raise ValueError("context domains must be unique")
        if self.represented_domains != tuple(item.domain for item in self.contexts):
            raise ValueError("represented_domains must preserve context domain order")
        if any(domain not in ENVIRONMENT_DOMAINS for domain in self.represented_domains):
            raise ValueError("represented_domains contains unsupported domain")
        if set(self.represented_domains) & set(self.missing_domains):
            raise ValueError("represented and missing domains must be disjoint")
        if set(self.represented_domains) | set(self.missing_domains) != set(ENVIRONMENT_DOMAINS):
            raise ValueError("represented and missing domains must partition known environment domains")
        if self.context_ids != tuple(item.context_id for item in self.contexts):
            raise ValueError("context_ids must preserve context order")
        if self.qualification_ids != tuple(item.qualification_id for item in self.contexts):
            raise ValueError("qualification_ids must preserve context order")
        if self.provenance_ids != tuple(item.provenance_id for item in self.contexts):
            raise ValueError("provenance_ids must preserve context order")
        if not isinstance(self.data_by_domain, Mapping):
            raise TypeError("data_by_domain must be a mapping")
        if tuple(self.data_by_domain.keys()) != self.represented_domains:
            raise ValueError("data_by_domain must preserve represented domain order")
        object.__setattr__(self, "data_by_domain", _freeze(self.data_by_domain))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def usable_for_reasoning(self) -> bool:
        return bool(self.contexts) and all(item.usable_for_reasoning for item in self.contexts)


class EnvironmentContextCompositionError(RuntimeError):
    """Raised when current-context evidence cannot be safely composed."""


class EnvironmentContextCompositionService:
    """Compose independent current-context evidence without merging authority."""

    def compose(
        self,
        contexts: tuple[EnvironmentCurrentContext, ...] | list[EnvironmentCurrentContext],
        *,
        bundle_id: str,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentCurrentContextBundle:
        normalized = tuple(contexts)
        if not normalized:
            raise EnvironmentContextCompositionError("at least one current context is required")
        for context in normalized:
            if type(context) is not EnvironmentCurrentContext:
                raise TypeError("contexts must contain EnvironmentCurrentContext values")
            if context.evidence_status is not EvidenceQualification.USABLE:
                raise EnvironmentContextCompositionError("only USABLE current contexts may be composed")

        environment_id = normalized[0].environment_id
        if any(context.environment_id != environment_id for context in normalized):
            raise EnvironmentContextCompositionError("contexts must belong to the same environment")
        if len({context.context_id for context in normalized}) != len(normalized):
            raise EnvironmentContextCompositionError("duplicate context_id")
        if len({context.domain for context in normalized}) != len(normalized):
            raise EnvironmentContextCompositionError("duplicate context domain")

        represented_domains = tuple(context.domain for context in normalized)
        missing_domains = tuple(domain for domain in ENVIRONMENT_DOMAINS if domain not in represented_domains)
        data_by_domain = {
            context.domain: context.data
            for context in normalized
        }

        return EnvironmentCurrentContextBundle(
            bundle_id=bundle_id,
            environment_id=environment_id,
            contexts=normalized,
            represented_domains=represented_domains,
            missing_domains=missing_domains,
            data_by_domain=data_by_domain,
            context_ids=tuple(context.context_id for context in normalized),
            qualification_ids=tuple(context.qualification_id for context in normalized),
            provenance_ids=tuple(context.provenance_id for context in normalized),
            lineage=lineage or {"context_ids": tuple(context.context_id for context in normalized)},
        )
