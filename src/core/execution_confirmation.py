import hashlib
import json
import uuid

from src.core.execution_confirmation_models import (
    ExecutionConfirmationStatus,
    ExecutionPendingOperation,
)

from src.core.execution_plan_models import (
    ExecutionPlan,
)


def execution_plan_fingerprint(
    plan: ExecutionPlan,
) -> str:
    """
    Produce a deterministic fingerprint for an execution plan.
    """

    payload = {
        "plan_id": plan.plan_id,
        "task_description": plan.task_description,
        "status": plan.status.value,
        "metadata": plan.metadata,
        "steps": [
            {
                "step_id": step.step_id,
                "description": step.description,
                "action": step.action,
                "order": step.order,
                "depends_on": step.depends_on,
                "status": step.status.value,
                "requires_confirmation": (
                    step.requires_confirmation
                ),
                "metadata": step.metadata,
            }
            for step in plan.steps
        ],
    }

    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")

    return hashlib.sha256(
        encoded
    ).hexdigest()


class ExecutionConfirmationService:
    """
    Manages execution plans awaiting confirmation.

    V1 state is intentionally in-memory.

    This service:
        - stages plans
        - retrieves plans
        - confirms plans
        - cancels plans

    It does NOT execute plans.
    """

    def __init__(self):
        self._operations = {}

    def stage(
        self,
        plan: ExecutionPlan,
        metadata=None,
    ) -> ExecutionPendingOperation:

        if not isinstance(plan, ExecutionPlan):
            raise TypeError(
                "plan must be an ExecutionPlan."
            )

        operation_id = str(uuid.uuid4())

        operation_metadata = (
            dict(metadata)
            if metadata is not None
            else {}
        )

        operation_metadata.setdefault(
            "plan_fingerprint",
            execution_plan_fingerprint(plan),
        )

        operation = ExecutionPendingOperation(
            operation_id=operation_id,
            plan=plan,
            created_at=(
                ExecutionPendingOperation.now_iso()
            ),
            metadata=operation_metadata,
        )

        self._operations[
            operation.operation_id
        ] = operation

        return operation

    def get(
        self,
        operation_id: str,
    ) -> ExecutionPendingOperation | None:
        """
        Retrieve an operation regardless of lifecycle status.

        Returns None only when the operation ID does not exist.
        """

        if not isinstance(operation_id, str):
            raise TypeError(
                "operation_id must be a string."
            )

        return self._operations.get(
            operation_id
        )

    def get_pending(
        self,
    ) -> ExecutionPendingOperation | None:

        for operation in self._operations.values():
            if operation.is_pending:
                return operation

        return None

    def confirm(
        self,
        operation_id: str | None = None,
    ) -> ExecutionPendingOperation | None:

        operation = self._resolve_pending(
            operation_id
        )

        if operation is None:
            return None

        confirmed = ExecutionPendingOperation(
            operation_id=operation.operation_id,
            plan=operation.plan,
            created_at=operation.created_at,
            status=(
                ExecutionConfirmationStatus.CONFIRMED
            ),
            metadata=operation.metadata,
        )

        self._operations[
            operation.operation_id
        ] = confirmed

        return confirmed

    def cancel(
        self,
        operation_id: str | None = None,
    ) -> ExecutionPendingOperation | None:

        operation = self._resolve_pending(
            operation_id
        )

        if operation is None:
            return None

        cancelled = ExecutionPendingOperation(
            operation_id=operation.operation_id,
            plan=operation.plan,
            created_at=operation.created_at,
            status=(
                ExecutionConfirmationStatus.CANCELLED
            ),
            metadata=operation.metadata,
        )

        self._operations[
            operation.operation_id
        ] = cancelled

        return cancelled

    def clear(self) -> None:
        self._operations.clear()

    def _resolve_pending(
        self,
        operation_id: str | None,
    ) -> ExecutionPendingOperation | None:
        """
        Resolve an operation only when it is pending.

        None means "use the first pending operation".
        """

        if operation_id is not None:
            operation = self._operations.get(
                operation_id
            )

            if operation is None:
                return None

            if not operation.is_pending:
                return None

            return operation

        return self.get_pending()
