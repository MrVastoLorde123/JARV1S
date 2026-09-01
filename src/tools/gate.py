"""Policy and confirmation boundary for tool invocation."""

from __future__ import annotations

from typing import Optional

from .confirmation import AutoDenyConfirmationProvider, ConfirmationProvider, ConfirmationResponse
from .errors import InvalidConfirmationResponseError, InvalidPolicyVerdictError, InvalidRequestError
from .models import ToolDefinition, ToolError, ToolRequest, ToolResult
from .policy import Policy, PolicyDecision, PolicyVerdict
from .registry import ToolRegistry
from .service import ToolService


class PolicyGate:
    """Enforces policy and confirmation before delegating to ToolService."""

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

    def list_definitions(self) -> tuple[ToolDefinition, ...]:
        """Return the immutable capability catalog visible to callers."""
        return tuple(self._registry.list_definitions())

    def invoke(self, request: ToolRequest) -> ToolResult:
        """Run one request through Policy -> Confirmation -> ToolService."""
        if not isinstance(request, ToolRequest):
            raise InvalidRequestError(
                f"PolicyGate.invoke expects a ToolRequest, got {type(request).__name__}"
            )

        handler = self._registry.get(request.tool_name)
        definition = handler.definition()

        verdict = self._policy.evaluate(definition, request)
        if not isinstance(verdict, PolicyVerdict):
            raise InvalidPolicyVerdictError(
                f"Policy {self._policy!r} returned {type(verdict).__name__}, expected PolicyVerdict"
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
                    message=response.reason or f"Confirmation was not granted for tool '{request.tool_name}'",
                )

        return self._service.invoke(request)

    @staticmethod
    def _blocked_result(request: ToolRequest, *, code: str, message: str) -> ToolResult:
        return ToolResult(
            success=False,
            tool_name=request.tool_name,
            error=ToolError(code=code, message=message),
            invocation_id=request.invocation_id,
        )
