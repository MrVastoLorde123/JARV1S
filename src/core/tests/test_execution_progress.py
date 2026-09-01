import unittest

from src.core.execution_executor_models import (
    PlanExecutionResult,
    PlanExecutionStatus,
    StepExecutionResult,
    StepExecutionStatus,
)
from src.core.execution_progress import ExecutionProgress
from src.core.execution_state import ExecutionState


class ExecutionProgressTests(unittest.TestCase):
    def _state(self, plan_id, status, step_id, output=None, error=None):
        step_status = (
            StepExecutionStatus.COMPLETED
            if status == PlanExecutionStatus.COMPLETED
            else StepExecutionStatus.FAILED
        )
        return ExecutionState.from_execution(
            "finish the objective",
            PlanExecutionResult(
                plan_id=plan_id,
                status=status,
                steps=(
                    StepExecutionResult(
                        step_id=step_id,
                        action="PROVIDE_INFORMATION",
                        status=step_status,
                        output=output,
                        error=error,
                    ),
                ),
                error=error,
            ),
        )

    def test_first_state_creates_one_attempt(self):
        state = self._state("p1", PlanExecutionStatus.FAILED, "step-1", error="boom")
        progress = ExecutionProgress.from_state(state)

        self.assertEqual(progress.attempt_count, 1)
        self.assertIs(progress.current, state)
        self.assertEqual(progress.completed_steps, ())

    def test_record_adds_attempt_without_mutating_previous_progress(self):
        first = self._state("p1", PlanExecutionStatus.FAILED, "step-1", error="boom")
        second = self._state("p2", PlanExecutionStatus.COMPLETED, "step-2", output="done")
        progress = ExecutionProgress.from_state(first)
        updated = progress.record(second)

        self.assertEqual(progress.attempt_count, 1)
        self.assertEqual(updated.attempt_count, 2)
        self.assertEqual(updated.current, second)
        self.assertEqual(updated.completed_steps, ("p2:step-2",))
        self.assertEqual(updated.available_outputs[0].value, "done")

    def test_goal_cannot_change_across_attempts(self):
        first = self._state("p1", PlanExecutionStatus.FAILED, "step-1", error="boom")
        second = ExecutionState.from_execution(
            "different objective",
            PlanExecutionResult(
                plan_id="p2",
                status=PlanExecutionStatus.COMPLETED,
                steps=(),
            ),
        )
        progress = ExecutionProgress.from_state(first)

        with self.assertRaises(ValueError):
            progress.record(second)

    def test_context_retains_attempt_history_and_current_actions(self):
        first = self._state("p1", PlanExecutionStatus.FAILED, "step-1", error="boom")
        second = self._state("p2", PlanExecutionStatus.COMPLETED, "step-2", output="done")
        progress = ExecutionProgress.from_state(first).record(second)

        context = progress.to_context()

        self.assertEqual(context["goal"], "finish the objective")
        self.assertEqual(context["attempt_count"], 2)
        self.assertEqual(len(context["attempts"]), 2)
        self.assertEqual(context["current"]["plan_id"], "p2")
        self.assertEqual(context["next_allowed_actions"], ("COMPLETE",))
        self.assertEqual(
            context["completed_steps_across_attempts"],
            ("p2:step-2",),
        )


if __name__ == "__main__":
    unittest.main()
