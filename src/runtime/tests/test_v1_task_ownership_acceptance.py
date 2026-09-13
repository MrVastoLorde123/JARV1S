from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_task_ownership import AutonomousTaskOwnershipState
from src.runtime.autonomous_task_runtime import SQLiteAutonomousTaskRuntime
from src.runtime.autonomous_task_runtime_loop import AutonomousTaskRuntimeLoop


class V1TaskOwnershipAcceptanceTests(unittest.TestCase):
    def test_task_is_owned_worked_across_cycles_and_restored_after_restart(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            path = Path(directory.name) / "jarvis.db"
            calls = {"count": 0}

            def reason(job):
                calls["count"] += 1
                if calls["count"] == 1:
                    return AutonomousReasoningAction(
                        "cycle-1",
                        AutonomousReasoningDisposition.CONTINUE,
                        "collect devices",
                        metadata={
                            "task_ownership": {
                                "remaining_work": ["collect devices", "validate uplinks"],
                                "next_action": "collect devices",
                            }
                        },
                    )
                if calls["count"] == 2:
                    return AutonomousReasoningAction(
                        "cycle-2",
                        AutonomousReasoningDisposition.CONTINUE,
                        "validate uplinks",
                        metadata={
                            "task_ownership": {
                                "remaining_work": ["publish inventory"],
                                "next_action": "publish inventory",
                            }
                        },
                    )
                return AutonomousReasoningAction(
                    "cycle-3",
                    AutonomousReasoningDisposition.COMPLETE,
                    "publish inventory",
                    result="inventory published",
                    metadata={
                        "task_ownership": {
                            "remaining_work": [],
                            "next_action": None,
                        }
                    },
                )

            runtime = SQLiteAutonomousTaskRuntime(
                reason,
                connection_factory=lambda: sqlite3.connect(path),
            )
            runtime.submit("complete network inventory", now=1, interval=1, job_id="owned-task")

            clock = iter((1.0, 2.0, 3.0))
            loop = AutonomousTaskRuntimeLoop(runtime, now=lambda: next(clock), sleep=lambda _: None)
            loop.run(max_iterations=3, sleep_seconds=0, max_jobs=1)

            state = runtime.ownership("owned-task")
            self.assertEqual(calls["count"], 3)
            self.assertTrue(state.complete)
            self.assertEqual(state.step_count, 3)
            self.assertEqual(state.remaining_work, ())
            self.assertIsNone(state.next_action)
            self.assertEqual(state.last_step_summary, "publish inventory")

            restarted = SQLiteAutonomousTaskRuntime(
                reason,
                connection_factory=lambda: sqlite3.connect(path),
            )
            restored = AutonomousTaskOwnershipState.from_job(restarted.inspect("owned-task"))
            self.assertTrue(restored.complete)
            self.assertEqual(restored.step_count, 3)
            self.assertEqual(restored.remaining_work, ())
            self.assertEqual(calls["count"], 3)
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()
