"""M12.5 event-integrated system runtime.

This module composes the verified SystemRuntime with the existing interface
EventRuntime. Events describe transport progress only; they do not interpret
intent, grant authority, authorize execution, select providers, or mutate
policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from uuid import uuid4

from src.core.system_runtime import SystemRuntime
from src.core.session_runtime import SessionRuntimeResult
from src.interface.boundary import InterfaceChannel, InterfaceRequest, InterfaceResponse
from src.interface.events import InterfaceEventRuntime, InterfaceEventStream


@dataclass(frozen=True)
class EventIntegratedResult:
    """Canonical runtime result paired with its immutable interface event stream."""

    result: SessionRuntimeResult
    events: InterfaceEventStream

    def to_interface_response(self) -> InterfaceResponse:
        return self.result.to_interface_response()


class EventIntegratedRuntime:
    """Add transport lifecycle events around the existing system runtime."""

    def __init__(
        self,
        system_runtime: SystemRuntime,
        *,
        event_runtime: InterfaceEventRuntime | None = None,
        event_id_factory: Callable[[], str] | None = None,
    ) -> None:
        if not isinstance(system_runtime, SystemRuntime):
            raise TypeError("system_runtime must be a SystemRuntime")
        if event_runtime is not None and not isinstance(event_runtime, InterfaceEventRuntime):
            raise TypeError("event_runtime must be an InterfaceEventRuntime")
        if event_id_factory is not None and not callable(event_id_factory):
            raise TypeError("event_id_factory must be callable or None")

        self._system_runtime = system_runtime
        self._event_runtime = event_runtime or InterfaceEventRuntime()
        self._event_id_factory = event_id_factory or (lambda: str(uuid4()))

    @property
    def system_runtime(self) -> SystemRuntime:
        return self._system_runtime

    @property
    def event_runtime(self) -> InterfaceEventRuntime:
        return self._event_runtime

    def receive(
        self,
        *,
        request_id: str,
        channel: InterfaceChannel,
        content: str,
        session_id: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> EventIntegratedResult:
        """Create an interface request, emit lifecycle events, and invoke the system runtime."""
        request = InterfaceRequest(
            request_id=request_id,
            channel=channel,
            content=content,
            session_id=session_id,
            metadata={} if metadata is None else metadata,
        )
        return self.process(request)

    def process(self, request: InterfaceRequest) -> EventIntegratedResult:
        """Run one interface request through system runtime with event lifecycle reporting."""
        if not isinstance(request, InterfaceRequest):
            raise TypeError("request must be an InterfaceRequest")

        stream = self._event_runtime.start(
            request_id=request.request_id,
            event_id=self._event_id_factory(),
            session_id=request.session_id,
        )

        try:
            result = self._system_runtime.process(request)
            response = self._system_runtime.respond(result)
            stream = self._event_runtime.complete(
                stream,
                event_id=self._event_id_factory(),
                content=response.content,
                metadata={"integration": "M12.5"},
            )
            return EventIntegratedResult(result=result, events=stream)
        except Exception as exc:
            stream = self._event_runtime.fail(
                stream,
                event_id=self._event_id_factory(),
                content=f"{type(exc).__name__}: {exc}",
                metadata={"integration": "M12.5"},
            )
            raise

    def respond(self, result: EventIntegratedResult) -> InterfaceResponse:
        """Project only the underlying canonical response; events remain transport history."""
        if not isinstance(result, EventIntegratedResult):
            raise TypeError("result must be an EventIntegratedResult")
        return result.to_interface_response()


__all__ = ["EventIntegratedResult", "EventIntegratedRuntime"]
