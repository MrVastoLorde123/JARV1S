"""M21.5 bounded proactive scheduling and notification boundary.

This module creates advisory timing and notification proposals for proactive
recommendations. Creating a proposal is not scheduling, dispatch, delivery,
authorization, or execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Mapping


class SchedulingError(ValueError):
    """Raised when a scheduling or notification contract is invalid."""


class SchedulingStatus(str, Enum):
    PROPOSED = "PROPOSED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    NOT_SCHEDULABLE = "NOT_SCHEDULABLE"


class NotificationChannel(str, Enum):
    NONE = "NONE"
    OPERATOR = "OPERATOR"
    MESSAGE = "MESSAGE"
    DESKTOP = "DESKTOP"


@dataclass(frozen=True)
class ProactiveScheduleProposal:
    """Immutable advisory timing recommendation; never an active schedule."""

    proposal_id: str
    scheduled_for: datetime
    reason: str
    notification_channel: NotificationChannel = NotificationChannel.NONE
    notification_message: str | None = None
    expires_at: datetime | None = None
    bounded: bool = True
    authorization_granted: bool = False
    execution_requested: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.proposal_id, str) or not self.proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string")
        if not isinstance(self.scheduled_for, datetime) or self.scheduled_for.tzinfo is None:
            raise ValueError("scheduled_for must be timezone-aware")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
        if not isinstance(self.notification_channel, NotificationChannel):
            try:
                object.__setattr__(self, "notification_channel", NotificationChannel(self.notification_channel))
            except (TypeError, ValueError) as exc:
                raise TypeError("notification_channel must be a NotificationChannel") from exc
        if self.expires_at is not None:
            if not isinstance(self.expires_at, datetime) or self.expires_at.tzinfo is None:
                raise ValueError("expires_at must be None or timezone-aware")
            if self.expires_at < self.scheduled_for:
                raise ValueError("expires_at cannot precede scheduled_for")
        if self.notification_channel is NotificationChannel.NONE:
            if self.notification_message is not None:
                raise ValueError("notification_message requires a notification channel")
        elif not isinstance(self.notification_message, str) or not self.notification_message.strip():
            raise ValueError("notification_message is required when a notification channel is selected")
        for field in ("bounded", "authorization_granted", "execution_requested"):
            if not isinstance(getattr(self, field), bool):
                raise TypeError(f"{field} must be a bool")
            if field == "bounded" and not getattr(self, field):
                raise SchedulingError("schedule proposals must remain bounded")
            if field != "bounded" and getattr(self, field):
                raise SchedulingError(f"schedule proposals cannot set {field} to true")

    def to_context(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "scheduled_for": self.scheduled_for.isoformat(),
            "reason": self.reason,
            "notification_channel": self.notification_channel.value,
            "notification_message": self.notification_message,
            "expires_at": None if self.expires_at is None else self.expires_at.isoformat(),
            "bounded": True,
            "authorization_granted": False,
            "execution_requested": False,
            "scheduled": False,
            "notification_sent": False,
        }


@dataclass(frozen=True)
class SchedulingEvaluation:
    """Immutable evaluation of whether an advisory schedule may be proposed."""

    proposal_id: str
    status: SchedulingStatus
    reason: str
    schedule: ProactiveScheduleProposal | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.proposal_id, str) or not self.proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
        if not isinstance(self.status, SchedulingStatus):
            try:
                object.__setattr__(self, "status", SchedulingStatus(self.status))
            except (TypeError, ValueError) as exc:
                raise TypeError("status must be a SchedulingStatus") from exc
        if self.schedule is not None:
            if not isinstance(self.schedule, ProactiveScheduleProposal):
                raise TypeError("schedule must be a ProactiveScheduleProposal")
            if self.schedule.proposal_id != self.proposal_id:
                raise ValueError("schedule/proposal identity mismatch")
        if self.status is SchedulingStatus.PROPOSED and self.schedule is None:
            raise ValueError("PROPOSED evaluation requires a schedule")
        if self.status is not SchedulingStatus.PROPOSED and self.schedule is not None:
            raise ValueError("non-PROPOSED evaluation cannot contain a schedule")

    def to_context(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "status": self.status.value,
            "reason": self.reason,
            "schedule": None if self.schedule is None else self.schedule.to_context(),
            "authority_granted": False,
            "execution_requested": False,
            "scheduled": False,
            "notification_sent": False,
        }


def propose_schedule(
    proposal_id: str,
    *,
    scheduled_for: datetime,
    reason: str,
    notification_channel: NotificationChannel = NotificationChannel.NONE,
    notification_message: str | None = None,
    expires_at: datetime | None = None,
    proposal_active: bool = True,
) -> SchedulingEvaluation:
    """Create a bounded advisory timing recommendation without scheduling it."""
    if not isinstance(scheduled_for, datetime) or scheduled_for.tzinfo is None:
        raise ValueError("scheduled_for must be timezone-aware")
    if not isinstance(proposal_active, bool):
        raise TypeError("proposal_active must be a bool")
    if not proposal_active:
        return SchedulingEvaluation(
            proposal_id=proposal_id,
            status=SchedulingStatus.NOT_SCHEDULABLE,
            reason="source proposal is not active enough for a scheduling recommendation",
        )
    schedule = ProactiveScheduleProposal(
        proposal_id=proposal_id,
        scheduled_for=scheduled_for,
        reason=reason,
        notification_channel=notification_channel,
        notification_message=notification_message,
        expires_at=expires_at,
    )
    return SchedulingEvaluation(
        proposal_id=proposal_id,
        status=SchedulingStatus.PROPOSED,
        reason="bounded scheduling and notification recommendation created",
        schedule=schedule,
    )


def rank_schedule_proposals(
    evaluations: Mapping[str, SchedulingEvaluation],
) -> tuple[SchedulingEvaluation, ...]:
    """Order advisory scheduling recommendations deterministically by time and identity."""
    for proposal_id, evaluation in evaluations.items():
        if evaluation.proposal_id != proposal_id:
            raise ValueError("mapping key must match evaluation.proposal_id")
    proposed = [evaluation for evaluation in evaluations.values() if evaluation.status is SchedulingStatus.PROPOSED]
    return tuple(
        sorted(
            proposed,
            key=lambda evaluation: (
                evaluation.schedule.scheduled_for if evaluation.schedule is not None else datetime.max,
                evaluation.proposal_id,
            ),
        )
    )
