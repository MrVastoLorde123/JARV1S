"""Policy, confirmation, and explicit authorization boundary for tool invocation."""

from __future__ import annotations

import hashlib
import json
from typing import Optional

from .authorization import AuthorizationDecision, ExplicitAuthorizationService
from .confirmation import AutoDenyConfirmationProvider, ConfirmationProvider
from .errors import InvalidRequestError
from .models import ToolDefinition, ToolError, ToolRequest, ToolResult
from .policy import Policy, PolicyDecision
from .registry import ToolRegistry
from .service import ToolService


class PolicyGate:
    """Enforces policy and confirmation before delegating to ToolService.

    ``authorize()`` is the explicit non-executing authority boundary. ``invoke()``
    consumes that decision and remains the only public path that crosses into
    ``ToolService``.
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
        self._authorization = ExplicitAuthorizationService(
            policy,
            self._confirmation_provider,
        )

    def list_definitions(self) -> tuple[ToolDefinition, ...]:
        """Return the immutable capability catalog visible to callers."""
        return tuple(self._registry.list_definitions())

    def authorize(
        self,
        request: ToolRequest,
        *,
        authorization_id: str | None = None,
    ) -> AuthorizationDecision:
        """Evaluate one request through policy + confirmation without execution."""
        if not isinstance(request, ToolRequest):
            raise InvalidRequestError(
                f"PolicyGate.authorize expects a ToolRequest, got {type(request).__name__}"
            )

        handler = self._registry.get(request.tool_name)
        definition = handler.definition()
        identity = authorization_id or self._default_authorization_id(request)
        return self._authorization.authorize(
            definition,
            request,
            authorization_id=identity,
        )

    def invoke(self, request: ToolRequest) -> ToolResult:
        """Run one request through explicit authorization, then ToolService."""
        decision = self.authorize(request)

        if not decision.authorized:
            if decision.policy_decision is PolicyDecision.DENY:
                return self._blocked_result(
                    request,
                    code="policy_denied",
                    message=decision.reason
                    or f"Tool '{request.tool_name}' was denied by policy",
                )
            return self._blocked_result(
                request,
                code="confirmation_denied",
                message=decision.reason
                or f"Confirmation was not granted for tool '{request.tool_name}'",
            )

        return self._service.invoke(request)

    @staticmethod
    def _default_authorization_id(request: ToolRequest) -> str:
        payload = json.dumps(
            {
                "tool_name": request.tool_name.strip().lower(),
                "arguments": request.arguments,
                "invocation_id": request.invocation_id,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()[:24]
        return f"auth-{digest}"

    @staticmethod
    def _blocked_result(request: ToolRequest, *, code: str, message: str) -> ToolResult:
        return ToolResult(
            success=False,
            tool_name=request.tool_name,
            error=ToolError(code=code, message=message),
            invocation_id=request.invocation_id,
        )
