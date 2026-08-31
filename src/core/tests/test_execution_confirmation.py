import unittest

from src.core.execution_confirmation import (
    ExecutionConfirmationService,
    execution_plan_fingerprint,
)
from src.core.execution_confirmation_models import (
    ExecutionConfirmationStatus,
)
from src.core.execution_plan_models import (
    ExecutionPlan,
    PlanStatus,
    PlanStep,
    StepStatus,
    StepType,
)


class ExecutionConfirmationServiceTests(unittest.TestCase):

    def setUp(self):
        self.service = (
            ExecutionConfirmationService()
        )

    def _plan(
        self,
        plan_id="plan-1",
        action="PERFORM_ACTION",
    ):
        return ExecutionPlan(
            plan_id=plan_id,
            task_description="Execute a test action.",
            steps=(
                PlanStep(
                    step_id="step-1",
                    description="Execute test action.",
                    action=action,
                    step_type=StepType.ACTION,
                    order=0,
                    depends_on=(),
                    status=StepStatus.READY,
                    requires_confirmation=True,
                    metadata={},
                ),
            ),
            status=PlanStatus.READY,
            metadata={},
        )

    def test_operation_can_be_staged(self):
        plan = self._plan()

        operation = self.service.stage(
            plan
        )

        self.assertIsNotNone(
            operation
        )

        self.assertTrue(
            operation.is_pending
        )

    def test_staged_plan_is_preserved_exactly(self):
        plan = self._plan()

        operation = self.service.stage(
            plan
        )

        self.assertIs(
            operation.plan,
            plan,
        )

    def test_staged_operation_has_fingerprint(self):
        plan = self._plan()

        operation = self.service.stage(
            plan
        )

        self.assertEqual(
            operation.metadata[
                "plan_fingerprint"
            ],
            execution_plan_fingerprint(
                plan
            ),
        )

    def test_staged_operation_has_unique_id(self):
        plan = self._plan()

        first = self.service.stage(
            plan
        )

        second = self.service.stage(
            plan
        )

        self.assertNotEqual(
            first.operation_id,
            second.operation_id,
        )

    def test_operation_can_be_retrieved(self):
        plan = self._plan()

        operation = self.service.stage(
            plan
        )

        retrieved = self.service.get(
            operation.operation_id
        )

        self.assertIs(
            retrieved,
            operation,
        )

    def test_unknown_operation_returns_none(self):
        result = self.service.get(
            "does-not-exist"
        )

        self.assertIsNone(
            result
        )

    def test_non_string_operation_id_is_rejected(self):
        with self.assertRaises(TypeError):
            self.service.get(123)

    def test_pending_operation_can_be_retrieved(self):
        plan = self._plan()

        operation = self.service.stage(
            plan
        )

        pending = self.service.get_pending()

        self.assertIs(
            pending,
            operation,
        )

    def test_no_pending_operation_returns_none(self):
        self.assertIsNone(
            self.service.get_pending()
        )

    def test_confirm_changes_status(self):
        plan = self._plan()

        operation = self.service.stage(
            plan
        )

        confirmed = self.service.confirm(
            operation.operation_id
        )

        self.assertEqual(
            confirmed.status,
            ExecutionConfirmationStatus.CONFIRMED,
        )

        self.assertFalse(
            confirmed.is_pending
        )

    def test_confirm_preserves_exact_plan(self):
        plan = self._plan()

        operation = self.service.stage(
            plan
        )

        confirmed = self.service.confirm(
            operation.operation_id
        )

        self.assertIs(
            confirmed.plan,
            plan,
        )

    def test_confirm_does_not_execute_plan(self):
        plan = self._plan()

        operation = self.service.stage(
            plan
        )

        confirmed = self.service.confirm(
            operation.operation_id
        )

        self.assertIsNotNone(
            confirmed
        )

        # The confirmation service has no executor.
        # Its responsibility ends at authorization state.
        self.assertEqual(
            confirmed.status,
            ExecutionConfirmationStatus.CONFIRMED,
        )

    def test_confirmed_operation_cannot_be_confirmed_again(self):
        plan = self._plan()

        operation = self.service.stage(
            plan
        )

        self.service.confirm(
            operation.operation_id
        )

        second = self.service.confirm(
            operation.operation_id
        )

        self.assertIsNone(
            second
        )

    def test_cancel_changes_status(self):
        plan = self._plan()

        operation = self.service.stage(
            plan
        )

        cancelled = self.service.cancel(
            operation.operation_id
        )

        self.assertEqual(
            cancelled.status,
            ExecutionConfirmationStatus.CANCELLED,
        )

        self.assertFalse(
            cancelled.is_pending
        )

    def test_cancel_preserves_exact_plan(self):
        plan = self._plan()

        operation = self.service.stage(
            plan
        )

        cancelled = self.service.cancel(
            operation.operation_id
        )

        self.assertIs(
            cancelled.plan,
            plan,
        )

    def test_cancelled_operation_cannot_be_confirmed(self):
        plan = self._plan()

        operation = self.service.stage(
            plan
        )

        self.service.cancel(
            operation.operation_id
        )

        confirmed = self.service.confirm(
            operation.operation_id
        )

        self.assertIsNone(
            confirmed
        )

    def test_confirm_unknown_operation_returns_none(self):
        result = self.service.confirm(
            "does-not-exist"
        )

        self.assertIsNone(
            result
        )

    def test_cancel_unknown_operation_returns_none(self):
        result = self.service.cancel(
            "does-not-exist"
        )

        self.assertIsNone(
            result
        )

    def test_default_confirmation_uses_pending_operation(self):
        plan = self._plan()

        operation = self.service.stage(
            plan
        )

        confirmed = self.service.confirm()

        self.assertEqual(
            confirmed.operation_id,
            operation.operation_id,
        )

        self.assertEqual(
            confirmed.status,
            ExecutionConfirmationStatus.CONFIRMED,
        )

    def test_default_cancellation_uses_pending_operation(self):
        plan = self._plan()

        operation = self.service.stage(
            plan
        )

        cancelled = self.service.cancel()

        self.assertEqual(
            cancelled.operation_id,
            operation.operation_id,
        )

        self.assertEqual(
            cancelled.status,
            ExecutionConfirmationStatus.CANCELLED,
        )

    def test_multiple_pending_operations_return_first_pending(self):
        first = self.service.stage(
            self._plan(plan_id="plan-1")
        )

        second = self.service.stage(
            self._plan(plan_id="plan-2")
        )

        pending = self.service.get_pending()

        self.assertEqual(
            pending.operation_id,
            first.operation_id,
        )

        self.assertNotEqual(
            pending.operation_id,
            second.operation_id,
        )

    def test_confirm_first_pending_leaves_second_pending(self):
        first = self.service.stage(
            self._plan(plan_id="plan-1")
        )

        second = self.service.stage(
            self._plan(plan_id="plan-2")
        )

        self.service.confirm()

        pending = self.service.get_pending()

        self.assertEqual(
            pending.operation_id,
            second.operation_id,
        )

        self.assertNotEqual(
            pending.operation_id,
            first.operation_id,
        )

    def test_cancel_first_pending_leaves_second_pending(self):
        first = self.service.stage(
            self._plan(plan_id="plan-1")
        )

        second = self.service.stage(
            self._plan(plan_id="plan-2")
        )

        self.service.cancel()

        pending = self.service.get_pending()

        self.assertEqual(
            pending.operation_id,
            second.operation_id,
        )

        self.assertNotEqual(
            pending.operation_id,
            first.operation_id,
        )

    def test_clear_removes_operations(self):
        self.service.stage(
            self._plan()
        )

        self.assertIsNotNone(
            self.service.get_pending()
        )

        self.service.clear()

        self.assertIsNone(
            self.service.get_pending()
        )

    def test_metadata_is_preserved(self):
        plan = self._plan()

        operation = self.service.stage(
            plan,
            metadata={
                "source": "jarvis",
                "reason": "user confirmation",
            },
        )

        self.assertEqual(
            operation.metadata["source"],
            "jarvis",
        )

        self.assertEqual(
            operation.metadata["reason"],
            "user confirmation",
        )

    def test_fingerprint_is_deterministic(self):
        plan = self._plan()

        first = execution_plan_fingerprint(
            plan
        )

        second = execution_plan_fingerprint(
            plan
        )

        self.assertEqual(
            first,
            second,
        )

    def test_different_plans_have_different_fingerprints(
        self,
    ):
        first = execution_plan_fingerprint(
            self._plan(
                plan_id="plan-1"
            )
        )

        second = execution_plan_fingerprint(
            self._plan(
                plan_id="plan-2"
            )
        )

        self.assertNotEqual(
            first,
            second,
        )

