"""Deterministic name -> handler mapping.

The registry owns no execution logic and no tool-specific conditionals.
It also owns the registration-time binding between a concrete capability
handler instance and an explicitly configured verification-source identity.
That binding is a trust anchor for the live outcome path.
"""

from __future__ import annotations

from typing import Dict, List

from .errors import (
    DuplicateToolError,
    DuplicateVerificationSourceError,
    InvalidHandlerError,
    UnknownToolError,
)
from .models import ToolDefinition
from .protocol import ToolHandler, ToolVerificationProvider


def normalize_name(name: str) -> str:
    """Normalize a tool name for lookup purposes."""
    if not isinstance(name, str):
        raise UnknownToolError(f"Tool name must be a string, got {type(name).__name__}")
    return name.strip().lower()


class ToolRegistry:
    """Maps normalized tool names to handlers and binds verifier identities."""

    def __init__(self) -> None:
        self._handlers: Dict[str, ToolHandler] = {}
        self._verification_source_bindings: Dict[int, str] = {}
        self._verification_source_owners: Dict[str, int] = {}

    def register(
        self,
        handler: ToolHandler,
        *,
        replace: bool = False,
        verification_source_id: str | None = None,
    ) -> ToolDefinition:
        """Register a handler and optionally bind its concrete verifier identity.

        verification_source_id is registration authority. A capability
        cannot make an arbitrary source identity admissible merely by emitting
        that string in verification provenance.
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

        normalized_source_id = None
        if verification_source_id is not None:
            if not isinstance(verification_source_id, str) or not verification_source_id.strip():
                raise InvalidHandlerError(
                    "verification_source_id must be a non-empty string or None"
                )
            normalized_source_id = verification_source_id.strip()
            if not isinstance(handler, ToolVerificationProvider):
                raise InvalidHandlerError(
                    "verification_source_id requires a ToolVerificationProvider handler"
                )
            if normalized_source_id not in definition.admissible_verification_sources:
                raise InvalidHandlerError(
                    "verification_source_id must be declared in "
                    "ToolDefinition.admissible_verification_sources"
                )

        key = normalize_name(definition.name)
        previous = self._handlers.get(key)
        if previous is not None and not replace:
            raise DuplicateToolError(
                f"A tool is already registered under the name '{definition.name}' "
                f"(normalized: '{key}')"
            )

        previous_source = (
            self._verification_source_bindings.get(id(previous))
            if previous is not None
            else None
        )
        if normalized_source_id is not None:
            owner = self._verification_source_owners.get(normalized_source_id)
            if owner is not None and owner != id(previous):
                raise DuplicateVerificationSourceError(
                    f"Verification source '{normalized_source_id}' is already "
                    "bound to another registered handler"
                )

        if previous is not None:
            self._verification_source_bindings.pop(id(previous), None)
            if previous_source is not None:
                self._verification_source_owners.pop(previous_source, None)

        self._handlers[key] = handler

        if normalized_source_id is not None:
            handler_identity = id(handler)
            self._verification_source_bindings[handler_identity] = normalized_source_id
            self._verification_source_owners[normalized_source_id] = handler_identity

        return definition

    def unregister(self, name: str) -> None:
        """Remove a registered tool and its verifier binding."""
        key = normalize_name(name)
        handler = self._handlers.get(key)
        if handler is None:
            raise UnknownToolError(f"No tool registered under the name '{name}'")
        source_id = self._verification_source_bindings.pop(id(handler), None)
        if source_id is not None:
            self._verification_source_owners.pop(source_id, None)
        del self._handlers[key]

    def get(self, name: str) -> ToolHandler:
        """Look up a handler by name."""
        key = normalize_name(name)
        handler = self._handlers.get(key)
        if handler is None:
            raise UnknownToolError(f"No tool registered under the name '{name}'")
        return handler

    def verification_source_id(self, name: str) -> str | None:
        """Return the registration-bound verifier identity for one capability."""
        handler = self.get(name)
        return self._verification_source_bindings.get(id(handler))

    def has(self, name: str) -> bool:
        """Return whether a tool is registered under the given name."""
        return normalize_name(name) in self._handlers

    def list_definitions(self) -> List[ToolDefinition]:
        """Return all registered tool definitions in normalized-name order."""
        return [
            self._handlers[key].definition()
            for key in sorted(self._handlers.keys())
        ]

    def __len__(self) -> int:
        return len(self._handlers)

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and self.has(name)
