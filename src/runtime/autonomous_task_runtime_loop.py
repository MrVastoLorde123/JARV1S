"""Host-level bounded loop for repeatedly advancing durable autonomous tasks."""

from __future__ import annotations

import time
from typing import Callable

from src.runtime.autonomous_runtime_scheduler import AutonomousRuntimeScheduleResult
from src.runtime.autonomous_task_runtime import AutonomousTaskRuntime


class AutonomousTaskRuntimeLoop:
    """Repeatedly advance an autonomous task runtime under explicit bounds."""

    def __init__(
        self,
        runtime: AutonomousTaskRuntime,
        *,
        now: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if not isinstance(runtime, AutonomousTaskRuntime):
            raise TypeError("runtime must be an AutonomousTaskRuntime")
        if not callable(now):
            raise TypeError("now must be callable")
        if not callable(sleep):
            raise TypeError("sleep must be callable")
        self._runtime = runtime
        self._now = now
        self._sleep = sleep
        self._stop_requested = False

    def stop(self) -> None:
        """Request that the loop stop after the current iteration."""
        self._stop_requested = True

    @property
    def stopped(self) -> bool:
        return self._stop_requested

    def run(
        self,
        *,
        max_iterations: int | None = None,
        sleep_seconds: float = 0.5,
        max_jobs: int = 1,
        lease_seconds: float = 30.0,
        max_backoff_multiplier: int = 8,
    ) -> tuple[tuple[AutonomousRuntimeScheduleResult, ...], ...]:
        """Advance the runtime until stopped or an optional iteration bound is reached."""
        if max_iterations is not None and (
            isinstance(max_iterations, bool) or not isinstance(max_iterations, int) or max_iterations <= 0
        ):
            raise ValueError("max_iterations must be a positive integer or None")
        if isinstance(sleep_seconds, bool) or not isinstance(sleep_seconds, (int, float)) or sleep_seconds < 0:
            raise ValueError("sleep_seconds must be a non-negative number")

        results: list[tuple[AutonomousRuntimeScheduleResult, ...]] = []
        self._stop_requested = False
        iterations = 0
        while not self._stop_requested:
            results.append(
                self._runtime.tick(
                    self._now(),
                    max_jobs=max_jobs,
                    lease_seconds=lease_seconds,
                    max_backoff_multiplier=max_backoff_multiplier,
                )
            )
            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                break
            if sleep_seconds > 0:
                self._sleep(sleep_seconds)
        return tuple(results)


__all__ = ["AutonomousTaskRuntimeLoop"]
