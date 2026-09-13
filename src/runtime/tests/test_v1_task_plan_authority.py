from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_job import AutonomousJobStatus
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_task_plan import AutonomousTaskPlan
from src.runtime.autonomous_task_runtime import SQLiteAutonomousTaskRuntime


class V1TaskPlanAuthorityTests(unittest.TestCase):
    def test_existing_runtime_owned_plan_is_not_overwritten_by_model_proposal(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            path = Path(directory.name) / "jarvis.db"
            calls = {"count": 0}

            def reason(job):
                calls["count"] += 1
                return AutonomousReasoningAction(
                    "propose-change",
                    AutonomousReasoningDisposition.CONTINUE,
                    "continue current work",
                    metadata={
                        "task_plan": {
                            "steps": [
                                {"step_id": "model-step", "description": "replace plan"},
                            ]
                        }
                    },
                )

            runtime = SQLiteAutonomousTaskRuntime(reason, connection_factory=lambda: sqlite3.connect(path))
            runtime.submit("preserve plan", now=1, interval=5, job_id="plan-authority")
            runtime.set_plan("plan-authority", AutonomousTaskPlan.from_descriptions(["runtime-owned", "second"]))
            runtime.tick(1)

            plan = runtime.plan("plan-authority")
            self.assertEqual(plan.steps[0].step_id, "step-1")
            self.assertEqual(plan.steps[0].description, "runtime-owned")
            job = runtime.inspect("plan-authority")
            self.assertIn("task_plan_proposal", job.working_context)
            self.assertEqual(calls["count"], 1)
        finally:
            directory.cleanup()

    def test_step_budget_exhaustion_fails_deterministically(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            path = Path(directory.name) / "jarvis.db"
            runtime = SQLiteAutonomousTaskRuntime(
                lambda job: AutonomousReasoningAction(
                    "continue",
                    AutonomousReasoningDisposition.CONTINUE,
                    "keep working",
                ),
                connection_factory=lambda: sqlite3.connect(path),
            )
            runtime.submit("bounded task", now=1, interval=5, job_id="budget", max_steps=1)
            first = runtime.tick(1)[0]
            self.assertEqual(first.run.job.status, AutonomousJobStatus.RUNNING)
            second = runtime.tick(6)[0]
            self.assertEqual(second.run.job.status, AutonomousJobStatus.FAILED)
            self.assertIn("maximum autonomous step budget exhausted", second.run.job.failure_reason)
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()
