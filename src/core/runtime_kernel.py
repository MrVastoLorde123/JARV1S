"""M26.1: compose the verified M25 interface stack into one runtime kernel."""
from __future__ import annotations

from typing import Callable, Mapping, TextIO

from src.core.interface_adapter import InterfaceAdapter
from src.core.interface_backend import (
    InterfaceOperation,
    InterfaceOrchestrationPort,
    SelfImprovementInterfaceBackend,
)
from src.core.interface_session_state import InterfaceSessionStateProjector
from src.core.runtime_activity_stream import (
    InterfaceRuntimeActivityRecorder,
    ObservableInterfaceOrchestration,
    RuntimeActivityStream,
)
from src.interface_surface import TerminalInterfaceSurface


class JarvisRuntimeError(RuntimeError):
    """Raised when the JARVIS runtime kernel cannot compose or operate safely."""


class JarvisRuntime:
    """Composition root for the verified M25 interface, activity, and session stack."""

    def __init__(
        self,
        *,
        orchestration: InterfaceOrchestrationPort,
        session_id: str,
        actor_id: str,
        request_id_factory: Callable[[], str] | None = None,
    ) -> None:
        if orchestration is None or not callable(getattr(orchestration, "dispatch", None)):
            raise TypeError("orchestration must provide callable dispatch")
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        if not isinstance(actor_id, str) or not actor_id.strip():
            raise ValueError("actor_id must be a non-empty string")
        if request_id_factory is not None and not callable(request_id_factory):
            raise TypeError("request_id_factory must be callable")

        self._orchestration = orchestration
        self._activity_stream = RuntimeActivityStream()
        self._activity_recorder = InterfaceRuntimeActivityRecorder(self._activity_stream)
        self._observable_orchestration = ObservableInterfaceOrchestration(
            orchestration,
            self._activity_recorder,
        )
        self._backend = SelfImprovementInterfaceBackend(self._observable_orchestration)
        self._adapter = InterfaceAdapter(self._backend)
        self._session_projector = InterfaceSessionStateProjector()
        self._surface = TerminalInterfaceSurface(
            adapter=self._adapter,
            activity_stream=self._activity_stream,
            session_projector=self._session_projector,
            session_id=session_id,
            actor_id=actor_id,
            request_id_factory=request_id_factory,
        )

    def submit(
        self,
        operation: InterfaceOperation | str,
        *,
        payload: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> Mapping[str, object]:
        """Submit one interface operation through the complete M25 runtime path."""
        return self._surface.submit(operation, payload=payload, metadata=metadata)

    def handle_line(self, line: str) -> str:
        """Handle one terminal command through the composed runtime."""
        return self._surface.handle_line(line)

    def render_status(self) -> str:
        """Return the current session projection rendered by the interface surface."""
        return self._surface.render_status()

    def render_activity(self, *, limit: int | None = None) -> str:
        """Return the current session activity rendered by the interface surface."""
        return self._surface.render_activity(limit=limit)

    def run(self, input_stream: TextIO, output_stream: TextIO) -> None:
        """Run the terminal surface using the composed runtime."""
        self._surface.run(input_stream, output_stream)

    @property
    def session_id(self) -> str:
        return self._surface.session_id

    @property
    def actor_id(self) -> str:
        return self._surface.actor_id

    @property
    def activity_stream(self) -> RuntimeActivityStream:
        return self._activity_stream

    @property
    def session_projector(self) -> InterfaceSessionStateProjector:
        return self._session_projector

    @property
    def interface_adapter(self) -> InterfaceAdapter:
        return self._adapter

    @property
    def interface_backend(self) -> SelfImprovementInterfaceBackend:
        return self._backend

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def executes_capability(self) -> bool:
        return False

    @property
    def mutates_state(self) -> bool:
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


__all__ = ["JarvisRuntimeError", "JarvisRuntime"]
