import unittest

from src.commands.handler import (
    CommandHandler,
)

from src.commands.models import (
    CommandRequest,
    CommandResult,
)

from src.commands.registry import (
    CommandRegistry,
)


class FakeHandler(
    CommandHandler
):

    def __init__(
        self,
        name="TEST",
    ):
        self.name = name

    def command_name(
        self,
    ) -> str:
        return self.name

    def execute(
        self,
        request: CommandRequest,
    ) -> CommandResult:

        return CommandResult(
            success=True,
            command=request.name,
            message="Executed.",
        )


class CommandRegistryTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):
        self.registry = CommandRegistry()

    def test_handler_can_be_registered(
        self,
    ):
        handler = FakeHandler()

        self.registry.register(
            handler
        )

        self.assertEqual(
            self.registry.get("TEST"),
            handler,
        )

    def test_command_names_are_case_insensitive(
        self,
    ):
        handler = FakeHandler(
            "test"
        )

        self.registry.register(
            handler
        )

        self.assertEqual(
            self.registry.get("TEST"),
            handler,
        )

        self.assertEqual(
            self.registry.get("test"),
            handler,
        )

    def test_names_are_normalized(
        self,
    ):
        handler = FakeHandler(
            "  test  "
        )

        self.registry.register(
            handler
        )

        self.assertEqual(
            self.registry.names(),
            ("TEST",),
        )

    def test_names_are_sorted(
        self,
    ):
        self.registry.register(
            FakeHandler("ZED")
        )

        self.registry.register(
            FakeHandler("ALPHA")
        )

        self.registry.register(
            FakeHandler("MIDDLE")
        )

        self.assertEqual(
            self.registry.names(),
            (
                "ALPHA",
                "MIDDLE",
                "ZED",
            ),
        )

    def test_missing_handler_returns_none(
        self,
    ):
        self.assertIsNone(
            self.registry.get(
                "MISSING"
            )
        )

    def test_invalid_handler_type_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            self.registry.register(
                object()
            )

    def test_non_string_name_is_rejected(
        self,
    ):
        handler = FakeHandler()

        handler.command_name = (
            lambda: 123
        )

        with self.assertRaises(
            TypeError
        ):
            self.registry.register(
                handler
            )

    def test_empty_name_is_rejected(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            self.registry.register(
                FakeHandler(" ")
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )