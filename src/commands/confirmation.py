import uuid

from src.commands.confirmation_models import (
    CANCELLED,
    CONFIRMED,
    EXPIRED,
    PENDING,
    PendingOperation,
)

from src.commands.models import (
    CommandResult,
)


class ConfirmationService:
    """
    Manages explicitly pending operations.

    V1 keeps pending operations in memory.

    This is intentional:
        - confirmation is temporary state
        - it is not memory
        - it is not conversation history
        - it is not persistent application state

    Persistence can be introduced later if required.
    """

    def __init__(
        self,
    ):
        self._pending = {}

    def create_pending(
        self,
        command: str,
        arguments: tuple[str, ...],
        description: str,
        metadata=None,
    ) -> PendingOperation:
        """
        Create a new pending operation.
        """

        if not isinstance(
            command,
            str,
        ):
            raise TypeError(
                "command must be a string."
            )

        if not isinstance(
            arguments,
            tuple,
        ):
            raise TypeError(
                "arguments must be a tuple."
            )

        if not isinstance(
            description,
            str,
        ):
            raise TypeError(
                "description must be a string."
            )

        command = command.strip().upper()

        if not command:
            raise ValueError(
                "command cannot be empty."
            )

        description = description.strip()

        if not description:
            raise ValueError(
                "description cannot be empty."
            )

        operation = PendingOperation(
            operation_id=str(
                uuid.uuid4()
            ),
            command=command,
            arguments=arguments,
            description=description,
            created_at=(
                PendingOperation.now_iso()
            ),
            status=PENDING,
            metadata=(
                dict(metadata)
                if metadata is not None
                else {}
            ),
        )

        self._pending[
            operation.operation_id
        ] = operation

        return operation

    def get_pending(
        self,
    ) -> PendingOperation | None:
        """
        Return the current pending operation.

        V1 permits only one pending operation at a time.
        """

        for operation in self._pending.values():

            if operation.status == PENDING:
                return operation

        return None

    def confirm(
        self,
        operation_id: str | None = None,
    ) -> PendingOperation | None:
        """
        Confirm a pending operation.

        The returned operation is marked CONFIRMED.

        It is still the caller's responsibility to execute it.
        """

        operation = self._resolve_operation(
            operation_id
        )

        if operation is None:
            return None

        confirmed = PendingOperation(
            operation_id=operation.operation_id,
            command=operation.command,
            arguments=operation.arguments,
            description=operation.description,
            created_at=operation.created_at,
            status=CONFIRMED,
            metadata=operation.metadata,
        )

        self._pending[
            operation.operation_id
        ] = confirmed

        return confirmed

    def cancel(
        self,
        operation_id: str | None = None,
    ) -> PendingOperation | None:
        """
        Cancel a pending operation.
        """

        operation = self._resolve_operation(
            operation_id
        )

        if operation is None:
            return None

        cancelled = PendingOperation(
            operation_id=operation.operation_id,
            command=operation.command,
            arguments=operation.arguments,
            description=operation.description,
            created_at=operation.created_at,
            status=CANCELLED,
            metadata=operation.metadata,
        )

        self._pending[
            operation.operation_id
        ] = cancelled

        return cancelled

    def clear(
        self,
    ) -> None:
        """
        Remove all stored operations.
        """

        self._pending.clear()

    def _resolve_operation(
        self,
        operation_id: str | None,
    ) -> PendingOperation | None:

        if operation_id is not None:

            operation = self._pending.get(
                operation_id
            )

            if operation is None:
                return None

            if operation.status != PENDING:
                return None

            return operation

        return self.get_pending()