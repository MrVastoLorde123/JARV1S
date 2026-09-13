from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_task_ownership import AutonomousTaskOwnershipState
from src.runtime.autonomous_task_runtime import SQLiteAutonomousTaskRuntime
from src.runtime.autonomous_runtime_scheduler import AutonomousRuntimeScheduleResult


class V1TaskOwnershipRestartTests(unittest.TestCase):
    def test_ownership_state_survives_runtime_restart_and_updates_until_completion(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            path = Path(directory.name) / "jarvis.db"
            calls = {"count": 0}

            def reason(job):
                calls["count"] += 1
                if calls["count"] == 1:
                    return AutonomousReasoningAction(
                        "plan-work",
                        AutonomousReasoningDisposition.CONTINUE,
                        "collect the switch list",
                        metadata={
                            "task_ownership": {
                                "remaining_work": ["collect the switch list", "validate uplinks"],
                                "next_action": "collect the switch list",
                            }
                        },
                    )
                return AutonomousReasoningAction(
                    "finish-work",
                    AutonomousReasoningDisposition.COMPLETE,
                    "inventory finished",
                    result="inventory complete",
                    metadata={
                        "task_ownership": {
                            "remaining_work": [],
                            "next_action": None,
                        }
                    },
                )

            runtime1 = SQLiteAutonomousTaskRuntime(
                reason,
                connection_factory=lambda: sqlite3.connect(path),
            )
            runtime1.submit("build switch inventory", now=1, interval=5, job_id="ownership-restart")
            first = runtime1.tick(1)
            self.assertEqual(len(first), 1)
            state1 = runtime1.ownership("ownership-restart")
            self.assertEqual(state1.remaining_work, ("collect the switch list", "validate uplinks"))
            self.assertEqual(state1.next_action, "collect the switch list")
            self.assertTrue(state1.working)

            runtime2 = SQLiteAutonomousTaskRuntime(
                reason,
                connection_factory=lambda: sqlite3.connect(path),
            )
            restored = runtime2.ownership("ownership-restart")
            self.assertEqual(restored.remaining_work, ("collect the switch list", "validate uplinks"))
            self.assertEqual(restored.next_action, "collect the switch list")

            second = runtime2.tick(6)
            self.assertEqual(len(second), 1)
            state2 = runtime2.ownership("ownership-restart")
            self.assertTrue(state2.complete)
            self.assertEqual(state2.remaining_work, ())
            self.assertIsNone(state2.next_action)
            self.assertEqual(calls["count"], 2)
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()
