import unittest

from src.commands.models import (
    CommandRequest,
    CommandResult,
)

class CommandModelTests(
    unittest.TestCase
):

    def test_command_request_can_be_created(
        self,
    ):
        request = CommandRequest(
            name="DELETE",
            arguments=("pcvue_skill",),
            raw_text="/DELETE pcvue_skill",
        )

        self.assertEqual(
            request.name,
            "DELETE",
        )

        self.assertEqual(
            request.arguments,
            ("pcvue_skill",),
        )

    def test_command_request_defaults(
        self,
    ):
        request = CommandRequest(
            name="HELP"
        )

        self.assertEqual(
            request.arguments,
            (),
        )

        self.assertEqual(
            request.raw_text,
            "",
        )

    def test_command_result_can_be_created(
        self,
    ):
        result = CommandResult(
            success=True,
            command="HELP",
            message="Available commands.",
        )

        self.assertTrue(
            result.success
        )

        self.assertEqual(
            result.command,
            "HELP",
        )

    def test_confirmation_defaults_to_false(
        self,
    ):
        result = CommandResult(
            success=True,
            command="SHOW-MEMORY",
            message="Done.",
        )

        self.assertFalse(
            result.requires_confirmation
        )

    def test_metadata_defaults_to_empty_dict(
        self,
    ):
        request = CommandRequest(
            name="TEST"
        )

        result = CommandResult(
            success=True,
            command="TEST",
            message="Done.",
        )

        self.assertEqual(
            request.metadata,
            {},
        )

        self.assertEqual(
            result.metadata,
            {},
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )