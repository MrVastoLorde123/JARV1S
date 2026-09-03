"""M12.2 session-to-core binding runtime.

This module binds an interface JARVISRequest session identity to an existing
JARVIS processor. It owns routing of session identity only; it does not
interpret intent, evaluate policy, authorize execution, or create a second
semantic path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from src.core.unified_request_runtime import UnifiedRequestResult, UnifiedRequestRuntime
from src.interface.request import JARVISRequest


class SessionProcessor(Protocol):
    """Minimal processor contract required by the session runtime."""

    def ask(self, query: str) -> object: ...


class SessionProcessorFactory(Protocol):
    """Factory for a processor bound to one persistent conversation/session."""

    def __call__(self, session_id: str) -> SessionProcessor: ...


@dataclass(frozen=True)
class SessionRuntimeResult:
    """Result of processing a request through its bound session processor."""

    session_id: str | None
    result: UnifiedRequestResult

    def to_interface_response(self):
        """Project the underlying core result back to the interface boundary."""
        return self.result.to_interface_response()


class SessionRuntime:
    """Bind request sessions to existing JARVIS processors."""

    def __init__(
        self,
        default_processor: SessionProcessor,
        session_processor_factory: SessionProcessorFactory | None = None,
    ) -> None:
        if not callable(getattr(default_processor, "ask", None)):
            raise TypeError("default_processor must provide an ask(query) method")
        if session_processor_factory is not None and not callable(session_processor_factory):
            raise TypeError("session_processor_factory must be callable or None")

        self._default_processor = default_processor
        self._session_processor_factory = session_processor_factory
        self._runtimes: dict[str, UnifiedRequestRuntime] = {}

    def process(self, request: JARVISRequest) -> SessionRuntimeResult:
        """Process one normalized request through the session-bound core."""
        if not isinstance(request, JARVISRequest):
            raise TypeError("request must be a JARVISRequest")

        runtime = self._runtime_for(request.session_id)
        result = runtime.process(request)
        return SessionRuntimeResult(
            session_id=request.session_id,
            result=result,
        )

    def _runtime_for(self, session_id: str | None) -> UnifiedRequestRuntime:
        if session_id is None:
            return UnifiedRequestRuntime(self._default_processor)

        runtime = self._runtimes.get(session_id)
        if runtime is not None:
            return runtime

        if self._session_processor_factory is None:
            processor = self._default_processor
        else:
            processor = self._session_processor_factory(session_id)
            if not callable(getattr(processor, "ask", None)):
                raise TypeError("session processor must provide an ask(query) method")

        runtime = UnifiedRequestRuntime(processor)
        self._runtimes[session_id] = runtime
        return runtime

    def session_count(self) -> int:
        """Return the number of session-bound runtimes currently cached."""
        return len(self._runtimes)

    def clear_session(self, session_id: str) -> None:
        """Forget only the in-memory binding; persistent conversation state is untouched."""
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        self._runtimes.pop(session_id.strip(), None)

    def clear_all_sessions(self) -> None:
        """Forget all in-memory bindings; no core or authority state is mutated."""
        self._runtimes.clear()
