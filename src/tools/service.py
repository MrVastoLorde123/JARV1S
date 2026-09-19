"""Orchestrates a single tool invocation.

ToolService is deliberately thin. It performs exactly the five
steps described in the architecture doc and nothing else:

    1. validate the request
    2. resolve the tool
    3. validate tool availability
    4. invoke the handler
    5. validate the returned result

It never talks to a database, never makes an AI decision about
whether a tool should run, and never contains logic specific to any
individual tool. Those concerns belong elsewhere (JARVIS core, the
future policy/confirmation layer, and the tool handlers themselves,
respectively).

Optional external observation/verification evidence is an additive
capability contract. The service exposes provider methods for the
plan-step adapter to consume without changing ToolResult semantics.
"""

from __future__ import annotations

from .errors import InvalidRequestError, InvalidResultError, UnknownToolError
from .models import ToolError, ToolRequest, ToolResult
from .outcome import ExternalObservation, ExternalVerification
from .protocol import (
    ToolObservationProvider,
    ToolVerificationProvider,
    ToolVerificationBindingProvider,
)
from .registry import ToolRegistry, normalize_name


class ToolService:
    """Validates, resolves, and invokes tools via a ToolRegistry."""

    def __init__(self, registry: ToolRegistry) -> None:
        if not isinstance(registry, ToolRegistry):
            raise TypeError(
                f"ToolService.registry must be a ToolRegistry, got {type(registry).__name__}"
            )
        self._registry = registry

    def invoke(self, request: ToolRequest) -> ToolResult:
        """Run one tool invocation end to end."""
        self._validate_request(request)

        handler = self._registry.get(request.tool_name)

        # Availability is currently synonymous with "resolved without
        # raising UnknownToolError". This is a distinct step from
        # resolution so future availability concerns have a clear place.
        self._validate_availability(request)

        result = self._invoke_handler(handler, request)

        self._validate_result(result, request)
        return result

    def provide_external_observation(
        self,
        request: ToolRequest,
        result: ToolResult,
    ) -> ExternalObservation | None:
        """Expose optional typed observation evidence from the capability."""
        self._validate_request(request)
        if not isinstance(result, ToolResult):
            raise InvalidResultError(
                f"ToolService evidence expects ToolResult, got {type(result).__name__}"
            )

        handler = self._registry.get(request.tool_name)
        if not isinstance(handler, ToolObservationProvider):
            return None

        return handler.provide_external_observation(request, result)

    def provide_external_verification(
        self,
        request: ToolRequest,
        result: ToolResult,
        observation: ExternalObservation,
    ) -> ExternalVerification | None:
        """Expose optional typed verification evidence from the capability."""
        self._validate_request(request)
        if not isinstance(result, ToolResult):
            raise InvalidResultError(
                f"ToolService evidence expects ToolResult, got {type(result).__name__}"
            )
        if not isinstance(observation, ExternalObservation):
            raise TypeError("observation must be an ExternalObservation")

        handler = self._registry.get(request.tool_name)
        if not isinstance(handler, ToolVerificationProvider):
            return None

        return handler.provide_external_verification(
            request,
            result,
            observation,
        )

    def admissible_verification_sources(
        self,
        request: ToolRequest,
    ) -> tuple[str, ...]:
        """Return the registered capability's deterministic verification allowlist."""
        self._validate_request(request)
        handler = self._registry.get(request.tool_name)
        definition = handler.definition()
        return definition.admissible_verification_sources

    def verification_source_id(
        self,
        request: ToolRequest,
    ) -> str | None:
        """Return the registry-bound verifier identity for this capability."""
        self._validate_request(request)
        return self._registry.verification_source_id(request.tool_name)

    def _validate_request(self, request: ToolRequest) -> None:
        if not isinstance(request, ToolRequest):
            raise InvalidRequestError(
                f"ToolService.invoke expects a ToolRequest, got {type(request).__name__}"
            )

    def _validate_availability(self, request: ToolRequest) -> None:
        if not self._registry.has(request.tool_name):
            raise UnknownToolError(f"No tool registered under the name '{request.tool_name}'")

    def _invoke_handler(self, handler, request: ToolRequest) -> ToolResult:
        try:
            return handler.execute(request)
        except Exception as exc:  # noqa: BLE001 - intentionally broad
            return ToolResult(
                success=False,
                tool_name=request.tool_name,
                error=ToolError(
                    code="tool_execution_error",
                    message=str(exc) or exc.__class__.__name__,
                    details={"exception_type": exc.__class__.__name__},
                ),
                invocation_id=request.invocation_id,
            )

    def _validate_result(self, result: ToolResult, request: ToolRequest) -> None:
        if not isinstance(result, ToolResult):
            raise InvalidResultError(
                f"Tool '{request.tool_name}' handler returned "
                f"{type(result).__name__}, expected ToolResult"
            )
        if normalize_name(result.tool_name) != normalize_name(request.tool_name):
            raise InvalidResultError(
                f"Tool '{request.tool_name}' handler returned a result for "
                f"'{result.tool_name}' instead"
            )
        if result.invocation_id != request.invocation_id:
            raise InvalidResultError(
                f"Tool '{request.tool_name}' handler returned invocation_id "
                f"'{result.invocation_id}' for request invocation_id '{request.invocation_id}'"
            )
