from __future__ import annotations

from dataclasses import dataclass
import uuid
from typing import Protocol, Any


@dataclass(frozen=True)
class AutonomousRuntimeSchedule:
    job_id: str
    next_due: float
    interval: float
    claim_token: str | None = None
    lease_until: float | None = None
    failure_count: int = 0
    last_failure: str | None = None
    last_failure_at: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.job_id, str) or not self.job_id.strip():
            raise ValueError("job_id must be non-empty")
        if isinstance(self.next_due, bool) or not isinstance(self.next_due, (int, float)):
            raise TypeError("next_due must be numeric")
        if isinstance(self.interval, bool) or not isinstance(self.interval, (int, float)) or self.interval <= 0:
            raise ValueError("interval must be positive")
        if self.claim_token is not None and (not isinstance(self.claim_token, str) or not self.claim_token.strip()):
            raise ValueError("claim_token must be non-empty or None")
        if self.lease_until is not None and (
            isinstance(self.lease_until, bool) or not isinstance(self.lease_until, (int, float))
        ):
            raise TypeError("lease_until must be numeric or None")
        if isinstance(self.failure_count, bool) or not isinstance(self.failure_count, int) or self.failure_count < 0:
            raise ValueError("failure_count must be a non-negative integer")
        if self.last_failure is not None and (
            not isinstance(self.last_failure, str) or not self.last_failure.strip()
        ):
            raise ValueError("last_failure must be non-empty or None")
        if self.last_failure_at is not None and (
            isinstance(self.last_failure_at, bool) or not isinstance(self.last_failure_at, (int, float))
        ):
            raise TypeError("last_failure_at must be numeric or None")
        if (self.last_failure is None) != (self.last_failure_at is None):
            raise ValueError("last_failure and last_failure_at must be set together")
        if (self.claim_token is None) != (self.lease_until is None):
            raise ValueError("claim_token and lease_until must be set together")


class AutonomousRuntimeScheduleStore(Protocol):
    def save(self, schedule: AutonomousRuntimeSchedule) -> None: ...
    def load_due(self, now: float) -> list[AutonomousRuntimeSchedule]: ...
    def list_all(self, *, limit: int = 500) -> tuple[AutonomousRuntimeSchedule, ...]: ...
    def delete(self, job_id: str) -> bool: ...
    def claim(self, schedule: AutonomousRuntimeSchedule, now: float, lease_seconds: float) -> str | None: ...
    def complete_claim(
        self,
        schedule: AutonomousRuntimeSchedule,
        claim_token: str,
        replacement: AutonomousRuntimeSchedule | None,
    ) -> bool: ...


@dataclass(frozen=True)
class AutonomousRuntimeScheduleResult:
    schedule: AutonomousRuntimeSchedule
    run: Any | None
    removed: bool
    claim_token: str | None = None
    completed_claim: bool = False
    failure: str | None = None


