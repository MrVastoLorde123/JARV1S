"""Application-level lifecycle for durable autonomous task ownership."""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from typing import Any, Callable

from src.database import get_connection
from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceReceipt, AutonomousJobPersistenceService
from src.runtime.autonomous_job_persistence_sqlite import SQLiteAutonomousJobStore
from src.runtime.autonomous_reasoning_feedback_pulse import AutonomousReasoningFeedbackPulse
from src.runtime.autonomous_reasoning_run_loop import AutonomousReasoningRunLoop
from src.runtime.autonomous_reasoning_tool_feedback_cycle import AutonomousReasoningToolFeedbackCycleCoordinator
from src.runtime.autonomous_reasoning_tool_gate import AutonomousReasoningToolGate
from src.runtime.autonomous_reasoning_worker import AutonomousReasoningWorker
from src.runtime.autonomous_runtime_schedule_persistence import SQLiteAutonomousRuntimeScheduleStore
from src.runtime.autonomous_runtime_scheduler import AutonomousRuntimeSchedule, AutonomousRuntimeScheduleResult, AutonomousRuntimeScheduler
from src.runtime.autonomous_task_ownership import AutonomousTaskOwnershipState
from src.runtime.autonomous_task_ownership_controller import AutonomousTaskOwnershipController, AutonomousTaskOwnershipUpdateResult
from src.runtime.autonomous_task_plan import AutonomousTaskPlan
from src.runtime.autonomous_task_plan_controller import AutonomousTaskPlanController, AutonomousTaskPlanUpdateResult
from src.runtime.autonomous_task_progress import AutonomousTaskProgressEvaluator
from src.runtime.autonomous_task_snapshot import AutonomousTaskSnapshot
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService


@dataclass(frozen=True)
class AutonomousTaskSubmissionResult:
    """Durable receipt for accepting a goal into autonomous work."""
    job: AutonomousJob
    persistence_receipt: AutonomousJobPersistenceReceipt
    schedule: AutonomousRuntimeSchedule


@dataclass(frozen=True)
class AutonomousTaskResumeResult:
    """Durable receipt for explicitly re-arming a waiting task."""
    job: AutonomousJob
    persistence_receipt: AutonomousJobPersistenceReceipt
    schedule: AutonomousRuntimeSchedule


@dataclass(frozen=True)
class AutonomousTaskLifecycleResult:
    """Durable receipt for an explicit pause or cancellation transition."""
    job: AutonomousJob
    persistence_receipt: AutonomousJobPersistenceReceipt


class AutonomousTaskRuntime:
    """Own the application lifecycle that turns a goal into durable ongoing work."""

    def __init__(self, persistence: AutonomousJobPersistenceService, scheduler: AutonomousRuntimeScheduler) -> None:
        if not isinstance(persistence, AutonomousJobPersistenceService):
            raise TypeError("persistence must be an AutonomousJobPersistenceService")
        if not isinstance(scheduler, AutonomousRuntimeScheduler):
            raise TypeError("scheduler must be an AutonomousRuntimeScheduler")
        self._persistence = persistence
        self._scheduler = scheduler
        self._ownership_controller = AutonomousTaskOwnershipController(self, persistence)
        self._plan_controller = AutonomousTaskPlanController(self, persistence)

    def submit(self, goal: str, *, now: float, interval: float, job_id: str | None = None, max_steps: int = 32, working_context: dict[str, object] | None = None) -> AutonomousTaskSubmissionResult:
        candidate = AutonomousJob.create(goal, job_id=job_id, max_steps=max_steps, working_context=working_context)
        if self._persistence.restore(candidate.job_id) is not None:
            raise ValueError(f"autonomous task already exists: {candidate.job_id}")
        receipt = self._persistence.persist(candidate)
        schedule = self._scheduler.schedule(candidate.job_id, next_due=now, interval=interval)
        return AutonomousTaskSubmissionResult(candidate, receipt, schedule)

    def inspect(self, job_id: str) -> AutonomousJob | None:
        return self._persistence.restore(job_id)

    def snapshot(self, job_id: str) -> AutonomousTaskSnapshot | None:
        job = self.inspect(job_id)
        return None if job is None else AutonomousTaskSnapshot.from_job(job)

    def ownership(self, job_id: str) -> AutonomousTaskOwnershipState | None:
        return self._ownership_controller.inspect(job_id)

    def update_ownership(self, job_id: str, *, remaining_work: list[str] | tuple[str, ...], next_action: str | None, blocker: str | None = None) -> AutonomousTaskOwnershipUpdateResult:
        return self._ownership_controller.update(job_id, remaining_work=remaining_work, next_action=next_action, blocker=blocker)

    def plan(self, job_id: str) -> AutonomousTaskPlan | None:
        return self._plan_controller.inspect(job_id)

    def set_plan(self, job_id: str, plan: AutonomousTaskPlan) -> AutonomousTaskPlanUpdateResult:
        return self._plan_controller.set_plan(job_id, plan)

    def start_plan_step(self, job_id: str, step_id: str) -> AutonomousTaskPlanUpdateResult:
        return self._plan_controller.start(job_id, step_id)

    def complete_plan_step(self, job_id: str, step_id: str, reason: str | None = None) -> AutonomousTaskPlanUpdateResult:
        return self._plan_controller.complete(job_id, step_id, reason=reason)

    def skip_plan_step(self, job_id: str, step_id: str, reason: str) -> AutonomousTaskPlanUpdateResult:
        return self._plan_controller.skip(job_id, step_id, reason)

    def block_plan_step(self, job_id: str, step_id: str, reason: str) -> AutonomousTaskPlanUpdateResult:
        return self._plan_controller.block(job_id, step_id, reason)

    def pause(self, job_id: str, reason: str) -> AutonomousTaskLifecycleResult:
        job = self._persistence.restore(job_id)
        if job is None:
            raise LookupError(f"autonomous task not found: {job_id}")
        if job.status is not AutonomousJobStatus.RUNNING:
            raise ValueError("only RUNNING tasks can be paused")
        paused = job.pause(reason)
        return AutonomousTaskLifecycleResult(paused, self._persistence.persist(paused))

    def cancel(self, job_id: str, reason: str = "Job cancelled") -> AutonomousTaskLifecycleResult:
        job = self._persistence.restore(job_id)
        if job is None:
            raise LookupError(f"autonomous task not found: {job_id}")
        cancelled = job.cancel(reason)
        return AutonomousTaskLifecycleResult(cancelled, self._persistence.persist(cancelled))

    def tick(self, now: float, *, max_jobs: int = 1, lease_seconds: float = 30.0, max_backoff_multiplier: int = 8) -> tuple[AutonomousRuntimeScheduleResult, ...]:
        return self._scheduler.tick(now, max_jobs=max_jobs, lease_seconds=lease_seconds, max_backoff_multiplier=max_backoff_multiplier)

    def resume(self, job_id: str, *, now: float, interval: float) -> AutonomousTaskResumeResult:
        job = self._persistence.restore(job_id)
        if job is None:
            raise LookupError(f"autonomous task not found: {job_id}")
        if job.status not in {AutonomousJobStatus.WAITING_AUTHORIZATION, AutonomousJobStatus.WAITING_INPUT, AutonomousJobStatus.WAITING_TOOL, AutonomousJobStatus.PAUSED}:
            raise ValueError("only waiting or paused tasks can be resumed")
        resumed = job.resume()
        receipt = self._persistence.persist(resumed)
        schedule = self._scheduler.schedule(resumed.job_id, next_due=now, interval=interval)
        return AutonomousTaskResumeResult(resumed, receipt, schedule)

    def is_working(self, job_id: str) -> bool:
        job = self._persistence.restore(job_id)
        return job is not None and job.status in {AutonomousJobStatus.QUEUED, AutonomousJobStatus.RUNNING}


