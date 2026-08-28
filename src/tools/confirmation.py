"""Confirmation: the second half of the confirmation boundary.

See ``policy.py`` for the full pipeline diagram. Where ``Policy``
decides *whether* confirmation is needed, ``ConfirmationProvider``
decides *how* confirmation is obtained and whether it was granted.

This milestone does not implement a real, user-facing confirmation
mechanism (e.g. prompting through JARVIS's UI). It defines the
contract and two deterministic, non-interactive implementations
intended for wiring and tests. A real provider (backed by JARVIS's
actual user-interaction channel) is future work and should be added
as a new class satisfying this same protocol -- ``PolicyGate`` does
not need to change to support it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable

from .errors import InvalidConfirmationResponseError
from .models import ToolDefinition, ToolRequest


@dataclass(frozen=True)
class ConfirmationResponse:
    """The outcome of asking for confirmation on one request.

    Attributes:
        approved: Whether the user (or delegate) granted confirmation.
        reason: Optional human-readable explanation, surfaced into the
            resulting ``ToolResult`` on denial.
    """

    approved: bool
    reason: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.approved, bool):
            raise InvalidConfirmationResponseError(
                "ConfirmationResponse.approved must be a bool"
            )
        if self.reason is not None and not isinstance(self.reason, str):
            raise InvalidConfirmationResponseError(
                "ConfirmationResponse.reason must be a string or None"
            )


@runtime_checkable
class ConfirmationProvider(Protocol):
    """Structural contract for obtaining confirmation on a request."""

    def confirm(
        self, definition: ToolDefinition, request: ToolRequest
    ) -> ConfirmationResponse:
        """Obtain a confirmation decision for ``request``.

        Called by ``PolicyGate`` only when a ``Policy`` returned
        ``REQUIRE_CONFIRMATION``. Implementations are free to do I/O
        here (unlike ``Policy.evaluate``) -- prompting a user is
        exactly the kind of side effect this step exists to isolate.
        """
        ...


class AutoDenyConfirmationProvider:
    """Denies every confirmation request.

    This is the safe default: if ``PolicyGate`` is constructed without
    an explicit ``ConfirmationProvider``, it uses this one, so that a
    tool requiring confirmation is never silently approved just
    because no real confirmation mechanism has been wired up yet.
    """

    def confirm(
        self, definition: ToolDefinition, request: ToolRequest
    ) -> ConfirmationResponse:
        return ConfirmationResponse(
            approved=False,
            reason=(
                f"No confirmation provider is configured; denying '{definition.name}' "
                "by default"
            ),
        )


class AutoApproveConfirmationProvider:
    """Approves every confirmation request, unconditionally.

    Intended strictly for tests and local development of the plumbing
    around ``PolicyGate``. This must never be wired into a real
    JARVIS deployment in place of an actual user-confirmation
    mechanism -- doing so is exactly the "automatic permission
    bypass" this architecture is designed to prevent.
    """

    def confirm(
        self, definition: ToolDefinition, request: ToolRequest
    ) -> ConfirmationResponse:
        return ConfirmationResponse(approved=True, reason="auto-approved (test provider)")
