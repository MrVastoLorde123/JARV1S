"""M12.3 application-facing system runtime facade.

The facade composes the already-bounded interface, request, session, and core
runtimes into one entrypoint. It owns composition only; semantic interpretation,
policy, authorization, and execution remain delegated to the existing JARVIS
core and its established boundaries.
"""

from __future__ import annotations

from typing import Mapping

from src.core.jarvis import JARVIS
from src.core.session_runtime import SessionRuntime, SessionRuntimeResult
from src.interface.boundary import InterfaceBoundary, InterfaceChannel, InterfaceRequest
from src.interface.request import InterfaceRequestBridge


class SystemRuntime:
    """Compose the external interface path into the existing JARVIS system."""

    def __init__(
        self,
        processor: JARVIS,
        *,
        interface_boundary: InterfaceBoundary | None = None,
        request_bridge: InterfaceRequestBridge | None = None,
        session_runtime: SessionRuntime | None = None,
    ) -> None:
        if not callable(getattr(processor, "ask", None)):
            raise TypeError("processor must provide an ask(query) method")
        self._processor = processor
        self._interface_boundary = interface_boundary or InterfaceBoundary()
        self._request_bridge = request_bridge or InterfaceRequestBridge()
        self._session_runtime = session_runtime or SessionRuntime(processor)

    @property
    def session_runtime(self) -> SessionRuntime:
        """Expose the composed session runtime without exposing new authority."""
        return self._session_runtime

    def receive(
        self,
        *,
        request_id: str,
        channel: InterfaceChannel,
        content: str,
        session_id: str | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> SessionRuntimeResult:
        """Create an interface envelope and route it through the canonical path."""
        interface_request = self._interface_boundary.request(
            request_id=request_id,
            channel=channel,
            content=content,
            session_id=session_id,
            metadata=metadata,
        )
        return self.process(interface_request)

    def process(self, request: InterfaceRequest) -> SessionRuntimeResult:
        """Route an existing interface request through bridge → session → core."""
        if not isinstance(request, InterfaceRequest):
            raise TypeError("request must be an InterfaceRequest")
        jarvis_request = self._request_bridge.to_jarvis_request(request)
        return self._session_runtime.process(jarvis_request)

    def respond(self, result: SessionRuntimeResult):
        """Project a canonical runtime result back to the interface boundary."""
        if not isinstance(result, SessionRuntimeResult):
            raise TypeError("result must be a SessionRuntimeResult")
        return result.to_interface_response()


__all__ = ["SystemRuntime"]