class AutonomousRuntimeScheduler:
    """Host-neutral durable scheduler with lease fencing and bounded backoff."""

    def __init__(self, store: AutonomousRuntimeScheduleStore, run_loop) -> None:
        if not all(hasattr(store, name) for name in ("save", "load_due", "claim")):
            raise TypeError("store must implement save, load_due, and claim")
        if not callable(getattr(run_loop, "run", None)):
            raise TypeError("run_loop must provide callable run(job_id, ...)")
        self._store = store
        self._run_loop = run_loop

    def schedule(self, job_id: str, *, next_due: float, interval: float) -> AutonomousRuntimeSchedule:
        schedule = AutonomousRuntimeSchedule(job_id, next_due, interval)
        self._store.save(schedule)
        return schedule

    def tick(
        self,
        now: float,
        *,
        max_jobs: int = 1,
        lease_seconds: float = 30.0,
        max_backoff_multiplier: int = 8,
    ) -> tuple[AutonomousRuntimeScheduleResult, ...]:
        if isinstance(now, bool) or not isinstance(now, (int, float)):
            raise TypeError("now must be numeric")
        if isinstance(max_jobs, bool) or not isinstance(max_jobs, int) or max_jobs <= 0:
            raise ValueError("max_jobs must be positive")
        if isinstance(lease_seconds, bool) or not isinstance(lease_seconds, (int, float)) or lease_seconds <= 0:
            raise ValueError("lease_seconds must be positive")
        if isinstance(max_backoff_multiplier, bool) or not isinstance(max_backoff_multiplier, int) or max_backoff_multiplier <= 0:
            raise ValueError("max_backoff_multiplier must be a positive integer")

        results: list[AutonomousRuntimeScheduleResult] = []
        for schedule in self._store.load_due(now)[:max_jobs]:
            claim = self._store.claim(schedule, now, lease_seconds)
            if claim is None:
                results.append(AutonomousRuntimeScheduleResult(schedule, None, False))
                continue

            try:
                run = self._run_loop.run(schedule.job_id, max_pulses=1)
            except Exception as exc:
                failure = f"{type(exc).__name__}: {exc}"
                replacement = self._failure_replacement(
                    schedule,
                    now,
                    failure,
                    max_backoff_multiplier=max_backoff_multiplier,
                )
                completed = self._complete_claim(schedule, claim, replacement)
                results.append(
                    AutonomousRuntimeScheduleResult(
                        schedule,
                        None,
                        False,
                        claim,
                        completed,
                        failure,
                    )
                )
                continue

            job = getattr(run, "job", None)
            if job is None:
                failure = "scheduler run result did not expose job state"
                replacement = self._failure_replacement(
                    schedule,
                    now,
                    failure,
                    max_backoff_multiplier=max_backoff_multiplier,
                )
                completed = self._complete_claim(schedule, claim, replacement)
                results.append(
                    AutonomousRuntimeScheduleResult(
                        schedule,
                        run,
                        False,
                        claim,
                        completed,
                        failure,
                    )
                )
                continue

            terminal = getattr(job, "terminal", False)
            waiting = getattr(job, "resumable", False)
            removed = bool(terminal or waiting)

            replacement = None
            if not removed:
                replacement = AutonomousRuntimeSchedule(
                    job_id=schedule.job_id,
                    next_due=now + schedule.interval,
                    interval=schedule.interval,
                )

            completed = self._complete_claim(schedule, claim, replacement)
            results.append(
                AutonomousRuntimeScheduleResult(
                    schedule,
                    run,
                    removed,
                    claim,
                    completed,
                    None,
                )
            )

        return tuple(results)

    def _complete_claim(
        self,
        schedule: AutonomousRuntimeSchedule,
        claim: str,
        replacement: AutonomousRuntimeSchedule | None,
    ) -> bool:
        complete_claim = getattr(self._store, "complete_claim", None)
        if callable(complete_claim):
            return bool(complete_claim(schedule, claim, replacement))

        # Backward-compatible fallback for older in-memory test stores.
        if replacement is None:
            delete = getattr(self._store, "delete", None)
            if not callable(delete):
                raise TypeError("scheduler store must provide complete_claim or delete")
            delete(schedule.job_id)
            return True

        self._store.save(replacement)
        return True

    @staticmethod
    def _failure_replacement(
        schedule: AutonomousRuntimeSchedule,
        now: float,
        failure: str,
        *,
        max_backoff_multiplier: int,
    ) -> AutonomousRuntimeSchedule:
        count = schedule.failure_count + 1
        multiplier = min(2 ** max(count - 1, 0), max_backoff_multiplier)
        return AutonomousRuntimeSchedule(
            job_id=schedule.job_id,
            next_due=now + schedule.interval * multiplier,
            interval=schedule.interval,
            failure_count=count,
            last_failure=failure,
            last_failure_at=now,
        )


def scheduler_claim_token(job_id: str, now: float, lease_seconds: float) -> str:
    if not isinstance(job_id, str) or not job_id.strip():
        raise ValueError("job_id must be non-empty")
    if isinstance(now, bool) or not isinstance(now, (int, float)):
        raise TypeError("now must be numeric")
    if isinstance(lease_seconds, bool) or not isinstance(lease_seconds, (int, float)) or lease_seconds <= 0:
        raise ValueError("lease_seconds must be positive")
    return f"scheduler-claim-{uuid.uuid4().hex}"


def scheduler_lease_expired(lease_until: float, now: float) -> bool:
    if isinstance(lease_until, bool) or not isinstance(lease_until, (int, float)):
        raise TypeError("lease_until must be numeric")
    if isinstance(now, bool) or not isinstance(now, (int, float)):
        raise TypeError("now must be numeric")
    return lease_until <= now


__all__ = [
    "AutonomousRuntimeSchedule",
    "AutonomousRuntimeScheduleStore",
    "AutonomousRuntimeScheduleResult",
    "AutonomousRuntimeScheduler",
    "scheduler_claim_token",
    "scheduler_lease_expired",
]
