from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_driver import AutonomousCycleDisposition
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceReceipt, AutonomousJobPersistenceService
from src.runtime.autonomous_reasoning_tool_feedback_cycle import AutonomousReasoningToolFeedbackCycle, AutonomousReasoningToolFeedbackCycleCoordinator
from src.runtime.autonomous_task_plan import AutonomousTaskPlan, AutonomousTaskPlanValidationError
from src.runtime.autonomous_task_progress import AutonomousTaskProgressEvaluator, AutonomousTaskProgressResult, DeterministicAutonomousTaskProgressEvaluator


_RUNTIME_RESUME_AUTHORIZATION_KEY = "_runtime_resume_authorization"


@dataclass(frozen=True)
class AutonomousReasoningFeedbackPulseResult:
    job: AutonomousJob
    cycle: AutonomousReasoningToolFeedbackCycle | None
    persistence_receipt: AutonomousJobPersistenceReceipt | None
    progressed: bool
    progress: AutonomousTaskProgressResult | None = None

    @property
    def waiting(self) -> bool:
        return self.job.status in {AutonomousJobStatus.WAITING_AUTHORIZATION, AutonomousJobStatus.WAITING_INPUT, AutonomousJobStatus.WAITING_TOOL, AutonomousJobStatus.PAUSED}


class AutonomousReasoningFeedbackPulse:
    def __init__(self, persistence: AutonomousJobPersistenceService, coordinator: AutonomousReasoningToolFeedbackCycleCoordinator, progress_evaluator: AutonomousTaskProgressEvaluator | None = None) -> None:
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
        if current.step_count >= current.max_steps:
            failed = current.fail("maximum autonomous step budget exhausted")
            receipt = self._persistence.persist(failed)
            return AutonomousReasoningFeedbackPulseResult(failed, None, receipt, True, None)

        runtime_resume_authorization = current.working_context.get(_RUNTIME_RESUME_AUTHORIZATION_KEY)
        continuation_confirmed = confirmed and runtime_resume_authorization is None
        cycle = self._coordinator.run_cycle(
            current,
            confirmed=continuation_confirmed,
            authorization_token=runtime_resume_authorization if isinstance(runtime_resume_authorization, dict) else None,
        )
        cycle_context = dict(cycle.cycle.context_delta)
        if runtime_resume_authorization is not None:
            cycle_context[_RUNTIME_RESUME_AUTHORIZATION_KEY] = None
        proposed_plan = cycle_context.pop("task_plan_proposal", None)
        if proposed_plan is not None:
            if "task_plan" in current.working_context:
                cycle_context["task_plan_proposal"] = proposed_plan
            else:
                cycle_context["task_plan"] = proposed_plan

        next_job = current.record_step(
            phase=cycle.cycle.phase,
            summary=cycle.cycle.summary,
            observation=cycle.cycle.observation,
            context_delta=cycle_context,
        )
        progress = self._progress_evaluator.evaluate(current, next_job, cycle.cycle)
        progress_context = {"task_progress": progress.to_context()}
        d = cycle.cycle.disposition
        completion_rejected = False
        if d is AutonomousCycleDisposition.COMPLETE and "task_plan" in current.working_context:
            try:
                plan = AutonomousTaskPlan.from_mapping(current.working_context["task_plan"])
            except (TypeError, AutonomousTaskPlanValidationError) as exc:
                failed = next_job.fail(
                    f"runtime-owned task plan could not be validated during completion: {type(exc).__name__}: {exc}",
                    context_delta=progress_context,
                )
                receipt = self._persistence.persist(failed)
                return AutonomousReasoningFeedbackPulseResult(failed, cycle, receipt, True, progress)
            if not plan.complete:
                completion_rejected = True
                progress_context["task_completion_rejected"] = {
                    "reason": "runtime-owned task plan is not complete",
                    "remaining_steps": [step.to_dict() for step in plan.steps if not step.terminal],
                }
                d = AutonomousCycleDisposition.CONTINUE
        if d is AutonomousCycleDisposition.WAIT_AUTHORIZATION:
            next_job = next_job.wait_for_authorization(cycle.cycle.reason or "authorization required")
        elif d is AutonomousCycleDisposition.WAIT_INPUT:
            next_job = next_job.wait_for_input(cycle.cycle.reason or "input required")
        elif d is AutonomousCycleDisposition.WAIT_TOOL:
            next_job = next_job.wait_for_tool(cycle.cycle.reason or "tool completion required")
        elif d is AutonomousCycleDisposition.PAUSE:
            next_job = next_job.pause(cycle.cycle.reason or "job paused")
        elif d is AutonomousCycleDisposition.COMPLETE:
            next_job = next_job.complete(cycle.cycle.result or "job completed", context_delta=progress_context)
        elif d is AutonomousCycleDisposition.FAIL:
            next_job = next_job.fail(cycle.cycle.reason or "job failed", context_delta=progress_context)
        else:
            next_job = next_job.with_working_context(progress_context)

        progressed = next_job != job or completion_rejected
        receipt = self._persistence.persist(next_job) if progressed else None
        return AutonomousReasoningFeedbackPulseResult(next_job, cycle, receipt, progressed, progress)


__all__ = ["AutonomousReasoningFeedbackPulse", "AutonomousReasoningFeedbackPulseResult"]
