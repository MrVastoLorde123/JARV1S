"""M23.9: evidence-preserving current context built from qualified environment evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_observation import EnvironmentObservation
from src.core.environment_observation_aggregation import EnvironmentObservationAggregate
from src.core.environment_observation_evidence_qualification import (
    EnvironmentObservationEvidenceQualification,
    EvidenceQualification,
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
class EnvironmentCurrentContext:
    """Immutable descriptive current-context evidence derived from qualification."""

    context_id: str
    environment_id: str
    domain: str
    subject_kind: str
    data: Mapping[str, Any]
    evidence_status: EvidenceQualification
    observation_ids: tuple[str, ...]
    adapter_ids: tuple[str, ...]
    provenance_id: str
    qualification_id: str
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("context_id", "environment_id", "domain", "provenance_id", "qualification_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.subject_kind not in {"observation", "aggregate"}:
            raise ValueError("subject_kind must be 'observation' or 'aggregate'")
        if not isinstance(self.data, Mapping):
            raise TypeError("data must be a mapping")
        if not isinstance(self.observation_ids, tuple) or not self.observation_ids:
            raise ValueError("observation_ids must be a non-empty tuple")
        if not isinstance(self.adapter_ids, tuple) or len(self.adapter_ids) != len(self.observation_ids):
            raise ValueError("adapter_ids must align with observation_ids")
        if len(set(self.observation_ids)) != len(self.observation_ids):
            raise ValueError("observation_ids must be unique")
        if len(set(self.adapter_ids)) != len(self.adapter_ids):
            raise ValueError("adapter_ids must be unique")
        if not isinstance(self.evidence_status, EvidenceQualification):
            raise TypeError("evidence_status must be an EvidenceQualification")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "data", _freeze(self.data))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def usable_for_reasoning(self) -> bool:
        return self.evidence_status is EvidenceQualification.USABLE


class EnvironmentEvidenceCurrentContextError(RuntimeError):
    """Raised when qualified evidence cannot form a valid current context."""


class EnvironmentEvidenceCurrentContextService:
    """Translate qualified evidence into descriptive context without inventing state."""

    def from_observation(
        self,
        observation: EnvironmentObservation,
        qualification: EnvironmentObservationEvidenceQualification,
        *,
        context_id: str,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentCurrentContext:
        if type(observation) is not EnvironmentObservation:
            raise TypeError("observation must be EnvironmentObservation")
        self._validate_qualification(qualification)
        self._validate_observation_alignment(observation, qualification)
        if qualification.qualification is not EvidenceQualification.USABLE:
            raise EnvironmentEvidenceCurrentContextError("only USABLE qualification may form current context")
        return EnvironmentCurrentContext(
            context_id=context_id,
            environment_id=observation.environment_id,
            domain=observation.domain,
            subject_kind="observation",
            data={"observed": dict(observation.payload), "status": "qualified"},
            evidence_status=qualification.qualification,
            observation_ids=qualification.observation_ids,
            adapter_ids=qualification.adapter_ids,
            provenance_id=qualification.provenance_id,
            qualification_id=qualification.qualification_id,
            lineage=lineage or {"qualification_id": qualification.qualification_id},
        )

    def from_aggregate(
        self,
        aggregate: EnvironmentObservationAggregate,
        qualification: EnvironmentObservationEvidenceQualification,
        *,
        context_id: str,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentCurrentContext:
        if type(aggregate) is not EnvironmentObservationAggregate:
            raise TypeError("aggregate must be EnvironmentObservationAggregate")
        self._validate_qualification(qualification)
        self._validate_aggregate_alignment(aggregate, qualification)
        if qualification.qualification is not EvidenceQualification.USABLE:
            raise EnvironmentEvidenceCurrentContextError("only USABLE qualification may form current context")
        return EnvironmentCurrentContext(
            context_id=context_id,
            environment_id=aggregate.environment_id,
            domain=aggregate.domain,
            subject_kind="aggregate",
            data={"observed": dict(aggregate.payload), "status": "qualified"},
            evidence_status=qualification.qualification,
            observation_ids=qualification.observation_ids,
            adapter_ids=qualification.adapter_ids,
            provenance_id=qualification.provenance_id,
            qualification_id=qualification.qualification_id,
            lineage=lineage or {"qualification_id": qualification.qualification_id},
        )

    @staticmethod
    def _validate_qualification(qualification: EnvironmentObservationEvidenceQualification) -> None:
        if type(qualification) is not EnvironmentObservationEvidenceQualification:
            raise TypeError("qualification must be EnvironmentObservationEvidenceQualification")

    @staticmethod
    def _validate_observation_alignment(
        observation: EnvironmentObservation,
        qualification: EnvironmentObservationEvidenceQualification,
    ) -> None:
        if qualification.subject_kind != "observation":
            raise EnvironmentEvidenceCurrentContextError("qualification subject kind mismatch")
        if qualification.environment_id != observation.environment_id or qualification.domain != observation.domain:
            raise EnvironmentEvidenceCurrentContextError("qualification scope mismatch")
        if qualification.observation_ids != (observation.observation_id,):
            raise EnvironmentEvidenceCurrentContextError("qualification observation identity mismatch")
        if qualification.adapter_ids != (observation.adapter_id,):
            raise EnvironmentEvidenceCurrentContextError("qualification adapter identity mismatch")

    @staticmethod
    def _validate_aggregate_alignment(
        aggregate: EnvironmentObservationAggregate,
        qualification: EnvironmentObservationEvidenceQualification,
    ) -> None:
        if qualification.subject_kind != "aggregate":
            raise EnvironmentEvidenceCurrentContextError("qualification subject kind mismatch")
        if qualification.environment_id != aggregate.environment_id or qualification.domain != aggregate.domain:
            raise EnvironmentEvidenceCurrentContextError("qualification scope mismatch")
        if qualification.observation_ids != aggregate.observation_ids:
            raise EnvironmentEvidenceCurrentContextError("qualification observation identities mismatch")
        if qualification.adapter_ids != aggregate.adapter_ids:
            raise EnvironmentEvidenceCurrentContextError("qualification adapter identities mismatch")
