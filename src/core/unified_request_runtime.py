"""M12.1 unified provider-neutral request entrypoint.

M12.1 connects the completed interface request boundary to the existing JARVIS
core without creating a second semantic, policy, or authorization path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.interface.boundary import InterfaceResponse
from src.interface.request import JARVISRequest


class JARVISProcessor(Protocol):
    """Minimal core contract required by the unified runtime."""

    def ask(self, query: str) -> object:
        """Process normalized user content through the existing JARVIS core."""


@dataclass(frozen=True)
class UnifiedRequestResult:
    """Immutable result preserving interface correlation around the core result."""

    request_id: str
    session_id: str | None
    core_response: object

    def to_interface_response(self) -> InterfaceResponse:
        content = getattr(self.core_response, "content", None)
        if not isinstance(content, str) or not content.strip():
            raise ValueError("core response must expose non-empty string content")
        metadata = getattr(self.core_response, "metadata", {})
        if not isinstance(metadata, dict):
            try:
                metadata = dict(metadata)
            except (TypeError, ValueError) as exc:
                raise TypeError("core response metadata must be mapping-compatible") from exc
        return InterfaceResponse(
            request_id=self.request_id,
            content=content,
            metadata={
                **metadata,
                "session_id": self.session_id,
                "integration": "M12.1",
            },
        )


class UnifiedRequestRuntime:
    """Route one normalized JARVISRequest into the existing JARVIS core."""

    def __init__(self, processor: JARVISProcessor) -> None:
        if not hasattr(processor, "ask") or not callable(processor.ask):
            raise TypeError("processor must provide a callable ask(query) method")
        self._processor = processor

    def process(self, request: JARVISRequest) -> UnifiedRequestResult:
        if not isinstance(request, JARVISRequest):
            raise TypeError("request must be a JARVISRequest")

        core_response = self._processor.ask(request.content)
        return UnifiedRequestResult(
            request_id=request.request_id,
            session_id=request.session_id,
            core_response=core_response,
        )
