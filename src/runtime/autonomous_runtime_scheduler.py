from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.runtime.autonomous_job import AutonomousJobStatus
from src.runtime.autonomous_reasoning_run_loop import AutonomousReasoningRunLoop, AutonomousReasoningRunResult


@dataclass(frozen=True)
class AutonomousRuntimeSchedule:
    job_id: str
    next_due: float
    interval: float
    max_pulses: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.job_id, str) or not self.job_id.strip():
            raise ValueError("job_id must be non-empty")
        if isinstance(self.next_due, bool) or not isinstance(self.next_due, (int, float)):
            raise TypeError("next_due must be numeric")
        if isinstance(self.interval, bool) or not isinstance(self.interval, (int, float)) or self.interval <= 0:
            raise ValueError("interval must be positive")
        if isinstance(self.max_pulses, bool) or not isinstance(self.max_pulses, int) or self.max_pulses <= 0:
            raise ValueError("max_pulses must be positive")


class AutonomousRuntimeScheduleStore(Protocol):
    def save(self, schedule: AutonomousRuntimeSchedule) -> None: ...
    def load_due(self, now: float) -> list[AutonomousRuntimeSchedule]: ...
    def delete(self, job_id: str) -> None: ...


@dataclass(frozen=True)
class AutonomousRuntimeScheduleResult:
    schedule: AutonomousRuntimeSchedule
    run: AutonomousReasoningRunResult
    removed: bool


class AutonomousRuntimeScheduler:
    def __init__(self, store: AutonomousRuntimeScheduleStore, run_loop: AutonomousReasoningRunLoop) -> None:
        if not hasattr(store, "save") or not hasattr(store, "load_due") or not hasattr(store, "delete"):
            raise TypeError("store must implement save, load_due, and delete")
        if not isinstance(run_loop, AutonomousReasoningRunLoop):
            raise TypeError("run_loop must be an AutonomousReasoningRunLoop")
        self._store = store
        self._run_loop = run_loop

    def schedule(self, job_id: str, *, next_due: float, interval: float, max_pulses: int = 1) -> AutonomousRuntimeSchedule:
        schedule = AutonomousRuntimeSchedule(job_id, next_due, interval, max_pulses)
        self._store.save(schedule)
        return schedule

    def tick(self, now: float, *, max_jobs: int = 1) -> tuple[AutonomousRuntimeScheduleResult, ...]:
        if isinstance(now, bool) or not isinstance(now, (int, float)):
            raise TypeError("now must be numeric")
        if isinstance(max_jobs, bool) or not isinstance(max_jobs, int) or max_jobs <= 0:
            raise ValueError("max_jobs must be positive")
        due = self._store.load_due(now)[:max_jobs]
        results: list[AutonomousRuntimeScheduleResult] = []
        for schedule in due:
            run = self._run_loop.run(schedule.job_id, max_pulses=schedule.max_pulses)
            terminal = run.job.status in {AutonomousJobStatus.COMPLETED, AutonomousJobStatus.FAILED, AutonomousJobStatus.CANCELLED}
            waiting = run.job.resumable
            removed = terminal or waiting
            if removed:
                self._store.delete(schedule.job_id)
            else:
                self._store.save(AutonomousRuntimeSchedule(schedule.job_id, now + schedule.interval, schedule.interval, schedule.max_pulses))
            results.append(AutonomousRuntimeScheduleResult(schedule, run, removed))
        return tuple(results)


__all__ = ["AutonomousRuntimeSchedule", "AutonomousRuntimeScheduleStore", "AutonomousRuntimeScheduleResult", "AutonomousRuntimeScheduler"]
