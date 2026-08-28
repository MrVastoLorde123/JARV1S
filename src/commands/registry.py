from src.commands.handler import (
    CommandHandler,
)


class CommandRegistry:
    """
    Registry of available command handlers.

    The registry does not execute handlers.
    It only maps command names to implementations.
    """

    def __init__(
        self,
    ):
        self._handlers = {}

    def register(
        self,
        handler: CommandHandler,
    ) -> None:
        """
        Register a command handler.
        """

        if not isinstance(
            handler,
            CommandHandler,
        ):
            raise TypeError(
                "Handler must implement "
                "CommandHandler."
            )

        name = handler.command_name()

        if not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "Command name must be a string."
            )

        name = name.strip().upper()

        if not name:
            raise ValueError(
                "Command name cannot be empty."
            )

        self._handlers[name] = handler

    def get(
        self,
        name: str,
    ) -> CommandHandler | None:
        """
        Return the handler registered for a command.
        """

        if not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "Command name must be a string."
            )

        return self._handlers.get(
            name.strip().upper()
        )

    def names(
        self,
    ) -> tuple[str, ...]:
        """
        Return all registered command names
        in deterministic order.
        """

        return tuple(
            sorted(
                self._handlers.keys()
            )
        )