import unittest

from src.core.execution_assessment import ExecutionAssessment, ExecutionAssessmentService
from src.core.execution_executor_models import PlanExecutionStatus
from src.core.execution_state import ExecutionOutput, ExecutionState


class ExecutionAssessmentTests(unittest.TestCase):
    def setUp(self):
        self.service = ExecutionAssessmentService()

    def test_completed_state_is_assessed_as_objective_completed(self):
        state = ExecutionState(
            goal="inspect project",
            plan_id="plan-1",
            status=PlanExecutionStatus.COMPLETED,
            completed_steps=("step-1",),
            available_outputs=(ExecutionOutput("step-1", "done"),),
            next_allowed_actions=("COMPLETE",),
        )

        result = self.service.assess(state)

        self.assertEqual(result.situation, "objective_completed")
        self.assertEqual(result.completed, ("step-1",))
        self.assertEqual(result.remaining, ())
        self.assertEqual(result.blockers, ())
        self.assertIsNone(result.recommended_next_action)
        self.assertEqual(result.useful_outputs, state.available_outputs)

    def test_failed_state_is_assessed_as_blocked(self):
        state = ExecutionState(
            goal="modify file",
            plan_id="plan-2",
            status=PlanExecutionStatus.FAILED,
            completed_steps=("inspect",),
            failed_steps=("modify",),
            unresolved_requirements=("Resolve failed step 'modify': permission denied",),
            next_allowed_actions=("CORRECT", "STOP"),
        )

        result = self.service.assess(state)

        self.assertEqual(result.situation, "blocked")
        self.assertEqual(result.completed, ("inspect",))
        self.assertEqual(result.remaining, state.unresolved_requirements)
        self.assertEqual(result.blockers, state.unresolved_requirements)
        self.assertEqual(result.recommended_next_action, "CORRECT")

    def test_explicitly_blocked_state_is_assessed_as_blocked(self):
        state = ExecutionState(
            goal="modify file",
            plan_id="plan-3",
            status=PlanExecutionStatus.BLOCKED,
            completed_steps=("inspect",),
            unresolved_requirements=("confirmation required",),
            next_allowed_actions=("STOP",),
        )

        result = self.service.assess(state)

        self.assertEqual(result.situation, "blocked")
        self.assertEqual(result.completed, ("inspect",))
        self.assertEqual(result.remaining, ("confirmation required",))
        self.assertEqual(result.blockers, ("confirmation required",))
        self.assertIsNone(result.recommended_next_action)

    def test_terminal_state_with_completed_work_and_no_blocker_is_partial_progress(self):
        state = ExecutionState(
            goal="inspect then summarize",
            plan_id="plan-4",
            status=PlanExecutionStatus.FAILED,
            completed_steps=("inspect",),
            next_allowed_actions=("CORRECT", "STOP"),
        )

        result = self.service.assess(state)

        self.assertEqual(result.situation, "partial_progress")
        self.assertEqual(result.completed, ("inspect",))
        self.assertEqual(result.remaining, ())
        self.assertEqual(result.blockers, ())
        self.assertEqual(result.recommended_next_action, "CORRECT")

    def test_terminal_state_without_completed_work_or_blocker_is_no_progress(self):
        state = ExecutionState(
            goal="inspect project",
            plan_id="plan-5",
            status=PlanExecutionStatus.BLOCKED,
            next_allowed_actions=("STOP",),
        )

        result = self.service.assess(state)

        self.assertEqual(result.situation, "no_progress")
        self.assertEqual(result.completed, ())
        self.assertEqual(result.remaining, ())
        self.assertEqual(result.blockers, ())
        self.assertEqual(result.recommended_next_action, "STOP")

    def test_assessment_is_provider_neutral(self):
        state = ExecutionState(
            goal="inspect project",
            plan_id="plan-6",
            status=PlanExecutionStatus.COMPLETED,
        )

        result = self.service.assess(state)
        context = result.to_context()

        self.assertIsInstance(result, ExecutionAssessment)
        self.assertEqual(context["goal"], "inspect project")
        self.assertNotIn("provider", context)
        self.assertNotIn("executor", context)

    def test_non_state_input_is_rejected(self):
        with self.assertRaises(TypeError):
            self.service.assess("not state")


if __name__ == "__main__":
    unittest.main()
