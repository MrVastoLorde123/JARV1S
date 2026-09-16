"""Authorize concrete tool executions without conflating planning or confirmation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from src.core.execution_plan_models import PlanStep
from src.tools.models import ToolRequest


@dataclass(frozen=True)
class ToolExecutionAuthorization:
    """Immutable authorization decision bound to one exact step/request."""

    step_id: str
    request: ToolRequest
    authorized: bool
    policy_id: str
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.step_id, str) or not self.step_id.strip():
            raise ValueError("step_id must be a non-empty string")
        if not isinstance(self.request, ToolRequest):
            raise TypeError("request must be a ToolRequest")
        if not isinstance(self.authorized, bool):
            raise TypeError("authorized must be a bool")
        if not isinstance(self.policy_id, str) or not self.policy_id.strip():
            raise ValueError("policy_id must be a non-empty string")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")


@runtime_checkable
class ToolAuthorizationPolicy(Protocol):
    """Authority-bearing policy boundary for a concrete tool request."""

    def authorize(
        self,
        step: PlanStep,
        request: ToolRequest,
    ) -> ToolExecutionAuthorization:
        ...


def require_authorization(
    step: PlanStep,
    request: ToolRequest,
    authorization: ToolExecutionAuthorization,
) -> None:
    """Reject authorization that is absent, denied, stale, or mis-bound."""
    if not isinstance(authorization, ToolExecutionAuthorization):
        raise TypeError("authorization must be a ToolExecutionAuthorization")
    if authorization.step_id != step.step_id or authorization.request != request:
        raise PermissionError(
            "authorization does not match the requested plan step execution"
        )
    if not authorization.authorized:
        raise PermissionError(
            f"tool plan step '{step.step_id}' is not authorized: "
            f"{authorization.reason}"
        )
