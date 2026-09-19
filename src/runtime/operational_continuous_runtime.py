"""OPS-08 live long-horizon runtime around the canonical JARVIS processor."""
from __future__ import annotations

from dataclasses import dataclass
import threading
import time
from typing import Any, Mapping

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_driver import (
    AutonomousCycleDisposition,
    AutonomousCycleResult,
    AutonomousJobDriver,
)
from src.runtime.autonomous_job_execution_pulse import AutonomousJobExecutionPulse
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceService
from src.runtime.autonomous_job_persistence_sqlite import SQLiteAutonomousJobStore
from src.runtime.autonomous_job_resume import (
    AutonomousJobResumeBoundary,
    AutonomousJobResumeKind,
    AutonomousJobResumeRequest,
)
from src.runtime.autonomous_runtime_schedule_persistence import SQLiteAutonomousRuntimeScheduleStore
from src.runtime.autonomous_runtime_scheduler import (
    AutonomousRuntimeScheduleResult,
    AutonomousRuntimeScheduler,
)


_MAX_RESPONSE_CONTEXT = 6000


def _safe_text(value: Any, maximum: int = _MAX_RESPONSE_CONTEXT) -> str:
    text = str(value if value is not None else "")
    return text if len(text) <= maximum else text[:maximum] + "...[truncated]"


def _safe_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key in (
        "route",
        "stage",
        "success",
        "execution_status",
        "plan_id",
        "operation_id",
        "plan_fingerprint",
        "capability",
        "capability_realized",
        "operational_learning_status",
    ):
        if key in metadata:
            value = metadata[key]
            if isinstance(value, (str, int, float, bool)) or value is None:
                safe[key] = value
    learning = metadata.get("operational_learning")
    if isinstance(learning, Mapping):
        safe["operational_learning"] = {
            key: learning[key]
            for key in (
                "evaluation_status",
                "adaptation_hint_status",
                "guidance",
                "experience_id",
                "evaluation_id",
            )
            if key in learning and isinstance(learning[key], (str, int, float, bool)) or key in learning and learning[key] is None
        }
    return safe


@dataclass(frozen=True)
class OperationalAutonomousRunResult:
    job: AutonomousJob
    pulse: object
    budget_exhausted: bool = False


class JARVISAutonomousWorker:
    """
    Execute one bounded autonomous work cycle through the canonical JARVIS
    processor. This worker does not own policy, authorization, capability
    selection, execution, or learning authority.
    """

    def __init__(
        self,
        processor=None,
        *,
        processor_factory=None,
        max_recovery_attempts: int = 2,
    ) -> None:
        if processor is None and processor_factory is None:
            raise ValueError("processor or processor_factory is required")
        if processor is not None and not callable(getattr(processor, "ask", None)):
            raise TypeError("processor must provide ask(query)")
        if processor_factory is not None and not callable(processor_factory):
            raise TypeError("processor_factory must be callable")
        if isinstance(max_recovery_attempts, bool) or not isinstance(max_recovery_attempts, int):
            raise TypeError("max_recovery_attempts must be an integer")
        if max_recovery_attempts < 0:
            raise ValueError("max_recovery_attempts must be non-negative")
        self._processor = processor
        self._processor_factory = processor_factory
        self._max_recovery_attempts = max_recovery_attempts

    def run_cycle(self, job: AutonomousJob) -> AutonomousCycleResult:
        if not isinstance(job, AutonomousJob):
            raise TypeError("job must be an AutonomousJob")

        prompt = self._build_prompt(job)
        processor = self._processor
        try:
            if self._processor_factory is not None:
                processor = self._processor_factory(job)
            if not callable(getattr(processor, "ask", None)):
                raise TypeError("processor factory must return an object providing ask(query)")
            response = processor.ask(prompt)
            record_turn = getattr(processor, "record_operational_turn", None)
            if callable(record_turn):
                try:
                    record_turn(prompt, _safe_text(getattr(response, "content", "")))
                except Exception as context_exc:
                    # Operational context persistence is observational: never
                    # convert a successful execution into a retry or authority.
                    context_persistence_error = {
                        "error_type": type(context_exc).__name__,
                        "error": str(context_exc),
                    }
                else:
                    context_persistence_error = None
            else:
                context_persistence_error = None
        except Exception as exc:
            attempts = self._recovery_attempts(job)
            if attempts < self._max_recovery_attempts:
                return AutonomousCycleResult(
                    disposition=AutonomousCycleDisposition.CONTINUE,
                    phase="processor_recovery",
                    summary="The canonical processor failed; a bounded retry is scheduled.",
                    observation=f"{type(exc).__name__}: {exc}",
                    context_delta={
                        "recovery_attempts": attempts + 1,
                        "last_error": _safe_text(exc, 2000),
                    },
                )
            return AutonomousCycleResult(
                disposition=AutonomousCycleDisposition.FAIL,
                phase="processor_failure",
                summary="The canonical processor failed and the recovery budget was exhausted.",
                reason=f"{type(exc).__name__}: {exc}",
            )

        metadata = getattr(response, "metadata", {})
        if not isinstance(metadata, Mapping):
            metadata = {}

        route = str(metadata.get("route", "")).upper()
        stage = str(metadata.get("stage", "")).upper()
        execution_status = str(metadata.get("execution_status", "")).upper()
        content = _safe_text(getattr(response, "content", ""))

        response_context = {
            "route": route,
            "stage": stage,
            "execution_status": execution_status,
            "content": content,
            "metadata": _safe_metadata(metadata),
        }
        if context_persistence_error is not None:
            response_context["context_persistence_error"] = context_persistence_error

        if stage == "CONFIRMATION":
            operation_id = metadata.get("operation_id")
            return AutonomousCycleResult(
                disposition=AutonomousCycleDisposition.WAIT_AUTHORIZATION,
                phase="authorization",
                summary="The autonomous task reached an existing JARVIS confirmation boundary.",
                observation=content,
                reason="Explicit confirmation is required before this operation may execute.",
                context_delta={
                    "pending_operation_id": operation_id,
                    "pending_plan_id": metadata.get("plan_id"),
                    "pending_plan_fingerprint": metadata.get("plan_fingerprint"),
                    "last_response": response_context,
                },
            )

        if stage == "CAPABILITY_SELECTION":
            return AutonomousCycleResult(
                disposition=AutonomousCycleDisposition.WAIT_INPUT,
                phase="capability_selection",
                summary="No bounded capability was available for the requested autonomous work.",
                observation=content,
                reason="Additional user guidance is required to identify an available capability.",
                context_delta={"last_response": response_context},
            )

        if stage in {"VALIDATION", "POLICY", "CAPABILITY_INVOCATION", "CAPABILITY_REALIZATION"}:
            return AutonomousCycleResult(
                disposition=AutonomousCycleDisposition.FAIL,
                phase=stage.lower(),
                summary="The canonical JARVIS path rejected the autonomous operation before execution.",
                observation=content,
                reason=content or f"JARVIS returned stage {stage}.",
                context_delta={"last_response": response_context},
            )

        if execution_status == "COMPLETED":
            return AutonomousCycleResult(
                disposition=AutonomousCycleDisposition.COMPLETE,
                phase="execution",
                summary="The autonomous objective produced a completed JARVIS execution.",
                observation=content,
                result=content or "Autonomous execution completed.",
                context_delta={
                    "last_response": response_context,
                    "recovery_attempts": 0,
                },
            )

        if execution_status == "FAILED":
            attempts = self._recovery_attempts(job)
            if attempts < self._max_recovery_attempts:
                return AutonomousCycleResult(
                    disposition=AutonomousCycleDisposition.CONTINUE,
                    phase="bounded_recovery",
                    summary="The autonomous execution failed; a bounded corrective cycle will be attempted.",
                    observation=content,
                    context_delta={
                        "recovery_attempts": attempts + 1,
                        "last_response": response_context,
                        "recovery_instruction": (
                            "Continue the objective using the previous execution result as evidence. "
                            "Do not repeat a failed action unchanged when another bounded path is available."
                        ),
                    },
                )
            return AutonomousCycleResult(
                disposition=AutonomousCycleDisposition.FAIL,
                phase="bounded_recovery",
                summary="Autonomous execution failed and the bounded recovery budget was exhausted.",
                observation=content,
                reason=content or "execution failed",
                context_delta={"last_response": response_context, "recovery_attempts": attempts},
            )

        if route == "TASK":
            return AutonomousCycleResult(
                disposition=AutonomousCycleDisposition.FAIL,
                phase="task",
                summary="The autonomous task did not produce an executable completion result.",
                observation=content,
                reason=content or "JARVIS task did not produce an execution result.",
                context_delta={"last_response": response_context},
            )

        # Non-task responses are useful autonomous read/answer work: the
        # canonical JARVIS processor remains the source of the result.
        return AutonomousCycleResult(
            disposition=AutonomousCycleDisposition.COMPLETE,
            phase="information",
            summary="The canonical JARVIS processor completed an autonomous information cycle.",
            observation=content,
            result=content or "Autonomous information cycle completed.",
            context_delta={"last_response": response_context},
        )

    @staticmethod
    def _recovery_attempts(job: AutonomousJob) -> int:
        value = job.working_context.get("recovery_attempts", 0)
        return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 0

    def _build_prompt(self, job: AutonomousJob) -> str:
        previous = job.working_context.get("last_response")
        recovery_instruction = job.working_context.get("recovery_instruction")
        if not previous and not recovery_instruction:
            return job.goal

        previous_text = _safe_text(previous, 5000) if previous is not None else "No previous response."
        instruction = (
            recovery_instruction
            if isinstance(recovery_instruction, str) and recovery_instruction.strip()
            else "Continue the objective from the latest verified result without repeating completed work unnecessarily."
        )
        return (
            f"Continue the autonomous objective: {job.goal}\n\n"
            f"Operational instruction: {instruction}\n\n"
            f"Previous cycle evidence: {previous_text}"
        )


class OperationalAutonomousRunLoop:
    """Adapt the existing one-pulse autonomous execution boundary for OPS-08."""

    def __init__(self, pulse: AutonomousJobExecutionPulse) -> None:
        if not isinstance(pulse, AutonomousJobExecutionPulse):
            raise TypeError("pulse must be an AutonomousJobExecutionPulse")
        self._pulse = pulse

    def run(
        self,
        job_id: str,
        *,
        max_pulses: int = 1,
        confirmed: bool = False,
    ) -> OperationalAutonomousRunResult:
        if isinstance(max_pulses, bool) or not isinstance(max_pulses, int) or max_pulses <= 0:
            raise ValueError("max_pulses must be positive")
        if not isinstance(confirmed, bool):
            raise TypeError("confirmed must be a bool")

        current = None
        for index in range(max_pulses):
            pulse = self._pulse.pulse(job_id)
            current = pulse.job
            if pulse.waiting or current.terminal:
                return OperationalAutonomousRunResult(current, pulse, False)

        assert current is not None
        return OperationalAutonomousRunResult(current, pulse, True)


class OperationalContinuousRuntime:
    """
    Durable continuous runtime composed around the live JARVIS processor.

    The runtime owns scheduling, durable autonomous job lifecycle, and
    background cadence. It does not own policy, authorization, capability
    selection, tool execution, or learning authority.
    """

    def __init__(
        self,
        processor=None,
        *,
        processor_factory=None,
        connection_factory=None,
        max_recovery_attempts: int = 2,
        poll_interval: float = 1.0,
    ) -> None:
        if processor is None and processor_factory is None:
            raise ValueError("processor or processor_factory is required")
        if processor is not None and not callable(getattr(processor, "ask", None)):
            raise TypeError("processor must provide ask(query)")
        if processor_factory is not None and not callable(processor_factory):
            raise TypeError("processor_factory must be callable")
        if connection_factory is not None and not callable(connection_factory):
            raise TypeError("connection_factory must be callable")
        if isinstance(poll_interval, bool) or not isinstance(poll_interval, (int, float)) or poll_interval <= 0:
            raise ValueError("poll_interval must be positive")

        from src.database import get_connection
        factory = connection_factory or get_connection
        self._persistence = AutonomousJobPersistenceService(
            SQLiteAutonomousJobStore(factory)
        )
        self._schedule_store = SQLiteAutonomousRuntimeScheduleStore(factory)
        self._worker = JARVISAutonomousWorker(
            processor,
            processor_factory=processor_factory,
            max_recovery_attempts=max_recovery_attempts,
        )
        self._pulse = AutonomousJobExecutionPulse(
            self._persistence,
            AutonomousJobDriver(self._worker),
        )
        self._run_loop = OperationalAutonomousRunLoop(self._pulse)
        self._scheduler = AutonomousRuntimeScheduler(
            self._schedule_store,
            self._run_loop,
        )
        self._resume_boundary = AutonomousJobResumeBoundary(self._persistence)
        self._poll_interval = float(poll_interval)
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.RLock()
        self._pending_operations: dict[str, str] = {}

    @property
    def scheduler(self) -> AutonomousRuntimeScheduler:
        return self._scheduler

    @property
    def persistence(self) -> AutonomousJobPersistenceService:
        return self._persistence

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def submit(
        self,
        goal: str,
        *,
        interval: float = 1.0,
        now: float | None = None,
        job_id: str | None = None,
        max_steps: int = 32,
        working_context: Mapping[str, Any] | None = None,
    ) -> AutonomousJob:
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("goal must be a non-empty string")
        if isinstance(interval, bool) or not isinstance(interval, (int, float)) or interval <= 0:
            raise ValueError("interval must be positive")
        current_time = time.time() if now is None else now
        if isinstance(current_time, bool) or not isinstance(current_time, (int, float)):
            raise TypeError("now must be numeric")
        candidate = AutonomousJob.create(
            goal,
            job_id=job_id,
            max_steps=max_steps,
            working_context=working_context,
        )
        if self._persistence.restore(candidate.job_id) is not None:
            raise ValueError(f"autonomous job already exists: {candidate.job_id}")
        self._persistence.persist(candidate)
        self._scheduler.schedule(candidate.job_id, next_due=float(current_time), interval=float(interval))
        return candidate

    def inspect(self, job_id: str) -> AutonomousJob | None:
        return self._persistence.restore(job_id)

    def list_jobs(self, *, limit: int = 100) -> tuple[AutonomousJob, ...]:
        """Return bounded durable job snapshots for observation surfaces."""
        return self._persistence.list_jobs(limit=limit)

    def tick(
        self,
        now: float | None = None,
        *,
        max_jobs: int = 1,
        lease_seconds: float = 30.0,
        max_backoff_multiplier: int = 8,
    ) -> tuple[AutonomousRuntimeScheduleResult, ...]:
        current_time = time.time() if now is None else now
        self.reconcile_durable_state(current_time)
        results = self._scheduler.tick(
            current_time,
            max_jobs=max_jobs,
            lease_seconds=lease_seconds,
            max_backoff_multiplier=max_backoff_multiplier,
        )
        for result in results:
            job = getattr(getattr(result, "run", None), "job", None)
            if job is None or job.status is not AutonomousJobStatus.WAITING_AUTHORIZATION:
                continue
            operation_id = job.working_context.get("pending_operation_id")
            if isinstance(operation_id, str) and operation_id.strip():
                self._pending_operations[operation_id] = job.job_id
        return results

    def reconcile_durable_state(self, now: float) -> dict[str, int]:
        """Repair safe job/schedule drift without reviving RUNNING work."""
        if isinstance(now, bool) or not isinstance(now, (int, float)):
            raise TypeError("now must be numeric")

        jobs = self._persistence.list_jobs(limit=500)
        schedules = self._schedule_store.list_all(limit=500)
        jobs_by_id = {job.job_id: job for job in jobs}
        schedules_by_id = {schedule.job_id: schedule for schedule in schedules}

        removed_schedules = 0
        restored_schedules = 0

        for job in jobs:
            schedule = schedules_by_id.get(job.job_id)
            if job.terminal or job.resumable:
                if schedule is not None and self._schedule_store.delete(job.job_id):
                    removed_schedules += 1
                continue

            if job.status is AutonomousJobStatus.QUEUED and schedule is None:
                self._schedule_store.save(
                    __import__("src.runtime.autonomous_runtime_scheduler", fromlist=["AutonomousRuntimeSchedule"]).AutonomousRuntimeSchedule(
                        job_id=job.job_id,
                        next_due=float(now),
                        interval=max(self._poll_interval, 1.0),
                    )
                )
                restored_schedules += 1

        for schedule in schedules:
            if schedule.job_id not in jobs_by_id and self._schedule_store.delete(schedule.job_id):
                removed_schedules += 1

        return {
            "queued_schedules_restored": restored_schedules,
            "stale_schedules_removed": removed_schedules,
        }

    def reconcile_confirmation(self, metadata: Mapping[str, Any]) -> AutonomousJob | None:
        """Synchronize an externally confirmed JARVIS operation into its waiting job."""
        if not isinstance(metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        operation_id = metadata.get("operation_id")
        if not isinstance(operation_id, str) or not operation_id.strip():
            return None
        job_id = self._pending_operations.get(operation_id)
        if job_id is None:
            job_id = self._find_waiting_authorization_job(operation_id)
            if job_id is not None:
                self._pending_operations[operation_id] = job_id
        if job_id is None:
            return None

        job = self.inspect(job_id)
        if job is None or job.status is not AutonomousJobStatus.WAITING_AUTHORIZATION:
            self._pending_operations.pop(operation_id, None)
            return None

        command = str(metadata.get("command", "")).upper()
        execution_status = str(metadata.get("execution_status", "")).upper()
        success = metadata.get("success")
        if command != "CONFIRM":
            return None
        if success is False:
            return None
        if execution_status and execution_status != "COMPLETED":
            return None

        completed = job.resume()
        completed = completed.complete(
            str(metadata.get("result") or "Autonomous authorization completed through JARVIS.")
        )
        self._persistence.persist(completed)
        self._pending_operations.pop(operation_id, None)
        return completed

    def _find_waiting_authorization_job(self, operation_id: str) -> str | None:
        """Find a persisted authorization wait when the in-memory map was lost."""
        for job in self._persistence.list_jobs(limit=500):
            if job.status is not AutonomousJobStatus.WAITING_AUTHORIZATION:
                continue
            pending = job.working_context.get("pending_operation_id")
            if pending == operation_id:
                return job.job_id
        return None

    def resume(
        self,
        job_id: str,
        *,
        confirmed: bool = False,
        input_context: Mapping[str, Any] | None = None,
        now: float | None = None,
        interval: float = 1.0,
    ) -> AutonomousJob:
        job = self.inspect(job_id)
        if job is None:
            raise LookupError(f"autonomous job not found: {job_id}")
        kinds = {
            AutonomousJobStatus.WAITING_AUTHORIZATION: AutonomousJobResumeKind.AUTHORIZATION,
            AutonomousJobStatus.WAITING_INPUT: AutonomousJobResumeKind.INPUT,
            AutonomousJobStatus.WAITING_TOOL: AutonomousJobResumeKind.TOOL,
            AutonomousJobStatus.PAUSED: AutonomousJobResumeKind.PAUSE,
        }
        kind = kinds.get(job.status)
        if kind is None:
            raise ValueError("only waiting or paused autonomous jobs can be resumed")

        resumed = self._resume_boundary.resume(
            AutonomousJobResumeRequest(
                job_id=job_id,
                kind=kind,
                confirmed=confirmed,
                input_context=input_context,
            )
        )
        current_time = time.time() if now is None else now
        self._scheduler.schedule(
            job_id,
            next_due=float(current_time),
            interval=float(interval),
        )
        return resumed.job

    def cancel(self, job_id: str, reason: str = "Autonomous job cancelled") -> AutonomousJob:
        job = self.inspect(job_id)
        if job is None:
            raise LookupError(f"autonomous job not found: {job_id}")
        cancelled = job.cancel(reason)
        self._persistence.persist(cancelled)
        self._schedule_store.delete(job_id)
        return cancelled

    def start(self) -> None:
        with self._lock:
            if self.running:
                return
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run_background,
                name="jarvis-autonomous-runtime",
                daemon=True,
            )
            self._thread.start()

    def stop(self) -> None:
        with self._lock:
            thread = self._thread
            if thread is None:
                return
            self._stop_event.set()
        if thread is not threading.current_thread():
            thread.join(timeout=max(1.0, self._poll_interval * 4))
        with self._lock:
            if self._thread is thread:
                self._thread = None

    def _run_background(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.tick()
            except Exception:
                # Scheduler failures are contained by the bounded background
                # loop; durable worker/scheduler state remains inspectable.
                pass
            self._stop_event.wait(self._poll_interval)


__all__ = [
    "JARVISAutonomousWorker",
    "OperationalAutonomousRunLoop",
    "OperationalAutonomousRunResult",
    "OperationalContinuousRuntime",
]
