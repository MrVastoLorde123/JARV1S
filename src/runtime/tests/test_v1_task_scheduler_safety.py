from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_job import AutonomousJobStatus
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_task_runtime import SQLiteAutonomousTaskRuntime


class V1TaskSchedulerSafetyTests(unittest.TestCase):
    def _runtime(self, directory, reason):
        path = Path(directory.name) / "jarvis.db"
        return SQLiteAutonomousTaskRuntime(
            reason,
            connection_factory=lambda: sqlite3.connect(path),
        )

    def test_worker_exception_is_durable_retry_with_exponential_backoff(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            calls = {"count": 0}

            def reason(job):
                calls["count"] += 1
                raise RuntimeError("provider unavailable")

            runtime = self._runtime(directory, reason)
            runtime.submit("retry provider failure", now=1, interval=5, job_id="retry-1")

            first = runtime.tick(1)[0]
            self.assertIsNone(first.run)
            self.assertEqual(first.failure, "RuntimeError: provider unavailable")
            self.assertEqual(first.schedule.failure_count, 0)
            self.assertFalse(first.removed)
            self.assertEqual(calls["count"], 1)
            self.assertEqual(runtime.schedule_store.load_due(5), [])

            second = runtime.tick(6)[0]
            self.assertIsNone(second.run)
            self.assertEqual(second.schedule.failure_count, 0)
            self.assertEqual(calls["count"], 2)
            self.assertEqual(runtime.schedule_store.load_due(15), [])
            self.assertEqual(len(runtime.schedule_store.load_due(16)), 1)
        finally:
            directory.cleanup()

    def test_pause_stops_future_scheduler_rearming_until_explicit_resume(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            runtime = self._runtime(
                directory,
                lambda job: AutonomousReasoningAction(
                    "continue",
                    AutonomousReasoningDisposition.CONTINUE,
                    "continue work",
                ),
            )
            runtime.submit("pause scheduler", now=1, interval=5, job_id="pause-schedule")
            runtime.tick(1)
            paused = runtime.pause("pause-schedule", "operator requested pause")
            self.assertEqual(paused.job.status, AutonomousJobStatus.PAUSED)

            result = runtime.tick(6)[0]
            self.assertTrue(result.removed)
            self.assertEqual(result.run.job.status, AutonomousJobStatus.PAUSED)
            self.assertEqual(runtime.schedule_store.load_due(100), [])

            resumed = runtime.resume("pause-schedule", now=10, interval=5)
            self.assertEqual(resumed.job.status, AutonomousJobStatus.RUNNING)
            resumed_tick = runtime.tick(10)[0]
            self.assertEqual(resumed_tick.run.job.status, AutonomousJobStatus.RUNNING)
        finally:
            directory.cleanup()

    def test_cancelled_task_is_not_resurrected_by_existing_schedule(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            runtime = self._runtime(
                directory,
                lambda job: AutonomousReasoningAction(
                    "complete",
                    AutonomousReasoningDisposition.COMPLETE,
                    "should never run",
                    result="unexpected",
                ),
            )
            runtime.submit("cancel scheduler", now=1, interval=5, job_id="cancel-schedule")
            cancelled = runtime.cancel("cancel-schedule", "operator cancelled task")
            self.assertEqual(cancelled.job.status, AutonomousJobStatus.CANCELLED)

            result = runtime.tick(1)[0]
            self.assertTrue(result.removed)
            self.assertEqual(result.run.job.status, AutonomousJobStatus.CANCELLED)
            self.assertEqual(result.run.job.step_count, 0)
            self.assertEqual(runtime.inspect("cancel-schedule").status, AutonomousJobStatus.CANCELLED)
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
