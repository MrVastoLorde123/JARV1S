"""Compose policy authorization with the policy-neutral tool execution adapter."""

from __future__ import annotations

from src.core.execution_plan_models import PlanStep
from src.core.tool_authorization import (
    ToolAuthorizationPolicy,
    require_authorization,
)
from src.core.tool_execution import ToolExecutionConfirmation, ToolPlanStepHandler, ToolInvoker


class AuthorizedToolPlanStepHandler:
    """Execute a tool plan step only after an external policy authorizes it."""

    def __init__(
        self,
        invoker: ToolInvoker,
        policy: ToolAuthorizationPolicy,
    ) -> None:
        if not isinstance(invoker, ToolInvoker):
            raise TypeError("invoker must implement ToolInvoker")
        if not isinstance(policy, ToolAuthorizationPolicy):
            raise TypeError("policy must implement ToolAuthorizationPolicy")
        self._handler = ToolPlanStepHandler(invoker)
        self._policy = policy

    def __call__(
        self,
        step: PlanStep,
        confirmation: ToolExecutionConfirmation | None = None,
    ) -> object:
        request = ToolPlanStepHandler.build_request(step)
        authorization = self._policy.authorize(step, request)
        require_authorization(step, request, authorization)
        return self._handler(step, confirmation)
