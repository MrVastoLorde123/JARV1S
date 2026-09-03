"""M11.4 provider-neutral streaming and event experience boundary.

Events describe observable interface progress without interpreting intent,
creating authority, authorizing execution, or selecting an AI provider.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class InterfaceEventKind(str, Enum):
    """Transport-level lifecycle events exposed to interface clients."""

    RESPONSE_STARTED = "RESPONSE_STARTED"
    CONTENT_DELTA = "CONTENT_DELTA"
    RESPONSE_COMPLETED = "RESPONSE_COMPLETED"
    RESPONSE_FAILED = "RESPONSE_FAILED"


@dataclass(frozen=True)
class InterfaceEvent:
    """Immutable, ordered, provider-neutral event for one JARVIS request."""

    event_id: str
    request_id: str
    kind: InterfaceEventKind
    sequence: int
    session_id: str | None = None
    content: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("event_id", "request_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.kind, InterfaceEventKind):
            try:
                object.__setattr__(self, "kind", InterfaceEventKind(self.kind))
            except (TypeError, ValueError) as exc:
                raise TypeError("kind must be an InterfaceEventKind") from exc
        if (
            not isinstance(self.sequence, int)
            or isinstance(self.sequence, bool)
            or self.sequence <= 0
        ):
            raise ValueError("sequence must be a positive integer")
        if self.session_id is not None and (
            not isinstance(self.session_id, str) or not self.session_id.strip()
        ):
            raise ValueError("session_id must be a non-empty string or None")
        if not isinstance(self.content, str):
            raise TypeError("content must be a string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        object.__setattr__(self, "event_id", self.event_id.strip())
        object.__setattr__(self, "request_id", self.request_id.strip())
        if self.session_id is not None:
            object.__setattr__(self, "session_id", self.session_id.strip())
        object.__setattr__(self, "content", self.content)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

        if self.kind is InterfaceEventKind.RESPONSE_STARTED and self.content:
            raise ValueError("RESPONSE_STARTED cannot carry content")
        if self.kind is InterfaceEventKind.CONTENT_DELTA and not self.content:
            raise ValueError("CONTENT_DELTA must carry non-empty content")
        if self.kind is InterfaceEventKind.RESPONSE_COMPLETED and not self.content:
            raise ValueError("RESPONSE_COMPLETED must carry non-empty content")
        if self.kind is InterfaceEventKind.RESPONSE_FAILED and not self.content:
            raise ValueError("RESPONSE_FAILED must carry a non-empty failure description")

    @property
    def terminal(self) -> bool:
        return self.kind in {
            InterfaceEventKind.RESPONSE_COMPLETED,
            InterfaceEventKind.RESPONSE_FAILED,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "kind": self.kind.value,
            "sequence": self.sequence,
            "content": self.content,
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
class InterfaceEventStream:
    """Immutable ordered event history for a single request."""

    request_id: str
    session_id: str | None = None
    events: tuple[InterfaceEvent, ...] = ()
    max_events: int = 256

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str) or not self.request_id.strip():
            raise ValueError("request_id must be a non-empty string")
        if self.session_id is not None and (
            not isinstance(self.session_id, str) or not self.session_id.strip()
        ):
            raise ValueError("session_id must be a non-empty string or None")
        if not isinstance(self.events, tuple):
            raise TypeError("events must be a tuple")
        if (
            not isinstance(self.max_events, int)
            or isinstance(self.max_events, bool)
            or self.max_events <= 0
        ):
            raise ValueError("max_events must be a positive integer")
        if len(self.events) > self.max_events:
            raise ValueError("event history exceeds max_events")

        expected_sequence = 1
        event_ids: set[str] = set()
        terminal_seen = False
        for event in self.events:
            if not isinstance(event, InterfaceEvent):
                raise TypeError("events must contain InterfaceEvent values")
            if event.request_id != self.request_id:
                raise ValueError("event request_id must match the stream")
            if event.session_id not in (None, self.session_id):
                raise ValueError("event session_id must match the stream")
            if event.sequence != expected_sequence:
                raise ValueError("event sequences must be contiguous from 1")
            if event.event_id in event_ids:
                raise ValueError("event_id must be unique within the stream")
            if terminal_seen:
                raise ValueError("terminal events must be the final event")
            event_ids.add(event.event_id)
            terminal_seen = event.terminal
            expected_sequence += 1

        object.__setattr__(self, "request_id", self.request_id.strip())
        if self.session_id is not None:
            object.__setattr__(self, "session_id", self.session_id.strip())

    @property
    def terminal(self) -> bool:
        return bool(self.events) and self.events[-1].terminal

    @property
    def latest(self) -> InterfaceEvent | None:
        return self.events[-1] if self.events else None

    def append(self, event: InterfaceEvent) -> "InterfaceEventStream":
        if not isinstance(event, InterfaceEvent):
            raise TypeError("event must be an InterfaceEvent")
        if event.request_id != self.request_id:
            raise ValueError("event request_id must match the stream")
        if event.session_id not in (None, self.session_id):
            raise ValueError("event session_id must match the stream")
        if self.terminal:
            raise ValueError("cannot append an event after stream termination")
        if len(self.events) >= self.max_events:
            raise ValueError("stream event bound has been reached")
        expected_sequence = len(self.events) + 1
        if event.sequence != expected_sequence:
            raise ValueError("event sequence must be the next contiguous sequence")
        if any(existing.event_id == event.event_id for existing in self.events):
            raise ValueError(f"event_id '{event.event_id}' is already in the stream")
        return InterfaceEventStream(
            request_id=self.request_id,
            session_id=self.session_id,
            events=self.events + (event,),
            max_events=self.max_events,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "session_id": self.session_id,
            "events": [event.to_dict() for event in self.events],
            "max_events": self.max_events,
            "terminal": self.terminal,
            "intent_interpreted": False,
            "truth_guaranteed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


class InterfaceEventRuntime:
    """Build ordered interface events without interpreting or authorizing them."""

    def start(
        self,
        *,
        request_id: str,
        event_id: str,
        session_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        max_events: int = 256,
    ) -> InterfaceEventStream:
        stream = InterfaceEventStream(
            request_id=request_id,
            session_id=session_id,
            max_events=max_events,
        )
        return stream.append(
            InterfaceEvent(
                event_id=event_id,
                request_id=request_id,
                session_id=session_id,
                kind=InterfaceEventKind.RESPONSE_STARTED,
                sequence=1,
                metadata=metadata or {},
            )
        )

    def delta(
        self,
        stream: InterfaceEventStream,
        *,
        event_id: str,
        content: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> InterfaceEventStream:
        return stream.append(
            InterfaceEvent(
                event_id=event_id,
                request_id=stream.request_id,
                session_id=stream.session_id,
                kind=InterfaceEventKind.CONTENT_DELTA,
                sequence=len(stream.events) + 1,
                content=content,
                metadata=metadata or {},
            )
        )

    def complete(
        self,
        stream: InterfaceEventStream,
        *,
        event_id: str,
        content: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> InterfaceEventStream:
        return stream.append(
            InterfaceEvent(
                event_id=event_id,
                request_id=stream.request_id,
                session_id=stream.session_id,
                kind=InterfaceEventKind.RESPONSE_COMPLETED,
                sequence=len(stream.events) + 1,
                content=content,
                metadata=metadata or {},
            )
        )

    def fail(
        self,
        stream: InterfaceEventStream,
        *,
        event_id: str,
        content: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> InterfaceEventStream:
        return stream.append(
            InterfaceEvent(
                event_id=event_id,
                request_id=stream.request_id,
                session_id=stream.session_id,
                kind=InterfaceEventKind.RESPONSE_FAILED,
                sequence=len(stream.events) + 1,
                content=content,
                metadata=metadata or {},
            )
        )
