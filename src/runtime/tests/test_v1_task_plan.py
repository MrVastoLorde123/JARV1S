from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_task_plan import (
    AutonomousTaskPlan,
    AutonomousTaskPlanStepStatus,
    AutonomousTaskPlanValidationError,
)
from src.runtime.autonomous_task_runtime import SQLiteAutonomousTaskRuntime


class V1TaskPlanTests(unittest.TestCase):
    def test_plan_transitions_one_step_at_a_time(self) -> None:
        plan = AutonomousTaskPlan.from_descriptions(["collect", "validate", "publish"])
        self.assertEqual(plan.current.step_id, "step-1")

        plan = plan.start("step-1")
        self.assertEqual(plan.current.status, AutonomousTaskPlanStepStatus.IN_PROGRESS)
        plan = plan.complete_step("step-1")
        self.assertEqual(plan.current.step_id, "step-2")
        self.assertEqual(plan.current.status, AutonomousTaskPlanStepStatus.PENDING)

    def test_only_one_step_can_be_in_progress(self) -> None:
        plan = AutonomousTaskPlan.from_descriptions(["collect", "validate"])
        plan = plan.start("step-1")
        with self.assertRaises(AutonomousTaskPlanValidationError):
            plan.start("step-2")

    def test_blocked_step_requires_reason_and_is_not_complete(self) -> None:
        plan = AutonomousTaskPlan.from_descriptions(["collect"])
        with self.assertRaises(AutonomousTaskPlanValidationError):
            plan.block("step-1", "")
        plan = plan.block("step-1", "device list unavailable")
        self.assertTrue(plan.blocked)
        self.assertFalse(plan.complete)
        self.assertEqual(plan.current.status, AutonomousTaskPlanStepStatus.BLOCKED)

    def test_runtime_persists_plan_and_restores_after_restart(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            path = Path(directory.name) / "jarvis.db"
            runtime1 = SQLiteAutonomousTaskRuntime(
                lambda job: AutonomousReasoningAction(
                    "continue",
                    AutonomousReasoningDisposition.CONTINUE,
                    "wait for the plan controller",
                ),
                connection_factory=lambda: sqlite3.connect(path),
            )
            runtime1.submit("publish inventory", now=1, interval=5, job_id="plan-restart")
            runtime1.set_plan(
                "plan-restart",
                AutonomousTaskPlan.from_descriptions(["collect", "validate", "publish"]),
            )
            runtime1.start_plan_step("plan-restart", "step-1")
            runtime1.complete_plan_step("plan-restart", "step-1")

            runtime2 = SQLiteAutonomousTaskRuntime(
                lambda job: AutonomousReasoningAction(
                    "continue",
                    AutonomousReasoningDisposition.CONTINUE,
                    "restored",
                ),
                connection_factory=lambda: sqlite3.connect(path),
            )
            restored = runtime2.plan("plan-restart")
            self.assertIsNotNone(restored)
            self.assertEqual(restored.steps[0].status, AutonomousTaskPlanStepStatus.COMPLETED)
            self.assertEqual(restored.current.step_id, "step-2")
        finally:
            directory.cleanup()

    def test_terminal_task_rejects_plan_mutation(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            path = Path(directory.name) / "jarvis.db"
            runtime = SQLiteAutonomousTaskRuntime(
                lambda job: AutonomousReasoningAction(
                    "finish",
                    AutonomousReasoningDisposition.COMPLETE,
                    "done",
                    result="complete",
                ),
                connection_factory=lambda: sqlite3.connect(path),
            )
            runtime.submit("finish", now=1, interval=5, job_id="plan-terminal")
            runtime.tick(1)
            self.assertTrue(runtime.inspect("plan-terminal").terminal)
            with self.assertRaises(ValueError):
                runtime.set_plan(
                    "plan-terminal",
                    AutonomousTaskPlan.from_descriptions(["cannot mutate"]),
                )
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()
