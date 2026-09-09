"""M25.4: derive immutable per-session interface state from runtime activity."""
from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from types import MappingProxyType
from typing import Any, Mapping

from src.core.interface_backend import InterfaceOperation, InterfaceResponseStatus
from src.core.runtime_activity_stream import RuntimeActivityEvent, RuntimeActivityKind


class InterfaceSessionStateError(RuntimeError):
    """Raised when session projection cannot be updated safely."""


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
class InterfaceSessionState:
    """Immutable projection of observed activity for one interface session."""

    session_id: str
    actor_id: str
    event_count: int
    first_sequence: int
    last_sequence: int
    latest_event_id: str
    latest_request_id: str
    latest_operation: InterfaceOperation
    latest_kind: RuntimeActivityKind
    latest_status: InterfaceResponseStatus | None
    latest_stage: str
    is_active: bool
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "session_id",
            "actor_id",
            "latest_event_id",
            "latest_request_id",
            "latest_stage",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if type(self.event_count) is not int or self.event_count < 1:
            raise ValueError("event_count must be a positive integer")
        if type(self.first_sequence) is not int or self.first_sequence < 1:
            raise ValueError("first_sequence must be a positive integer")
        if type(self.last_sequence) is not int or self.last_sequence < self.first_sequence:
            raise ValueError("last_sequence must be >= first_sequence")
        if self.event_count > self.last_sequence - self.first_sequence + 1:
            raise ValueError("event_count cannot exceed the sequence span")
        if not isinstance(self.latest_operation, InterfaceOperation):
            raise TypeError("latest_operation must be an interface operation")
        if not isinstance(self.latest_kind, RuntimeActivityKind):
            raise TypeError("latest_kind must be a runtime activity kind")
        if self.latest_status is not None and not isinstance(
            self.latest_status, InterfaceResponseStatus
        ):
            raise TypeError("latest_status must be an interface response status or None")
        if type(self.is_active) is not bool:
            raise TypeError("is_active must be a bool")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", _freeze(self.metadata))


class InterfaceSessionStateProjector:
    """Maintain immutable derived state for each observed session."""

    def __init__(self) -> None:
        self._states: dict[str, InterfaceSessionState] = {}
        self._lock = RLock()

    @staticmethod
    def _active_for(kind: RuntimeActivityKind) -> bool:
        return kind is RuntimeActivityKind.REQUEST_RECEIVED

    @staticmethod
    def _metadata(event: RuntimeActivityEvent) -> Mapping[str, Any]:
        return {
            "projection_source": "runtime_activity_stream",
            "latest_event_kind": event.kind.value,
        }

    def apply(self, event: RuntimeActivityEvent) -> InterfaceSessionState:
        if type(event) is not RuntimeActivityEvent:
            raise TypeError("event must be a runtime activity event")
        with self._lock:
            previous = self._states.get(event.session_id)
            if previous is None:
                state = InterfaceSessionState(
                    session_id=event.session_id,
                    actor_id=event.actor_id,
                    event_count=1,
                    first_sequence=event.sequence,
                    last_sequence=event.sequence,
                    latest_event_id=event.event_id,
                    latest_request_id=event.request_id,
                    latest_operation=event.operation,
                    latest_kind=event.kind,
                    latest_status=event.status,
                    latest_stage=event.stage,
                    is_active=self._active_for(event.kind),
                    metadata=self._metadata(event),
                )
            else:
                if event.actor_id != previous.actor_id:
                    raise InterfaceSessionStateError("session actor identity mismatch")
                if event.sequence <= previous.last_sequence:
                    raise InterfaceSessionStateError(
                        "session event sequence must advance strictly"
                    )
                state = InterfaceSessionState(
                    session_id=previous.session_id,
                    actor_id=previous.actor_id,
                    event_count=previous.event_count + 1,
                    first_sequence=previous.first_sequence,
                    last_sequence=event.sequence,
                    latest_event_id=event.event_id,
                    latest_request_id=event.request_id,
                    latest_operation=event.operation,
                    latest_kind=event.kind,
                    latest_status=event.status,
                    latest_stage=event.stage,
                    is_active=self._active_for(event.kind),
                    metadata=self._metadata(event),
                )
            self._states[event.session_id] = state
            return state

    def state(self, session_id: str) -> InterfaceSessionState | None:
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        with self._lock:
            return self._states.get(session_id)

    def snapshot(self) -> Mapping[str, InterfaceSessionState]:
        with self._lock:
            return MappingProxyType(dict(self._states))

    def project(self, events: tuple[RuntimeActivityEvent, ...]) -> Mapping[str, InterfaceSessionState]:
        if type(events) is not tuple:
            raise TypeError("events must be an immutable tuple")
        for event in events:
            self.apply(event)
        return self.snapshot()

    @property
    def session_count(self) -> int:
        with self._lock:
            return len(self._states)

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def executes_capability(self) -> bool:
        return False

    @property
    def mutates_runtime_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
        return False

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_certainty(self) -> bool:
        return False

    @property
    def is_ai_provider(self) -> bool:
        return False


__all__ = [
    "InterfaceSessionStateError",
    "InterfaceSessionState",
    "InterfaceSessionStateProjector",
]
