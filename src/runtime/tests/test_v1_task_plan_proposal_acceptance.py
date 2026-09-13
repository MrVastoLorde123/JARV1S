import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_task_runtime import SQLiteAutonomousTaskRuntime


class V1TaskPlanProposalAcceptanceTests(unittest.TestCase):
    def test_initial_model_plan_proposal_is_promoted_once(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            path = Path(directory.name) / "jarvis.db"
            runtime = SQLiteAutonomousTaskRuntime(
                lambda job: AutonomousReasoningAction(
                    "plan",
                    AutonomousReasoningDisposition.CONTINUE,
                    "start plan",
                    metadata={"task_plan": {"steps": [{"step_id": "discover", "description": "discover"}, {"step_id": "publish", "description": "publish"}]}},
                ),
                connection_factory=lambda: sqlite3.connect(path),
            )
            runtime.submit("inventory", now=1, interval=5, job_id="proposal-accept")
            runtime.tick(1)
            plan = runtime.plan("proposal-accept")
            self.assertIsNotNone(plan)
            self.assertEqual(plan.steps[0].step_id, "discover")
            self.assertNotIn("task_plan_proposal", runtime.inspect("proposal-accept").working_context)
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()
