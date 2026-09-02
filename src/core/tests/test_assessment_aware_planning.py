import unittest
from unittest.mock import Mock

from src.core.assessment_aware_planning import AssessmentAwarePlanningService
from src.core.execution_assessment import ExecutionAssessment
from src.core.execution_executor_models import PlanExecutionStatus
from src.core.execution_plan_models import ExecutionPlan, PlanStatus, PlanStep, StepStatus
from src.core.execution_state import ExecutionState
from src.core.remaining_work import RemainingWork
from src.core.task_models import TaskRequest, TaskType


class AssessmentAwarePlanningTests(unittest.TestCase):
    def setUp(self):
        self.task = TaskRequest("inspect project then modify identified file", TaskType.ACTION)
        self.state = ExecutionState(
            goal=self.task.content,
            plan_id="attempt-1",
            status=PlanExecutionStatus.FAILED,
            completed_steps=("inspect",),
            failed_steps=("modify",),
            unresolved_requirements=("Resolve failed step 'modify': permission denied",),
            next_allowed_actions=("CORRECT", "STOP"),
        )
        self.assessment = ExecutionAssessment(
            goal=self.state.goal,
            situation="blocked",
            completed=("inspect project",),
            remaining=("modify identified file",),
            blockers=("permission denied",),
            recommended_next_action="address permissions",
            confidence=0.9,
        )

    @staticmethod
    def _plan(task, progress=None, remaining_work=None):
        return ExecutionPlan(
            plan_id="plan-next",
            task_description=task.content,
            steps=(
                PlanStep(
                    step_id="step-1",
                    description="resolve modify permission issue",
                    action="PERFORM_ACTION",
                    order=0,
                    status=StepStatus.READY,
                ),
            ),
            status=PlanStatus.READY,
            metadata={
                "remaining": None if remaining_work is None else remaining_work.items,
            },
        )

    def test_valid_assessment_is_reconciled_before_planning(self):
        planner = Mock()
        planner.plan.side_effect = self._plan
        service = AssessmentAwarePlanningService(planner)

        plan = service.plan(self.task, self.state, self.assessment)

        self.assertIsInstance(plan, ExecutionPlan)
        planner.plan.assert_called_once()
        remaining = planner.plan.call_args.kwargs["remaining_work"]
        self.assertIsInstance(remaining, RemainingWork)
        self.assertIn("Resolve failed step 'modify': permission denied", remaining.items)
        self.assertIn("modify identified file", remaining.items)

    def test_invalid_assessment_never_reaches_planner(self):
        planner = Mock()
        service = AssessmentAwarePlanningService(planner)
        invalid = ExecutionAssessment(
            goal=self.state.goal,
            situation="objective_completed",
            completed=("modify authentication config",),
        )

        with self.assertRaises(ValueError):
            service.plan(self.task, self.state, invalid)

        planner.plan.assert_not_called()

    def test_goal_mismatch_between_task_and_state_is_rejected(self):
        planner = Mock()
        service = AssessmentAwarePlanningService(planner)
        mismatched_state = ExecutionState(
            goal="different objective",
            plan_id="attempt-2",
            status=PlanExecutionStatus.FAILED,
        )

        with self.assertRaisesRegex(ValueError, "task objective"):
            service.plan(self.task, mismatched_state, self.assessment)

        planner.plan.assert_not_called()

    def test_completed_state_produces_empty_remaining_work(self):
        planner = Mock()
        planner.plan.side_effect = self._plan
        service = AssessmentAwarePlanningService(planner)
        state = ExecutionState(
            goal="inspect project",
            plan_id="attempt-3",
            status=PlanExecutionStatus.COMPLETED,
            completed_steps=("inspect",),
            next_allowed_actions=("COMPLETE",),
        )
        assessment = ExecutionAssessment(
            goal=state.goal,
            situation="objective_completed",
            completed=("inspect",),
        )
        task = TaskRequest("inspect project", TaskType.ACTION)

        result = service.plan(task, state, assessment)

        remaining = planner.plan.call_args.kwargs["remaining_work"]
        self.assertEqual(remaining.items, ())
        self.assertEqual(remaining.blockers, ())
        self.assertIsInstance(result, ExecutionPlan)

    def test_planner_contract_accepts_grounded_remaining_work_without_metadata_fallback(self):
        planner = Mock()
        planner.plan.side_effect = self._plan
        service = AssessmentAwarePlanningService(planner)

        service.plan(self.task, self.state, self.assessment)

        kwargs = planner.plan.call_args.kwargs
        self.assertIn("remaining_work", kwargs)
        self.assertIsNone(kwargs["progress"])
        self.assertNotIn("assessment_remaining_work", self.task.metadata)

    def test_resolve_remaining_work_exposes_grounded_result_without_planning(self):
        planner = Mock()
        service = AssessmentAwarePlanningService(planner)

        remaining = service.resolve_remaining_work(self.state, self.assessment)

        self.assertEqual(remaining.goal, self.state.goal)
        self.assertEqual(remaining.source_requirements, self.state.unresolved_requirements)
        planner.plan.assert_not_called()


if __name__ == "__main__":
    unittest.main()
