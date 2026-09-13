from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_task_plan import AutonomousTaskPlan
from src.runtime.autonomous_task_progress import AutonomousTaskProgressVerdict
from src.runtime.autonomous_task_runtime import SQLiteAutonomousTaskRuntime
from src.runtime.autonomous_task_snapshot import AutonomousTaskSnapshot


class V1TaskSnapshotTests(unittest.TestCase):
    def test_snapshot_aggregates_job_ownership_plan_and_progress(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            path = Path(directory.name) / "jarvis.db"
            runtime = SQLiteAutonomousTaskRuntime(
                lambda job: AutonomousReasoningAction(
                    "complete",
                    AutonomousReasoningDisposition.COMPLETE,
                    "finish task",
                    result="done",
                ),
                connection_factory=lambda: sqlite3.connect(path),
            )
            runtime.submit("finish task", now=1, interval=5, job_id="snapshot-1")
            runtime.set_plan("snapshot-1", AutonomousTaskPlan.from_descriptions(["collect", "publish"]))
            runtime.start_plan_step("snapshot-1", "step-1")
            runtime.complete_plan_step("snapshot-1", "step-1", reason="collected")
            runtime.start_plan_step("snapshot-1", "step-2")
            runtime.complete_plan_step("snapshot-1", "step-2", reason="published")
            runtime.tick(1)

            job = runtime.inspect("snapshot-1")
            snapshot = AutonomousTaskSnapshot.from_job(job)
            self.assertTrue(snapshot.terminal)
            self.assertTrue(snapshot.plan is not None)
            self.assertTrue(snapshot.plan.complete)
            self.assertTrue(snapshot.progress is not None)
            self.assertEqual(snapshot.progress.verdict, AutonomousTaskProgressVerdict.COMPLETED)
            self.assertIsNone(snapshot.plan.current)
            encoded = snapshot.to_dict()
            self.assertEqual(encoded["job"]["status"], "COMPLETED")
            self.assertEqual(encoded["progress"]["verdict"], "COMPLETED")
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()
