import shlex

from src.commands.models import (
    CommandRequest,
)


class CommandParser:
    """
    Parse explicit slash commands.

    V1 syntax:

        /COMMAND
        /COMMAND argument
        /COMMAND argument1 argument2

    Quoted arguments are supported through shlex.
    """

    COMMAND_PREFIX = "/"

    def parse(
        self,
        text: str,
    ) -> CommandRequest | None:
        """
        Parse a command.

        Returns:
            CommandRequest for command input.
            None for ordinary conversational input.

        Raises:
            TypeError:
                Input is not a string.

            ValueError:
                Input begins with '/' but contains
                no valid command name.
        """

        if not isinstance(
            text,
            str,
        ):
            raise TypeError(
                "Command input must be a string."
            )

        text = text.strip()

        if not text.startswith(
            self.COMMAND_PREFIX
        ):
            return None

        if text == self.COMMAND_PREFIX:
            raise ValueError(
                "Command name is missing."
            )

        try:
            parts = shlex.split(
                text
            )
        except ValueError as exc:
            raise ValueError(
                f"Invalid command syntax: {exc}"
            ) from exc

        if not parts:
            return None

        command = (
            parts[0][
                len(self.COMMAND_PREFIX):
            ]
            .strip()
            .upper()
        )

        if not command:
            raise ValueError(
                "Command name is missing."
            )

        return CommandRequest(
            name=command,
            arguments=tuple(
                parts[1:]
            ),
            raw_text=text,
        )