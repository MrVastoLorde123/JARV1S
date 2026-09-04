"""M15.5 proactive scheduling boundary.

Scheduling defines when an initiative may be surfaced or revisited. It does
not create urgency, authorization, confirmation, policy authority, or
execution permission.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Mapping
from types import MappingProxyType

from .proposals import InitiativeProposal


class ProactiveScheduleValidationError(ValueError):
    """Raised when a proactive schedule violates the M15.5 boundary."""


class ScheduleStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


MAX_ID_LENGTH = 256
MAX_TIMEZONE_LENGTH = 128
MAX_METADATA_ITEMS = 32
MAX_REFERENCE_LENGTH = 256


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProactiveScheduleValidationError(f"{field_name} must be a non-empty string")
    if len(value) > maximum:
        raise ProactiveScheduleValidationError(
            f"{field_name} exceeds maximum length of {maximum}"
        )
    return value


def _validate_timestamp(value: str, field_name: str) -> str:
    _text(value, field_name, MAX_REFERENCE_LENGTH)
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProactiveScheduleValidationError(f"{field_name} must be ISO-8601") from exc
    return value


def _freeze(value: Any, path: str = "metadata") -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, float) and not (value == value and abs(value) != float("inf")):
            raise ProactiveScheduleValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ProactiveScheduleValidationError(f"{path} keys must be non-empty strings")
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[]") for item in value)
    raise ProactiveScheduleValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class ProactiveSchedule:
    """Immutable schedule for surfacing or revisiting one initiative proposal."""

    schedule_id: str
    proposal: InitiativeProposal
    next_at: str
    timezone: str = "UTC"
    interval_minutes: int | None = None
    status: ScheduleStatus = ScheduleStatus.ACTIVE
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.schedule_id, "schedule_id", MAX_ID_LENGTH)
        if not isinstance(self.proposal, InitiativeProposal):
            raise ProactiveScheduleValidationError("proposal must be an InitiativeProposal")
        _validate_timestamp(self.next_at, "next_at")
        _text(self.timezone, "timezone", MAX_TIMEZONE_LENGTH)
        if self.interval_minutes is not None:
            if isinstance(self.interval_minutes, bool) or not isinstance(self.interval_minutes, int):
                raise ProactiveScheduleValidationError("interval_minutes must be an integer or None")
            if self.interval_minutes <= 0:
                raise ProactiveScheduleValidationError("interval_minutes must be positive")
        if not isinstance(self.status, ScheduleStatus):
            try:
                object.__setattr__(self, "status", ScheduleStatus(self.status))
            except (TypeError, ValueError) as exc:
                raise ProactiveScheduleValidationError("status must be a supported ScheduleStatus") from exc
        if not isinstance(self.metadata, Mapping):
            raise ProactiveScheduleValidationError("metadata must be a mapping")
        if len(self.metadata) > MAX_METADATA_ITEMS:
            raise ProactiveScheduleValidationError(
                f"metadata exceeds maximum item count of {MAX_METADATA_ITEMS}"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @property
    def proposal_id(self) -> str:
        return self.proposal.proposal_id

    def reschedule(self, next_at: str) -> "ProactiveSchedule":
        _validate_timestamp(next_at, "next_at")
        return ProactiveSchedule(
            schedule_id=self.schedule_id,
            proposal=self.proposal,
            next_at=next_at,
            timezone=self.timezone,
            interval_minutes=self.interval_minutes,
            status=self.status,
            metadata=self.metadata,
        )

    def with_status(self, status: ScheduleStatus) -> "ProactiveSchedule":
        return ProactiveSchedule(
            schedule_id=self.schedule_id,
            proposal=self.proposal,
            next_at=self.next_at,
            timezone=self.timezone,
            interval_minutes=self.interval_minutes,
            status=status,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schedule_id": self.schedule_id,
            "proposal_id": self.proposal_id,
            "next_at": self.next_at,
            "timezone": self.timezone,
            "interval_minutes": self.interval_minutes,
            "status": self.status.value,
            "metadata": _thaw(self.metadata),
            "scheduling_is_authorization": False,
            "scheduling_is_confirmation": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
            "initiative_is_instruction": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
