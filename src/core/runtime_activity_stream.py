"""M25.3: immutable runtime activity events and a bounded observable stream."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from threading import RLock
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Protocol

from src.core.interface_backend import (
    InterfaceOperation,
    InterfaceRequest,
    InterfaceResponse,
    InterfaceResponseStatus,
)


class RuntimeActivityError(RuntimeError):
    """Raised when runtime activity cannot be recorded safely."""


class RuntimeActivityKind(str, Enum):
    REQUEST_RECEIVED = "REQUEST_RECEIVED"
    RESPONSE_EMITTED = "RESPONSE_EMITTED"
    REQUEST_REJECTED = "REQUEST_REJECTED"
    REQUEST_FAILED = "REQUEST_FAILED"


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
class RuntimeActivityEvent:
    """Immutable observation of one runtime/interface transition."""

    event_id: str
    sequence: int
    session_id: str
    actor_id: str
    request_id: str
    operation: InterfaceOperation
    kind: RuntimeActivityKind
    status: InterfaceResponseStatus | None
    stage: str
    summary: str
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "event_id", "session_id", "actor_id", "request_id", "stage", "summary"
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if type(self.sequence) is not int or self.sequence < 1:
            raise ValueError("sequence must be a positive integer")
        if not isinstance(self.operation, InterfaceOperation):
            raise TypeError("operation must be an interface operation")
        if not isinstance(self.kind, RuntimeActivityKind):
            raise TypeError("kind must be a runtime activity kind")
        if self.status is not None and not isinstance(self.status, InterfaceResponseStatus):
            raise TypeError("status must be an interface response status or None")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", _freeze(self.metadata))


class RuntimeActivitySink(Protocol):
    """Write-only seam for runtime activity observers."""

    def publish(self, event: RuntimeActivityEvent) -> None:
        ...


class RuntimeActivityStream:
    """Thread-safe append-only in-memory activity stream with immutable snapshots."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._events: list[RuntimeActivityEvent] = []

    def publish(self, event: RuntimeActivityEvent) -> None:
        if type(event) is not RuntimeActivityEvent:
            raise TypeError("event must be a runtime activity event")
        with self._lock:
            expected_sequence = len(self._events) + 1
            if event.sequence != expected_sequence:
                raise RuntimeActivityError("event sequence must be contiguous")
            self._events.append(event)

    def snapshot(self) -> tuple[RuntimeActivityEvent, ...]:
        with self._lock:
            return tuple(self._events)

    def since(self, sequence: int) -> tuple[RuntimeActivityEvent, ...]:
        if type(sequence) is not int or sequence < 0:
            raise ValueError("sequence must be a non-negative integer")
        with self._lock:
            return tuple(event for event in self._events if event.sequence > sequence)

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._events)


class InterfaceRuntimeActivityRecorder:
    """Observe M25.1 requests/responses without changing their semantics."""

    def __init__(self, stream: RuntimeActivitySink) -> None:
        if stream is None or not callable(getattr(stream, "publish", None)):
            raise TypeError("stream must provide callable publish")
        self._stream = stream
        self._sequence = 0
        self._lock = RLock()

    def record_request(self, request: InterfaceRequest) -> RuntimeActivityEvent:
        if type(request) is not InterfaceRequest:
            raise TypeError("request must be an interface request")
        event = self._next_event(
            session_id=request.session_id,
            actor_id=request.actor_id,
            request_id=request.request_id,
            operation=request.operation,
            kind=RuntimeActivityKind.REQUEST_RECEIVED,
            status=None,
            stage="INTERFACE_BACKEND",
            summary=f"interface request received for {request.operation.value}",
            metadata={"event_source": "interface_backend"},
        )
        self._stream.publish(event)
        return event

    def record_response(self, request: InterfaceRequest, response: InterfaceResponse) -> RuntimeActivityEvent:
        if type(request) is not InterfaceRequest:
            raise TypeError("request must be an interface request")
        if type(response) is not InterfaceResponse:
            raise TypeError("response must be an interface response")
        if response.request_id != request.request_id or response.operation is not request.operation:
            raise RuntimeActivityError("response identity does not match request")
        kind = (
            RuntimeActivityKind.RESPONSE_EMITTED
            if response.status is InterfaceResponseStatus.ACCEPTED
            else RuntimeActivityKind.REQUEST_REJECTED
            if response.status is InterfaceResponseStatus.REJECTED
            else RuntimeActivityKind.REQUEST_FAILED
        )
        stage = str(response.metadata.get("artifact_type", request.operation.value))
        event = self._next_event(
            session_id=request.session_id,
            actor_id=request.actor_id,
            request_id=request.request_id,
            operation=request.operation,
            kind=kind,
            status=response.status,
            stage=stage,
            summary=f"interface response {response.status.value.lower()} for {request.operation.value}",
            metadata={"event_source": "interface_backend", **dict(response.metadata)},
        )
        self._stream.publish(event)
        return event

    def _next_event(
        self,
        *,
        session_id: str,
        actor_id: str,
        request_id: str,
        operation: InterfaceOperation,
        kind: RuntimeActivityKind,
        status: InterfaceResponseStatus | None,
        stage: str,
        summary: str,
        metadata: Mapping[str, Any],
    ) -> RuntimeActivityEvent:
        with self._lock:
            self._sequence += 1
            return RuntimeActivityEvent(
                event_id=f"runtime-event-{self._sequence}",
                sequence=self._sequence,
                session_id=session_id,
                actor_id=actor_id,
                request_id=request_id,
                operation=operation,
                kind=kind,
                status=status,
                stage=stage,
                summary=summary,
                metadata=metadata,
            )


class ObservableInterfaceOrchestration:
    """Wrap any interface orchestration port with observational activity recording."""

    def __init__(self, orchestration: Any, recorder: InterfaceRuntimeActivityRecorder) -> None:
        if orchestration is None or not callable(getattr(orchestration, "dispatch", None)):
            raise TypeError("orchestration must provide callable dispatch")
        if type(recorder) is not InterfaceRuntimeActivityRecorder:
            raise TypeError("recorder must be an interface runtime activity recorder")
        self._orchestration = orchestration
        self._recorder = recorder

    def dispatch(self, request: InterfaceRequest) -> InterfaceResponse:
        if type(request) is not InterfaceRequest:
            raise TypeError("request must be an interface request")
        self._recorder.record_request(request)
        try:
            response = self._orchestration.dispatch(request)
        except Exception:
            self._recorder.record_response(
                request,
                InterfaceResponse(
                    request_id=request.request_id,
                    operation=request.operation,
                    status=InterfaceResponseStatus.FAILED,
                    payload={},
                    metadata={"event_source": "interface_backend", "exception": "orchestration"},
                ),
            )
            raise
        self._recorder.record_response(request, response)
        return response


__all__ = [
    "RuntimeActivityError",
    "RuntimeActivityKind",
    "RuntimeActivityEvent",
    "RuntimeActivitySink",
    "RuntimeActivityStream",
    "InterfaceRuntimeActivityRecorder",
    "ObservableInterfaceOrchestration",
]
