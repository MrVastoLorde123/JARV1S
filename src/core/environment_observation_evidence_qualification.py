"""M23.8: deterministic qualification of environment observation evidence.

Qualification combines existing evidence artifacts without converting them into
truth, authority, permission, or executability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_observation import EnvironmentObservation
from src.core.environment_observation_aggregation import EnvironmentObservationAggregate
from src.core.environment_observation_consistency import (
    EnvironmentObservationConsistency,
    ObservationConsistency,
)
from src.core.environment_observation_freshness import (
    EnvironmentObservationValidity,
    ObservationFreshness,
)
from src.core.environment_observation_provenance import EnvironmentObservationProvenance


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


class EvidenceQualification(str, Enum):
    """Deterministic qualification state for an evidence bundle."""

    USABLE = "USABLE"
    UNUSABLE = "UNUSABLE"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"


@dataclass(frozen=True)
class EnvironmentObservationEvidenceQualification:
    """Immutable record of evidence-gating for one observation or aggregate."""

    qualification_id: str
    subject_kind: str
    environment_id: str
    domain: str
    observation_ids: tuple[str, ...]
    adapter_ids: tuple[str, ...]
    validity: tuple[ObservationFreshness, ...]
    consistency: tuple[ObservationConsistency, ...]
    provenance_id: str
    qualified_at: datetime
    qualification: EvidenceQualification
    reasons: tuple[str, ...] = ()
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "qualification_id",
            "subject_kind",
            "environment_id",
            "domain",
            "provenance_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.subject_kind not in {"observation", "aggregate"}:
            raise ValueError("subject_kind must be 'observation' or 'aggregate'")
        if not isinstance(self.observation_ids, tuple) or not self.observation_ids:
            raise ValueError("observation_ids must be a non-empty tuple")
        if len(self.adapter_ids) != len(self.observation_ids):
            raise ValueError("adapter_ids must align with observation_ids")
        if len(set(self.observation_ids)) != len(self.observation_ids):
            raise ValueError("observation_ids must be unique")
        if len(set(self.adapter_ids)) != len(self.adapter_ids):
            raise ValueError("adapter_ids must be unique")
        if not isinstance(self.validity, tuple):
            raise TypeError("validity must be a tuple")
        if not all(isinstance(item, ObservationFreshness) for item in self.validity):
            raise TypeError("validity must contain ObservationFreshness values")
        if not isinstance(self.consistency, tuple):
            raise TypeError("consistency must be a tuple")
        if not all(isinstance(item, ObservationConsistency) for item in self.consistency):
            raise TypeError("consistency must contain ObservationConsistency values")
        if not isinstance(self.qualification, EvidenceQualification):
            raise TypeError("qualification must be an EvidenceQualification")
        if not isinstance(self.reasons, tuple) or not all(isinstance(item, str) and item.strip() for item in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        object.__setattr__(self, "qualified_at", _require_aware_utc(self.qualified_at, "qualified_at"))
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def usable_for_downstream_reasoning(self) -> bool:
        return self.qualification is EvidenceQualification.USABLE


class EnvironmentObservationEvidenceQualificationError(RuntimeError):
    """Raised when supplied evidence violates the qualification contract."""


class EnvironmentObservationEvidenceQualificationService:
    """Qualify evidence bundles using only deterministic upstream evidence gates."""

    def qualify_observation(
        self,
        observation: EnvironmentObservation,
        validity: EnvironmentObservationValidity,
        provenance: EnvironmentObservationProvenance,
        *,
        qualification_id: str,
        qualified_at: datetime,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentObservationEvidenceQualification:
        self._validate_observation_bundle(observation, validity, provenance)
        qualification = (
            EvidenceQualification.USABLE
            if validity.freshness is ObservationFreshness.CURRENT
            else EvidenceQualification.UNUSABLE
        )
        reasons = (
            ("observation is CURRENT and provenance identities align",)
            if qualification is EvidenceQualification.USABLE
            else (f"observation freshness is {validity.freshness.value}",)
        )
        return EnvironmentObservationEvidenceQualification(
            qualification_id=qualification_id,
            subject_kind="observation",
            environment_id=observation.environment_id,
            domain=observation.domain,
            observation_ids=(observation.observation_id,),
            adapter_ids=(observation.adapter_id,),
            validity=(validity.freshness,),
            consistency=(),
            provenance_id=provenance.provenance_id,
            qualified_at=qualified_at,
            qualification=qualification,
            reasons=reasons,
            lineage=lineage or {},
        )

    def qualify_aggregate(
        self,
        aggregate: EnvironmentObservationAggregate,
        validities: tuple[EnvironmentObservationValidity, ...] | list[EnvironmentObservationValidity],
        consistency: tuple[EnvironmentObservationConsistency, ...] | list[EnvironmentObservationConsistency],
        provenance: EnvironmentObservationProvenance,
        *,
        qualification_id: str,
        qualified_at: datetime,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentObservationEvidenceQualification:
        self._validate_aggregate_bundle(aggregate, tuple(validities), tuple(consistency), provenance)

        expected_pairs = len(aggregate.observation_ids) * (len(aggregate.observation_ids) - 1) // 2
        consistency_states = tuple(item.consistency for item in consistency)
        if len(consistency) < expected_pairs:
            qualification = EvidenceQualification.INSUFFICIENT
            reasons = ("consistency evidence is incomplete",)
        elif any(item.consistency is ObservationConsistency.CONFLICTING for item in consistency):
            qualification = EvidenceQualification.CONFLICTING
            reasons = ("one or more supplied observation comparisons are CONFLICTING",)
        elif any(item.freshness is not ObservationFreshness.CURRENT for item in validities):
            qualification = EvidenceQualification.UNUSABLE
            reasons = ("one or more supplied observation validities are not CURRENT",)
        else:
            qualification = EvidenceQualification.USABLE
            reasons = ("all required temporal, consistency, aggregation, and provenance gates pass",)

        return EnvironmentObservationEvidenceQualification(
            qualification_id=qualification_id,
            subject_kind="aggregate",
            environment_id=aggregate.environment_id,
            domain=aggregate.domain,
            observation_ids=aggregate.observation_ids,
            adapter_ids=aggregate.adapter_ids,
            validity=tuple(item.freshness for item in validities),
            consistency=consistency_states,
            provenance_id=provenance.provenance_id,
            qualified_at=qualified_at,
            qualification=qualification,
            reasons=reasons,
            lineage=lineage or {},
        )

    @staticmethod
    def _validate_observation_bundle(
        observation: EnvironmentObservation,
        validity: EnvironmentObservationValidity,
        provenance: EnvironmentObservationProvenance,
    ) -> None:
        if type(observation) is not EnvironmentObservation:
            raise TypeError("observation must be EnvironmentObservation")
        if type(validity) is not EnvironmentObservationValidity:
            raise TypeError("validity must be EnvironmentObservationValidity")
        if type(provenance) is not EnvironmentObservationProvenance:
            raise TypeError("provenance must be EnvironmentObservationProvenance")
        if validity.observation_id != observation.observation_id:
            raise EnvironmentObservationEvidenceQualificationError("validity observation identity mismatch")
        if validity.environment_id != observation.environment_id or validity.domain != observation.domain:
            raise EnvironmentObservationEvidenceQualificationError("validity scope mismatch")
        if provenance.observation_ids != (observation.observation_id,):
            raise EnvironmentObservationEvidenceQualificationError("provenance observation identity mismatch")
        if provenance.adapter_ids != (observation.adapter_id,):
            raise EnvironmentObservationEvidenceQualificationError("provenance adapter identity mismatch")
        if provenance.environment_id != observation.environment_id or provenance.domain != observation.domain:
            raise EnvironmentObservationEvidenceQualificationError("provenance scope mismatch")
        if provenance.observed_at != (validity.observed_at,):
            raise EnvironmentObservationEvidenceQualificationError("provenance observed_at mismatch")

    @staticmethod
    def _validate_aggregate_bundle(
        aggregate: EnvironmentObservationAggregate,
        validities: tuple[EnvironmentObservationValidity, ...],
        consistency: tuple[EnvironmentObservationConsistency, ...],
        provenance: EnvironmentObservationProvenance,
    ) -> None:
        if type(aggregate) is not EnvironmentObservationAggregate:
            raise TypeError("aggregate must be EnvironmentObservationAggregate")
        if any(type(item) is not EnvironmentObservationValidity for item in validities):
            raise TypeError("validities must contain EnvironmentObservationValidity values")
        if any(type(item) is not EnvironmentObservationConsistency for item in consistency):
            raise TypeError("consistency must contain EnvironmentObservationConsistency values")
        if type(provenance) is not EnvironmentObservationProvenance:
            raise TypeError("provenance must be EnvironmentObservationProvenance")
        if len(validities) != len(aggregate.observation_ids):
            raise EnvironmentObservationEvidenceQualificationError("validities must align with aggregate observations")
        validity_ids = tuple(item.observation_id for item in validities)
        if validity_ids != aggregate.observation_ids:
            raise EnvironmentObservationEvidenceQualificationError("validity identities must align with aggregate")
        if any(item.environment_id != aggregate.environment_id or item.domain != aggregate.domain for item in validities):
            raise EnvironmentObservationEvidenceQualificationError("validity scope mismatch")
        if provenance.observation_ids != aggregate.observation_ids:
            raise EnvironmentObservationEvidenceQualificationError("provenance observation identities mismatch")
        if provenance.adapter_ids != aggregate.adapter_ids:
            raise EnvironmentObservationEvidenceQualificationError("provenance adapter identities mismatch")
        if provenance.environment_id != aggregate.environment_id or provenance.domain != aggregate.domain:
            raise EnvironmentObservationEvidenceQualificationError("provenance scope mismatch")
        if provenance.observed_at != aggregate.observed_at:
            raise EnvironmentObservationEvidenceQualificationError("provenance observed_at mismatch")

        expected_pairs = len(aggregate.observation_ids) * (len(aggregate.observation_ids) - 1) // 2
        pair_keys = {
            (item.left_observation_id, item.right_observation_id)
            for item in consistency
        }
        expected_keys = {
            (aggregate.observation_ids[index], aggregate.observation_ids[right_index])
            for index in range(len(aggregate.observation_ids))
            for right_index in range(index + 1, len(aggregate.observation_ids))
        }
        if len(consistency) > expected_pairs or pair_keys != expected_keys:
            raise EnvironmentObservationEvidenceQualificationError("consistency evidence does not match aggregate source pairs")
        for item in consistency:
            if item.environment_id != aggregate.environment_id or item.domain != aggregate.domain:
                raise EnvironmentObservationEvidenceQualificationError("consistency scope mismatch")
