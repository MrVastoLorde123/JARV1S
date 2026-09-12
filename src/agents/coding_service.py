"""JARVIS-facing orchestration service for bounded coding-agent work."""

from __future__ import annotations

from src.agents.ai_coding_planner import AICodingAgentPlanner
from src.agents.coding_worker import (
    CodingAgentPlan,
    CodingAgentResult,
    CodingAgentTask,
    CodingAgentWorker,
)
from src.agents.repository_context import RepositoryContextComposer


class CodingAgentService:
    """Compose JARVIS context, a planner, and a bounded coding worker."""

    def __init__(self, planner, worker: CodingAgentWorker, context_composer=None) -> None:
        self._planner = planner
        self._worker = worker
        self._context_composer = context_composer

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
        context_composer = RepositoryContextComposer(tool_invoker)
        return cls(planner, worker, context_composer)

    def plan(self, task: CodingAgentTask) -> CodingAgentPlan:
        """Compose observed environment context before generating a proposal."""
        if not isinstance(task, CodingAgentTask):
            raise TypeError("task must be a CodingAgentTask")

        enriched_task = task
        if self._context_composer is not None:
            repository_context = self._context_composer.compose()
            enriched_metadata = {
                **dict(task.metadata),
                "repository_context": repository_context.render(),
            }
            enriched_task = CodingAgentTask(
                objective=task.objective,
                task_id=task.task_id,
                metadata=enriched_metadata,
            )

        return self._worker.plan(enriched_task)

    def execute(self, task: CodingAgentTask, plan: CodingAgentPlan) -> CodingAgentResult:
        """Execute exactly the supplied plan through the worker authority boundary."""
        if not isinstance(task, CodingAgentTask):
            raise TypeError("task must be a CodingAgentTask")
        if not isinstance(plan, CodingAgentPlan):
            raise TypeError("plan must be a CodingAgentPlan")
        return self._worker.execute(task, plan)


__all__ = ["CodingAgentService"]
