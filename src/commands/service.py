from src.commands.confirmation import (
    ConfirmationService,
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


class CommandService:
    """
    Orchestrates command parsing, routing,
    confirmation state, and handler execution.

    The service itself contains no command-specific behavior.
    """

    def __init__(
        self,
        registry: CommandRegistry,
        parser: CommandParser | None = None,
        confirmation_service: (
            ConfirmationService | None
        ) = None,
    ):

        if not isinstance(
            registry,
            CommandRegistry,
        ):
            raise TypeError(
                "registry must be a CommandRegistry."
            )

        self.registry = registry

        self.parser = (
            parser
            if parser is not None
            else CommandParser()
        )

        self.confirmation_service = (
            confirmation_service
            if confirmation_service is not None
            else ConfirmationService()
        )

    def execute_text(
        self,
        text: str,
    ) -> CommandResult | None:

        request = self.parser.parse(
            text
        )

        if request is None:
            return None

        return self.execute(
            request
        )

    def execute(
        self,
        request: CommandRequest,
    ) -> CommandResult:

        if not isinstance(
            request,
            CommandRequest,
        ):
            raise TypeError(
                "request must be a CommandRequest."
            )

        handler = self.registry.get(
            request.name
        )

        if handler is None:
            return CommandResult(
                success=False,
                command=request.name,
                message=(
                    f"Unknown command: "
                    f"/{request.name}"
                ),
            )

        result = handler.execute(
            request
        )

        if not isinstance(
            result,
            CommandResult,
        ):
            raise TypeError(
                "Command handler must return "
                "a CommandResult."
            )

        # ---------------------------------------------------------
        # Confirmation staging
        # ---------------------------------------------------------

        if (
            result.success
            and result.requires_confirmation
        ):

            operation = (
                self.confirmation_service.create_pending(
                    command=request.name,
                    arguments=request.arguments,
                    description=result.message,
                    metadata=result.metadata,
                )
            )

            return CommandResult(
                success=True,
                command=result.command,
                message=(
                    f"{result.message}\n\n"
                    "Confirmation required.\n"
                    f"Operation ID: "
                    f"{operation.operation_id}\n"
                    "Use /CONFIRM to approve "
                    "or /CANCEL to reject."
                ),
                requires_confirmation=True,
                metadata={
                    **result.metadata,
                    "operation_id": (
                        operation.operation_id
                    ),
                    "operation_status": (
                        operation.status
                    ),
                },
            )

        return result