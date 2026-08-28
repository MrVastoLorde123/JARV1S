"""Policy: the first half of the confirmation boundary.

Per the architecture doc:

    JARVIS decides
          |
          v
    ToolRequest
          |
          v
    Policy            <-- this module
          |
          v
    Confirmation      <-- confirmation.py
          |
          v
    ToolService
          |
          v
    ToolHandler

A ``Policy`` never executes anything and never talks to a handler. It
looks at a ``ToolDefinition`` (what the tool declares about itself)
and a ``ToolRequest`` (what's being asked) and returns a
``PolicyVerdict`` describing what should happen next: proceed, be
blocked outright, or require confirmation before proceeding.

This module makes no decision about *how* confirmation is obtained --
that's ``confirmation.py``'s job. It also does not know about
``ToolService`` at all, keeping it independently testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import AbstractSet, FrozenSet, Optional, Protocol, runtime_checkable

from .errors import InvalidPolicyVerdictError
from .models import RiskLevel, ToolDefinition, ToolRequest
from .registry import normalize_name


class PolicyDecision(str, Enum):
    """What a ``Policy`` decided should happen with a request."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_CONFIRMATION = "require_confirmation"


@dataclass(frozen=True)
class PolicyVerdict:
    """The outcome of evaluating a request against a policy.

    Attributes:
        decision: What should happen next.
        reason: Optional human-readable explanation, surfaced to the
            caller (and, on denial, into the resulting ``ToolResult``)
            for reviewability.
    """

    decision: PolicyDecision
    reason: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.decision, PolicyDecision):
            raise InvalidPolicyVerdictError(
                "PolicyVerdict.decision must be a PolicyDecision member"
            )
        if self.reason is not None and not isinstance(self.reason, str):
            raise InvalidPolicyVerdictError("PolicyVerdict.reason must be a string or None")


@runtime_checkable
class Policy(Protocol):
    """Structural contract for a policy implementation."""

    def evaluate(self, definition: ToolDefinition, request: ToolRequest) -> PolicyVerdict:
        """Decide what should happen with ``request`` against ``definition``.

        Implementations must be side-effect free: no I/O, no prompting
        a user, no invoking a handler. Obtaining confirmation is a
        separate step performed by a ``ConfirmationProvider`` only
        when this returns ``REQUIRE_CONFIRMATION``.
        """
        ...


class DefaultPolicy:
    """A conservative, declaration-driven default ``Policy``.

    Rules, applied in order:

        1. If the tool's normalized name is in ``blocked_tools`` ->
           ``DENY``.
        2. If the definition declares ``requires_confirmation=True``,
           or its ``risk_level`` is in ``confirmation_risk_levels`` ->
           ``REQUIRE_CONFIRMATION``.
        3. Otherwise -> ``ALLOW``.

    This is intentionally simple and fully driven by what the tool
    *declares about itself* plus a static block list -- it does not
    inspect request arguments, conversation state, or memory. Request-
    content-aware policy (e.g. "deny `delete_file` when path is
    outside the project root") is a natural extension but is left for
    a future milestone to avoid smuggling tool-specific conditionals
    into the generic policy layer prematurely.
    """

    def __init__(
        self,
        *,
        blocked_tools: AbstractSet[str] = frozenset(),
        confirmation_risk_levels: AbstractSet[RiskLevel] = frozenset(
            {RiskLevel.HIGH, RiskLevel.CRITICAL}
        ),
    ) -> None:
        self._blocked_tools: FrozenSet[str] = frozenset(
            normalize_name(name) for name in blocked_tools
        )
        self._confirmation_risk_levels: FrozenSet[RiskLevel] = frozenset(confirmation_risk_levels)

    def evaluate(self, definition: ToolDefinition, request: ToolRequest) -> PolicyVerdict:
        key = normalize_name(definition.name)

        if key in self._blocked_tools:
            return PolicyVerdict(
                decision=PolicyDecision.DENY,
                reason=f"Tool '{definition.name}' is blocked by policy",
            )

        if definition.requires_confirmation:
            return PolicyVerdict(
                decision=PolicyDecision.REQUIRE_CONFIRMATION,
                reason=f"Tool '{definition.name}' declares requires_confirmation=True",
            )

        if definition.risk_level in self._confirmation_risk_levels:
            return PolicyVerdict(
                decision=PolicyDecision.REQUIRE_CONFIRMATION,
                reason=(
                    f"Tool '{definition.name}' has risk level "
                    f"'{definition.risk_level.value}', which requires confirmation"
                ),
            )

        return PolicyVerdict(decision=PolicyDecision.ALLOW)
