import unittest

from src.core.execution_plan_models import (
    ExecutionPlan,
    PlanStatus,
    PlanStep,
    StepStatus,
)


class ExecutionPlanModelTests(
    unittest.TestCase
):

    def test_plan_step_can_be_created(
        self,
    ):
        step = PlanStep(
            step_id="step-1",
            description="Inspect repository.",
            action="INSPECT_REPOSITORY",
            order=0,
        )

        self.assertEqual(
            step.step_id,
            "step-1",
        )

        self.assertEqual(
            step.status,
            StepStatus.PENDING,
        )

    def test_plan_step_defaults_to_no_dependencies(
        self,
    ):
        step = PlanStep(
            step_id="step-1",
            description="Inspect repository.",
            action="INSPECT_REPOSITORY",
            order=0,
        )

        self.assertEqual(
            step.depends_on,
            (),
        )

    def test_plan_can_be_created(
        self,
    ):
        step = PlanStep(
            step_id="step-1",
            description="Inspect repository.",
            action="INSPECT_REPOSITORY",
            order=0,
        )

        plan = ExecutionPlan(
            plan_id="plan-1",
            task_description="Inspect project.",
            steps=(step,),
        )

        self.assertEqual(
            plan.plan_id,
            "plan-1",
        )

        self.assertEqual(
            plan.status,
            PlanStatus.DRAFT,
        )

    def test_duplicate_step_ids_are_rejected(
        self,
    ):
        step_one = PlanStep(
            step_id="step-1",
            description="One.",
            action="ONE",
            order=0,
        )

        step_two = PlanStep(
            step_id="step-1",
            description="Two.",
            action="TWO",
            order=1,
        )

        with self.assertRaises(
            ValueError
        ):
            ExecutionPlan(
                plan_id="plan-1",
                task_description="Test.",
                steps=(
                    step_one,
                    step_two,
                ),
            )

    def test_unknown_dependency_is_rejected(
        self,
    ):
        step = PlanStep(
            step_id="step-1",
            description="One.",
            action="ONE",
            order=0,
            depends_on=(
                "missing-step",
            ),
        )

        with self.assertRaises(
            ValueError
        ):
            ExecutionPlan(
                plan_id="plan-1",
                task_description="Test.",
                steps=(step,),
            )

    def test_existing_dependency_is_allowed(
        self,
    ):
        step_one = PlanStep(
            step_id="step-1",
            description="One.",
            action="ONE",
            order=0,
        )

        step_two = PlanStep(
            step_id="step-2",
            description="Two.",
            action="TWO",
            order=1,
            depends_on=(
                "step-1",
            ),
        )

        plan = ExecutionPlan(
            plan_id="plan-1",
            task_description="Test.",
            steps=(
                step_one,
                step_two,
            ),
        )

        self.assertEqual(
            plan.steps[1].depends_on,
            ("step-1",),
        )

    def test_empty_step_id_is_rejected(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            PlanStep(
                step_id=" ",
                description="Test.",
                action="TEST",
                order=0,
            )

    def test_empty_description_is_rejected(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            PlanStep(
                step_id="step-1",
                description=" ",
                action="TEST",
                order=0,
            )

    def test_empty_action_is_rejected(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            PlanStep(
                step_id="step-1",
                description="Test.",
                action=" ",
                order=0,
            )

    def test_negative_order_is_rejected(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            PlanStep(
                step_id="step-1",
                description="Test.",
                action="TEST",
                order=-1,
            )

    def test_invalid_step_type_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            ExecutionPlan(
                plan_id="plan-1",
                task_description="Test.",
                steps=("not a step",),
            )

    def test_plan_metadata_defaults_to_empty(
        self,
    ):
        plan = ExecutionPlan(
            plan_id="plan-1",
            task_description="Test.",
            steps=(),
        )

        self.assertEqual(
            plan.metadata,
            {},
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )