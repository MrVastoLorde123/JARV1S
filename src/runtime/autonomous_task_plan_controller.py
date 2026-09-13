"""Application boundary for durable task-plan mutation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.runtime.autonomous_job import AutonomousJob
from src.runtime.autonomous_job_persistence import (
    AutonomousJobPersistenceReceipt,
    AutonomousJobPersistenceService,
)
from src.runtime.autonomous_task_plan import (
    AutonomousTaskPlan,
    AutonomousTaskPlanStepStatus,
)


class _TaskRuntime(Protocol):
    def inspect(self, job_id: str) -> AutonomousJob | None: ...


@dataclass(frozen=True)
class AutonomousTaskPlanUpdateResult:
    """Durable receipt for one validated plan mutation."""

    job: AutonomousJob
    plan: AutonomousTaskPlan
    persistence_receipt: AutonomousJobPersistenceReceipt


class AutonomousTaskPlanController:
    """Read and mutate durable task plans without owning execution authority."""

    def __init__(
        self,
        runtime: _TaskRuntime,
        persistence: AutonomousJobPersistenceService,
    ) -> None:
        if not hasattr(runtime, "inspect") or not callable(runtime.inspect):
            raise TypeError("runtime must provide inspect(job_id)")
        if not isinstance(persistence, AutonomousJobPersistenceService):
            raise TypeError("persistence must be an AutonomousJobPersistenceService")
        self._runtime = runtime
        self._persistence = persistence

    def inspect(self, job_id: str) -> AutonomousTaskPlan | None:
        job = self._runtime.inspect(job_id)
        if job is None:
            return None
        payload = job.working_context.get("task_plan")
        if payload is None:
            return None
        return AutonomousTaskPlan.from_mapping(payload)

    def set_plan(
        self,
        job_id: str,
        plan: AutonomousTaskPlan,
    ) -> AutonomousTaskPlanUpdateResult:
        return self._persist(job_id, plan)

    def start(self, job_id: str, step_id: str) -> AutonomousTaskPlanUpdateResult:
        plan = self._require_plan(job_id)
        return self._persist(job_id, plan.start(step_id))

    def complete(self, job_id: str, step_id: str, reason: str | None = None) -> AutonomousTaskPlanUpdateResult:
        plan = self._require_plan(job_id)
        return self._persist(job_id, plan.complete_step(step_id, reason=reason))

    def block(self, job_id: str, step_id: str, reason: str) -> AutonomousTaskPlanUpdateResult:
        plan = self._require_plan(job_id)
        return self._persist(job_id, plan.block(step_id, reason))

    def _require_plan(self, job_id: str) -> AutonomousTaskPlan:
        plan = self.inspect(job_id)
        if plan is None:
            raise LookupError(f"task plan not found: {job_id}")
        return plan

    def _persist(self, job_id: str, plan: AutonomousTaskPlan) -> AutonomousTaskPlanUpdateResult:
        job = self._runtime.inspect(job_id)
        if job is None:
            raise LookupError(f"autonomous task not found: {job_id}")
        if job.terminal:
            raise ValueError("terminal tasks cannot mutate task plans")
        updated = job.with_working_context({"task_plan": plan.to_dict()})
        receipt = self._persistence.persist(updated)
        return AutonomousTaskPlanUpdateResult(updated, plan, receipt)


__all__ = ["AutonomousTaskPlanController", "AutonomousTaskPlanUpdateResult"]
