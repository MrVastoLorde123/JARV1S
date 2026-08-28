import unittest

from src.commands.confirmation import (
    ConfirmationService,
)

from src.commands.confirmation_models import (
    CANCELLED,
    CONFIRMED,
    PENDING,
)


class ConfirmationServiceTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):
        self.service = (
            ConfirmationService()
        )

    def test_operation_can_be_created(
        self,
    ):
        operation = (
            self.service.create_pending(
                command="DELETE",
                arguments=("pcvue_skill",),
                description="Delete PCVUE memory.",
            )
        )

        self.assertEqual(
            operation.status,
            PENDING,
        )

        self.assertEqual(
            operation.command,
            "DELETE",
        )

    def test_operation_can_be_retrieved(
        self,
    ):
        operation = (
            self.service.create_pending(
                command="DELETE",
                arguments=("pcvue_skill",),
                description="Delete.",
            )
        )

        pending = (
            self.service.get_pending()
        )

        self.assertEqual(
            pending,
            operation,
        )

    def test_confirmation_changes_status(
        self,
    ):
        operation = (
            self.service.create_pending(
                command="DELETE",
                arguments=("pcvue_skill",),
                description="Delete.",
            )
        )

        confirmed = (
            self.service.confirm(
                operation.operation_id
            )
        )

        self.assertEqual(
            confirmed.status,
            CONFIRMED,
        )

    def test_default_confirmation_uses_pending_operation(
        self,
    ):
        operation = (
            self.service.create_pending(
                command="DELETE",
                arguments=("pcvue_skill",),
                description="Delete.",
            )
        )

        confirmed = (
            self.service.confirm()
        )

        self.assertEqual(
            confirmed.operation_id,
            operation.operation_id,
        )

    def test_missing_operation_cannot_be_confirmed(
        self,
    ):
        result = (
            self.service.confirm(
                "missing"
            )
        )

        self.assertIsNone(
            result
        )

    def test_confirmation_cannot_be_repeated(
        self,
    ):
        operation = (
            self.service.create_pending(
                command="DELETE",
                arguments=("pcvue_skill",),
                description="Delete.",
            )
        )

        first = self.service.confirm(
            operation.operation_id
        )

        second = self.service.confirm(
            operation.operation_id
        )

        self.assertEqual(
            first.status,
            CONFIRMED,
        )

        self.assertIsNone(
            second
        )

    def test_operation_can_be_cancelled(
        self,
    ):
        operation = (
            self.service.create_pending(
                command="DELETE",
                arguments=("pcvue_skill",),
                description="Delete.",
            )
        )

        cancelled = (
            self.service.cancel(
                operation.operation_id
            )
        )

        self.assertEqual(
            cancelled.status,
            CANCELLED,
        )

    def test_cancelled_operation_cannot_be_confirmed(
        self,
    ):
        operation = (
            self.service.create_pending(
                command="DELETE",
                arguments=("pcvue_skill",),
                description="Delete.",
            )
        )

        self.service.cancel(
            operation.operation_id
        )

        result = self.service.confirm(
            operation.operation_id
        )

        self.assertIsNone(
            result
        )

    def test_multiple_pending_operations_return_first_pending(
        self,
    ):
        first = (
            self.service.create_pending(
                command="DELETE",
                arguments=("one",),
                description="Delete one.",
            )
        )

        self.service.create_pending(
            command="DELETE",
            arguments=("two",),
            description="Delete two.",
        )

        pending = (
            self.service.get_pending()
        )

        self.assertEqual(
            pending.operation_id,
            first.operation_id,
        )

    def test_clear_removes_all_operations(
        self,
    ):
        self.service.create_pending(
            command="DELETE",
            arguments=("one",),
            description="Delete one.",
        )

        self.service.clear()

        self.assertIsNone(
            self.service.get_pending()
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )