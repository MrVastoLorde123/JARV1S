import unittest

from src.core.execution_plan_models import (
    ExecutionPlan,
)

from src.core.plan_validation_models import (
    PlanValidationIssue,
    PlanValidationResult,
)


class PlanValidationModelTests(
    unittest.TestCase
):

    def _plan(self):
        return ExecutionPlan(
            plan_id="plan-1",
            task_description="Test.",
            steps=(),
        )

    def test_issue_can_be_created(
        self,
    ):
        issue = PlanValidationIssue(
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
        issue = PlanValidationIssue(
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
        result = PlanValidationResult(
            valid=True,
            plan=self._plan(),
        )

        self.assertTrue(
            result.valid
        )

    def test_result_issues_default_to_empty(
        self,
    ):
        result = PlanValidationResult(
            valid=True,
            plan=self._plan(),
        )

        self.assertEqual(
            result.issues,
            (),
        )

    def test_error_count_is_available(
        self,
    ):
        result = PlanValidationResult(
            valid=False,
            plan=self._plan(),
            issues=(
                PlanValidationIssue(
                    code="ONE",
                    message="One.",
                ),
                PlanValidationIssue(
                    code="TWO",
                    message="Two.",
                ),
            ),
        )

        self.assertEqual(
            result.error_count,
            2,
        )

    def test_non_plan_is_rejected_by_result(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            PlanValidationResult(
                valid=True,
                plan="not a plan",
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )