"""Application-level lifecycle for durable autonomous task ownership."""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from typing import Any, Callable

from src.database import get_connection
from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import (
    AutonomousJobPersistenceReceipt,
    AutonomousJobPersistenceService,
)
from src.runtime.autonomous_job_persistence_sqlite import SQLiteAutonomousJobStore
from src.runtime.autonomous_reasoning_feedback_pulse import AutonomousReasoningFeedbackPulse
from src.runtime.autonomous_reasoning_run_loop import AutonomousReasoningRunLoop
from src.runtime.autonomous_reasoning_tool_feedback_cycle import AutonomousReasoningToolFeedbackCycleCoordinator
from src.runtime.autonomous_reasoning_tool_gate import AutonomousReasoningToolGate
from src.runtime.autonomous_reasoning_worker import AutonomousReasoningWorker
from src.runtime.autonomous_runtime_schedule_persistence import SQLiteAutonomousRuntimeScheduleStore
from src.runtime.autonomous_runtime_scheduler import (
    AutonomousRuntimeSchedule,
    AutonomousRuntimeScheduleResult,
    AutonomousRuntimeScheduler,
)
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


class AutonomousTaskRuntime:
    """Own the application lifecycle that turns a goal into durable ongoing work."""

    def __init__(
        self,
        persistence: AutonomousJobPersistenceService,
        scheduler: AutonomousRuntimeScheduler,
    ) -> None:
        if not isinstance(persistence, AutonomousJobPersistenceService):
            raise TypeError("persistence must be an AutonomousJobPersistenceService")
        if not isinstance(scheduler, AutonomousRuntimeScheduler):
            raise TypeError("scheduler must be an AutonomousRuntimeScheduler")
        self._persistence = persistence
        self._scheduler = scheduler

    def submit(
        self,
        goal: str,
        *,
        now: float,
        interval: float,
        job_id: str | None = None,
        max_steps: int = 32,
        working_context: dict[str, object] | None = None,
    ) -> AutonomousTaskSubmissionResult:
        job = AutonomousJob.create(
            goal,
            job_id=job_id,
            max_steps=max_steps,
            working_context=working_context,
        )
        receipt = self._persistence.persist(job)
        schedule = self._scheduler.schedule(
            job.job_id,
            next_due=now,
            interval=interval,
        )
        return AutonomousTaskSubmissionResult(job, receipt, schedule)

    def inspect(self, job_id: str) -> AutonomousJob | None:
        """Return the durable task snapshot without changing its state."""
        return self._persistence.restore(job_id)

    def tick(
        self,
        now: float,
        *,
        max_jobs: int = 1,
        lease_seconds: float = 30.0,
        max_backoff_multiplier: int = 8,
    ) -> tuple[AutonomousRuntimeScheduleResult, ...]:
        """Run one bounded scheduler cycle against durable task ownership."""
        return self._scheduler.tick(
            now,
            max_jobs=max_jobs,
            lease_seconds=lease_seconds,
            max_backoff_multiplier=max_backoff_multiplier,
        )

    def resume(
        self,
        job_id: str,
        *,
        now: float,
        interval: float,
    ) -> AutonomousTaskResumeResult:
        """Explicitly resume a waiting task and re-arm its durable schedule."""
        job = self._persistence.restore(job_id)
        if job is None:
            raise LookupError(f"autonomous task not found: {job_id}")
        if job.status not in {
            AutonomousJobStatus.WAITING_AUTHORIZATION,
            AutonomousJobStatus.WAITING_INPUT,
            AutonomousJobStatus.WAITING_TOOL,
            AutonomousJobStatus.PAUSED,
        }:
            raise ValueError("only waiting or paused tasks can be resumed")

        resumed = job.resume()
        receipt = self._persistence.persist(resumed)
        schedule = self._scheduler.schedule(
            resumed.job_id,
            next_due=now,
            interval=interval,
        )
        return AutonomousTaskResumeResult(resumed, receipt, schedule)

    def is_working(self, job_id: str) -> bool:
        """Return whether the durable task is currently able to perform another cycle."""
        job = self._persistence.restore(job_id)
        return job is not None and job.status in {
            AutonomousJobStatus.QUEUED,
            AutonomousJobStatus.RUNNING,
        }


class SQLiteAutonomousTaskRuntime(AutonomousTaskRuntime):
    """Compose the durable task lifecycle from SQLite-backed runtime primitives."""

    def __init__(
        self,
        reason: Callable[[AutonomousJob], Any],
        *,
        connection_factory: Callable[[], sqlite3.Connection] = get_connection,
        registry: ToolRegistry | None = None,
    ) -> None:
        if not callable(reason):
            raise TypeError("reason must be callable")
        if not callable(connection_factory):
            raise TypeError("connection_factory must be callable")
        if registry is not None and not isinstance(registry, ToolRegistry):
            raise TypeError("registry must be a ToolRegistry or None")

        tool_registry = registry or ToolRegistry()
        tool_service = ToolService(tool_registry)
        persistence = AutonomousJobPersistenceService(
            SQLiteAutonomousJobStore(connection_factory)
        )
        worker = AutonomousReasoningWorker(reason)
        gate = AutonomousReasoningToolGate(tool_registry, tool_service)
        coordinator = AutonomousReasoningToolFeedbackCycleCoordinator(worker, gate)
        pulse = AutonomousReasoningFeedbackPulse(persistence, coordinator)
        run_loop = AutonomousReasoningRunLoop(pulse)
        scheduler = AutonomousRuntimeScheduler(
            SQLiteAutonomousRuntimeScheduleStore(connection_factory),
            run_loop,
        )

        super().__init__(persistence, scheduler)
        self._registry = tool_registry

    @property
    def registry(self) -> ToolRegistry:
        """Return the tool registry owned by this runtime."""
        return self._registry


__all__ = [
    "AutonomousTaskRuntime",
    "AutonomousTaskSubmissionResult",
    "AutonomousTaskResumeResult",
    "SQLiteAutonomousTaskRuntime",
]
