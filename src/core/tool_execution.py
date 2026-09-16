"""Orchestrate tool invocation behind explicit plan-step boundaries.

``ToolService`` remains the low-level tool boundary: it validates a
``ToolRequest``, resolves a registered tool, invokes it, and validates the
result. This module adds the plan-step adapter above that boundary.

The plan-step adapter deliberately does not own policy or authority. A tool
execution must carry a separate, request-bound authorization artifact, and a
step that declares ``requires_confirmation=True`` must also carry a separate,
request-bound confirmation artifact. Authorization and confirmation are
independent execution preconditions; neither is verification truth.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from src.core.execution_plan_models import PlanStep
from src.core.tool_authorization import ToolExecutionAuthorization, require_authorization
from src.tools.models import ToolDefinition, ToolRequest, ToolResult


@dataclass(frozen=True)
class ToolExecutionConfirmation:
    """Explicit confirmation bound to one immutable plan/request identity."""

    step_id: str
    request: ToolRequest
    confirmed: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.step_id, str) or not self.step_id.strip():
            raise ValueError("step_id must be a non-empty string")
        if not isinstance(self.request, ToolRequest):
            raise TypeError("request must be a ToolRequest")
        if not isinstance(self.confirmed, bool):
            raise TypeError("confirmed must be a bool")


@runtime_checkable
class ToolInvoker(Protocol):
    """Minimal contract required to invoke a tool safely."""

    def invoke(self, request: ToolRequest) -> ToolResult:
        ...


@runtime_checkable
class ToolCapabilityGateway(ToolInvoker, Protocol):
    """Capability boundary used by JARVIS to discover and invoke tools."""

    def list_definitions(self) -> tuple[ToolDefinition, ...]:
        ...


class ToolPlanStepHandler:
    """Adapt an explicit ``USE_TOOL`` plan step to a tool invoker.

    This adapter performs structural request validation and enforces explicit
    authorization for every tool execution. It separately enforces the plan's
    confirmation requirement when requested. It never decides policy itself,
    and it never turns confirmation into authority.
    """

    ACTION = "USE_TOOL"

    def __init__(self, invoker: ToolInvoker) -> None:
        if not isinstance(invoker, ToolInvoker):
            raise TypeError("invoker must implement ToolInvoker")
        self._invoker = invoker

    def __call__(
        self,
        step: PlanStep,
        authorization: ToolExecutionAuthorization | None = None,
        confirmation: ToolExecutionConfirmation | None = None,
    ) -> object:
        if not isinstance(step, PlanStep):
            raise TypeError("step must be a PlanStep")

        if step.action.strip().upper() != self.ACTION:
            raise ValueError(
                f"ToolPlanStepHandler cannot execute action {step.action!r}"
            )

        tool_name = step.metadata.get("tool_name")
        if not isinstance(tool_name, str) or not tool_name.strip():
            raise ValueError("tool plan step requires a non-empty 'tool_name'")

        arguments = step.metadata.get("arguments", {})
        if not isinstance(arguments, Mapping):
            raise ValueError("tool plan step 'arguments' must be a mapping")

        invocation_id = step.metadata.get("invocation_id")
        if invocation_id is not None and not isinstance(invocation_id, str):
            raise ValueError("tool plan step 'invocation_id' must be a string or None")

        request = ToolRequest(
            tool_name=tool_name,
            arguments=dict(arguments),
            invocation_id=invocation_id or step.step_id,
        )

        require_authorization(step, request, authorization)

        if step.requires_confirmation:
            self._require_confirmation(step, request, confirmation)

        result = self._invoker.invoke(request)

        if not isinstance(result, ToolResult):
            raise TypeError(
                f"Tool invoker returned {type(result).__name__}, expected ToolResult"
            )

        if not result.success:
            assert result.error is not None
            raise RuntimeError(
                f"tool '{tool_name}' failed: "
                f"{result.error.code}: {result.error.message}"
            )

        return result.content

    @staticmethod
    def _require_confirmation(
        step: PlanStep,
        request: ToolRequest,
        confirmation: ToolExecutionConfirmation | None,
    ) -> None:
        if confirmation is None:
            raise PermissionError(
                f"tool plan step '{step.step_id}' requires explicit confirmation"
            )
        if not isinstance(confirmation, ToolExecutionConfirmation):
            raise TypeError(
                "confirmation must be a ToolExecutionConfirmation or None"
            )
        if not confirmation.confirmed:
            raise PermissionError(
                f"tool plan step '{step.step_id}' was not confirmed"
            )
        if confirmation.step_id != step.step_id or confirmation.request != request:
            raise PermissionError(
                "confirmation does not match the requested plan step execution"
            )
