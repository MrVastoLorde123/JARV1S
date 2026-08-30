import unittest

from src.core.execution_executor_models import (
    PlanExecutionResult,
    PlanExecutionStatus,
    StepExecutionResult,
    StepExecutionStatus,
)

from src.core.execution_plan_models import (
    ExecutionPlan,
)


class ExecutionExecutorModelTests(
    unittest.TestCase
):

    def _plan(self):
        return ExecutionPlan(
            plan_id="plan-1",
            task_description="Test plan.",
            steps=(),
        )

    def test_completed_step_result_can_be_created(
        self,
    ):
        result = StepExecutionResult(
            step_id="step-1",
            action="TEST",
            status=StepExecutionStatus.COMPLETED,
            output="done",
        )

        self.assertEqual(
            result.status,
            StepExecutionStatus.COMPLETED,
        )

        self.assertEqual(
            result.output,
            "done",
        )

    def test_failed_step_requires_error(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            StepExecutionResult(
                step_id="step-1",
                action="TEST",
                status=StepExecutionStatus.FAILED,
            )

    def test_completed_step_cannot_have_error(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            StepExecutionResult(
                step_id="step-1",
                action="TEST",
                status=StepExecutionStatus.COMPLETED,
                error="bad",
            )

    def test_failed_step_result_can_be_created(
        self,
    ):
        result = StepExecutionResult(
            step_id="step-1",
            action="TEST",
            status=StepExecutionStatus.FAILED,
            error="Failure.",
        )

        self.assertEqual(
            result.error,
            "Failure.",
        )

    def test_plan_execution_result_can_be_created(
        self,
    ):
        result = PlanExecutionResult(
            plan_id="plan-1",
            status=PlanExecutionStatus.COMPLETED,
            steps=(),
        )

        self.assertTrue(
            result.success
        )

    def test_failed_plan_is_not_successful(
        self,
    ):
        result = PlanExecutionResult(
            plan_id="plan-1",
            status=PlanExecutionStatus.FAILED,
            steps=(),
            error="Failure.",
        )

        self.assertFalse(
            result.success
        )

    def test_step_count_is_available(
        self,
    ):
        step = StepExecutionResult(
            step_id="step-1",
            action="TEST",
            status=StepExecutionStatus.COMPLETED,
        )

        result = PlanExecutionResult(
            plan_id="plan-1",
            status=PlanExecutionStatus.COMPLETED,
            steps=(step,),
        )

        self.assertEqual(
            result.step_count,
            1,
        )

    def test_failed_steps_are_available(
        self,
    ):
        completed = StepExecutionResult(
            step_id="step-1",
            action="ONE",
            status=StepExecutionStatus.COMPLETED,
        )

        failed = StepExecutionResult(
            step_id="step-2",
            action="TWO",
            status=StepExecutionStatus.FAILED,
            error="Failure.",
        )

        result = PlanExecutionResult(
            plan_id="plan-1",
            status=PlanExecutionStatus.FAILED,
            steps=(
                completed,
                failed,
            ),
        )

        self.assertEqual(
            result.failed_steps,
            (failed,),
        )

    def test_non_plan_id_is_not_checked_here(
        self,
    ):
        result = PlanExecutionResult(
            plan_id="plan-1",
            status=PlanExecutionStatus.COMPLETED,
            steps=(),
        )

        self.assertEqual(
            result.plan_id,
            "plan-1",
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )