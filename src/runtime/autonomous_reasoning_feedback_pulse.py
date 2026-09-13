from __future__ import annotations

from dataclasses import dataclass

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_driver import AutonomousCycleDisposition
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceReceipt, AutonomousJobPersistenceService
from src.runtime.autonomous_reasoning_tool_feedback_cycle import AutonomousReasoningToolFeedbackCycle, AutonomousReasoningToolFeedbackCycleCoordinator
from src.runtime.autonomous_task_progress import (
    AutonomousTaskProgressEvaluator,
    AutonomousTaskProgressResult,
    DeterministicAutonomousTaskProgressEvaluator,
)


@dataclass(frozen=True)
class AutonomousReasoningFeedbackPulseResult:
    job: AutonomousJob
    cycle: AutonomousReasoningToolFeedbackCycle | None
    persistence_receipt: AutonomousJobPersistenceReceipt | None
    progressed: bool
    progress: AutonomousTaskProgressResult | None = None

    @property
    def waiting(self) -> bool:
        return self.job.status in {
            AutonomousJobStatus.WAITING_AUTHORIZATION,
            AutonomousJobStatus.WAITING_INPUT,
            AutonomousJobStatus.WAITING_TOOL,
            AutonomousJobStatus.PAUSED,
        }


class AutonomousReasoningFeedbackPulse:
    def __init__(
        self,
        persistence: AutonomousJobPersistenceService,
        coordinator: AutonomousReasoningToolFeedbackCycleCoordinator,
        progress_evaluator: AutonomousTaskProgressEvaluator | None = None,
    ) -> None:
        if not isinstance(persistence, AutonomousJobPersistenceService):
            raise TypeError("persistence must be an AutonomousJobPersistenceService")
        if not isinstance(coordinator, AutonomousReasoningToolFeedbackCycleCoordinator):
            raise TypeError("coordinator must be an AutonomousReasoningToolFeedbackCycleCoordinator")
        if progress_evaluator is not None and not callable(getattr(progress_evaluator, "evaluate", None)):
            raise TypeError("progress_evaluator must provide evaluate(before, after, cycle)")
        self._persistence = persistence
        self._coordinator = coordinator
        self._progress_evaluator = progress_evaluator or DeterministicAutonomousTaskProgressEvaluator()

    def pulse(self, job_id: str, *, confirmed: bool = False) -> AutonomousReasoningFeedbackPulseResult:
        if not isinstance(confirmed, bool):
            raise TypeError("confirmed must be a bool")
        job = self._persistence.restore(job_id)
        if job is None:
            raise LookupError(f"autonomous job not found: {job_id}")
        current = job.start() if job.status is AutonomousJobStatus.QUEUED else job
        if current.status is not AutonomousJobStatus.RUNNING:
            return AutonomousReasoningFeedbackPulseResult(current, None, None, current != job, None)
        cycle = self._coordinator.run_cycle(current, confirmed=confirmed)
        next_job = current.record_step(
            phase=cycle.cycle.phase,
            summary=cycle.cycle.summary,
            observation=cycle.cycle.observation,
            context_delta=cycle.cycle.context_delta,
        )
        d = cycle.cycle.disposition
        if d is AutonomousCycleDisposition.WAIT_AUTHORIZATION:
            next_job = next_job.wait_for_authorization(cycle.cycle.reason or "authorization required")
        elif d is AutonomousCycleDisposition.WAIT_INPUT:
            next_job = next_job.wait_for_input(cycle.cycle.reason or "input required")
        elif d is AutonomousCycleDisposition.WAIT_TOOL:
            next_job = next_job.wait_for_tool(cycle.cycle.reason or "tool completion required")
        elif d is AutonomousCycleDisposition.PAUSE:
            next_job = next_job.pause(cycle.cycle.reason or "job paused")
        elif d is AutonomousCycleDisposition.COMPLETE:
            next_job = next_job.complete(cycle.cycle.result or "job completed")
        elif d is AutonomousCycleDisposition.FAIL:
            next_job = next_job.fail(cycle.cycle.reason or "job failed")

        progress = self._progress_evaluator.evaluate(current, next_job, cycle.cycle)
        next_job = next_job.with_working_context({"task_progress": progress.to_context()}) if not next_job.terminal else next_job
        progressed = next_job != job
        receipt = self._persistence.persist(next_job) if progressed else None
        return AutonomousReasoningFeedbackPulseResult(next_job, cycle, receipt, progressed, progress)


__all__ = ["AutonomousReasoningFeedbackPulse", "AutonomousReasoningFeedbackPulseResult"]
