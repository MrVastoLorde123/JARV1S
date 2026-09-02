import unittest

from src.core.execution_assessment import ExecutionAssessment
from src.core.execution_assessment_validator import ExecutionAssessmentValidator
from src.core.execution_executor_models import PlanExecutionStatus
from src.core.execution_state import ExecutionOutput, ExecutionState


class ExecutionAssessmentValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = ExecutionAssessmentValidator()
        self.state = ExecutionState(
            goal="inspect project then modify identified file",
            plan_id="plan-1",
            status=PlanExecutionStatus.FAILED,
            completed_steps=("inspect",),
            failed_steps=("modify",),
            available_outputs=(ExecutionOutput("inspect", "auth/config.py"),),
            unresolved_requirements=("Resolve failed step 'modify': permission denied",),
            next_allowed_actions=("CORRECT", "STOP"),
        )

    def _assessment(
        self,
        *,
        situation="partial_progress",
        completed=("inspect project",),
        remaining=("modify auth/config.py",),
        blockers=("permission denied",),
    ):
        return ExecutionAssessment(
            goal=self.state.goal,
            situation=situation,
            completed=completed,
            remaining=remaining,
            blockers=blockers,
            useful_outputs=self.state.available_outputs,
            recommended_next_action="address permissions",
            confidence=0.9,
        )

    def test_valid_model_interpretation_is_accepted(self):
        assessment = self._assessment()
        self.assertIs(self.validator.validate(self.state, assessment), assessment)

    def test_failed_step_cannot_be_claimed_as_completed(self):
        assessment = self._assessment(
            completed=("modify authentication config",),
        )

        with self.assertRaisesRegex(ValueError, "failed step 'modify'"):
            self.validator.validate(self.state, assessment)

    def test_unobserved_completed_work_is_rejected(self):
        assessment = self._assessment(
            completed=("deploy authentication fix",),
        )

        with self.assertRaisesRegex(ValueError, "not grounded"):
            self.validator.validate(self.state, assessment)

    def test_observed_unresolved_requirement_cannot_be_omitted(self):
        assessment = self._assessment(blockers=())

        with self.assertRaisesRegex(ValueError, "unresolved requirement"):
            self.validator.validate(self.state, assessment)

    def test_non_completed_state_cannot_be_declared_complete(self):
        assessment = self._assessment(situation="objective_completed")

        with self.assertRaisesRegex(ValueError, "non-completed execution"):
            self.validator.validate(self.state, assessment)

    def test_completed_state_requires_objective_completed(self):
        state = ExecutionState(
            goal="inspect project",
            plan_id="plan-2",
            status=PlanExecutionStatus.COMPLETED,
            completed_steps=("inspect",),
            next_allowed_actions=("COMPLETE",),
        )
        assessment = ExecutionAssessment(
            goal=state.goal,
            situation="partial_progress",
            completed=("inspect project",),
        )

        with self.assertRaisesRegex(ValueError, "observed completed execution"):
            self.validator.validate(state, assessment)

    def test_goal_mismatch_is_rejected(self):
        assessment = ExecutionAssessment(
            goal="different goal",
            situation="partial_progress",
            completed=("inspect",),
        )

        with self.assertRaisesRegex(ValueError, "goal does not match"):
            self.validator.validate(self.state, assessment)

    def test_input_types_are_rejected(self):
        with self.assertRaises(TypeError):
            self.validator.validate("not state", self._assessment())
        with self.assertRaises(TypeError):
            self.validator.validate(self.state, "not assessment")


if __name__ == "__main__":
    unittest.main()
