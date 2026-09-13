import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_task_runtime import SQLiteAutonomousTaskRuntime


class V1TaskSubmissionIntegrityTests(unittest.TestCase):
    def test_duplicate_job_id_is_rejected_without_overwriting_existing_task(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            path = Path(directory.name) / "jarvis.db"
            runtime = SQLiteAutonomousTaskRuntime(
                lambda job: AutonomousReasoningAction("continue", AutonomousReasoningDisposition.CONTINUE, "continue"),
                connection_factory=lambda: sqlite3.connect(path),
            )
            first = runtime.submit("original", now=1, interval=5, job_id="duplicate")
            with self.assertRaises(ValueError):
                runtime.submit("replacement", now=2, interval=10, job_id="duplicate")
            restored = runtime.inspect("duplicate")
            self.assertEqual(restored.goal, "original")
            self.assertEqual(restored.job_id, first.job.job_id)
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()
