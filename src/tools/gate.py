"""Policy, confirmation, authorization, integrity, sandbox, handoff, and execution-attempt gate."""

from __future__ import annotations

import hashlib
import json
from typing import Optional

from src.plugins.sandbox import SandboxProfileRegistry

from .authorization import AuthorizationDecision, ExplicitAuthorizationService
from .authorization_integrity import AuthorizationIntegrityService
from .confirmation import AutoDenyConfirmationProvider, ConfirmationProvider
from .errors import InvalidRequestError
from .execution_attempt import ExecutionAttemptService, ExecutionAttemptStatus, ToolExecutor
from .execution_preparation import ExecutionPreparationError, ExecutionPreparationService
from .models import ToolDefinition, ToolError, ToolRequest, ToolResult
from .policy import Policy, PolicyDecision
from .registry import ToolRegistry
from .sandbox_admission import SandboxAdmissionService, build_default_sandbox_profiles
from .service import ToolService


class _ToolServiceExecutor:
    """Adapter that executes a prepared handoff through the existing ToolService."""

    def __init__(self, service: ToolService) -> None:
        self._service = service

    def execute(self, handoff) -> ToolResult:
        return self._service.invoke(
            ToolRequest(
                tool_name=handoff.tool_name,
                arguments=dict(handoff.arguments),
                invocation_id=handoff.invocation_id,
            )
        )


class PolicyGate:
    """Enforces policy, confirmation, authorization, integrity, sandbox, handoff, and execution attempt."""

    def __init__(
        self,
        registry: ToolRegistry,
        service: ToolService,
        policy: Policy,
        confirmation_provider: Optional[ConfirmationProvider] = None,
        sandbox_profile_registry: Optional[SandboxProfileRegistry] = None,
        executor: Optional[ToolExecutor] = None,
    ) -> None:
        self._registry = registry
        self._service = service
        self._policy = policy
        self._confirmation_provider = confirmation_provider or AutoDenyConfirmationProvider()
        self._authorization = ExplicitAuthorizationService(
            policy,
            self._confirmation_provider,
        )
        self._authorization_integrity = AuthorizationIntegrityService()
        self._sandbox_profiles = sandbox_profile_registry or build_default_sandbox_profiles()
        self._sandbox_admission = SandboxAdmissionService(self._sandbox_profiles)
        self._execution_preparation = ExecutionPreparationService()
        self._executor = executor or _ToolServiceExecutor(service)
        self._execution_attempt = ExecutionAttemptService(self._executor)

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
        """Run one request through all authority boundaries before the executor."""
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

        integrity = self._authorization_integrity.attest(decision, request)
        if not self._authorization_integrity.verify(integrity, decision, request):
            return self._blocked_result(
                request,
                code="authorization_integrity_failed",
                message=integrity.reason or "Authorization integrity verification failed",
            )

        handler = self._registry.get(request.tool_name)
        definition = handler.definition()
        declared_profile = definition.metadata.get("sandbox_profile_id")
        admission = self._sandbox_admission.admit(
            decision,
            integrity,
            request,
            profile_id=declared_profile,
        )
        if not admission.admissible:
            return self._blocked_result(
                request,
                code="sandbox_admission_failed",
                message=admission.reason or "Sandbox admission failed",
            )

        try:
            handoff = self._execution_preparation.prepare(
                decision,
                integrity,
                admission,
                request,
            )
        except (ExecutionPreparationError, TypeError) as exc:
            return self._blocked_result(
                request,
                code="execution_preparation_failed",
                message=str(exc) or "Execution preparation failed",
            )

        outcome = self._execution_attempt.attempt(handoff)
        if outcome.status is ExecutionAttemptStatus.COMPLETED:
            if outcome.result is None:
                return self._blocked_result(
                    request,
                    code="execution_attempt_failed",
                    message="execution attempt reported completion without a result",
                )
            return outcome.result

        return self._blocked_result(
            request,
            code="execution_attempt_failed",
            message=outcome.reason or "execution attempt failed",
        )

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
