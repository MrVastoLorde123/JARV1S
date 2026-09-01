import unittest

from src.core.execution_plan_models import (
    PlanStatus,
    StepStatus,
)

from src.core.execution_planner import (
    ExecutionPlanner,
)

from src.core.task_models import (
    TaskRequest,
    TaskType,
)


class ExecutionPlannerTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):
        self.planner = ExecutionPlanner()

    def test_information_task_produces_information_action(
        self,
    ):
        task = TaskRequest(
            content="Explain Modbus.",
            task_type=TaskType.INFORMATION,
        )

        plan = self.planner.plan(
            task
        )

        self.assertEqual(
            plan.steps[0].action,
            "PROVIDE_INFORMATION",
        )

    def test_action_task_produces_action(
        self,
    ):
        task = TaskRequest(
            content="Organize these files.",
            task_type=TaskType.ACTION,
        )

        plan = self.planner.plan(
            task
        )

        self.assertEqual(
            plan.steps[0].action,
            "PERFORM_ACTION",
        )

    def test_tool_task_produces_tool_action(
        self,
    ):
        task = TaskRequest(
            content="Inspect the repository.",
            task_type=TaskType.TOOL,
            metadata={
                "tool_name": "list_directory",
                "arguments": {"path": "."},
            },
        )

        plan = self.planner.plan(
            task
        )

        self.assertEqual(
            plan.steps[0].action,
            "USE_TOOL",
        )

    def test_unknown_task_produces_unclassified_action(
        self,
    ):
        task = TaskRequest(
            content="Do something.",
        )

        plan = self.planner.plan(
            task
        )

        self.assertEqual(
            plan.steps[0].action,
            "UNCLASSIFIED_TASK",
        )

    def test_plan_is_ready(
        self,
    ):
        task = TaskRequest(
            content="Inspect repository.",
            task_type=TaskType.ACTION,
        )

        plan = self.planner.plan(
            task
        )

        self.assertEqual(
            plan.status,
            PlanStatus.READY,
        )

    def test_first_step_is_ready(
        self,
    ):
        task = TaskRequest(
            content="Inspect repository.",
            task_type=TaskType.ACTION,
        )

        plan = self.planner.plan(
            task
        )

        self.assertEqual(
            plan.steps[0].status,
            StepStatus.READY,
        )

    def test_task_description_is_preserved(
        self,
    ):
        task = TaskRequest(
            content="  Inspect repository.  ",
            task_type=TaskType.ACTION,
        )

        plan = self.planner.plan(
            task
        )

        self.assertEqual(
            plan.task_description,
            "Inspect repository.",
        )

        self.assertEqual(
            plan.steps[0].description,
            "Inspect repository.",
        )

    def test_plan_contains_one_step_in_v1(
        self,
    ):
        task = TaskRequest(
            content="Inspect repository.",
            task_type=TaskType.ACTION,
        )

        plan = self.planner.plan(
            task
        )

        self.assertEqual(
            len(plan.steps),
            1,
        )

    def test_step_has_stable_order(
        self,
    ):
        task = TaskRequest(
            content="Inspect repository.",
            task_type=TaskType.ACTION,
        )

        plan = self.planner.plan(
            task
        )

        self.assertEqual(
            plan.steps[0].order,
            0,
        )

    def test_plan_ids_are_unique(
        self,
    ):
        task = TaskRequest(
            content="Inspect repository.",
            task_type=TaskType.ACTION,
        )

        first = self.planner.plan(
            task
        )

        second = self.planner.plan(
            task
        )

        self.assertNotEqual(
            first.plan_id,
            second.plan_id,
        )

    def test_invalid_task_type_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            self.planner.plan(
                "not a task"
            )

    def test_empty_task_is_rejected(
        self,
    ):
        task = TaskRequest(
            content=" ",
            task_type=TaskType.ACTION,
        )

        with self.assertRaises(
            ValueError
        ):
            self.planner.plan(
                task
            )

    def test_planner_metadata_is_present(
        self,
    ):
        task = TaskRequest(
            content="Inspect repository.",
            task_type=TaskType.ACTION,
        )

        plan = self.planner.plan(
            task
        )

        self.assertEqual(
            plan.metadata["planner"],
            "deterministic",
        )

        self.assertEqual(
            plan.metadata["task_type"],
            "ACTION",
        )

        self.assertEqual(
            plan.metadata["step_count"],
            1,
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )