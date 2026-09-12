"""JARVIS-facing orchestration service for bounded coding-agent work."""

from __future__ import annotations

from src.agents.coding_worker import (
    CodingAgentPlan,
    CodingAgentResult,
    CodingAgentTask,
    CodingAgentWorker,
)
from src.agents.ai_coding_planner import AICodingAgentPlanner


class CodingAgentService:
    """Compose a planner and bounded worker without owning tool authority."""

    def __init__(self, planner, worker: CodingAgentWorker) -> None:
        self._planner = planner
        self._worker = worker

    @classmethod
    def from_ai_service(cls, ai_service, tool_invoker, *, provider_name: str | None = None):
        planner = AICodingAgentPlanner(
            ai_service,
            provider_name=provider_name,
        )
        worker = CodingAgentWorker(
            planner,
            tool_invoker,
        )
        return cls(planner, worker)

    def plan(self, task: CodingAgentTask) -> CodingAgentPlan:
        """Generate a proposal without invoking repository tools."""
        if not isinstance(task, CodingAgentTask):
            raise TypeError("task must be a CodingAgentTask")
        return self._worker.plan(task)

    def execute(self, task: CodingAgentTask, plan: CodingAgentPlan) -> CodingAgentResult:
        """Execute exactly the supplied plan through the worker authority boundary."""
        if not isinstance(task, CodingAgentTask):
            raise TypeError("task must be a CodingAgentTask")
        if not isinstance(plan, CodingAgentPlan):
            raise TypeError("plan must be a CodingAgentPlan")
        return self._worker.execute(task, plan)


__all__ = ["CodingAgentService"]
