"""Bridge explicit tool plans to the tool-layer capability boundary."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol, runtime_checkable

from src.core.execution_plan_models import PlanStep
from src.tools.models import ToolDefinition, ToolRequest, ToolResult


@runtime_checkable
class ToolInvoker(Protocol):
    """Minimal contract required to invoke a tool safely."""

    def invoke(self, request: ToolRequest) -> ToolResult:
        ...


@runtime_checkable
class ToolCapabilityGateway(ToolInvoker, Protocol):
    """Capability boundary used by JARVIS to discover and invoke tools."""

    def list_definitions(self) -> Sequence[ToolDefinition]:
        """Return the currently available tool capability definitions."""
        ...


class ToolPlanStepHandler:
    """Adapt an explicit ``USE_TOOL`` plan step to a tool invoker."""

    ACTION = "USE_TOOL"

    def __init__(self, invoker: ToolInvoker) -> None:
        if not isinstance(invoker, ToolInvoker):
            raise TypeError("invoker must implement ToolInvoker")
        self._invoker = invoker

    def __call__(self, step: PlanStep) -> object:
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

        result = self._invoker.invoke(
            ToolRequest(
                tool_name=tool_name,
                arguments=dict(arguments),
                invocation_id=invocation_id or step.step_id,
            )
        )

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
