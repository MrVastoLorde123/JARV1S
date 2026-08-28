"""``PolicyGate`` wires the confirmation boundary in front of ``ToolService``.

    JARVIS decides
          |
          v
    ToolRequest
          |
          v
    Policy
          |
          v
    Confirmation
          |
          v
    ToolService   <-- unchanged from milestone 1
          |
          v
    ToolHandler

``PolicyGate`` is the new thing JARVIS core calls instead of calling
``ToolService`` directly. ``ToolService`` itself is untouched: it has
no awareness of policy or confirmation, and can still be used directly
by anything (e.g. tests, or a future trusted internal caller) that
has already made its own confirmation decision.

Error handling policy mirrors ``ToolService``: structural problems
(bad request, unknown tool, a ``Policy``/``ConfirmationProvider`` that
violates its contract) raise typed exceptions. A policy denial or a
declined confirmation is a routine, expected outcome -- like a tool
execution failure -- and is returned as a failed ``ToolResult``, never
raised.
"""

from __future__ import annotations

from typing import Optional

from .confirmation import AutoDenyConfirmationProvider, ConfirmationProvider, ConfirmationResponse
from .errors import (
    InvalidConfirmationResponseError,
    InvalidPolicyVerdictError,
    InvalidRequestError,
)
from .models import ToolError, ToolRequest, ToolResult
from .policy import Policy, PolicyDecision, PolicyVerdict
from .registry import ToolRegistry
from .service import ToolService


class PolicyGate:
    """Enforces Policy -> Confirmation before delegating to ``ToolService``.

    Args:
        registry: Used to resolve a request's ``ToolDefinition`` so
            the policy has something to evaluate against. The same
            registry instance should be the one backing ``service``.
        service: The downstream ``ToolService`` that actually invokes
            handlers once a request is allowed (or confirmed).
        policy: Decides ALLOW / DENY / REQUIRE_CONFIRMATION for each
            request. See ``policy.py``.
        confirmation_provider: Obtains confirmation when the policy
            requires it. Defaults to ``AutoDenyConfirmationProvider``
            -- a safe default that never silently approves anything.
    """

    def __init__(
        self,
        registry: ToolRegistry,
        service: ToolService,
        policy: Policy,
        confirmation_provider: Optional[ConfirmationProvider] = None,
    ) -> None:
        self._registry = registry
        self._service = service
        self._policy = policy
        self._confirmation_provider = confirmation_provider or AutoDenyConfirmationProvider()

    def invoke(self, request: ToolRequest) -> ToolResult:
        """Run one request through Policy -> Confirmation -> ToolService.

        Raises:
            InvalidRequestError: ``request`` is not a ``ToolRequest``.
            UnknownToolError: No handler is registered for
                ``request.tool_name`` (propagated from the registry).
            InvalidPolicyVerdictError: ``policy`` returned something
                other than a ``PolicyVerdict``.
            InvalidConfirmationResponseError: the confirmation
                provider returned something other than a
                ``ConfirmationResponse``.
        """
        if not isinstance(request, ToolRequest):
            raise InvalidRequestError(
                f"PolicyGate.invoke expects a ToolRequest, got {type(request).__name__}"
            )

        # Resolution failures (unknown tool) propagate as UnknownToolError,
        # same as ToolService -- this is a structural problem, not a
        # policy decision.
        handler = self._registry.get(request.tool_name)
        definition = handler.definition()

        verdict = self._policy.evaluate(definition, request)
        if not isinstance(verdict, PolicyVerdict):
            raise InvalidPolicyVerdictError(
                f"Policy {self._policy!r} returned {type(verdict).__name__}, "
                "expected PolicyVerdict"
            )

        if verdict.decision == PolicyDecision.DENY:
            return self._blocked_result(
                request,
                code="policy_denied",
                message=verdict.reason or f"Tool '{request.tool_name}' was denied by policy",
            )

        if verdict.decision == PolicyDecision.REQUIRE_CONFIRMATION:
            response = self._confirmation_provider.confirm(definition, request)
            if not isinstance(response, ConfirmationResponse):
                raise InvalidConfirmationResponseError(
                    f"Confirmation provider {self._confirmation_provider!r} returned "
                    f"{type(response).__name__}, expected ConfirmationResponse"
                )
            if not response.approved:
                return self._blocked_result(
                    request,
                    code="confirmation_denied",
                    message=response.reason
                    or f"Confirmation was not granted for tool '{request.tool_name}'",
                )

        # verdict.decision == ALLOW, or REQUIRE_CONFIRMATION that was approved.
        return self._service.invoke(request)

    def _blocked_result(self, request: ToolRequest, *, code: str, message: str) -> ToolResult:
        return ToolResult(
            success=False,
            tool_name=request.tool_name,
            error=ToolError(code=code, message=message),
            invocation_id=request.invocation_id,
        )
