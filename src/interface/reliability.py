"""M11.7 provider-neutral interface reliability and recovery boundary.

Reliability state describes transport/interaction continuity. Recovery eligibility
only determines whether the interface may mechanically retry, resume, or replay a
transport operation; it never authorizes a semantic action.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class InterfaceReliabilityState(str, Enum):
    """Observable interface continuity state."""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    RECOVERING = "RECOVERING"
    RECOVERED = "RECOVERED"
    FAILED = "FAILED"


class InterfaceRecoveryAction(str, Enum):
    """Mechanically safe transport recovery action; not permission."""

    NONE = "NONE"
    RETRY = "RETRY"
    RESUME = "RESUME"
    REPLAY = "REPLAY"
    ABANDON = "ABANDON"


@dataclass(frozen=True)
class InterfaceReliabilityRecord:
    """Immutable observation of one interface continuity condition."""

    record_id: str
    request_id: str
    state: InterfaceReliabilityState
    action: InterfaceRecoveryAction = InterfaceRecoveryAction.NONE
    attempt: int = 0
    reason: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("record_id", "request_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.state, InterfaceReliabilityState):
            try:
                object.__setattr__(self, "state", InterfaceReliabilityState(self.state))
            except (TypeError, ValueError) as exc:
                raise TypeError("state must be an InterfaceReliabilityState") from exc
        if not isinstance(self.action, InterfaceRecoveryAction):
            try:
                object.__setattr__(self, "action", InterfaceRecoveryAction(self.action))
            except (TypeError, ValueError) as exc:
                raise TypeError("action must be an InterfaceRecoveryAction") from exc
        if not isinstance(self.attempt, int) or isinstance(self.attempt, bool) or self.attempt < 0:
            raise ValueError("attempt must be a non-negative integer")
        if not isinstance(self.reason, str):
            raise TypeError("reason must be a string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        if self.state is InterfaceReliabilityState.HEALTHY and self.action is not InterfaceRecoveryAction.NONE:
            raise ValueError("healthy state cannot request recovery")
        if self.state is InterfaceReliabilityState.FAILED and self.action is InterfaceRecoveryAction.NONE:
            raise ValueError("failed state requires explicit recovery or abandon action")
        object.__setattr__(self, "record_id", self.record_id.strip())
        object.__setattr__(self, "request_id", self.request_id.strip())
        object.__setattr__(self, "reason", self.reason.strip())
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def recovery_requested(self) -> bool:
        return self.action is not InterfaceRecoveryAction.NONE

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "request_id": self.request_id,
            "state": self.state.value,
            "action": self.action.value,
            "attempt": self.attempt,
            "reason": self.reason,
            "metadata": dict(self.metadata),
            "intent_interpreted": False,
            "truth_guaranteed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


@dataclass(frozen=True)
class InterfaceRecoveryState:
    """Immutable bounded recovery history for one request."""

    request_id: str
    records: tuple[InterfaceReliabilityRecord, ...] = ()
    max_records: int = 32

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str) or not self.request_id.strip():
            raise ValueError("request_id must be a non-empty string")
        if not isinstance(self.records, tuple):
            raise TypeError("records must be a tuple")
        if not isinstance(self.max_records, int) or isinstance(self.max_records, bool) or self.max_records <= 0:
            raise ValueError("max_records must be a positive integer")
        if len(self.records) > self.max_records:
            raise ValueError("recovery history exceeds max_records")
        if any(record.request_id != self.request_id for record in self.records):
            raise ValueError("record request_id must match recovery state")
        ids = [record.record_id for record in self.records]
        if len(set(ids)) != len(ids):
            raise ValueError("record_id must be unique within recovery history")
        object.__setattr__(self, "request_id", self.request_id.strip())

    @property
    def latest(self) -> InterfaceReliabilityRecord | None:
        return self.records[-1] if self.records else None

    @property
    def state(self) -> InterfaceReliabilityState:
        return self.latest.state if self.latest else InterfaceReliabilityState.HEALTHY

    @property
    def recovery_action(self) -> InterfaceRecoveryAction:
        return self.latest.action if self.latest else InterfaceRecoveryAction.NONE

    def append(self, record: InterfaceReliabilityRecord) -> "InterfaceRecoveryState":
        if not isinstance(record, InterfaceReliabilityRecord):
            raise TypeError("record must be an InterfaceReliabilityRecord")
        if record.request_id != self.request_id:
            raise ValueError("record request_id must match recovery state")
        if len(self.records) >= self.max_records:
            raise ValueError("recovery history bound has been reached")
        if any(item.record_id == record.record_id for item in self.records):
            raise ValueError(f"record_id '{record.record_id}' is already present")
        return InterfaceRecoveryState(
            request_id=self.request_id,
            records=self.records + (record,),
            max_records=self.max_records,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "records": [record.to_dict() for record in self.records],
            "max_records": self.max_records,
            "state": self.state.value,
            "recovery_action": self.recovery_action.value,
            "intent_interpreted": False,
            "truth_guaranteed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


@dataclass(frozen=True)
class InterfaceRecoveryStore:
    """Immutable conflict-aware recovery-state registry."""

    states: tuple[InterfaceRecoveryState, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.states, tuple):
            raise TypeError("states must be a tuple")
        ids = [state.request_id for state in self.states]
        if len(set(ids)) != len(ids):
            raise ValueError("request_id must be unique within recovery store")

    def add(self, state: InterfaceRecoveryState) -> "InterfaceRecoveryStore":
        if not isinstance(state, InterfaceRecoveryState):
            raise TypeError("state must be an InterfaceRecoveryState")
        if self.get(state.request_id) is not None:
            raise ValueError(f"request '{state.request_id}' already exists")
        return InterfaceRecoveryStore(self.states + (state,))

    def replace(self, state: InterfaceRecoveryState) -> "InterfaceRecoveryStore":
        if not isinstance(state, InterfaceRecoveryState):
            raise TypeError("state must be an InterfaceRecoveryState")
        if self.get(state.request_id) is None:
            raise ValueError(f"request '{state.request_id}' does not exist")
        return InterfaceRecoveryStore(
            tuple(state if item.request_id == state.request_id else item for item in self.states)
        )

    def get(self, request_id: str) -> InterfaceRecoveryState | None:
        return next((item for item in self.states if item.request_id == request_id), None)

    def list(self) -> tuple[InterfaceRecoveryState, ...]:
        return self.states


class InterfaceReliabilityRuntime:
    """Record interface failures and mechanically bounded recovery eligibility."""

    def start(self, request_id: str, *, max_records: int = 32) -> InterfaceRecoveryState:
        return InterfaceRecoveryState(request_id=request_id, max_records=max_records)

    def healthy(self, state: InterfaceRecoveryState, *, record_id: str, metadata: Mapping[str, Any] | None = None) -> InterfaceRecoveryState:
        return state.append(
            InterfaceReliabilityRecord(
                record_id=record_id,
                request_id=state.request_id,
                state=InterfaceReliabilityState.HEALTHY,
                action=InterfaceRecoveryAction.NONE,
                metadata=metadata or {},
            )
        )

    def degrade(self, state: InterfaceRecoveryState, *, record_id: str, reason: str, attempt: int = 0, action: InterfaceRecoveryAction = InterfaceRecoveryAction.RETRY, metadata: Mapping[str, Any] | None = None) -> InterfaceRecoveryState:
        return state.append(
            InterfaceReliabilityRecord(
                record_id=record_id,
                request_id=state.request_id,
                state=InterfaceReliabilityState.DEGRADED,
                action=action,
                attempt=attempt,
                reason=reason,
                metadata=metadata or {},
            )
        )

    def recover(self, state: InterfaceRecoveryState, *, record_id: str, action: InterfaceRecoveryAction, attempt: int = 0, metadata: Mapping[str, Any] | None = None) -> InterfaceRecoveryState:
        if action not in {
            InterfaceRecoveryAction.RETRY,
            InterfaceRecoveryAction.RESUME,
            InterfaceRecoveryAction.REPLAY,
        }:
            raise ValueError("recover requires RETRY, RESUME, or REPLAY")
        return state.append(
            InterfaceReliabilityRecord(
                record_id=record_id,
                request_id=state.request_id,
                state=InterfaceReliabilityState.RECOVERING,
                action=action,
                attempt=attempt,
                metadata=metadata or {},
            )
        )

    def recovered(self, state: InterfaceRecoveryState, *, record_id: str, metadata: Mapping[str, Any] | None = None) -> InterfaceRecoveryState:
        return state.append(
            InterfaceReliabilityRecord(
                record_id=record_id,
                request_id=state.request_id,
                state=InterfaceReliabilityState.RECOVERED,
                action=InterfaceRecoveryAction.NONE,
                metadata=metadata or {},
            )
        )

    def failed(self, state: InterfaceRecoveryState, *, record_id: str, reason: str, action: InterfaceRecoveryAction = InterfaceRecoveryAction.ABANDON, attempt: int = 0, metadata: Mapping[str, Any] | None = None) -> InterfaceRecoveryState:
        return state.append(
            InterfaceReliabilityRecord(
                record_id=record_id,
                request_id=state.request_id,
                state=InterfaceReliabilityState.FAILED,
                action=action,
                attempt=attempt,
                reason=reason,
                metadata=metadata or {},
            )
        )
