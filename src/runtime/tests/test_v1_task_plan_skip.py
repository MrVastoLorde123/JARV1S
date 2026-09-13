import unittest

from src.runtime.autonomous_task_plan import AutonomousTaskPlan, AutonomousTaskPlanStepStatus, AutonomousTaskPlanValidationError


class V1TaskPlanSkipTests(unittest.TestCase):
    def test_skip_marks_step_terminal_and_advances_current(self) -> None:
        plan = AutonomousTaskPlan.from_descriptions(["collect", "publish"])
        skipped = plan.skip_step("step-1", "collector unavailable")
        self.assertEqual(skipped.steps[0].status, AutonomousTaskPlanStepStatus.SKIPPED)
        self.assertEqual(skipped.current.step_id, "step-2")
        self.assertFalse(skipped.complete)

    def test_skip_requires_reason(self) -> None:
        plan = AutonomousTaskPlan.from_descriptions(["collect"])
        with self.assertRaises(AutonomousTaskPlanValidationError):
            plan.skip_step("step-1", "")


if __name__ == "__main__":
    unittest.main()
