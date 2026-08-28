from abc import ABC, abstractmethod

from src.commands.models import (
    CommandRequest,
    CommandResult,
)


class CommandHandler(
    ABC
):
    """
    Contract implemented by every command handler.

    A handler owns the behavior of one command.

    It does not determine whether the input is a command.
    That is the parser's job.

    It does not perform command routing.
    That is the registry/service's job.
    """

    @abstractmethod
    def command_name(
        self,
    ) -> str:
        """
        Return the stable command name.

        Example:

            "REMEMBER"
        """
        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        request: CommandRequest,
    ) -> CommandResult:
        """
        Execute a validated command request.
        """
        raise NotImplementedError