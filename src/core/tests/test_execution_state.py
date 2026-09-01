import unittest

from src.core.execution_executor_models import (
    PlanExecutionResult,
    PlanExecutionStatus,
    StepExecutionResult,
    StepExecutionStatus,
)
from src.core.execution_state import ExecutionOutput, ExecutionState


class ExecutionStateTests(unittest.TestCase):
    def test_completed_execution_exposes_outputs_and_complete_action(self):
        execution = PlanExecutionResult(
            plan_id="plan-1",
            status=PlanExecutionStatus.COMPLETED,
            steps=(
                StepExecutionResult(
                    step_id="step-1",
                    action="PROVIDE_INFORMATION",
                    status=StepExecutionStatus.COMPLETED,
                    output="done",
                ),
            ),
        )

        state = ExecutionState.from_execution("do it", execution)

        self.assertEqual(state.goal, "do it")
        self.assertEqual(state.plan_id, "plan-1")
        self.assertEqual(state.completed_steps, ("step-1",))
        self.assertEqual(state.failed_steps, ())
        self.assertEqual(state.available_outputs, (ExecutionOutput("step-1", "done"),))
        self.assertEqual(state.unresolved_requirements, ())
        self.assertEqual(state.next_allowed_actions, ("COMPLETE",))

    def test_failed_execution_exposes_blocker_and_correction_action(self):
        execution = PlanExecutionResult(
            plan_id="plan-2",
            status=PlanExecutionStatus.FAILED,
            steps=(
                StepExecutionResult(
                    step_id="step-1",
                    action="PROVIDE_INFORMATION",
                    status=StepExecutionStatus.COMPLETED,
                    output="partial",
                ),
                StepExecutionResult(
                    step_id="step-2",
                    action="PROVIDE_INFORMATION",
                    status=StepExecutionStatus.FAILED,
                    error="missing input",
                ),
            ),
            error="missing input",
        )

        state = ExecutionState.from_execution("finish it", execution)

        self.assertEqual(state.completed_steps, ("step-1",))
        self.assertEqual(state.failed_steps, ("step-2",))
        self.assertEqual(state.available_outputs, (ExecutionOutput("step-1", "partial"),))
        self.assertEqual(
            state.unresolved_requirements,
            ("Resolve failed step 'step-2': missing input",),
        )
        self.assertEqual(state.next_allowed_actions, ("CORRECT", "STOP"))

    def test_to_context_is_provider_neutral(self):
        execution = PlanExecutionResult(
            plan_id="plan-1",
            status=PlanExecutionStatus.COMPLETED,
            steps=(),
        )
        state = ExecutionState.from_execution("do it", execution)

        context = state.to_context()

        self.assertEqual(context["goal"], "do it")
        self.assertEqual(context["status"], "COMPLETED")
        self.assertEqual(context["next_allowed_actions"], ("COMPLETE",))
        self.assertNotIn("ai_service", context)
        self.assertNotIn("executor", context)

    def test_invalid_output_entry_is_rejected(self):
        with self.assertRaises(TypeError):
            ExecutionState(
                goal="do it",
                plan_id="plan-1",
                status=PlanExecutionStatus.COMPLETED,
                available_outputs=("not an execution output",),
            )


if __name__ == "__main__":
    unittest.main()
