"""Shared test doubles and helpers, used by the unittest test modules.

This module has no dependency on pytest -- it's plain Python so the
whole suite runs with nothing beyond the standard library.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from src.tools.confirmation import ConfirmationResponse
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest, ToolResult
from src.tools.policy import PolicyDecision, PolicyVerdict


def make_definition(
    name: str = "echo",
    *,
    risk_level: RiskLevel = RiskLevel.LOW,
    requires_confirmation: bool = False,
    metadata: Optional[Mapping[str, Any]] = None,
) -> ToolDefinition:
    return ToolDefinition(
        name=name,
        description="Echoes back its input arguments.",
        version="1.0.0",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        metadata=metadata or {},
    )


class EchoHandler:
    """A well-behaved handler used across tests: echoes its arguments."""

    def __init__(self, name: str = "echo", **definition_kwargs: Any) -> None:
        self._definition = make_definition(name=name, **definition_kwargs)

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=self._definition.name,
            content=dict(request.arguments),
            invocation_id=request.invocation_id,
        )


class RaisingHandler:
    """A handler whose execute() always raises, to exercise error wrapping."""

    def __init__(self, name: str = "boom") -> None:
        self._definition = make_definition(name=name)

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest) -> ToolResult:
        raise RuntimeError("simulated tool failure")


class MalformedResultHandler:
    """A handler that violates the ToolHandler contract's return type."""

    def __init__(self, name: str = "malformed") -> None:
        self._definition = make_definition(name=name)

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest):  # type: ignore[override]
        return {"not": "a ToolResult"}


class WrongToolNameHandler:
    """A handler that returns a result claiming to be a different tool."""

    def __init__(self, name: str = "impersonator") -> None:
        self._definition = make_definition(name=name)

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest) -> ToolResult:
        return ToolResult(success=True, tool_name="someone-else", content=None)


class NotAHandler:
    """Deliberately missing execute() -- fails the ToolHandler protocol."""

    def definition(self) -> ToolDefinition:
        return make_definition(name="incomplete")


class BadDefinitionHandler:
    """definition() returns the wrong type entirely."""

    def definition(self):  # type: ignore[override]
        return {"name": "not-a-definition"}

    def execute(self, request: ToolRequest) -> ToolResult:
        return ToolResult(success=True, tool_name="not-a-definition", content=None)


class StubPolicy:
    """A policy that always returns a pre-configured verdict, regardless
    of the definition/request it's asked about."""

    def __init__(self, verdict: PolicyVerdict) -> None:
        self._verdict = verdict

    def evaluate(self, definition: ToolDefinition, request: ToolRequest) -> PolicyVerdict:
        return self._verdict


class StubConfirmationProvider:
    """A confirmation provider that always returns a pre-configured response."""

    def __init__(self, response: ConfirmationResponse) -> None:
        self._response = response

    def confirm(self, definition: ToolDefinition, request: ToolRequest) -> ConfirmationResponse:
        return self._response


class MalformedPolicy:
    """Violates the Policy contract by returning the wrong type."""

    def evaluate(self, definition: ToolDefinition, request: ToolRequest):  # type: ignore[override]
        return "allow"


class MalformedConfirmationProvider:
    """Violates the ConfirmationProvider contract by returning the wrong type."""

    def confirm(self, definition: ToolDefinition, request: ToolRequest):  # type: ignore[override]
        return True


def allow_policy() -> StubPolicy:
    return StubPolicy(PolicyVerdict(decision=PolicyDecision.ALLOW))


def deny_policy(reason: str = "blocked for test") -> StubPolicy:
    return StubPolicy(PolicyVerdict(decision=PolicyDecision.DENY, reason=reason))


def confirmation_required_policy(reason: str = "needs confirmation") -> StubPolicy:
    return StubPolicy(PolicyVerdict(decision=PolicyDecision.REQUIRE_CONFIRMATION, reason=reason))
