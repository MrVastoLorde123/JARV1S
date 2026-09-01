import unittest

from src.core.execution_plan_models import (
    ExecutionPlan,
    PlanStatus,
    PlanStep,
    StepStatus,
)
from src.core.execution_planner import ExecutionPlanner
from src.core.execution_planning import ExecutionPlannerProtocol
from src.core.task_models import TaskRequest, TaskType


class FakeMultiStepPlanner:
    """Minimal provider-neutral planner proving the boundary supports multi-step plans."""

    def plan(self, task: TaskRequest) -> ExecutionPlan:
        return ExecutionPlan(
            plan_id="multi-step-plan",
            task_description=task.content.strip(),
            steps=(
                PlanStep(
                    step_id="step-1",
                    description="Inspect the workspace.",
                    action="INSPECT",
                    order=0,
                    status=StepStatus.READY,
                ),
                PlanStep(
                    step_id="step-2",
                    description="Report the result.",
                    action="REPORT",
                    order=1,
                    depends_on=("step-1",),
                    status=StepStatus.PENDING,
                ),
            ),
            status=PlanStatus.READY,
            metadata={"planner": "fake-multi-step", "step_count": 2},
        )


class ExecutionPlanningProtocolTests(unittest.TestCase):
    def test_deterministic_planner_implements_provider_neutral_contract(self):
        self.assertIsInstance(ExecutionPlanner(), ExecutionPlannerProtocol)

    def test_multi_step_planner_implements_provider_neutral_contract(self):
        planner = FakeMultiStepPlanner()
        self.assertIsInstance(planner, ExecutionPlannerProtocol)

    def test_contract_returns_multi_step_execution_plan(self):
        planner = FakeMultiStepPlanner()
        task = TaskRequest(
            content="Inspect and report.",
            task_type=TaskType.ACTION,
        )

        plan = planner.plan(task)

        self.assertIsInstance(plan, ExecutionPlan)
        self.assertEqual(len(plan.steps), 2)
        self.assertEqual(plan.steps[1].depends_on, ("step-1",))
        self.assertEqual(plan.metadata["step_count"], 2)

    def test_contract_does_not_define_execution_authority(self):
        planner = FakeMultiStepPlanner()

        self.assertFalse(hasattr(planner, "execute"))
        self.assertFalse(hasattr(planner, "authorize"))
        self.assertFalse(hasattr(planner, "validate"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
