import unittest

from src.commands.confirmation_models import (
    PENDING,
    PendingOperation,
)


class ConfirmationModelTests(
    unittest.TestCase
):

    def test_pending_operation_can_be_created(
        self,
    ):
        operation = PendingOperation(
            operation_id="abc",
            command="DELETE",
            arguments=("pcvue_skill",),
            description="Delete PCVUE memory.",
            created_at="2026-08-27T00:00:00+00:00",
        )

        self.assertEqual(
            operation.status,
            PENDING,
        )

        self.assertTrue(
            operation.is_pending()
        )

    def test_metadata_defaults_to_empty(
        self,
    ):
        operation = PendingOperation(
            operation_id="abc",
            command="DELETE",
            arguments=(),
            description="Delete.",
            created_at="2026-08-27T00:00:00+00:00",
        )

        self.assertEqual(
            operation.metadata,
            {},
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )