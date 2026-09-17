"""M50: bounded scheduling and notification proposal substrate.

This module converts proactive proposals into explicit scheduling/notification
proposals without performing scheduling, sending notifications, requesting
authorization, or executing anything.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from .proactive_proposal import ProactiveProposal, ProactiveProposalSet


class SchedulingNotificationKind(str, Enum):
    """Descriptive downstream delivery mode for a proposal."""

    SCHEDULE = "SCHEDULE"
    NOTIFY = "NOTIFY"
    SCHEDULE_AND_NOTIFY = "SCHEDULE_AND_NOTIFY"


def _validate_timestamp(value: str | None, name: str) -> None:
    if value is None:
        return
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty ISO-8601 string when supplied")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{name} must be timezone-aware")


@dataclass(frozen=True)
class SchedulingNotificationProposal:
    """Immutable proposal for a future scheduling or notification action."""

    proposal_id: str
    source_proposal_set_id: str
    statement: str
    kind: SchedulingNotificationKind
    rationale: str
    scheduled_for: str | None = None
    earliest_at: str | None = None
    latest_at: str | None = None
    candidate_id: str | None = None
    unresolved_uncertainties: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("proposal_id", "source_proposal_set_id", "statement", "rationale"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.kind, SchedulingNotificationKind):
            raise TypeError("kind must be a SchedulingNotificationKind")
        if self.candidate_id is not None and (not isinstance(self.candidate_id, str) or not self.candidate_id.strip()):
            raise ValueError("candidate_id must be a non-empty string when supplied")
        for name in ("scheduled_for", "earliest_at", "latest_at"):
            _validate_timestamp(getattr(self, name), name)
        if self.scheduled_for is not None and self.earliest_at is not None:
            if datetime.fromisoformat(self.scheduled_for) < datetime.fromisoformat(self.earliest_at):
                raise ValueError("scheduled_for cannot precede earliest_at")
        if self.scheduled_for is not None and self.latest_at is not None:
            if datetime.fromisoformat(self.scheduled_for) > datetime.fromisoformat(self.latest_at):
                raise ValueError("scheduled_for cannot exceed latest_at")
        if self.earliest_at is not None and self.latest_at is not None:
            if datetime.fromisoformat(self.earliest_at) > datetime.fromisoformat(self.latest_at):
                raise ValueError("earliest_at cannot exceed latest_at")
        if not isinstance(self.unresolved_uncertainties, tuple):
            raise TypeError("unresolved_uncertainties must be a tuple")
        if len(set(self.unresolved_uncertainties)) != len(self.unresolved_uncertainties):
            raise ValueError("unresolved_uncertainties must contain unique values")
        if any(not isinstance(item, str) or not item.strip() for item in self.unresolved_uncertainties):
            raise ValueError("unresolved_uncertainties must contain non-empty strings")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "source_proposal_set_id": self.source_proposal_set_id,
            "statement": self.statement,
            "kind": self.kind.value,
            "rationale": self.rationale,
            "scheduled_for": self.scheduled_for,
            "earliest_at": self.earliest_at,
            "latest_at": self.latest_at,
            "candidate_id": self.candidate_id,
            "unresolved_uncertainties": self.unresolved_uncertainties,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "intent_established": False,
            "authority_granted": False,
            "scheduling_requested": False,
            "notification_requested": False,
            "authorization_requested": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class SchedulingNotificationProposalSet:
    """Immutable collection of bounded scheduling/notification proposals."""

    proposal_set_id: str
    source_proposal_set_id: str
    proposals: tuple[SchedulingNotificationProposal, ...] = ()
    unresolved_uncertainties: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("proposal_set_id", "source_proposal_set_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.proposals, tuple) or any(not isinstance(item, SchedulingNotificationProposal) for item in self.proposals):
            raise TypeError("proposals must be a tuple of SchedulingNotificationProposal values")
        ids = tuple(item.proposal_id for item in self.proposals)
        if len(set(ids)) != len(ids):
            raise ValueError("proposal IDs must be unique")
        if any(item.source_proposal_set_id != self.source_proposal_set_id for item in self.proposals):
            raise ValueError("source proposal-set identity mismatch")
        if not isinstance(self.unresolved_uncertainties, tuple):
            raise TypeError("unresolved_uncertainties must be a tuple")
        if len(set(self.unresolved_uncertainties)) != len(self.unresolved_uncertainties):
            raise ValueError("unresolved_uncertainties must contain unique values")
        if any(not isinstance(item, str) or not item.strip() for item in self.unresolved_uncertainties):
            raise ValueError("unresolved_uncertainties must contain non-empty strings")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def proposal_count(self) -> int:
        return len(self.proposals)

    def to_context(self) -> dict[str, Any]:
        return {
            "proposal_set_id": self.proposal_set_id,
            "source_proposal_set_id": self.source_proposal_set_id,
            "proposals": tuple(item.to_context() for item in self.proposals),
            "proposal_count": self.proposal_count,
            "unresolved_uncertainties": self.unresolved_uncertainties,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "intent_established": False,
            "authority_granted": False,
            "permissions_granted": False,
            "scheduling_requested": False,
            "notification_requested": False,
            "authorization_requested": False,
            "execution_requested": False,
        }


def build_scheduling_notification_proposal_set(
    proactive_proposals: ProactiveProposalSet,
    *,
    proposal_set_id: str,
    proposals: tuple[SchedulingNotificationProposal, ...] = (),
    metadata: Mapping[str, Any] | None = None,
) -> SchedulingNotificationProposalSet:
    """Build scheduling/notification proposals against one exact M49 set."""
    if not isinstance(proactive_proposals, ProactiveProposalSet):
        raise TypeError("proactive_proposals must be a ProactiveProposalSet")
    if not isinstance(proposal_set_id, str) or not proposal_set_id.strip():
        raise ValueError("proposal_set_id must be a non-empty string")
    if not isinstance(proposals, tuple) or any(not isinstance(item, SchedulingNotificationProposal) for item in proposals):
        raise TypeError("proposals must be a tuple of SchedulingNotificationProposal values")

    known_ids = {item.proposal_id for item in proactive_proposals.proposals}
    known_candidates = {
        item.candidate_id for item in proactive_proposals.proposals if item.candidate_id is not None
    }
    known_uncertainties = set(proactive_proposals.unresolved_uncertainties)

    for proposal in proposals:
        if proposal.source_proposal_set_id != proactive_proposals.proposal_set_id:
            raise ValueError("source proposal-set identity mismatch")
        if proposal.proposal_id in known_ids:
            raise ValueError("scheduling proposal ID must differ from its source M49 proposal ID")
        if proposal.candidate_id is not None and proposal.candidate_id not in known_candidates:
            raise ValueError("candidate lineage must reference the supplied proactive proposal set")
        if not set(proposal.unresolved_uncertainties).issubset(known_uncertainties):
            raise ValueError("unresolved uncertainties must come from the supplied proactive proposal set")

    return SchedulingNotificationProposalSet(
        proposal_set_id=proposal_set_id.strip(),
        source_proposal_set_id=proactive_proposals.proposal_set_id,
        proposals=proposals,
        unresolved_uncertainties=proactive_proposals.unresolved_uncertainties,
        metadata={"source": "M50", **dict(metadata or {})},
    )


__all__ = [
    "SchedulingNotificationKind",
    "SchedulingNotificationProposal",
    "SchedulingNotificationProposalSet",
    "build_scheduling_notification_proposal_set",
]
