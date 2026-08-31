import unittest

from src.core.execution_confirmation import (
    ExecutionConfirmationService,
    execution_plan_fingerprint,
)

from src.core.execution_confirmation_models import (
    ExecutionConfirmationStatus,
)

from src.core.execution_planner import ExecutionPlanner
from src.core.task_models import TaskRequest


class ExecutionConfirmationServiceTests(
    unittest.TestCase
):
    def setUp(self):
        self.planner = ExecutionPlanner()

        self.plan = self.planner.plan(
            TaskRequest(
                description="Perform a test action.",
                task_type="ACTION",
            )
        )

        self.service = (
            ExecutionConfirmationService()
        )

    def test_operation_can_be_staged(self):
        operation = self.service.stage(
            self.plan
        )

        self.assertIsNotNone(
            operation.operation_id
        )

        self.assertIs(
            operation.plan,
            self.plan,
        )

        self.assertEqual(
            operation.status,
            ExecutionConfirmationStatus.PENDING,
        )

    def test_staged_operation_is_retrievable(self):
        operation = self.service.stage(
            self.plan
        )

        retrieved = self.service.get(
            operation.operation_id
        )

        self.assertIs(
            retrieved,
            operation,
        )

    def test_missing_operation_returns_none(self):
        result = self.service.get(
            "does-not-exist"
        )

        self.assertIsNone(result)

    def test_first_pending_operation_is_available(self):
        first = self.service.stage(
            self.plan
        )

        second_plan = self.planner.plan(
            TaskRequest(
                description="Perform another test action.",
                task_type="ACTION",
            )
        )

        self.service.stage(
            second_plan
        )

        pending = (
            self.service.get_pending()
        )

        self.assertIsNotNone(
            pending
        )

        self.assertEqual(
            pending.operation_id,
            first.operation_id,
        )

    def test_operation_contains_plan_fingerprint(self):
        operation = self.service.stage(
            self.plan
        )

        self.assertIn(
            "plan_fingerprint",
            operation.metadata,
        )

        self.assertEqual(
            operation.metadata[
                "plan_fingerprint"
            ],
            execution_plan_fingerprint(
                self.plan
            ),
        )

    def test_plan_fingerprint_is_deterministic(self):
        first = execution_plan_fingerprint(
            self.plan
        )

        second = execution_plan_fingerprint(
            self.plan
        )

        self.assertEqual(
            first,
            second,
        )

    def test_confirmation_changes_status(self):
        operation = self.service.stage(
            self.plan
        )

        confirmed = (
            self.service.confirm(
                operation.operation_id
            )
        )

        self.assertIsNotNone(
            confirmed
        )

        self.assertEqual(
            confirmed.status,
            ExecutionConfirmationStatus.CONFIRMED,
        )

        self.assertFalse(
            confirmed.is_pending
        )

    def test_confirmation_preserves_exact_plan(self):
        operation = self.service.stage(
            self.plan
        )

        confirmed = (
            self.service.confirm(
                operation.operation_id
            )
        )

        self.assertIs(
            confirmed.plan,
            self.plan,
        )

    def test_confirmed_operation_is_no_longer_pending(self):
        operation = self.service.stage(
            self.plan
        )

        self.service.confirm(
            operation.operation_id
        )

        self.assertIsNone(
            self.service.get_pending()
        )

    def test_confirmed_operation_cannot_be_confirmed_again(
        self,
    ):
        operation = self.service.stage(
            self.plan
        )

        confirmed = (
            self.service.confirm(
                operation.operation_id
            )
        )

        self.assertIsNotNone(
            confirmed
        )

        second = (
            self.service.confirm(
                operation.operation_id
            )
        )

        self.assertIsNone(
            second
        )

    def test_cancellation_changes_status(self):
        operation = self.service.stage(
            self.plan
        )

        cancelled = (
            self.service.cancel(
                operation.operation_id
            )
        )

        self.assertIsNotNone(
            cancelled
        )

        self.assertEqual(
            cancelled.status,
            ExecutionConfirmationStatus.CANCELLED,
        )

        self.assertFalse(
            cancelled.is_pending
        )

    def test_cancelled_operation_cannot_be_confirmed(
        self,
    ):
        operation = self.service.stage(
            self.plan
        )

        cancelled = (
            self.service.cancel(
                operation.operation_id
            )
        )

        self.assertIsNotNone(
            cancelled
        )

        confirmed = (
            self.service.confirm(
                operation.operation_id
            )
        )

        self.assertIsNone(
            confirmed
        )

    def test_cancelled_operation_is_not_pending(self):
        operation = self.service.stage(
            self.plan
        )

        self.service.cancel(
            operation.operation_id
        )

        self.assertIsNone(
            self.service.get_pending()
        )

    def test_unknown_operation_cannot_be_confirmed(
        self,
    ):
        result = self.service.confirm(
            "unknown-operation"
        )

        self.assertIsNone(result)

    def test_unknown_operation_cannot_be_cancelled(
        self,
    ):
        result = self.service.cancel(
            "unknown-operation"
        )

        self.assertIsNone(result)

    def test_confirmation_service_does_not_execute_plan(
        self,
    ):
        """
        Confirmation service only changes operation state.

        It has no execution responsibility.
        """

        operation = self.service.stage(
            self.plan
        )

        confirmed = (
            self.service.confirm(
                operation.operation_id
            )
        )

        self.assertEqual(
            confirmed.status,
            ExecutionConfirmationStatus.CONFIRMED,
        )

        self.assertIs(
            confirmed.plan,
            operation.plan,
        )

    def test_cancel_does_not_change_plan(self):
        operation = self.service.stage(
            self.plan
        )

        cancelled = (
            self.service.cancel(
                operation.operation_id
            )
        )

        self.assertIs(
            cancelled.plan,
            self.plan,
        )

    def test_clear_removes_all_operations(self):
        self.service.stage(
            self.plan
        )

        self.service.clear()

        self.assertIsNone(
            self.service.get_pending()
        )

    def test_non_string_operation_id_is_rejected(
        self,
    ):
        with self.assertRaises(TypeError):
            self.service.get(123)


if __name__ == "__main__":
    unittest.main()