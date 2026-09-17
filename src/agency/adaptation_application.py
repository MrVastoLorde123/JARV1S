"""M66: apply validated learning to an immutable learning profile.

Application here is a bounded state transition. It does not mutate tools,
execution state, permissions, credentials, or authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .adaptation_validation import AdaptationValidation


@dataclass(frozen=True)
class LearningProfile:
    version: int = 0
    entries: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.version, int) or isinstance(self.version, bool) or self.version < 0:
            raise ValueError("version must be a non-negative integer")
        if not isinstance(self.entries, Mapping):
            raise TypeError("entries must be a mapping")
        if any(not isinstance(k, str) or not k.strip() or not isinstance(v, str) or not v.strip() for k, v in self.entries.items()):
            raise TypeError("profile entries must map non-empty strings to non-empty strings")
        object.__setattr__(self, "entries", MappingProxyType(dict(self.entries)))

    def to_context(self) -> dict[str, Any]:
        return {"version": self.version, "entries": dict(self.entries), "authority_granted": False}


@dataclass(frozen=True)
class AdaptationApplication:
    application_id: str
    validation: AdaptationValidation
    before: LearningProfile
    after: LearningProfile
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.validation, AdaptationValidation):
            raise TypeError("validation must be an AdaptationValidation")
        if not self.validation.applicable:
            raise ValueError("only valid adaptations may be applied")
        if not isinstance(self.before, LearningProfile) or not isinstance(self.after, LearningProfile):
            raise TypeError("before and after must be LearningProfile values")
        if not isinstance(self.application_id, str) or not self.application_id.strip():
            raise ValueError("application_id must be a non-empty string")
        if self.after.version != self.before.version + 1:
            raise ValueError("application must increment profile version exactly once")
        proposal = self.validation.proposal
        if self.after.entries.get(proposal.target) != proposal.description:
            raise ValueError("after profile must contain the proposed adaptation")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "application_id": self.application_id,
            "validation_id": self.validation.validation_id,
            "proposal_id": self.validation.proposal.proposal_id,
            "before": self.before.to_context(),
            "after": self.after.to_context(),
            "metadata": dict(self.metadata),
            "authorization_granted": False,
            "execution_requested": False,
            "external_mutation_performed": False,
        }


def apply_adaptation(
    validation: AdaptationValidation,
    profile: LearningProfile,
    *,
    application_id: str,
    metadata: Mapping[str, Any] | None = None,
) -> AdaptationApplication:
    if not isinstance(validation, AdaptationValidation):
        raise TypeError("validation must be an AdaptationValidation")
    if not isinstance(profile, LearningProfile):
        raise TypeError("profile must be a LearningProfile")
    if not validation.applicable:
        raise ValueError("validation must be VALID before application")
    proposal = validation.proposal
    entries = dict(profile.entries)
    entries[proposal.target] = proposal.description
    after = LearningProfile(version=profile.version + 1, entries=entries)
    return AdaptationApplication(
        application_id=application_id,
        validation=validation,
        before=profile,
        after=after,
        metadata=metadata or {},
    )


__all__ = ["AdaptationApplication", "LearningProfile", "apply_adaptation"]
