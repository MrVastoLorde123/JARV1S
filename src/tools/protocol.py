"""The stable contract every tool implementation must satisfy.

``ToolHandler`` is intentionally minimal: a handler describes itself
(``definition``) and executes one request (``execute``). It never
decides *whether* it should run -- that decision belongs to JARVIS
core, mediated by the (future) policy/confirmation layer. A handler
that inspects conversation state, memory, or user intent to decide
whether to act is out of architectural bounds for this layer.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import ToolDefinition, ToolRequest, ToolResult


@runtime_checkable
class ToolHandler(Protocol):
    """Structural contract for a tool implementation.

    Any object exposing these two methods with these signatures
    satisfies the contract, regardless of its base class. This keeps
    tool implementations free of a mandatory inheritance hierarchy
    while still giving the registry something concrete to validate
    against via ``isinstance``.
    """

    def definition(self) -> ToolDefinition:
        """Return this tool's static ``ToolDefinition``.

        Implementations should return a stable definition -- the same
        ``ToolDefinition`` (or an equal one) on every call. The
        registry may call this multiple times.
        """
        ...

    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute one invocation and return its ``ToolResult``.

        Implementations execute; they do not decide whether execution
        should happen. Any exception raised here is treated by
        ``ToolService`` as an execution-time failure and wrapped into
        a failed ``ToolResult`` -- handlers are not required to catch
        their own exceptions, though they may choose to for richer
        error content.
        """
        ...
