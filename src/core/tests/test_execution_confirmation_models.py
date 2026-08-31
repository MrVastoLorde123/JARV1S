import unittest

from src.core.execution_confirmation_models import (
    ExecutionConfirmationStatus,
    ExecutionPendingOperation,
)

from src.core.execution_planner import ExecutionPlanner
from src.core.task_models import TaskRequest, TaskType


class ExecutionConfirmationModelTests(
    unittest.TestCase
):
    def setUp(self):
        self.planner = ExecutionPlanner()

        self.plan = self.planner.plan(
            TaskRequest(
                content="Perform a test action.",
                task_type=TaskType.ACTION,
            )
        )

    def test_pending_operation_can_be_created(self):
        operation = ExecutionPendingOperation(
            operation_id="operation-1",
            plan=self.plan,
            created_at="2026-01-01T00:00:00+00:00",
        )

        self.assertEqual(
            operation.operation_id,
            "operation-1",
        )

        self.assertIs(
            operation.plan,
            self.plan,
        )

        self.assertEqual(
            operation.status,
            ExecutionConfirmationStatus.PENDING,
        )

    def test_default_status_is_pending(self):
        operation = ExecutionPendingOperation(
            operation_id="operation-1",
            plan=self.plan,
            created_at="2026-01-01T00:00:00+00:00",
        )

        self.assertEqual(
            operation.status,
            ExecutionConfirmationStatus.PENDING,
        )

        self.assertTrue(
            operation.is_pending
        )

    def test_operation_requires_string_id(self):
        with self.assertRaises(TypeError):
            ExecutionPendingOperation(
                operation_id=123,
                plan=self.plan,
                created_at="2026-01-01T00:00:00+00:00",
            )

    def test_operation_rejects_empty_id(self):
        with self.assertRaises(ValueError):
            ExecutionPendingOperation(
                operation_id="   ",
                plan=self.plan,
                created_at="2026-01-01T00:00:00+00:00",
            )

    def test_operation_requires_execution_plan(self):
        with self.assertRaises(TypeError):
            ExecutionPendingOperation(
                operation_id="operation-1",
                plan="not a plan",
                created_at="2026-01-01T00:00:00+00:00",
            )

    def test_operation_requires_string_created_at(self):
        with self.assertRaises(TypeError):
            ExecutionPendingOperation(
                operation_id="operation-1",
                plan=self.plan,
                created_at=123,
            )

    def test_confirmed_status_is_not_pending(self):
        operation = ExecutionPendingOperation(
            operation_id="operation-1",
            plan=self.plan,
            created_at="2026-01-01T00:00:00+00:00",
            status=(
                ExecutionConfirmationStatus.CONFIRMED
            ),
        )

        self.assertFalse(
            operation.is_pending
        )

    def test_cancelled_status_is_not_pending(self):
        operation = ExecutionPendingOperation(
            operation_id="operation-1",
            plan=self.plan,
            created_at="2026-01-01T00:00:00+00:00",
            status=(
                ExecutionConfirmationStatus.CANCELLED
            ),
        )

        self.assertFalse(
            operation.is_pending
        )

    def test_metadata_defaults_to_empty(self):
        operation = ExecutionPendingOperation(
            operation_id="operation-1",
            plan=self.plan,
            created_at="2026-01-01T00:00:00+00:00",
        )

        self.assertEqual(
            operation.metadata,
            {},
        )

    def test_metadata_is_preserved(self):
        operation = ExecutionPendingOperation(
            operation_id="operation-1",
            plan=self.plan,
            created_at="2026-01-01T00:00:00+00:00",
            metadata={
                "source": "test",
            },
        )

        self.assertEqual(
            operation.metadata,
            {
                "source": "test",
            },
        )

    def test_operation_is_frozen(self):
        operation = ExecutionPendingOperation(
            operation_id="operation-1",
            plan=self.plan,
            created_at="2026-01-01T00:00:00+00:00",
        )

        with self.assertRaises(
            AttributeError
        ):
            operation.operation_id = "changed"


if __name__ == "__main__":
    unittest.main()