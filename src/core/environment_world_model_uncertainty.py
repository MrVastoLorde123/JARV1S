"""M23.14: explicit uncertainty evidence for the descriptive environment world model.

This boundary represents uncertainty already supported by upstream evidence.
It never turns confidence into truth, authority, permission, or execution intent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_observation_evidence_qualification import EvidenceQualification
from src.core.environment_world_model import EnvironmentWorldModel


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
class EnvironmentWorldModelUncertainty:
    """Immutable uncertainty evidence attached to one world-model artifact."""

    uncertainty_id: str
    model_id: str
    environment_id: str
    represented_domains: tuple[str, ...]
    missing_domains: tuple[str, ...]
    evidence_status: EvidenceQualification
    confidence_by_domain: Mapping[str, float]
    uncertainty_by_domain: Mapping[str, float]
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("uncertainty_id", "model_id", "environment_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.represented_domains, tuple):
            raise TypeError("represented_domains must be a tuple")
        if not isinstance(self.missing_domains, tuple):
            raise TypeError("missing_domains must be a tuple")
        if set(self.represented_domains) & set(self.missing_domains):
            raise ValueError("represented and missing domains must be disjoint")
        if not isinstance(self.evidence_status, EvidenceQualification):
            raise TypeError("evidence_status must be an EvidenceQualification")
        self._validate_scores(self.confidence_by_domain, "confidence_by_domain")
        self._validate_scores(self.uncertainty_by_domain, "uncertainty_by_domain")
        expected = set(self.represented_domains)
        if set(self.confidence_by_domain) != expected:
            raise ValueError("confidence_by_domain must cover represented domains")
        if set(self.uncertainty_by_domain) != expected:
            raise ValueError("uncertainty_by_domain must cover represented domains")
        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "confidence_by_domain", _freeze(self.confidence_by_domain))
        object.__setattr__(self, "uncertainty_by_domain", _freeze(self.uncertainty_by_domain))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @staticmethod
    def _validate_scores(values: Mapping[str, float], field_name: str) -> None:
        if not isinstance(values, Mapping):
            raise TypeError(f"{field_name} must be a mapping")
        for domain, value in values.items():
            if not isinstance(domain, str) or not domain.strip():
                raise ValueError(f"{field_name} contains an invalid domain")
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{field_name} values must be numeric")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{field_name} values must be within [0, 1]")

    @property
    def is_descriptive_only(self) -> bool:
        return True

    @property
    def usable_for_reasoning(self) -> bool:
        return self.evidence_status is EvidenceQualification.USABLE


class EnvironmentWorldModelUncertaintyError(RuntimeError):
    """Raised when uncertainty evidence cannot be attached safely."""


class EnvironmentWorldModelUncertaintyService:
    """Derive bounded uncertainty evidence from an existing environment model."""

    def assess(
        self,
        model: EnvironmentWorldModel,
        *,
        uncertainty_id: str,
        confidence_by_domain: Mapping[str, float],
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelUncertainty:
        if type(model) is not EnvironmentWorldModel:
            raise TypeError("model must be EnvironmentWorldModel")
        if not isinstance(confidence_by_domain, Mapping):
            raise TypeError("confidence_by_domain must be a mapping")

        confidence: dict[str, float] = {}
        for domain, value in confidence_by_domain.items():
            if not isinstance(domain, str) or not domain.strip():
                raise ValueError("confidence_by_domain contains an invalid domain")
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError("confidence_by_domain values must be numeric")
            confidence[domain] = float(value)

        expected = set(model.represented_domains)
        if set(confidence) != expected:
            raise EnvironmentWorldModelUncertaintyError(
                "confidence must provide exactly one value for every represented domain"
            )
        uncertainty = {domain: 1.0 - value for domain, value in confidence.items()}
        return EnvironmentWorldModelUncertainty(
            uncertainty_id=uncertainty_id,
            model_id=model.model_id,
            environment_id=model.environment_id,
            represented_domains=model.represented_domains,
            missing_domains=model.missing_domains,
            evidence_status=EvidenceQualification.USABLE,
            confidence_by_domain=confidence,
            uncertainty_by_domain=uncertainty,
            reasons=reasons or {domain: "confidence is bounded evidence, not truth" for domain in expected},
            lineage=lineage or {"model_id": model.model_id},
        )
