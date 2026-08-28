import unittest

from src.core.task_models import (
    RequestType,
    RouteDecision,
    TaskRequest,
    TaskType,
)


class TaskModelTests(
    unittest.TestCase
):

    def test_task_request_can_be_created(
        self,
    ):
        task = TaskRequest(
            content="Inspect my project.",
            task_type=TaskType.TOOL,
        )

        self.assertEqual(
            task.content,
            "Inspect my project.",
        )

        self.assertEqual(
            task.task_type,
            TaskType.TOOL,
        )

    def test_task_request_defaults_to_unknown(
        self,
    ):
        task = TaskRequest(
            content="Do something."
        )

        self.assertEqual(
            task.task_type,
            TaskType.UNKNOWN,
        )

    def test_route_decision_can_represent_conversation(
        self,
    ):
        decision = RouteDecision(
            request_type=RequestType.CONVERSATION,
            original_input="Hello.",
            reason="Normal conversation.",
        )

        self.assertEqual(
            decision.request_type,
            RequestType.CONVERSATION,
        )

        self.assertIsNone(
            decision.command_name
        )

    def test_route_decision_can_represent_command(
        self,
    ):
        decision = RouteDecision(
            request_type=RequestType.COMMAND,
            original_input="/HELP",
            command_name="HELP",
        )

        self.assertEqual(
            decision.request_type,
            RequestType.COMMAND,
        )

        self.assertEqual(
            decision.command_name,
            "HELP",
        )

    def test_route_decision_can_represent_task(
        self,
    ):
        task = TaskRequest(
            content="Inspect the repository.",
            task_type=TaskType.TOOL,
        )

        decision = RouteDecision(
            request_type=RequestType.TASK,
            original_input=task.content,
            task=task,
        )

        self.assertEqual(
            decision.request_type,
            RequestType.TASK,
        )

        self.assertEqual(
            decision.task,
            task,
        )

    def test_metadata_defaults_to_empty(
        self,
    ):
        task = TaskRequest(
            content="Test."
        )

        decision = RouteDecision(
            request_type=RequestType.CONVERSATION,
            original_input="Test.",
        )

        self.assertEqual(
            task.metadata,
            {},
        )

        self.assertEqual(
            decision.metadata,
            {},
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )