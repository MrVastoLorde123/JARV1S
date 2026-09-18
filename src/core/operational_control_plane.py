"""OPS-06: observational operational control plane for the live JARVIS runtime.

The control plane projects already-observed interface activity into inspectable
operation/session state. It does not interpret intent, authorize execution,
execute capabilities, mutate policy, establish truth, or establish certainty.
"""

from __future__ import annotations

from typing import Mapping

from src.core.interface_backend import (
    InterfaceOperation,
    InterfaceRequest as BackendInterfaceRequest,
    InterfaceResponse as BackendInterfaceResponse,
    InterfaceResponseStatus,
)
from src.interface.boundary import InterfaceRequest, InterfaceResponse
from src.core.interface_session_state import InterfaceSessionState, InterfaceSessionStateProjector
from src.core.runtime_activity_stream import (
    InterfaceRuntimeActivityRecorder,
    RuntimeActivityEvent,
    RuntimeActivityStream,
)


class OperationalControlPlane:
    """Observe and project live runtime activity without becoming an authority."""

    def __init__(
        self,
        *,
        activity_stream: RuntimeActivityStream | None = None,
        session_projector: InterfaceSessionStateProjector | None = None,
        recorder: InterfaceRuntimeActivityRecorder | None = None,
    ) -> None:
        self._activity_stream = activity_stream or RuntimeActivityStream()
        self._session_projector = session_projector or InterfaceSessionStateProjector()
        self._recorder = recorder or InterfaceRuntimeActivityRecorder(self._activity_stream)

        if type(self._activity_stream) is not RuntimeActivityStream:
            raise TypeError("activity_stream must be a RuntimeActivityStream")
        if type(self._session_projector) is not InterfaceSessionStateProjector:
            raise TypeError("session_projector must be an InterfaceSessionStateProjector")
        if type(self._recorder) is not InterfaceRuntimeActivityRecorder:
            raise TypeError("recorder must be an InterfaceRuntimeActivityRecorder")

    @property
    def activity_stream(self) -> RuntimeActivityStream:
        return self._activity_stream

    @property
    def session_projector(self) -> InterfaceSessionStateProjector:
        return self._session_projector

    @staticmethod
    def _backend_request(request: InterfaceRequest) -> BackendInterfaceRequest:
        session_id = request.session_id or "default"
        actor_id = str(request.metadata.get("actor_id", "interface"))
        return BackendInterfaceRequest(
            request_id=request.request_id,
            session_id=session_id,
            actor_id=actor_id,
            operation=InterfaceOperation.STATUS,
            payload={
                "channel": request.channel.value,
                "content": request.content,
            },
            metadata={
                **dict(request.metadata),
                "operational_observation": True,
            },
        )

    @staticmethod
    def _backend_response(
        request: InterfaceRequest,
        response: InterfaceResponse,
        *,
        status: InterfaceResponseStatus,
        error: str | None = None,
    ) -> BackendInterfaceResponse:
        metadata = dict(response.metadata)
        if error is not None:
            metadata["error_type"] = error
        return BackendInterfaceResponse(
            request_id=request.request_id,
            operation=InterfaceOperation.STATUS,
            status=status,
            payload={"content": response.content},
            metadata=metadata,
        )

    def record_request(self, request: InterfaceRequest) -> RuntimeActivityEvent:
        backend_request = self._backend_request(request)
        event = self._recorder.record_request(backend_request)
        self._session_projector.apply(event)
        return event

    def record_response(
        self,
        request: InterfaceRequest,
        response: InterfaceResponse,
    ) -> RuntimeActivityEvent:
        backend_request = self._backend_request(request)
        backend_response = self._backend_response(
            request,
            response,
            status=InterfaceResponseStatus.ACCEPTED,
        )
        event = self._recorder.record_response(
            backend_request,
            backend_response,
        )
        self._session_projector.apply(event)
        return event

    def record_failure(
        self,
        request: InterfaceRequest,
        exc: BaseException,
    ) -> RuntimeActivityEvent:
        backend_request = self._backend_request(request)
        backend_response = BackendInterfaceResponse(
            request_id=request.request_id,
            operation=InterfaceOperation.STATUS,
            status=InterfaceResponseStatus.FAILED,
            payload={},
            metadata={
                "stage": "RUNTIME",
                "error_type": type(exc).__name__,
                "operational_observation": True,
            },
        )
        event = self._recorder.record_response(
            backend_request,
            backend_response,
        )
        self._session_projector.apply(event)
        return event

    def current_operation(self, request_id: str) -> RuntimeActivityEvent | None:
        if not isinstance(request_id, str) or not request_id.strip():
            raise ValueError("request_id must be a non-empty string")
        matching = [
            event
            for event in self._activity_stream.snapshot()
            if event.request_id == request_id
        ]
        return matching[-1] if matching else None

    def events(
        self,
        *,
        since_sequence: int = 0,
        limit: int | None = None,
    ) -> tuple[RuntimeActivityEvent, ...]:
        events = self._activity_stream.since(since_sequence)
        if limit is None:
            return events
        if type(limit) is not int or limit < 0:
            raise ValueError("limit must be a non-negative integer or None")
        if limit == 0:
            return ()
        return events[-limit:]

    def session_state(self, session_id: str) -> InterfaceSessionState | None:
        return self._session_projector.state(session_id)

    def session_states(self) -> Mapping[str, InterfaceSessionState]:
        return self._session_projector.snapshot()

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


__all__ = ["OperationalControlPlane"]
