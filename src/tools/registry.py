"""Deterministic name -> handler mapping.

The registry owns no execution logic and no tool-specific conditionals.
It also owns the registration-time binding between a concrete capability
handler and a distinct concrete verification provider identity. That binding
is the trust anchor for the live outcome path.
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
    """Maps normalized tool names to handlers and independent verifier bindings."""

    def __init__(self) -> None:
        self._handlers: Dict[str, ToolHandler] = {}
        self._verification_source_bindings: Dict[int, str] = {}
        self._verification_source_owners: Dict[str, tuple[int, int]] = {}
        self._verification_providers: Dict[int, ToolVerificationProvider] = {}
        self._verification_provider_owners: Dict[int, str] = {}

    def register(
        self,
        handler: ToolHandler,
        *,
        replace: bool = False,
        verification_source_id: str | None = None,
        verification_provider: ToolVerificationProvider | None = None,
    ) -> ToolDefinition:
        """Register a handler and optionally bind an independent verifier.

        verification_source_id and verification_provider are registration
        authority. A capability cannot make an arbitrary source identity
        admissible merely by emitting that string in verification provenance,
        and the executing handler instance cannot be its own live verifier.
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

        if verification_source_id is None and verification_provider is not None:
            raise InvalidHandlerError(
                "verification_provider requires verification_source_id"
            )

        normalized_source_id = None
        if verification_source_id is not None:
            if (
                not isinstance(verification_source_id, str)
                or not verification_source_id.strip()
            ):
                raise InvalidHandlerError(
                    "verification_source_id must be a non-empty string or None"
                )
            normalized_source_id = verification_source_id.strip()

            if not isinstance(verification_provider, ToolVerificationProvider):
                raise InvalidHandlerError(
                    "verification_source_id requires a separate "
                    "ToolVerificationProvider instance"
                )
            if verification_provider is handler:
                raise InvalidHandlerError(
                    "executor capability cannot also be its live verification provider"
                )
            if any(
                registered_handler is verification_provider
                for registered_handler in self._handlers.values()
            ):
                raise InvalidHandlerError(
                    "a concrete verification provider cannot also be a registered executor"
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

        if id(handler) in self._verification_provider_owners:
            raise InvalidHandlerError(
                "a concrete verifier provider cannot also be registered as an executor"
            )

        previous_source = (
            self._verification_source_bindings.get(id(previous))
            if previous is not None
            else None
        )
        previous_provider = (
            self._verification_providers.get(id(previous))
            if previous is not None
            else None
        )

        if normalized_source_id is not None:
            source_owner = self._verification_source_owners.get(normalized_source_id)
            if source_owner is not None and source_owner[0] != id(previous):
                raise DuplicateVerificationSourceError(
                    f"Verification source '{normalized_source_id}' is already "
                    "bound to another registered handler"
                )

            provider_identity = id(verification_provider)
            provider_owner = self._verification_provider_owners.get(provider_identity)
            if (
                provider_owner is not None
                and provider_owner != normalized_source_id
            ):
                raise DuplicateVerificationSourceError(
                    "the concrete verification provider instance is already "
                    "bound to another verification source"
                )

        if previous is not None:
            self._verification_source_bindings.pop(id(previous), None)
            if previous_source is not None:
                self._verification_source_owners.pop(previous_source, None)
            if previous_provider is not None:
                previous_provider_identity = id(previous_provider)
                self._verification_providers.pop(id(previous), None)
                self._verification_provider_owners.pop(
                    previous_provider_identity,
                    None,
                )

        self._handlers[key] = handler

        if normalized_source_id is not None:
            assert verification_provider is not None
            handler_identity = id(handler)
            provider_identity = id(verification_provider)
            self._verification_source_bindings[handler_identity] = normalized_source_id
            self._verification_source_owners[normalized_source_id] = (
                handler_identity,
                provider_identity,
            )
            self._verification_providers[handler_identity] = verification_provider
            self._verification_provider_owners[provider_identity] = normalized_source_id

        return definition

    def unregister(self, name: str) -> None:
        """Remove a registered tool and its verifier binding."""
        key = normalize_name(name)
        handler = self._handlers.get(key)
        if handler is None:
            raise UnknownToolError(f"No tool registered under the name '{name}'")

        source_id = self._verification_source_bindings.pop(id(handler), None)
        if source_id is not None:
            source_owner = self._verification_source_owners.pop(source_id, None)
            if source_owner is not None:
                self._verification_provider_owners.pop(source_owner[1], None)

        provider = self._verification_providers.pop(id(handler), None)
        if provider is not None:
            self._verification_provider_owners.pop(id(provider), None)

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

    def verification_provider(self, name: str) -> ToolVerificationProvider | None:
        """Return the concrete verifier provider bound to one capability."""
        handler = self.get(name)
        return self._verification_providers.get(id(handler))

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
