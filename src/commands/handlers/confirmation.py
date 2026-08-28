from src.commands.confirmation import (
    ConfirmationService,
)

from src.commands.confirmation_models import (
    CONFIRMED,
)

from src.commands.handler import (
    CommandHandler,
)

from src.commands.models import (
    CommandRequest,
    CommandResult,
)


class ConfirmCommandHandler(
    CommandHandler
):
    """
    Handles:

        /CONFIRM

    Confirmation only changes the state of a pending operation.

    It does not execute the underlying operation.
    """

    def __init__(
        self,
        confirmation_service: ConfirmationService,
    ):
        self.confirmation_service = (
            confirmation_service
        )

    def command_name(
        self,
    ) -> str:
        return "CONFIRM"

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

        if request.arguments:
            operation_id = (
                request.arguments[0]
            )

            if len(request.arguments) > 1:
                return CommandResult(
                    success=False,
                    command=request.name,
                    message=(
                        "Usage: /CONFIRM "
                        "[operation-id]"
                    ),
                )

        else:
            operation_id = None

        operation = (
            self.confirmation_service.confirm(
                operation_id
            )
        )

        if operation is None:
            return CommandResult(
                success=False,
                command=request.name,
                message=(
                    "There is no pending operation "
                    "to confirm."
                ),
            )

        return CommandResult(
            success=True,
            command=request.name,
            message=(
                "Operation confirmed.\n"
                f"Operation ID: "
                f"{operation.operation_id}\n"
                f"Command: /{operation.command}\n"
                f"Description: "
                f"{operation.description}"
            ),
            metadata={
                "operation_id": (
                    operation.operation_id
                ),
                "operation_command": (
                    operation.command
                ),
                "operation_status": CONFIRMED,
            },
        )


class CancelCommandHandler(
    CommandHandler
):
    """
    Handles:

        /CANCEL

    V1 cancellation is included because once confirmation
    exists, users need an explicit way to discard a pending
    operation.
    """

    def __init__(
        self,
        confirmation_service: ConfirmationService,
    ):
        self.confirmation_service = (
            confirmation_service
        )

    def command_name(
        self,
    ) -> str:
        return "CANCEL"

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

        if request.arguments:

            operation_id = (
                request.arguments[0]
            )

            if len(request.arguments) > 1:
                return CommandResult(
                    success=False,
                    command=request.name,
                    message=(
                        "Usage: /CANCEL "
                        "[operation-id]"
                    ),
                )

        else:
            operation_id = None

        operation = (
            self.confirmation_service.cancel(
                operation_id
            )
        )

        if operation is None:
            return CommandResult(
                success=False,
                command=request.name,
                message=(
                    "There is no pending operation "
                    "to cancel."
                ),
            )

        return CommandResult(
            success=True,
            command=request.name,
            message=(
                "Pending operation cancelled.\n"
                f"Operation ID: "
                f"{operation.operation_id}\n"
                f"Command: /{operation.command}"
            ),
            metadata={
                "operation_id": (
                    operation.operation_id
                ),
                "operation_command": (
                    operation.command
                ),
                "operation_status": (
                    operation.status
                ),
            },
        )
