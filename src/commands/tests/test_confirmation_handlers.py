import unittest

from src.commands.confirmation import (
    ConfirmationService,
)

from src.commands.handlers.confirmation import (
    CancelCommandHandler,
    ConfirmCommandHandler,
)

from src.commands.models import (
    CommandRequest,
)


class ConfirmationHandlerTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):

        self.confirmation_service = (
            ConfirmationService()
        )

        self.confirm_handler = (
            ConfirmCommandHandler(
                self.confirmation_service
            )
        )

        self.cancel_handler = (
            CancelCommandHandler(
                self.confirmation_service
            )
        )

    def test_confirm_command_name(
        self,
    ):
        self.assertEqual(
            self.confirm_handler.command_name(),
            "CONFIRM",
        )

    def test_cancel_command_name(
        self,
    ):
        self.assertEqual(
            self.cancel_handler.command_name(),
            "CANCEL",
        )

    def test_confirm_without_pending_operation_fails(
        self,
    ):
        result = self.confirm_handler.execute(
            CommandRequest(
                name="CONFIRM"
            )
        )

        self.assertFalse(
            result.success
        )

    def test_confirm_confirms_pending_operation(
        self,
    ):
        operation = (
            self.confirmation_service.create_pending(
                command="DELETE",
                arguments=("pcvue_skill",),
                description="Delete memory.",
            )
        )

        result = self.confirm_handler.execute(
            CommandRequest(
                name="CONFIRM"
            )
        )

        self.assertTrue(
            result.success
        )

        self.assertEqual(
            result.metadata["operation_id"],
            operation.operation_id,
        )

        self.assertIn(
            "confirmed",
            result.message.lower(),
        )

    def test_cancel_cancels_pending_operation(
        self,
    ):
        operation = (
            self.confirmation_service.create_pending(
                command="DELETE",
                arguments=("pcvue_skill",),
                description="Delete memory.",
            )
        )

        result = self.cancel_handler.execute(
            CommandRequest(
                name="CANCEL"
            )
        )

        self.assertTrue(
            result.success
        )

        self.assertEqual(
            result.metadata["operation_id"],
            operation.operation_id,
        )

        self.assertIn(
            "cancelled",
            result.message.lower(),
        )

    def test_multiple_confirm_arguments_are_rejected(
        self,
    ):
        result = self.confirm_handler.execute(
            CommandRequest(
                name="CONFIRM",
                arguments=(
                    "one",
                    "two",
                ),
            )
        )

        self.assertFalse(
            result.success
        )

    def test_invalid_request_type_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            self.confirm_handler.execute(
                "not a request"
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )