from __future__ import annotations

import unittest
from unittest.mock import Mock

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import (
    AutonomousJobPersistenceReceipt,
    AutonomousJobPersistenceService,
)
from src.runtime.autonomous_runtime_scheduler import AutonomousRuntimeSchedule
from src.runtime.autonomous_task_runtime import AutonomousTaskRuntime


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

        resumed = self.runtime.resume("task-3", now=75.0, interval=20.0)

        self.assertEqual(resumed.job.status, AutonomousJobStatus.RUNNING)
        self.assertEqual(resumed.job.events[-1].kind.value, "RESUMED")
        self.assertEqual(resumed.schedule.next_due, 75.0)
        self.assertEqual(len(self.scheduler.schedules), 2)
        self.assertEqual(self.persistence.jobs["task-3"], resumed.job)

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


if __name__ == "__main__":
    unittest.main()
