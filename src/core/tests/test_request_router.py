import unittest

from src.commands.parser import (
    CommandParser,
)

from src.core.request_router import (
    RequestRouter,
)

from src.core.task_models import (
    RequestType,
    TaskRequest,
    TaskType,
)


class RequestRouterTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):
        self.router = RequestRouter()

    def test_normal_text_routes_to_conversation(
        self,
    ):
        result = self.router.route(
            "What do you know about PCVUE?"
        )

        self.assertEqual(
            result.request_type,
            RequestType.CONVERSATION,
        )

        self.assertEqual(
            result.original_input,
            "What do you know about PCVUE?",
        )

        self.assertIsNone(
            result.command_name
        )

    def test_explicit_command_routes_to_command(
        self,
    ):
        result = self.router.route(
            "/SHOW-MEMORY pcvue_skill"
        )

        self.assertEqual(
            result.request_type,
            RequestType.COMMAND,
        )

        self.assertEqual(
            result.command_name,
            "SHOW-MEMORY",
        )

    def test_command_name_is_normalized(
        self,
    ):
        result = self.router.route(
            "/remember something"
        )

        self.assertEqual(
            result.request_type,
            RequestType.COMMAND,
        )

        self.assertEqual(
            result.command_name,
            "REMEMBER",
        )

    def test_command_arguments_are_preserved(
        self,
    ):
        result = self.router.route(
            "/DELETE pcvue_skill"
        )

        self.assertEqual(
            result.metadata[
                "command_arguments"
            ],
            (
                "pcvue_skill",
            ),
        )

    def test_whitespace_is_preserved_as_original_input(
        self,
    ):
        text = (
            "   /HELP   "
        )

        result = self.router.route(
            text
        )

        self.assertEqual(
            result.original_input,
            text,
        )

    def test_empty_input_is_rejected(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            self.router.route(
                "   "
            )

    def test_non_string_input_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            self.router.route(
                123
            )

    def test_explicit_task_can_be_routed(
        self,
    ):
        task = TaskRequest(
            content=(
                "Inspect the project repository."
            ),
            task_type=TaskType.TOOL,
        )

        result = self.router.route_task(
            task
        )

        self.assertEqual(
            result.request_type,
            RequestType.TASK,
        )

        self.assertEqual(
            result.task,
            task,
        )

    def test_empty_task_is_rejected(
        self,
    ):
        task = TaskRequest(
            content="   ",
            task_type=TaskType.TOOL,
        )

        with self.assertRaises(
            ValueError
        ):
            self.router.route_task(
                task
            )

    def test_invalid_task_type_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            self.router.route_task(
                "not a task"
            )

    def test_custom_parser_can_be_supplied(
        self,
    ):
        parser = CommandParser()

        router = RequestRouter(
            command_parser=parser
        )

        self.assertIs(
            router.command_parser,
            parser,
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )