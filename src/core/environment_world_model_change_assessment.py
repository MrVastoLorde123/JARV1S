"""M23.15: deterministic change evidence between descriptive world models.

This boundary identifies domain-level changes without deciding which model is true,
revising either model, or authorizing any downstream action.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model import EnvironmentWorldModel


class WorldModelChangeAssessmentError(RuntimeError):
    """Raised when world-model change assessment cannot be performed safely."""


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
class EnvironmentWorldModelChangeAssessment:
    """Immutable descriptive change evidence between two world-model artifacts."""

    assessment_id: str
    environment_id: str
    baseline_model_id: str
    candidate_model_id: str
    changed_domains: tuple[str, ...]
    unchanged_domains: tuple[str, ...]
    baseline_missing_domains: tuple[str, ...]
    candidate_missing_domains: tuple[str, ...]
    changes_by_domain: Mapping[str, Mapping[str, Any]]
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "assessment_id",
            "environment_id",
            "baseline_model_id",
            "candidate_model_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.baseline_model_id == self.candidate_model_id:
            raise ValueError("baseline and candidate model identities must differ")
        for name in (
            "changed_domains",
            "unchanged_domains",
            "baseline_missing_domains",
            "candidate_missing_domains",
        ):
            if not isinstance(getattr(self, name), tuple):
                raise TypeError(f"{name} must be a tuple")
        if set(self.changed_domains) & set(self.unchanged_domains):
            raise ValueError("changed and unchanged domains must be disjoint")
        if not isinstance(self.changes_by_domain, Mapping):
            raise TypeError("changes_by_domain must be a mapping")
        if set(self.changes_by_domain) != set(self.changed_domains):
            raise ValueError("changes_by_domain must exactly cover changed domains")
        for domain, change in self.changes_by_domain.items():
            if not isinstance(domain, str) or not domain.strip():
                raise ValueError("changes_by_domain contains an invalid domain")
            if not isinstance(change, Mapping):
                raise TypeError("each domain change must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "changes_by_domain", _freeze(self.changes_by_domain))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_descriptive_only(self) -> bool:
        return True


class EnvironmentWorldModelChangeAssessmentService:
    """Compare two descriptive environment world models without mutating either."""

    def assess(
        self,
        baseline: EnvironmentWorldModel,
        candidate: EnvironmentWorldModel,
        *,
        assessment_id: str,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelChangeAssessment:
        if type(baseline) is not EnvironmentWorldModel:
            raise TypeError("baseline must be EnvironmentWorldModel")
        if type(candidate) is not EnvironmentWorldModel:
            raise TypeError("candidate must be EnvironmentWorldModel")
        if baseline.environment_id != candidate.environment_id:
            raise WorldModelChangeAssessmentError(
                "baseline and candidate must belong to the same environment"
            )
        if baseline.model_id == candidate.model_id:
            raise WorldModelChangeAssessmentError(
                "baseline and candidate model identities must differ"
            )

        baseline_domains = set(baseline.represented_domains)
        candidate_domains = set(candidate.represented_domains)
        all_domains = tuple(
            dict.fromkeys((*baseline.represented_domains, *candidate.represented_domains))
        )

        changed: list[str] = []
        unchanged: list[str] = []
        changes: dict[str, Mapping[str, Any]] = {}
        for domain in all_domains:
            baseline_present = domain in baseline_domains
            candidate_present = domain in candidate_domains
            baseline_value = baseline.state_by_domain.get(domain)
            candidate_value = candidate.state_by_domain.get(domain)
            if baseline_present != candidate_present or baseline_value != candidate_value:
                changed.append(domain)
                changes[domain] = {
                    "baseline_present": baseline_present,
                    "candidate_present": candidate_present,
                    "baseline_state": baseline_value if baseline_present else None,
                    "candidate_state": candidate_value if candidate_present else None,
                }
            else:
                unchanged.append(domain)

        return EnvironmentWorldModelChangeAssessment(
            assessment_id=assessment_id,
            environment_id=baseline.environment_id,
            baseline_model_id=baseline.model_id,
            candidate_model_id=candidate.model_id,
            changed_domains=tuple(changed),
            unchanged_domains=tuple(unchanged),
            baseline_missing_domains=baseline.missing_domains,
            candidate_missing_domains=candidate.missing_domains,
            changes_by_domain=changes,
            lineage=lineage
            or {
                "baseline_model_id": baseline.model_id,
                "candidate_model_id": candidate.model_id,
            },
        )
