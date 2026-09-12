import hashlib
import json
import uuid

from src.agents.coding_confirmation_models import (
    CodingConfirmationStatus,
    CodingPendingOperation,
)
from src.agents.coding_worker import CodingAgentPlan, CodingAgentTask


def coding_plan_fingerprint(task: CodingAgentTask, plan: CodingAgentPlan) -> str:
    """Produce a deterministic fingerprint binding the task to the exact plan."""
    payload = {
        "task_id": task.task_id,
        "objective": task.objective,
        "metadata": dict(task.metadata),
        "edits": [
            {
                "path": edit.path,
                "content": edit.content,
                "overwrite": edit.overwrite,
                "create_parents": edit.create_parents,
            }
            for edit in plan.edits
        ],
        "verification": {
            "runner": plan.verification.runner,
            "arguments": list(plan.verification.arguments),
            "timeout_seconds": plan.verification.timeout_seconds,
        },
        "rationale": plan.rationale,
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class CodingAgentConfirmationService:
    """Stage, confirm, and cancel exact coding-agent proposals without executing them."""

    def __init__(self) -> None:
        self._operations: dict[str, CodingPendingOperation] = {}

    def stage(self, task: CodingAgentTask, plan: CodingAgentPlan, metadata=None) -> CodingPendingOperation:
        if not isinstance(task, CodingAgentTask):
            raise TypeError("task must be a CodingAgentTask")
        if not isinstance(plan, CodingAgentPlan):
            raise TypeError("plan must be a CodingAgentPlan")

        operation_metadata = dict(metadata) if metadata is not None else {}
        operation_metadata.setdefault("plan_fingerprint", coding_plan_fingerprint(task, plan))

        operation = CodingPendingOperation(
            operation_id=str(uuid.uuid4()),
            task=task,
            plan=plan,
            created_at=CodingPendingOperation.now_iso(),
            metadata=operation_metadata,
        )
        self._operations[operation.operation_id] = operation
        return operation

    def get(self, operation_id: str) -> CodingPendingOperation | None:
        if not isinstance(operation_id, str):
            raise TypeError("operation_id must be a string")
        return self._operations.get(operation_id)

    def get_pending(self) -> CodingPendingOperation | None:
        return next((operation for operation in self._operations.values() if operation.is_pending), None)

    def confirm(self, operation_id: str | None = None) -> CodingPendingOperation | None:
        operation = self._resolve_pending(operation_id)
        if operation is None:
            return None
        confirmed = CodingPendingOperation(
            operation_id=operation.operation_id,
            task=operation.task,
            plan=operation.plan,
            created_at=operation.created_at,
            status=CodingConfirmationStatus.CONFIRMED,
            metadata=operation.metadata,
        )
        self._operations[operation.operation_id] = confirmed
        return confirmed

    def cancel(self, operation_id: str | None = None) -> CodingPendingOperation | None:
        operation = self._resolve_pending(operation_id)
        if operation is None:
            return None
        cancelled = CodingPendingOperation(
            operation_id=operation.operation_id,
            task=operation.task,
            plan=operation.plan,
            created_at=operation.created_at,
            status=CodingConfirmationStatus.CANCELLED,
            metadata=operation.metadata,
        )
        self._operations[operation.operation_id] = cancelled
        return cancelled

    def clear(self) -> None:
        self._operations.clear()

    def _resolve_pending(self, operation_id: str | None) -> CodingPendingOperation | None:
        if operation_id is not None:
            operation = self._operations.get(operation_id)
            if operation is None or not operation.is_pending:
                return None
            return operation
        return self.get_pending()