class SQLiteAutonomousTaskRuntime(AutonomousTaskRuntime):
    """Compose the durable task lifecycle from SQLite-backed runtime primitives."""

    def __init__(self, reason: Callable[[AutonomousJob], Any], *, connection_factory: Callable[[], sqlite3.Connection] = get_connection, registry: ToolRegistry | None = None, progress_evaluator: AutonomousTaskProgressEvaluator | None = None) -> None:
        if not callable(reason):
            raise TypeError("reason must be callable")
        if not callable(connection_factory):
            raise TypeError("connection_factory must be callable")
        if registry is not None and not isinstance(registry, ToolRegistry):
            raise TypeError("registry must be a ToolRegistry or None")
        if progress_evaluator is not None and not callable(getattr(progress_evaluator, "evaluate", None)):
            raise TypeError("progress_evaluator must provide evaluate(before, after, cycle)")
        tool_registry = registry or ToolRegistry()
        tool_service = ToolService(tool_registry)
        job_store = SQLiteAutonomousJobStore(connection_factory)
        schedule_store = SQLiteAutonomousRuntimeScheduleStore(connection_factory)
        persistence = AutonomousJobPersistenceService(job_store)
        worker = AutonomousReasoningWorker(reason)
        gate = AutonomousReasoningToolGate(tool_registry, tool_service)
        coordinator = AutonomousReasoningToolFeedbackCycleCoordinator(worker, gate)
        pulse = AutonomousReasoningFeedbackPulse(persistence, coordinator, progress_evaluator=progress_evaluator)
        run_loop = AutonomousReasoningRunLoop(pulse)
        scheduler = AutonomousRuntimeScheduler(schedule_store, run_loop)
        super().__init__(persistence, scheduler)
        self._job_store = job_store
        self._schedule_store = schedule_store
        self._registry = tool_registry
        self._tool_service = tool_service

    @property
    def registry(self) -> ToolRegistry:
        return self._registry

    @property
    def job_store(self) -> SQLiteAutonomousJobStore:
        return self._job_store

    @property
    def schedule_store(self) -> SQLiteAutonomousRuntimeScheduleStore:
        return self._schedule_store

    @property
    def tool_service(self) -> ToolService:
        return self._tool_service


__all__ = ["AutonomousTaskLifecycleResult", "AutonomousTaskRuntime", "AutonomousTaskSubmissionResult", "AutonomousTaskResumeResult", "AutonomousTaskPlanUpdateResult", "AutonomousTaskOwnershipUpdateResult", "SQLiteAutonomousTaskRuntime"]
