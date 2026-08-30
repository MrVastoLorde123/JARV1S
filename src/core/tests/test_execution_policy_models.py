import unittest

from src.core.execution_plan_models import (
    ExecutionPlan,
)

from src.core.execution_policy_models import (
    ExecutionPolicyResult,
    PolicyDecision,
    PolicyIssue,
)


class ExecutionPolicyModelTests(
    unittest.TestCase
):

    def _plan(self):
        return ExecutionPlan(
            plan_id="plan-1",
            task_description="Test plan.",
            steps=(),
        )

    def test_issue_can_be_created(
        self,
    ):
        issue = PolicyIssue(
            code="TEST",
            message="Test issue.",
        )

        self.assertEqual(
            issue.code,
            "TEST",
        )

        self.assertIsNone(
            issue.step_id
        )

    def test_issue_metadata_defaults_to_empty(
        self,
    ):
        issue = PolicyIssue(
            code="TEST",
            message="Test issue.",
        )

        self.assertEqual(
            issue.metadata,
            {},
        )

    def test_result_can_be_created(
        self,
    ):
        result = ExecutionPolicyResult(
            decision=PolicyDecision.ALLOW,
            plan=self._plan(),
        )

        self.assertEqual(
            result.decision,
            PolicyDecision.ALLOW,
        )

    def test_result_helpers_are_available(
        self,
    ):
        plan = self._plan()

        allowed = ExecutionPolicyResult(
            decision=PolicyDecision.ALLOW,
            plan=plan,
        )

        confirmation = ExecutionPolicyResult(
            decision=(
                PolicyDecision.REQUIRE_CONFIRMATION
            ),
            plan=plan,
        )

        denied = ExecutionPolicyResult(
            decision=PolicyDecision.DENY,
            plan=plan,
        )

        self.assertTrue(
            allowed.allowed
        )

        self.assertTrue(
            confirmation.requires_confirmation
        )

        self.assertTrue(
            denied.denied
        )

    def test_issue_count_is_available(
        self,
    ):
        result = ExecutionPolicyResult(
            decision=PolicyDecision.DENY,
            plan=self._plan(),
            issues=(
                PolicyIssue(
                    code="ONE",
                    message="One.",
                ),
                PolicyIssue(
                    code="TWO",
                    message="Two.",
                ),
            ),
        )

        self.assertEqual(
            result.issue_count,
            2,
        )

    def test_non_plan_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            ExecutionPolicyResult(
                decision=PolicyDecision.ALLOW,
                plan="not a plan",
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )