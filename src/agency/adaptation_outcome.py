"""M67: measure the bounded outcome of an applied adaptation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from .adaptation_application import AdaptationApplication
from .experience_feedback import ExperienceFeedback


class AdaptationOutcomeDisposition(str, Enum):
    IMPROVED = "IMPROVED"
    NO_CHANGE = "NO_CHANGE"
    REGRESSED = "REGRESSED"
    UNMEASURED = "UNMEASURED"


@dataclass(frozen=True)
class AdaptationOutcome:
    outcome_id: str
    application: AdaptationApplication
    disposition: AdaptationOutcomeDisposition
    value_delta: float | None
    reason: str
    follow_up_feedback: ExperienceFeedback | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.application, AdaptationApplication):
            raise TypeError("application must be an AdaptationApplication")
        if not isinstance(self.disposition, AdaptationOutcomeDisposition):
            raise TypeError("disposition must be an AdaptationOutcomeDisposition")
        if not isinstance(self.outcome_id, str) or not self.outcome_id.strip():
            raise ValueError("outcome_id must be a non-empty string")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
        if self.value_delta is not None and not isinstance(self.value_delta, (int, float)):
            raise TypeError("value_delta must be numeric or None")
        if self.follow_up_feedback is not None and not isinstance(self.follow_up_feedback, ExperienceFeedback):
            raise TypeError("follow_up_feedback must be ExperienceFeedback or None")
        if self.disposition is AdaptationOutcomeDisposition.IMPROVED and (self.value_delta is None or self.value_delta <= 0):
            raise ValueError("IMPROVED outcome requires positive measured value_delta")
        if self.disposition is AdaptationOutcomeDisposition.REGRESSED and (self.value_delta is None or self.value_delta >= 0):
            raise ValueError("REGRESSED outcome requires negative measured value_delta")
        if self.disposition is AdaptationOutcomeDisposition.NO_CHANGE and self.value_delta not in (None, 0, 0.0):
            raise ValueError("NO_CHANGE outcome requires zero or absent value_delta")
        if self.disposition is AdaptationOutcomeDisposition.UNMEASURED and self.value_delta is not None:
            raise ValueError("UNMEASURED outcome cannot contain value_delta")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "outcome_id": self.outcome_id,
            "application_id": self.application.application_id,
            "proposal_id": self.application.validation.proposal.proposal_id,
            "disposition": self.disposition.value,
            "value_delta": self.value_delta,
            "reason": self.reason,
            "follow_up_feedback_id": None if self.follow_up_feedback is None else self.follow_up_feedback.experience_id,
            "metadata": dict(self.metadata),
            "authorization_granted": False,
            "execution_requested": False,
        }


def evaluate_adaptation_outcome(
    application: AdaptationApplication,
    *,
    outcome_id: str,
    disposition: AdaptationOutcomeDisposition,
    reason: str,
    value_delta: float | None = None,
    follow_up_feedback: ExperienceFeedback | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> AdaptationOutcome:
    return AdaptationOutcome(
        outcome_id=outcome_id,
        application=application,
        disposition=disposition,
        value_delta=value_delta,
        reason=reason,
        follow_up_feedback=follow_up_feedback,
        metadata=metadata or {},
    )


__all__ = ["AdaptationOutcome", "AdaptationOutcomeDisposition", "evaluate_adaptation_outcome"]
