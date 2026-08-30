import unittest

from src.core.execution_plan_models import (
    ExecutionPlan,
    PlanStatus,
    PlanStep,
    StepStatus,
)

from src.core.plan_validator import (
    PlanValidator,
)

from src.core.task_models import (
    TaskRequest,
    TaskType,
)


class PlanValidatorTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):
        self.validator = PlanValidator()

    def _step(
        self,
        step_id="step-1",
        order=0,
        action="TEST",
        depends_on=(),
        requires_confirmation=False,
    ):
        return PlanStep(
            step_id=step_id,
            description="Test step.",
            action=action,
            order=order,
            depends_on=depends_on,
            status=StepStatus.READY,
            requires_confirmation=(
                requires_confirmation
            ),
        )

    def _plan(
        self,
        steps,
    ):
        return ExecutionPlan(
            plan_id="plan-1",
            task_description="Test plan.",
            steps=tuple(steps),
            status=PlanStatus.READY,
        )

    def test_valid_plan_is_accepted(
        self,
    ):
        plan = self._plan(
            [
                self._step()
            ]
        )

        result = self.validator.validate(
            plan
        )

        self.assertTrue(
            result.valid
        )

        self.assertEqual(
            result.issues,
            (),
        )

    def test_result_contains_validator_metadata(
        self,
    ):
        plan = self._plan(
            [
                self._step()
            ]
        )

        result = self.validator.validate(
            plan
        )

        self.assertEqual(
            result.metadata["validator"],
            "deterministic",
        )

        self.assertEqual(
            result.metadata["step_count"],
            1,
        )

        self.assertEqual(
            result.metadata["issue_count"],
            0,
        )

    def test_non_plan_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            self.validator.validate(
                "not a plan"
            )

    def test_empty_action_is_rejected_before_validation(
            self,
    ):
        with self.assertRaises(
                ValueError
        ):
            PlanStep(
                step_id="step-1",
                description="Test step.",
                action=" ",
                order=0,
                status=StepStatus.READY,
            )

    def test_dependency_cycle_is_rejected(
        self,
    ):
        step_one = self._step(
            step_id="step-1",
            order=0,
            depends_on=("step-2",),
        )

        step_two = self._step(
            step_id="step-2",
            order=1,
            depends_on=("step-1",),
        )

        plan = self._plan(
            [
                step_one,
                step_two,
            ]
        )

        result = self.validator.validate(
            plan
        )

        self.assertFalse(
            result.valid
        )

        self.assertTrue(
            any(
                issue.code
                == "DEPENDENCY_CYCLE"
                for issue in result.issues
            )
        )

    def test_linear_dependencies_are_allowed(
        self,
    ):
        step_one = self._step(
            step_id="step-1",
            order=0,
        )

        step_two = self._step(
            step_id="step-2",
            order=1,
            depends_on=("step-1",),
        )

        step_three = self._step(
            step_id="step-3",
            order=2,
            depends_on=("step-2",),
        )

        plan = self._plan(
            [
                step_one,
                step_two,
                step_three,
            ]
        )

        result = self.validator.validate(
            plan
        )

        self.assertTrue(
            result.valid
        )

    def test_multiple_dependencies_are_allowed(
        self,
    ):
        step_one = self._step(
            step_id="step-1",
            order=0,
        )

        step_two = self._step(
            step_id="step-2",
            order=1,
        )

        step_three = self._step(
            step_id="step-3",
            order=2,
            depends_on=(
                "step-1",
                "step-2",
            ),
        )

        plan = self._plan(
            [
                step_one,
                step_two,
                step_three,
            ]
        )

        result = self.validator.validate(
            plan
        )

        self.assertTrue(
            result.valid
        )

    def test_duplicate_order_is_rejected(
        self,
    ):
        first = self._step(
            step_id="step-1",
            order=0,
        )

        second = self._step(
            step_id="step-2",
            order=0,
        )

        plan = self._plan(
            [
                first,
                second,
            ]
        )

        result = self.validator.validate(
            plan
        )

        self.assertFalse(
            result.valid
        )

        self.assertTrue(
            any(
                issue.code
                == "DUPLICATE_ORDER"
                for issue in result.issues
            )
        )

    def test_unsorted_order_is_rejected(
        self,
    ):
        first = self._step(
            step_id="step-1",
            order=1,
        )

        second = self._step(
            step_id="step-2",
            order=0,
        )

        plan = self._plan(
            [
                first,
                second,
            ]
        )

        result = self.validator.validate(
            plan
        )

        self.assertFalse(
            result.valid
        )

        self.assertTrue(
            any(
                issue.code
                == "UNSORTED_ORDER"
                for issue in result.issues
            )
        )

    def test_non_contiguous_order_is_rejected(
        self,
    ):
        first = self._step(
            step_id="step-1",
            order=0,
        )

        second = self._step(
            step_id="step-2",
            order=2,
        )

        plan = self._plan(
            [
                first,
                second,
            ]
        )

        result = self.validator.validate(
            plan
        )

        self.assertFalse(
            result.valid
        )

        self.assertTrue(
            any(
                issue.code
                == "INVALID_ORDER_SEQUENCE"
                for issue in result.issues
            )
        )

    def test_confirmation_flag_can_be_true(
        self,
    ):
        plan = self._plan(
            [
                self._step(
                    requires_confirmation=True
                )
            ]
        )

        result = self.validator.validate(
            plan
        )

        self.assertTrue(
            result.valid
        )

    def test_validator_does_not_modify_plan(
        self,
    ):
        plan = self._plan(
            [
                self._step()
            ]
        )

        before = plan

        self.validator.validate(
            plan
        )

        self.assertEqual(
            plan,
            before,
        )

    def test_valid_plan_with_empty_steps_is_allowed(
        self,
    ):
        plan = self._plan(
            []
        )

        result = self.validator.validate(
            plan
        )

        self.assertTrue(
            result.valid
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )