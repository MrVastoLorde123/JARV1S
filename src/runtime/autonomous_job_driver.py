"""M55 provider-neutral driver loop for long-running JARVIS jobs."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol

from src.runtime.autonomous_job import (
    AutonomousJob,
    AutonomousJobStatus,
)


class AutonomousJobDriverValidationError(ValueError):
    """Raised when an autonomous job driver contract is violated."""


class AutonomousCycleDisposition(str, Enum):
    CONTINUE = "CONTINUE"
    WAIT_AUTHORIZATION = "WAIT_AUTHORIZATION"
    WAIT_INPUT = "WAIT_INPUT"
    WAIT_TOOL = "WAIT_TOOL"
    PAUSE = "PAUSE"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


@dataclass(frozen=True)
class AutonomousCycleResult:
    """One explicit worker result consumed by the driver."""

    disposition: AutonomousCycleDisposition
    phase: str
    summary: str
    observation: str = ""
    context_delta: Mapping[str, Any] = field(default_factory=dict)
    reason: str | None = None
    result: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, AutonomousCycleDisposition):
            raise AutonomousJobDriverValidationError(
                "disposition must be an AutonomousCycleDisposition"
            )
        for field_name, value, maximum in (
            ("phase", self.phase, 256),
            ("summary", self.summary, 2048),
        ):
            if not isinstance(value, str) or not value.strip():
                raise AutonomousJobDriverValidationError(
                    f"{field_name} must be a non-empty string"
                )
            if len(value) > maximum:
                raise AutonomousJobDriverValidationError(
                    f"{field_name} exceeds maximum length of {maximum}"
                )
        if not isinstance(self.observation, str) or len(self.observation) > 16384:
            raise AutonomousJobDriverValidationError(
                "observation must be a bounded string"
            )
        if not isinstance(self.context_delta, Mapping):
            raise AutonomousJobDriverValidationError(
                "context_delta must be a mapping"
            )
        if self.reason is not None and (
            not isinstance(self.reason, str) or not self.reason.strip()
        ):
            raise AutonomousJobDriverValidationError(
                "reason must be a non-empty string or None"
            )
        if self.result is not None and (
            not isinstance(self.result, str) or not self.result.strip()
        ):
            raise AutonomousJobDriverValidationError(
                "result must be a non-empty string or None"
            )

        waiting_dispositions = {
            AutonomousCycleDisposition.WAIT_AUTHORIZATION,
            AutonomousCycleDisposition.WAIT_INPUT,
            AutonomousCycleDisposition.WAIT_TOOL,
            AutonomousCycleDisposition.PAUSE,
        }
        if self.disposition in waiting_dispositions and not self.reason:
            raise AutonomousJobDriverValidationError(
                "waiting dispositions require a reason"
            )
        if self.disposition is AutonomousCycleDisposition.COMPLETE and not self.result:
            raise AutonomousJobDriverValidationError(
                "COMPLETE disposition requires a result"
            )
        if self.disposition is AutonomousCycleDisposition.FAIL and not self.reason:
            raise AutonomousJobDriverValidationError(
                "FAIL disposition requires a reason"
            )


class AutonomousJobWorker(Protocol):
    """Injected reasoning/action adapter for one autonomous work cycle."""

    def run_cycle(self, job: AutonomousJob) -> AutonomousCycleResult:
        """Perform one bounded reasoning/action/observation cycle."""
        ...


class AutonomousJobDriver:
    """Advance autonomous jobs without owning provider or tool authority."""

    def __init__(self, worker: AutonomousJobWorker) -> None:
        if not hasattr(worker, "run_cycle") or not callable(worker.run_cycle):
            raise TypeError("worker must provide a callable run_cycle method")
        self._worker = worker

    def tick(self, job: AutonomousJob) -> AutonomousJob:
        """Advance a job by at most one worker cycle."""
        if not isinstance(job, AutonomousJob):
            raise TypeError("job must be an AutonomousJob")
        if job.terminal:
            return job
        if job.status is not AutonomousJobStatus.RUNNING:
            return job

        try:
            cycle = self._worker.run_cycle(job)
        except Exception as exc:
            return job.fail(f"autonomous worker cycle failed: {type(exc).__name__}: {exc}")

        if not isinstance(cycle, AutonomousCycleResult):
            return job.fail(
                "autonomous worker returned an invalid cycle result: "
                f"{type(cycle).__name__}"
            )

        stepped = job.record_step(
            phase=cycle.phase,
            summary=cycle.summary,
            observation=cycle.observation,
            context_delta=cycle.context_delta,
        )
        return self._apply_disposition(stepped, cycle)

    def run(
        self,
        job: AutonomousJob,
        *,
        max_cycles: int | None = None,
    ) -> AutonomousJob:
        """Drive a running job until it reaches a stopping condition."""
        if not isinstance(job, AutonomousJob):
            raise TypeError("job must be an AutonomousJob")
        if max_cycles is not None and (
            isinstance(max_cycles, bool) or not isinstance(max_cycles, int) or max_cycles <= 0
        ):
            raise ValueError("max_cycles must be a positive integer or None")

        current = job
        cycles = 0
        while current.status is AutonomousJobStatus.RUNNING:
            if max_cycles is not None and cycles >= max_cycles:
                return current.pause("driver cycle limit reached")
            current = self.tick(current)
            cycles += 1
        return current

    @staticmethod
    def _apply_disposition(
        job: AutonomousJob,
        cycle: AutonomousCycleResult,
    ) -> AutonomousJob:
        if cycle.disposition is AutonomousCycleDisposition.CONTINUE:
            return job
        if cycle.disposition is AutonomousCycleDisposition.WAIT_AUTHORIZATION:
            return job.wait_for_authorization(cycle.reason or "authorization required")
        if cycle.disposition is AutonomousCycleDisposition.WAIT_INPUT:
            return job.wait_for_input(cycle.reason or "input required")
        if cycle.disposition is AutonomousCycleDisposition.WAIT_TOOL:
            return job.wait_for_tool(cycle.reason or "tool completion required")
        if cycle.disposition is AutonomousCycleDisposition.PAUSE:
            return job.pause(cycle.reason or "job paused")
        if cycle.disposition is AutonomousCycleDisposition.COMPLETE:
            return job.complete(cycle.result or "job completed")
        if cycle.disposition is AutonomousCycleDisposition.FAIL:
            return job.fail(cycle.reason or "job failed")
        raise AutonomousJobDriverValidationError(
            f"unsupported cycle disposition: {cycle.disposition!r}"
        )


__all__ = [
    "AutonomousCycleDisposition",
    "AutonomousCycleResult",
    "AutonomousJobDriver",
    "AutonomousJobDriverValidationError",
    "AutonomousJobWorker",
]
