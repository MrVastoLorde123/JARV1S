import unittest

from src.core.execution_assessment import ExecutionAssessment
from src.core.execution_executor_models import PlanExecutionStatus
from src.core.execution_state import ExecutionState
from src.core.remaining_work import RemainingWorkResolver


class RemainingWorkResolverTests(unittest.TestCase):
    def setUp(self):
        self.resolver = RemainingWorkResolver()
        self.state = ExecutionState(
            goal="inspect project then modify identified file",
            plan_id="plan-1",
            status=PlanExecutionStatus.FAILED,
            completed_steps=("inspect",),
            failed_steps=("modify",),
            unresolved_requirements=("Resolve failed step 'modify': permission denied",),
            next_allowed_actions=("CORRECT", "STOP"),
        )

    def test_observed_requirements_are_always_preserved(self):
        assessment = ExecutionAssessment(
            goal=self.state.goal,
            situation="blocked",
            completed=("inspect",),
            remaining=(),
            blockers=(),
        )

        remaining = self.resolver.resolve(self.state, assessment)

        self.assertEqual(
            remaining.source_requirements,
            self.state.unresolved_requirements,
        )
        self.assertEqual(
            remaining.items,
            self.state.unresolved_requirements,
        )
        self.assertEqual(
            remaining.blockers,
            self.state.unresolved_requirements,
        )

    def test_matching_model_remaining_work_is_retained(self):
        assessment = ExecutionAssessment(
            goal=self.state.goal,
            situation="blocked",
            completed=("inspect",),
            remaining=("resolve the permission denied modify step",),
            blockers=("permission denied",),
        )

        remaining = self.resolver.resolve(self.state, assessment)

        self.assertIn(
            "resolve the permission denied modify step",
            remaining.items,
        )
        self.assertIn("permission denied", remaining.blockers)

    def test_unrelated_model_remaining_work_is_rejected(self):
        assessment = ExecutionAssessment(
            goal=self.state.goal,
            situation="blocked",
            completed=("inspect",),
            remaining=("deploy authentication fix",),
            blockers=("permission denied",),
        )

        remaining = self.resolver.resolve(self.state, assessment)

        self.assertNotIn("deploy authentication fix", remaining.items)
        self.assertEqual(
            remaining.items,
            self.state.unresolved_requirements,
        )

    def test_failed_step_can_ground_model_remaining_work_without_requirement_text(self):
        state = ExecutionState(
            goal="modify config",
            plan_id="plan-2",
            status=PlanExecutionStatus.FAILED,
            failed_steps=("modify",),
            unresolved_requirements=(),
            next_allowed_actions=("CORRECT", "STOP"),
        )
        assessment = ExecutionAssessment(
            goal=state.goal,
            situation="no_progress",
            remaining=("modify authentication config",),
        )

        remaining = self.resolver.resolve(state, assessment)

        self.assertEqual(remaining.items, ("modify authentication config",))
        self.assertEqual(remaining.source_requirements, ())

    def test_completed_execution_has_no_remaining_work(self):
        state = ExecutionState(
            goal="inspect project",
            plan_id="plan-3",
            status=PlanExecutionStatus.COMPLETED,
            completed_steps=("inspect",),
            next_allowed_actions=("COMPLETE",),
        )
        assessment = ExecutionAssessment(
            goal=state.goal,
            situation="objective_completed",
            completed=("inspect",),
            remaining=("do something else",),
        )

        remaining = self.resolver.resolve(state, assessment)

        self.assertEqual(remaining.items, ())
        self.assertEqual(remaining.blockers, ())
        self.assertEqual(remaining.source_requirements, ())

    def test_goal_mismatch_is_rejected(self):
        assessment = ExecutionAssessment(
            goal="different goal",
            situation="blocked",
        )

        with self.assertRaisesRegex(ValueError, "goal"):
            self.resolver.resolve(self.state, assessment)

    def test_invalid_inputs_are_rejected(self):
        assessment = ExecutionAssessment(
            goal=self.state.goal,
            situation="blocked",
        )

        with self.assertRaises(TypeError):
            self.resolver.resolve("not state", assessment)
        with self.assertRaises(TypeError):
            self.resolver.resolve(self.state, "not assessment")

    def test_only_meaningfully_matching_model_blockers_are_retained(self):
        assessment = ExecutionAssessment(
            goal=self.state.goal,
            situation="blocked",
            completed=("inspect",),
            blockers=("permission denied", "network issue"),
        )

        remaining = self.resolver.resolve(self.state, assessment)

        self.assertIn("permission denied", remaining.blockers)
        self.assertNotIn("network issue", remaining.blockers)


if __name__ == "__main__":
    unittest.main()
