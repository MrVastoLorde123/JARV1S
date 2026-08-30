import unittest

from src.core.execution_plan_models import (
    ExecutionPlan,
    PlanStatus,
    PlanStep,
    StepStatus,
)

from src.core.execution_policy import (
    ExecutionPolicy,
)

from src.core.execution_policy_models import (
    PolicyDecision,
)


class ExecutionPolicyTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):
        self.policy = ExecutionPolicy()

    def _step(
        self,
        action,
        step_id="step-1",
        order=0,
        requires_confirmation=False,
    ):
        return PlanStep(
            step_id=step_id,
            description="Test step.",
            action=action,
            order=order,
            status=StepStatus.READY,
            requires_confirmation=(
                requires_confirmation
            ),
        )

    def _plan(
        self,
        *steps,
    ):
        return ExecutionPlan(
            plan_id="plan-1",
            task_description="Test plan.",
            steps=tuple(steps),
            status=PlanStatus.READY,
        )

    def test_information_plan_is_allowed(
        self,
    ):
        plan = self._plan(
            self._step(
                "PROVIDE_INFORMATION"
            )
        )

        result = self.policy.evaluate(
            plan
        )

        self.assertEqual(
            result.decision,
            PolicyDecision.ALLOW,
        )

    def test_tool_plan_requires_confirmation(
        self,
    ):
        plan = self._plan(
            self._step(
                "USE_TOOL"
            )
        )

        result = self.policy.evaluate(
            plan
        )

        self.assertEqual(
            result.decision,
            PolicyDecision.REQUIRE_CONFIRMATION,
        )

    def test_action_plan_requires_confirmation(
        self,
    ):
        plan = self._plan(
            self._step(
                "PERFORM_ACTION"
            )
        )

        result = self.policy.evaluate(
            plan
        )

        self.assertEqual(
            result.decision,
            PolicyDecision.REQUIRE_CONFIRMATION,
        )

    def test_unclassified_task_is_denied(
        self,
    ):
        plan = self._plan(
            self._step(
                "UNCLASSIFIED_TASK"
            )
        )

        result = self.policy.evaluate(
            plan
        )

        self.assertEqual(
            result.decision,
            PolicyDecision.DENY,
        )

        self.assertTrue(
            result.issues
        )

    def test_unknown_action_is_denied(
        self,
    ):
        plan = self._plan(
            self._step(
                "DO_SOMETHING_MAGIC"
            )
        )

        result = self.policy.evaluate(
            plan
        )

        self.assertEqual(
            result.decision,
            PolicyDecision.DENY,
        )

        self.assertEqual(
            result.issues[0].code,
            "UNKNOWN_ACTION",
        )

    def test_explicit_confirmation_flag_requires_confirmation(
        self,
    ):
        plan = self._plan(
            self._step(
                "PROVIDE_INFORMATION",
                requires_confirmation=True,
            )
        )

        result = self.policy.evaluate(
            plan
        )

        self.assertEqual(
            result.decision,
            PolicyDecision.REQUIRE_CONFIRMATION,
        )

    def test_one_confirmation_step_causes_plan_confirmation(
        self,
    ):
        first = self._step(
            "PROVIDE_INFORMATION",
            step_id="step-1",
            order=0,
        )

        second = self._step(
            "USE_TOOL",
            step_id="step-2",
            order=1,
        )

        plan = self._plan(
            first,
            second,
        )

        result = self.policy.evaluate(
            plan
        )

        self.assertEqual(
            result.decision,
            PolicyDecision.REQUIRE_CONFIRMATION,
        )

    def test_deny_takes_precedence_over_confirmation(
        self,
    ):
        first = self._step(
            "USE_TOOL",
            step_id="step-1",
            order=0,
        )

        second = self._step(
            "UNCLASSIFIED_TASK",
            step_id="step-2",
            order=1,
        )

        plan = self._plan(
            first,
            second,
        )

        result = self.policy.evaluate(
            plan
        )

        self.assertEqual(
            result.decision,
            PolicyDecision.DENY,
        )

    def test_empty_plan_is_denied(
        self,
    ):
        plan = self._plan()

        result = self.policy.evaluate(
            plan
        )

        self.assertEqual(
            result.decision,
            PolicyDecision.DENY,
        )

        self.assertEqual(
            result.issues[0].code,
            "EMPTY_PLAN",
        )

    def test_non_plan_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            self.policy.evaluate(
                "not a plan"
            )

    def test_policy_does_not_modify_plan(
        self,
    ):
        plan = self._plan(
            self._step(
                "USE_TOOL"
            )
        )

        before = plan

        self.policy.evaluate(
            plan
        )

        self.assertEqual(
            plan,
            before,
        )

    def test_policy_is_deterministic(
        self,
    ):
        plan = self._plan(
            self._step(
                "USE_TOOL"
            )
        )

        first = self.policy.evaluate(
            plan
        )

        second = self.policy.evaluate(
            plan
        )

        self.assertEqual(
            first,
            second,
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )