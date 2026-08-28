"""Deterministic name -> handler mapping.

The registry owns no execution logic and no tool-specific
conditionals. It only knows how to store, validate, and enumerate
handlers.
"""

from __future__ import annotations

from typing import Dict, List

from .errors import DuplicateToolError, InvalidHandlerError, UnknownToolError
from .models import ToolDefinition
from .protocol import ToolHandler


def normalize_name(name: str) -> str:
    """Normalize a tool name for lookup purposes.

    Normalization is deliberately simple and total: strip surrounding
    whitespace, lowercase. This is the single source of truth for name
    normalization -- both ``register`` and ``get`` route through it,
    so lookups are case- and whitespace-insensitive by construction.
    """
    if not isinstance(name, str):
        raise UnknownToolError(f"Tool name must be a string, got {type(name).__name__}")
    return name.strip().lower()


class ToolRegistry:
    """Maps normalized tool names to ``ToolHandler`` implementations."""

    def __init__(self) -> None:
        self._handlers: Dict[str, ToolHandler] = {}

    def register(self, handler: ToolHandler, *, replace: bool = False) -> ToolDefinition:
        """Register a handler.

        Args:
            handler: Object satisfying the ``ToolHandler`` contract.
            replace: When True, allows overwriting an existing
                registration for the same normalized name instead of
                raising ``DuplicateToolError``. Defaults to False, so
                accidental re-registration is caught by default.

        Returns:
            The handler's ``ToolDefinition``, as a convenience.

        Raises:
            InvalidHandlerError: The object does not satisfy the
                ``ToolHandler`` contract, or its ``definition()``
                does not return a ``ToolDefinition``.
            DuplicateToolError: A handler is already registered under
                the same normalized name and ``replace`` is False.
        """
        if not isinstance(handler, ToolHandler):
            raise InvalidHandlerError(
                f"{handler!r} does not satisfy the ToolHandler contract "
                "(missing or malformed definition()/execute())"
            )

        definition = handler.definition()
        if not isinstance(definition, ToolDefinition):
            raise InvalidHandlerError(
                f"{handler!r}.definition() must return a ToolDefinition, "
                f"got {type(definition).__name__}"
            )

        key = normalize_name(definition.name)
        if key in self._handlers and not replace:
            raise DuplicateToolError(
                f"A tool is already registered under the name '{definition.name}' "
                f"(normalized: '{key}')"
            )

        self._handlers[key] = handler
        return definition

    def unregister(self, name: str) -> None:
        """Remove a registered handler by name.

        Raises:
            UnknownToolError: No handler is registered under ``name``.
        """
        key = normalize_name(name)
        if key not in self._handlers:
            raise UnknownToolError(f"No tool registered under the name '{name}'")
        del self._handlers[key]

    def get(self, name: str) -> ToolHandler:
        """Look up a handler by name.

        Raises:
            UnknownToolError: No handler is registered under ``name``.
        """
        key = normalize_name(name)
        handler = self._handlers.get(key)
        if handler is None:
            raise UnknownToolError(f"No tool registered under the name '{name}'")
        return handler

    def has(self, name: str) -> bool:
        """Return whether a handler is registered under ``name``."""
        return normalize_name(name) in self._handlers

    def list_definitions(self) -> List[ToolDefinition]:
        """Return all registered tool definitions.

        Enumeration order is deterministic: sorted by normalized name.
        """
        return [
            self._handlers[key].definition()
            for key in sorted(self._handlers.keys())
        ]

    def __len__(self) -> int:
        return len(self._handlers)

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and self.has(name)
