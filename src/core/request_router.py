from src.commands.models import (
    CommandRequest,
)

from src.commands.parser import (
    CommandParser,
)

from src.core.task_models import (
    RequestType,
    RouteDecision,
    TaskRequest,
    TaskType,
)


class RequestRouter:
    """
    Deterministically classify incoming user input.

    V1 routing rules:

        starts with '/' -> COMMAND

        everything else -> CONVERSATION

    Task classification is available as a model concept,
    but AI-driven task detection is intentionally deferred.
    """

    def __init__(
        self,
        command_parser: CommandParser | None = None,
    ):
        self.command_parser = (
            command_parser
            if command_parser is not None
            else CommandParser()
        )

    def route(
        self,
        text: str,
    ) -> RouteDecision:

        if not isinstance(
            text,
            str,
        ):
            raise TypeError(
                "Request input must be a string."
            )

        original_input = text

        stripped = text.strip()

        if not stripped:
            raise ValueError(
                "Request input cannot be empty."
            )

        # ---------------------------------------------------------
        # COMMAND
        # ---------------------------------------------------------

        command = self.command_parser.parse(
            stripped
        )

        if command is not None:

            return RouteDecision(
                request_type=RequestType.COMMAND,
                original_input=original_input,
                command_name=command.name,
                reason="Input uses explicit command syntax.",
                metadata={
                    "command_arguments": (
                        command.arguments
                    ),
                },
            )

        # ---------------------------------------------------------
        # CONVERSATION
        # ---------------------------------------------------------

        return RouteDecision(
            request_type=RequestType.CONVERSATION,
            original_input=original_input,
            reason=(
                "Input does not use explicit command syntax."
            ),
        )

    def route_task(
        self,
        task: TaskRequest,
    ) -> RouteDecision:

        if not isinstance(
            task,
            TaskRequest,
        ):
            raise TypeError(
                "task must be a TaskRequest."
            )

        content = task.content.strip()

        if not content:
            raise ValueError(
                "Task content cannot be empty."
            )

        return RouteDecision(
            request_type=RequestType.TASK,
            original_input=content,
            task=task,
            reason="Request was explicitly supplied as a task.",
        )