"""M51: bounded confirmation boundary for scheduling/notification proposals.

Confirmation records an explicit user-facing confirmation request and its
response without granting authorization, selecting capabilities, or executing
anything. Authorization remains a separate downstream boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from .scheduling_notification import SchedulingNotificationProposal, SchedulingNotificationProposalSet


class ConfirmationDisposition(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"


@dataclass(frozen=True)
class ConfirmationRequest:
    """Immutable request for explicit user confirmation of one proposal."""

    confirmation_id: str
    source_proposal_set_id: str
    proposal_id: str
    prompt: str
    disposition: ConfirmationDisposition = ConfirmationDisposition.PENDING
    response_text: str | None = None
    responded_at: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("confirmation_id", "source_proposal_set_id", "proposal_id", "prompt"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.disposition, ConfirmationDisposition):
            raise TypeError("disposition must be a ConfirmationDisposition")
        if self.response_text is not None and not isinstance(self.response_text, str):
            raise TypeError("response_text must be a string when supplied")
        if self.responded_at is not None and (not isinstance(self.responded_at, str) or not self.responded_at.strip()):
            raise ValueError("responded_at must be a non-empty string when supplied")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "confirmation_id": self.confirmation_id,
            "source_proposal_set_id": self.source_proposal_set_id,
            "proposal_id": self.proposal_id,
            "prompt": self.prompt,
            "disposition": self.disposition.value,
            "response_text": self.response_text,
            "responded_at": self.responded_at,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "intent_established": False,
            "authority_granted": False,
            "authorization_requested": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class ConfirmationResult:
    """Immutable collection of explicit confirmation requests/results."""

    result_id: str
    source_proposal_set_id: str
    requests: tuple[ConfirmationRequest, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("result_id", "source_proposal_set_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.requests, tuple) or any(not isinstance(item, ConfirmationRequest) for item in self.requests):
            raise TypeError("requests must be a tuple of ConfirmationRequest values")
        ids = tuple(item.confirmation_id for item in self.requests)
        if len(set(ids)) != len(ids):
            raise ValueError("confirmation IDs must be unique")
        if any(item.source_proposal_set_id != self.source_proposal_set_id for item in self.requests):
            raise ValueError("source proposal-set identity mismatch")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def confirmed_ids(self) -> tuple[str, ...]:
        return tuple(item.confirmation_id for item in self.requests if item.disposition is ConfirmationDisposition.CONFIRMED)

    @property
    def pending_ids(self) -> tuple[str, ...]:
        return tuple(item.confirmation_id for item in self.requests if item.disposition is ConfirmationDisposition.PENDING)

    def to_context(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "source_proposal_set_id": self.source_proposal_set_id,
            "requests": tuple(item.to_context() for item in self.requests),
            "confirmed_ids": self.confirmed_ids,
            "pending_ids": self.pending_ids,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "intent_established": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


def build_confirmation_result(
    proposals: SchedulingNotificationProposalSet,
    *,
    result_id: str,
    requests: tuple[ConfirmationRequest, ...] = (),
    metadata: Mapping[str, Any] | None = None,
) -> ConfirmationResult:
    """Bind confirmation requests to one exact scheduling/notification proposal set."""
    if not isinstance(proposals, SchedulingNotificationProposalSet):
        raise TypeError("proposals must be a SchedulingNotificationProposalSet")
    if not isinstance(result_id, str) or not result_id.strip():
        raise ValueError("result_id must be a non-empty string")
    if not isinstance(requests, tuple) or any(not isinstance(item, ConfirmationRequest) for item in requests):
        raise TypeError("requests must be a tuple of ConfirmationRequest values")

    known_ids = {item.proposal_id for item in proposals.proposals}
    for request in requests:
        if request.source_proposal_set_id != proposals.proposal_set_id:
            raise ValueError("source proposal-set identity mismatch")
        if request.proposal_id not in known_ids:
            raise ValueError("confirmation may only reference proposals from the supplied scheduling/notification set")
        if request.disposition is ConfirmationDisposition.PENDING and request.response_text is not None:
            raise ValueError("pending confirmation cannot carry response_text")

    return ConfirmationResult(
        result_id=result_id.strip(),
        source_proposal_set_id=proposals.proposal_set_id,
        requests=requests,
        metadata={"source": "M51", **dict(metadata or {})},
    )


__all__ = ["ConfirmationDisposition", "ConfirmationRequest", "ConfirmationResult", "build_confirmation_result"]
