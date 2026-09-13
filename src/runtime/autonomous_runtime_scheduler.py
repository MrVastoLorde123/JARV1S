from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Protocol

from src.runtime.autonomous_job import AutonomousJobStatus
from src.runtime.autonomous_reasoning_run_loop import AutonomousReasoningRunLoop, AutonomousReasoningRunResult


@dataclass(frozen=True)
class AutonomousRuntimeSchedule:
    job_id: str
    next_due: float
    interval: float
    claim_token: str | None = None
    lease_until: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.job_id, str) or not self.job_id.strip():
            raise ValueError("job_id must be non-empty")
        if isinstance(self.next_due, bool) or not isinstance(self.next_due, (int, float)):
            raise TypeError("next_due must be numeric")
        if isinstance(self.interval, bool) or not isinstance(self.interval, (int, float)) or self.interval <= 0:
            raise ValueError("interval must be positive")
        if self.claim_token is not None and (not isinstance(self.claim_token, str) or not self.claim_token.strip()):
            raise ValueError("claim_token must be non-empty or None")
        if self.lease_until is not None and (isinstance(self.lease_until, bool) or not isinstance(self.lease_until, (int, float))):
            raise TypeError("lease_until must be numeric or None")
        if (self.claim_token is None) != (self.lease_until is None):
            raise ValueError("claim_token and lease_until must be set together")


class AutonomousRuntimeScheduleStore(Protocol):
    def save(self, schedule: AutonomousRuntimeSchedule) -> None: ...
    def load_due(self, now: float) -> list[AutonomousRuntimeSchedule]: ...
    def claim(self, schedule: AutonomousRuntimeSchedule, now: float, lease_seconds: float) -> str | None: ...
    def delete(self, job_id: str) -> None: ...


@dataclass(frozen=True)
class AutonomousRuntimeScheduleResult:
    schedule: AutonomousRuntimeSchedule
    run: AutonomousReasoningRunResult | None
    removed: bool
    claim_token: str | None = None


class AutonomousRuntimeScheduler:
    def __init__(self, store: AutonomousRuntimeScheduleStore, run_loop: AutonomousReasoningRunLoop) -> None:
        if not all(hasattr(store, name) for name in ("save", "load_due", "claim", "delete")):
            raise TypeError("store must implement save, load_due, claim, and delete")
        if not isinstance(run_loop, AutonomousReasoningRunLoop):
            raise TypeError("run_loop must be an AutonomousReasoningRunLoop")
        self._store = store
        self._run_loop = run_loop

    def schedule(self, job_id: str, *, next_due: float, interval: float) -> AutonomousRuntimeSchedule:
        schedule = AutonomousRuntimeSchedule(job_id, next_due, interval)
        self._store.save(schedule)
        return schedule

    def tick(self, now: float, *, max_jobs: int = 1, lease_seconds: float = 30.0) -> tuple[AutonomousRuntimeScheduleResult, ...]:
        if isinstance(now, bool) or not isinstance(now, (int, float)):
            raise TypeError("now must be numeric")
        if isinstance(max_jobs, bool) or not isinstance(max_jobs, int) or max_jobs <= 0:
            raise ValueError("max_jobs must be positive")
        if isinstance(lease_seconds, bool) or not isinstance(lease_seconds, (int, float)) or lease_seconds <= 0:
            raise ValueError("lease_seconds must be positive")
        due = self._store.load_due(now)[:max_jobs]
        results: list[AutonomousRuntimeScheduleResult] = []
        for schedule in due:
            claim = self._store.claim(schedule, now, lease_seconds)
            if claim is None:
                results.append(AutonomousRuntimeScheduleResult(schedule, None, False, None))
                continue
            run = self._run_loop.run(schedule.job_id, max_pulses=1)
            terminal = run.job.status in {AutonomousJobStatus.COMPLETED, AutonomousJobStatus.FAILED, AutonomousJobStatus.CANCELLED}
            waiting = run.job.resumable
            removed = terminal or waiting
            if removed:
                self._store.delete(schedule.job_id)
            else:
                self._store.save(AutonomousRuntimeSchedule(schedule.job_id, now + schedule.interval, schedule.interval))
            results.append(AutonomousRuntimeScheduleResult(schedule, run, removed, claim))
        return tuple(results)


def scheduler_claim_token(job_id: str, now: float, lease_seconds: float) -> str:
    payload = f"{job_id}:{now}:{lease_seconds}".encode("utf-8")
    return f"scheduler-claim-{hashlib.sha256(payload).hexdigest()[:24]}"


__all__ = ["AutonomousRuntimeSchedule", "AutonomousRuntimeScheduleStore", "AutonomousRuntimeScheduleResult", "AutonomousRuntimeScheduler", "scheduler_claim_token"]
