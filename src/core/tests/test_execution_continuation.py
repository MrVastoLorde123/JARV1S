import unittest

from src.core.execution_executor_models import PlanExecutionStatus
from src.core.execution_loop import ExecutionContinuationService, ExecutionObservation
from src.core.execution_plan_models import ExecutionPlan, PlanStatus, PlanStep, StepStatus
from src.core.execution_state import ExecutionState


class ExecutionContinuationServiceTests(unittest.TestCase):
    def _observation(self, state):
        plan = ExecutionPlan(
            plan_id="plan-1",
            task_description="do it",
            status=PlanStatus.READY,
            steps=(
                PlanStep(
                    step_id="step-1",
                    description="do it",
                    action="PROVIDE_INFORMATION",
                    order=0,
                    status=StepStatus.READY,
                ),
            ),
        )
        from src.core.execution_executor_models import PlanExecutionResult

        execution = PlanExecutionResult(
            plan_id="plan-1",
            status=PlanExecutionStatus.FAILED,
            steps=(),
        )
        return ExecutionObservation(plan=plan, execution=execution, state=state)

    def test_complete_action_wins_when_state_marks_completion(self):
        state = ExecutionState(
            goal="do it",
            plan_id="plan-1",
            status=PlanExecutionStatus.COMPLETED,
            next_allowed_actions=("COMPLETE",),
        )

        decision = ExecutionContinuationService().decide(state)

        self.assertEqual(decision.action, "COMPLETE")
        self.assertFalse(decision.should_continue)

    def test_correct_action_allows_continuation(self):
        state = ExecutionState(
            goal="do it",
            plan_id="plan-1",
            status=PlanExecutionStatus.FAILED,
            failed_steps=("step-1",),
            unresolved_requirements=("Resolve failed step 'step-1': boom",),
            next_allowed_actions=("CORRECT", "STOP"),
        )

        decision = ExecutionContinuationService().decide(state)

        self.assertEqual(decision.action, "CONTINUE")
        self.assertTrue(decision.should_continue)

    def test_stop_only_state_prevents_continuation(self):
        state = ExecutionState(
            goal="do it",
            plan_id="plan-1",
            status=PlanExecutionStatus.BLOCKED,
            next_allowed_actions=("STOP",),
        )

        decision = ExecutionContinuationService().decide(state)

        self.assertEqual(decision.action, "STOP")
        self.assertFalse(decision.should_continue)

    def test_legacy_observation_input_is_still_supported(self):
        state = ExecutionState(
            goal="do it",
            plan_id="plan-1",
            status=PlanExecutionStatus.FAILED,
            next_allowed_actions=("CORRECT", "STOP"),
        )

        decision = ExecutionContinuationService().decide(self._observation(state))

        self.assertEqual(decision.action, "CONTINUE")

    def test_invalid_input_is_rejected(self):
        with self.assertRaises(TypeError):
            ExecutionContinuationService().decide(None)


if __name__ == "__main__":
    unittest.main()
