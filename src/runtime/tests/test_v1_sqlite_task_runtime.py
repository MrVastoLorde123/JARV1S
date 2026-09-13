import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_task_runtime import SQLiteAutonomousTaskRuntime
from src.tools.registry import ToolRegistry


class V1SQLiteTaskRuntimeTests(unittest.TestCase):
    def make_runtime(self, directory, reason):
        path = Path(directory.name) / "jarvis.db"
        return SQLiteAutonomousTaskRuntime(
            reason,
            connection_factory=lambda: sqlite3.connect(path),
            registry=ToolRegistry(),
        )

    def test_submit_tick_and_restart_continue_same_task(self):
        directory = tempfile.TemporaryDirectory()
        try:
            calls = {"count": 0}

            def reason(job):
                calls["count"] += 1
                if calls["count"] == 1:
                    return AutonomousReasoningAction(
                        "first-progress",
                        AutonomousReasoningDisposition.CONTINUE,
                        "made durable progress",
                    )
                return AutonomousReasoningAction(
                    "completed",
                    AutonomousReasoningDisposition.COMPLETE,
                    "task finished",
                    result="done",
                )

            runtime1 = self.make_runtime(directory, reason)
            submitted = runtime1.submit(
                "complete the persistent task",
                now=1,
                interval=5,
                job_id="task-1",
            )
            self.assertEqual(submitted.job.status, AutonomousJobStatus.QUEUED)

            first = runtime1.tick(1)[0]
            self.assertEqual(first.run.job.status, AutonomousJobStatus.RUNNING)
            self.assertEqual(first.run.job.step_count, 1)

            runtime2 = self.make_runtime(directory, reason)
            restored = runtime2.inspect("task-1")
            self.assertIsNotNone(restored)
            self.assertEqual(restored.step_count, 1)
            self.assertEqual(restored.goal, "complete the persistent task")

            second = runtime2.tick(6)[0]
            self.assertTrue(second.removed)
            self.assertEqual(second.run.job.status, AutonomousJobStatus.COMPLETED)
            self.assertEqual(second.run.job.result, "done")
            self.assertEqual(second.run.job.step_count, 2)
        finally:
            directory.cleanup()

    def test_composition_root_owns_registry_and_durable_stores(self):
        directory = tempfile.TemporaryDirectory()
        try:
            runtime = self.make_runtime(
                directory,
                lambda job: AutonomousReasoningAction(
                    "complete",
                    AutonomousReasoningDisposition.COMPLETE,
                    "complete task",
                    result="done",
                ),
            )
            self.assertIsInstance(runtime.registry, ToolRegistry)
            self.assertIsNotNone(runtime.job_store)
            self.assertIsNotNone(runtime.schedule_store)
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
