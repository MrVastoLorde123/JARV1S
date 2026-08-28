import unittest

from src.commands.handler import (
    CommandHandler,
)

from src.commands.models import (
    CommandRequest,
    CommandResult,
)

from src.commands.parser import (
    CommandParser,
)

from src.commands.registry import (
    CommandRegistry,
)

from src.commands.service import (
    CommandService,
)


class FakeHandler(
    CommandHandler
):

    def __init__(
        self,
        name="TEST",
    ):
        self.name = name
        self.received_request = None

    def command_name(
        self,
    ) -> str:
        return self.name

    def execute(
        self,
        request: CommandRequest,
    ) -> CommandResult:

        self.received_request = request

        return CommandResult(
            success=True,
            command=request.name,
            message="Fake command executed.",
        )


class CommandServiceTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):
        self.registry = CommandRegistry()

        self.handler = FakeHandler()

        self.registry.register(
            self.handler
        )

        self.service = CommandService(
            registry=self.registry
        )

    def test_normal_text_returns_none(
        self,
    ):
        result = self.service.execute_text(
            "What do you know about PCVUE?"
        )

        self.assertIsNone(
            result
        )

    def test_command_is_executed(
        self,
    ):
        result = self.service.execute_text(
            "/TEST hello"
        )

        self.assertIsNotNone(
            result
        )

        self.assertTrue(
            result.success
        )

        self.assertEqual(
            result.command,
            "TEST",
        )

    def test_handler_receives_parsed_request(
        self,
    ):
        self.service.execute_text(
            "/TEST one two"
        )

        self.assertIsNotNone(
            self.handler.received_request
        )

        self.assertEqual(
            self.handler.received_request.name,
            "TEST",
        )

        self.assertEqual(
            self.handler.received_request.arguments,
            (
                "one",
                "two",
            ),
        )

    def test_unknown_command_fails_safely(
        self,
    ):
        result = self.service.execute_text(
            "/UNKNOWN"
        )

        self.assertFalse(
            result.success
        )

        self.assertEqual(
            result.command,
            "UNKNOWN",
        )

    def test_direct_request_execution_works(
        self,
    ):
        request = CommandRequest(
            name="TEST",
            arguments=("hello",),
        )

        result = self.service.execute(
            request
        )

        self.assertTrue(
            result.success
        )

    def test_invalid_request_type_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            self.service.execute(
                "not a request"
            )

    def test_invalid_registry_type_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            CommandService(
                registry=object()
            )

    def test_custom_parser_can_be_supplied(
        self,
    ):
        parser = CommandParser()

        service = CommandService(
            registry=self.registry,
            parser=parser,
        )

        result = service.execute_text(
            "/TEST"
        )

        self.assertTrue(
            result.success
        )

        self.assertIs(
            service.parser,
            parser
        )

    def test_confirmation_required_result_is_staged(
            self,
    ):
        class DangerousHandler(
            CommandHandler
        ):

            def command_name(
                    self,
            ) -> str:
                return "DANGEROUS"

            def execute(
                    self,
                    request,
            ):
                return CommandResult(
                    success=True,
                    command=request.name,
                    message="This would change system state.",
                    requires_confirmation=True,
                    metadata={
                        "risk": "HIGH",
                    },
                )

        self.registry.register(
            DangerousHandler()
        )

        result = self.service.execute_text(
            "/DANGEROUS"
        )

        self.assertTrue(
            result.success
        )

        self.assertTrue(
            result.requires_confirmation
        )

        self.assertIn(
            "Confirmation required",
            result.message,
        )

        self.assertIn(
            "operation_id",
            result.metadata,
        )

        pending = (
            self.service.confirmation_service
            .get_pending()
        )

        self.assertIsNotNone(
            pending
        )

        self.assertEqual(
            pending.command,
            "DANGEROUS",
        )



if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )