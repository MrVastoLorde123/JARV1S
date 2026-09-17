"""M65: bounded validation of adaptation proposals."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from .adaptation_proposal import AdaptationProposal


class AdaptationValidationDisposition(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class AdaptationValidation:
    validation_id: str
    proposal: AdaptationProposal
    disposition: AdaptationValidationDisposition
    reason: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.proposal, AdaptationProposal):
            raise TypeError("proposal must be an AdaptationProposal")
        if not isinstance(self.disposition, AdaptationValidationDisposition):
            raise TypeError("disposition must be an AdaptationValidationDisposition")
        if not isinstance(self.validation_id, str) or not self.validation_id.strip():
            raise ValueError("validation_id must be a non-empty string")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def applicable(self) -> bool:
        return self.disposition is AdaptationValidationDisposition.VALID

    def to_context(self) -> dict[str, Any]:
        return {
            "validation_id": self.validation_id,
            "proposal_id": self.proposal.proposal_id,
            "disposition": self.disposition.value,
            "reason": self.reason,
            "applicable": self.applicable,
            "metadata": dict(self.metadata),
            "authorization_granted": False,
            "execution_requested": False,
        }


def validate_adaptation(
    proposal: AdaptationProposal,
    *,
    validation_id: str,
    disposition: AdaptationValidationDisposition,
    reason: str,
    metadata: Mapping[str, Any] | None = None,
) -> AdaptationValidation:
    return AdaptationValidation(
        validation_id=validation_id,
        proposal=proposal,
        disposition=disposition,
        reason=reason,
        metadata=metadata or {},
    )


__all__ = ["AdaptationValidation", "AdaptationValidationDisposition", "validate_adaptation"]
