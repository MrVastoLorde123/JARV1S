from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_job import AutonomousJobStatus
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_task_runtime import SQLiteAutonomousTaskRuntime


class V1TaskLifecycleControlTests(unittest.TestCase):
    def _runtime(self, directory):
        path = Path(directory.name) / "jarvis.db"
        return SQLiteAutonomousTaskRuntime(
            lambda job: AutonomousReasoningAction(
                "continue",
                AutonomousReasoningDisposition.CONTINUE,
                "keep working",
            ),
            connection_factory=lambda: sqlite3.connect(path),
        )

    def test_pause_is_explicit_and_persisted(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            runtime = self._runtime(directory)
            runtime.submit("pause me", now=1, interval=5, job_id="pause-1")
            runtime.tick(1)
            result = runtime.pause("pause-1", "operator requested pause")
            self.assertEqual(result.job.status, AutonomousJobStatus.PAUSED)
            restored = runtime.inspect("pause-1")
            self.assertEqual(restored.status, AutonomousJobStatus.PAUSED)
            self.assertEqual(restored.waiting_reason, "operator requested pause")
        finally:
            directory.cleanup()

    def test_pause_rejects_non_running_task(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            runtime = self._runtime(directory)
            runtime.submit("queued", now=1, interval=5, job_id="pause-2")
            with self.assertRaises(ValueError):
                runtime.pause("pause-2", "not running")
        finally:
            directory.cleanup()

    def test_cancel_is_explicit_terminal_and_persisted(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            runtime = self._runtime(directory)
            runtime.submit("cancel me", now=1, interval=5, job_id="cancel-1")
            result = runtime.cancel("cancel-1", "operator cancelled task")
            self.assertEqual(result.job.status, AutonomousJobStatus.CANCELLED)
            restored = runtime.inspect("cancel-1")
            self.assertEqual(restored.status, AutonomousJobStatus.CANCELLED)
            self.assertEqual(restored.failure_reason, "operator cancelled task")
            with self.assertRaises(ValueError):
                runtime.cancel("cancel-1", "again")
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()
