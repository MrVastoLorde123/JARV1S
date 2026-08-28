"""Orchestrates a single tool invocation.

``ToolService`` is deliberately thin. It performs exactly the five
steps described in the architecture doc and nothing else:

    1. validate the request
    2. resolve the tool
    3. validate tool availability
    4. invoke the handler
    5. validate the returned result

It never talks to a database, never makes an AI decision about
whether a tool *should* run, and never contains logic specific to any
individual tool. Those concerns belong elsewhere (JARVIS core, the
future policy/confirmation layer, and the tool handlers themselves,
respectively).

Error handling policy (see also ``errors.py``):

    * A malformed ``ToolRequest`` was already rejected by
      ``ToolRequest.__post_init__``; ``ToolService`` additionally
      guards against receiving something that isn't a ``ToolRequest``
      at all, raising ``InvalidRequestError``.
    * An unknown tool name is a structural error and raises
      ``UnknownToolError``.
    * A handler that fails the registry's contract check would have
      been rejected at *registration* time; if a handler nonetheless
      returns something other than a ``ToolResult`` (or a result for
      the wrong tool), that is treated as a handler bug and raises
      ``InvalidResultError``.
    * An exception raised *during* ``handler.execute(...)`` is treated
      as a normal (if unhappy) execution outcome and is converted into
      a failed ``ToolResult`` rather than propagated. This is the one
      case JARVIS core should expect as data, not as an exception,
      since tool execution failures (bad args, missing file, network
      error, ...) are routine.
"""

from __future__ import annotations

from .errors import InvalidRequestError, InvalidResultError, UnknownToolError
from .models import ToolError, ToolRequest, ToolResult
from .registry import ToolRegistry, normalize_name


class ToolService:
    """Validates, resolves, and invokes tools via a ``ToolRegistry``."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def invoke(self, request: ToolRequest) -> ToolResult:
        """Run one tool invocation end to end.

        Raises:
            InvalidRequestError: ``request`` is not a ``ToolRequest``.
            UnknownToolError: No handler is registered for
                ``request.tool_name``.
            InvalidResultError: The handler returned something that
                does not satisfy the ``ToolResult`` contract for this
                request.
        """
        self._validate_request(request)

        handler = self._registry.get(request.tool_name)

        # Availability is currently synonymous with "resolved without
        # raising UnknownToolError". This is a distinct step from
        # resolution so that future availability concerns (e.g. a
        # tool that is registered but temporarily disabled) have a
        # clear place to live without restructuring the pipeline.
        self._validate_availability(request)

        result = self._invoke_handler(handler, request)

        self._validate_result(result, request)
        return result

    def _validate_request(self, request: ToolRequest) -> None:
        if not isinstance(request, ToolRequest):
            raise InvalidRequestError(
                f"ToolService.invoke expects a ToolRequest, got {type(request).__name__}"
            )

    def _validate_availability(self, request: ToolRequest) -> None:
        if not self._registry.has(request.tool_name):
            # Mirrors registry.get's own check; kept as an explicit,
            # separately named step per the required pipeline shape.
            raise UnknownToolError(f"No tool registered under the name '{request.tool_name}'")

    def _invoke_handler(self, handler, request: ToolRequest) -> ToolResult:
        try:
            return handler.execute(request)
        except Exception as exc:  # noqa: BLE001 - intentionally broad: see module docstring
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
