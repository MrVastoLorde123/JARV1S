from __future__ import annotations

import unittest
from unittest.mock import Mock

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import (
    AutonomousJobPersistenceReceipt,
    AutonomousJobPersistenceService,
)
from src.runtime.autonomous_runtime_scheduler import (
    AutonomousRuntimeSchedule,
    AutonomousRuntimeScheduler,
)
from src.runtime.autonomous_task_runtime import AutonomousTaskRuntime
from src.runtime.autonomous_task_runtime_loop import AutonomousTaskRuntimeLoop


class _MemoryPersistence(AutonomousJobPersistenceService):
    def __new__(cls):
        return object.__new__(cls)

    def __init__(self) -> None:
        self.jobs: dict[str, AutonomousJob] = {}

    def persist(self, job: AutonomousJob) -> AutonomousJobPersistenceReceipt:
        self.jobs[job.job_id] = job
        return AutonomousJobPersistenceReceipt(
            receipt_id=f"receipt-{job.job_id}-{job.step_count}",
            job_id=job.job_id,
            revision=f"revision-{job.step_count}",
            persisted=True,
        )

    def restore(self, job_id: str) -> AutonomousJob | None:
        return self.jobs.get(job_id)


class _Scheduler(AutonomousRuntimeScheduler):
    def __new__(cls):
        return object.__new__(cls)

    def __init__(self) -> None:
        self.schedules: list[AutonomousRuntimeSchedule] = []
        self.ticks: list[float] = []

    def schedule(self, job_id: str, *, next_due: float, interval: float) -> AutonomousRuntimeSchedule:
        schedule = AutonomousRuntimeSchedule(job_id=job_id, next_due=next_due, interval=interval)
        self.schedules.append(schedule)
        return schedule

    def tick(self, now: float, *, max_jobs=1, lease_seconds=30.0, max_backoff_multiplier=8):
        self.ticks.append(now)
        return tuple()


class V1TaskRuntimeContinuationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.persistence = _MemoryPersistence()
        self.scheduler = _Scheduler()
        self.runtime = AutonomousTaskRuntime(self.persistence, self.scheduler)

    def test_submit_persists_goal_and_arms_schedule(self) -> None:
        submitted = self.runtime.submit(
            "finish the network inventory",
            now=100.0,
            interval=30.0,
            job_id="task-1",
        )

        self.assertEqual(submitted.job.job_id, "task-1")
        self.assertEqual(submitted.job.status, AutonomousJobStatus.QUEUED)
        self.assertIs(self.persistence.jobs["task-1"], submitted.job)
        self.assertEqual(submitted.schedule.job_id, "task-1")
        self.assertEqual(submitted.schedule.next_due, 100.0)
        self.assertEqual(submitted.schedule.interval, 30.0)

    def test_inspect_is_read_only(self) -> None:
        submitted = self.runtime.submit(
            "inspect persistent state",
            now=10.0,
            interval=5.0,
            job_id="task-2",
        )

        inspected = self.runtime.inspect("task-2")

        self.assertEqual(inspected, submitted.job)
        self.assertEqual(self.scheduler.schedules.__len__(), 1)
        self.assertEqual(self.persistence.jobs["task-2"].status, AutonomousJobStatus.QUEUED)

    def test_resume_is_explicit_and_rearms_waiting_task(self) -> None:
        submitted = self.runtime.submit(
            "wait for operator input",
            now=0.0,
            interval=20.0,
            job_id="task-3",
        )
        waiting = submitted.job.start().wait_for_input("operator input required")
        self.persistence.jobs["task-3"] = waiting

        resumed = self.runtime.resume(
            "task-3",
            now=75.0,
            interval=20.0,
            input_context={"operator_input": "continue"},
        )

        self.assertEqual(resumed.job.status, AutonomousJobStatus.RUNNING)
        self.assertEqual(resumed.job.events[-1].kind.value, "RESUMED")
        self.assertEqual(resumed.schedule.next_due, 75.0)
        self.assertEqual(len(self.scheduler.schedules), 2)
        self.assertEqual(self.persistence.jobs["task-3"], resumed.job)
        self.assertEqual(resumed.job.working_context["operator_input"], "continue")

    def test_resume_rejects_non_waiting_task(self) -> None:
        self.runtime.submit(
            "do not resume queued work",
            now=0.0,
            interval=20.0,
            job_id="task-4",
        )

        with self.assertRaises(ValueError):
            self.runtime.resume("task-4", now=1.0, interval=20.0)

    def test_tick_delegates_to_durable_scheduler(self) -> None:
        result = self.runtime.tick(123.0, max_jobs=2)

        self.assertEqual(result, tuple())
        self.assertEqual(self.scheduler.ticks, [123.0])


class _LoopRuntime:
    def __init__(self) -> None:
        self.calls: list[float] = []

    def tick(self, now: float, *, max_jobs, lease_seconds, max_backoff_multiplier):
        self.calls.append(now)
        return (now,)


class V1TaskRuntimeLoopTests(unittest.TestCase):
    def test_bounded_run_calls_runtime_and_sleeps_between_iterations(self) -> None:
        runtime = _LoopRuntime()
        clock = iter((1.0, 2.0, 3.0))
        sleeps: list[float] = []
        loop = AutonomousTaskRuntimeLoop(runtime, now=lambda: next(clock), sleep=sleeps.append)

        result = loop.run(max_iterations=3, sleep_seconds=0.25, max_jobs=2)

        self.assertEqual(runtime.calls, [1.0, 2.0, 3.0])
        self.assertEqual(result, ((1.0,), (2.0,), (3.0,)))
        self.assertEqual(sleeps, [0.25, 0.25])

    def test_stop_request_is_honored(self) -> None:
        runtime = _LoopRuntime()
        loop = AutonomousTaskRuntimeLoop(runtime, now=lambda: 10.0, sleep=lambda _: loop.stop())

        result = loop.run(sleep_seconds=0.1)

        self.assertEqual(result, ((10.0,),))
        self.assertTrue(loop.stopped)

    def test_sleep_zero_never_calls_sleep(self) -> None:
        runtime = _LoopRuntime()
        slept: list[float] = []
        loop = AutonomousTaskRuntimeLoop(runtime, now=lambda: 20.0, sleep=slept.append)

        loop.run(max_iterations=2, sleep_seconds=0)

        self.assertEqual(slept, [])
        self.assertEqual(runtime.calls, [20.0, 20.0])

    def test_invalid_bounds_are_rejected(self) -> None:
        runtime = _LoopRuntime()
        loop = AutonomousTaskRuntimeLoop(runtime)

        with self.assertRaises(ValueError):
            loop.run(max_iterations=0)
        with self.assertRaises(ValueError):
            loop.run(sleep_seconds=-1)


if __name__ == "__main__":
    unittest.main()
