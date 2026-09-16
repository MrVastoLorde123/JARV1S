"""Bind the full tool execution chain to the existing PlanExecutor action seam."""

from __future__ import annotations

from src.core.execution_plan_models import PlanStep
from src.core.plan_executor import PlanExecutor
from src.core.tool_execution_chain import ToolExecutionChain, ToolExecutionChainTrace


class ToolExecutionChainPlanHandler:
    """Expose a ``ToolExecutionChain`` as the deterministic ``USE_TOOL`` handler."""

    ACTION = "USE_TOOL"

    def __init__(self, chain: ToolExecutionChain) -> None:
        if not isinstance(chain, ToolExecutionChain):
            raise TypeError("chain must be a ToolExecutionChain")
        self._chain = chain
        self._traces: dict[str, ToolExecutionChainTrace] = {}

    def __call__(self, step: PlanStep) -> object:
        if not isinstance(step, PlanStep):
            raise TypeError("step must be a PlanStep")
        trace = self._chain.execute(step)
        self._traces[step.step_id] = trace
        return trace.result.content

    def register(self, executor: PlanExecutor) -> PlanExecutor:
        """Install this chain as the executor's ``USE_TOOL`` handler."""
        if not isinstance(executor, PlanExecutor):
            raise TypeError("executor must be a PlanExecutor")
        executor.register_handler(self.ACTION, self)
        return executor

    def trace_for_step(self, step_id: str) -> ToolExecutionChainTrace | None:
        if not isinstance(step_id, str) or not step_id.strip():
            raise ValueError("step_id must be a non-empty string")
        return self._traces.get(step_id)

    @property
    def traces(self) -> tuple[ToolExecutionChainTrace, ...]:
        return tuple(self._traces[key] for key in sorted(self._traces))


__all__ = ["ToolExecutionChainPlanHandler"]
