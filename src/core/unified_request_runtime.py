"""M12.1 unified provider-neutral request entrypoint.

M12.1 connects the completed interface request boundary to the existing JARVIS
core without creating a second semantic, policy, or authorization path.

CS1 additionally composes the existing Phase 6-9 advisory cognition chain
before the core request processor. The cognition result is observational
metadata; it does not authorize or execute the downstream request.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.core.canonical_cognitive_runtime import CanonicalCognitiveRuntime
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
                "authority_granted": False,
                "authorization_granted": False,
                "execution_requested": False,
            },
        )


class UnifiedRequestRuntime:
    """Route one normalized JARVISRequest through cognition and JARVIS core."""

    def __init__(
        self,
        processor: JARVISProcessor,
        cognitive_runtime: CanonicalCognitiveRuntime | None = None,
    ) -> None:
        if not hasattr(processor, "ask") or not callable(processor.ask):
            raise TypeError("processor must provide a callable ask(query) method")
        if cognitive_runtime is not None and not isinstance(cognitive_runtime, CanonicalCognitiveRuntime):
            raise TypeError("cognitive_runtime must be a CanonicalCognitiveRuntime")
        self._processor = processor
        self._cognitive_runtime = cognitive_runtime or CanonicalCognitiveRuntime()

    def process(self, request: JARVISRequest) -> UnifiedRequestResult:
        if not isinstance(request, JARVISRequest):
            raise TypeError("request must be a JARVISRequest")

        # The canonical JARVIS core now owns cognition for task execution.
        # Keep the historical sidecar only for processors that do not expose
        # the integrated cognitive runtime, avoiding duplicate cognition when
        # this compatibility facade wraps the live JARVIS processor.
        cognitive_result = None
        integrated_cognitive_runtime = getattr(self._processor, "cognitive_runtime", None)
        if (
            integrated_cognitive_runtime is None
            and not request.content.lstrip().startswith("/")
        ):
            cognitive_result = self._cognitive_runtime.run(
                request.content,
                request_id=request.request_id,
                context_ids=tuple(
                    item
                    for item in (request.session_id, request.source_request_id)
                    if item is not None
                ),
                metadata={
                    "channel": request.channel.value,
                    "interface_metadata": dict(request.metadata),
                },
            )

        core_response = self._processor.ask(request.content)
        if cognitive_result is not None:
            response_metadata = getattr(core_response, "metadata", None)
            if isinstance(response_metadata, dict):
                response_metadata["canonical_cognition"] = cognitive_result.to_context()

        return UnifiedRequestResult(
            request_id=request.request_id,
            session_id=request.session_id,
            core_response=core_response,
        )
