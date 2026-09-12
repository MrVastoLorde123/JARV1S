import hashlib
import json
import uuid

from src.agents.coding_confirmation_models import (
    CodingConfirmationStatus,
    CodingPendingOperation,
)
from src.agents.coding_worker import CodingAgentPlan, CodingAgentTask
from src.tools.models import ToolRequest


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
    """Stage, confirm, and authorize exact coding-agent proposals."""

    def __init__(self) -> None:
        self._operations: dict[str, CodingPendingOperation] = {}
        self._consumed_invocations: set[tuple[str, str]] = set()

    def stage(
        self,
        task: CodingAgentTask,
        plan: CodingAgentPlan,
        metadata=None,
    ) -> CodingPendingOperation:
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
        return next(
            (operation for operation in self._operations.values() if operation.is_pending),
            None,
        )

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

    def authorize_tool_request(self, operation_id: str, request: ToolRequest) -> bool:
        """Authorize one exact tool invocation from a confirmed coding plan.

        Approval is one-shot per invocation ID. The request must match the
        stored edit or verification arguments exactly.
        """
        if not isinstance(operation_id, str) or not operation_id.strip():
            raise TypeError("operation_id must be a non-empty string")
        if not isinstance(request, ToolRequest):
            raise TypeError("request must be a ToolRequest")

        operation = self._operations.get(operation_id)
        if operation is None or not operation.is_confirmed:
            return False
        expected_fingerprint = operation.metadata.get("plan_fingerprint")
        if expected_fingerprint != coding_plan_fingerprint(operation.task, operation.plan):
            return False
        if request.invocation_id is None:
            return False
        if request.metadata.get("coding_operation_id") != operation_id:
            return False
        if request.metadata.get("task_id") != operation.task.task_id:
            return False

        key = (operation_id, request.invocation_id)
        if key in self._consumed_invocations:
            return False

        if request.tool_name == "write_file":
            edit_index = request.metadata.get("edit_index")
            if not isinstance(edit_index, int) or isinstance(edit_index, bool):
                return False
            if edit_index < 0 or edit_index >= len(operation.plan.edits):
                return False
            edit = operation.plan.edits[edit_index]
            expected_arguments = {
                "path": edit.path,
                "content": edit.content,
                "overwrite": edit.overwrite,
                "create_parents": edit.create_parents,
            }
        elif request.tool_name == "run_test":
            if request.metadata.get("phase") != "verification":
                return False
            expected_arguments = {
                "runner": operation.plan.verification.runner,
                "arguments": list(operation.plan.verification.arguments),
            }
            if operation.plan.verification.timeout_seconds is not None:
                expected_arguments["timeout_seconds"] = operation.plan.verification.timeout_seconds
        else:
            return False

        if dict(request.arguments) != expected_arguments:
            return False

        self._consumed_invocations.add(key)
        return True

    def clear(self) -> None:
        self._operations.clear()
        self._consumed_invocations.clear()

    def _resolve_pending(self, operation_id: str | None) -> CodingPendingOperation | None:
        if operation_id is not None:
            operation = self._operations.get(operation_id)
            if operation is None or not operation.is_pending:
                return None
            return operation
        return self.get_pending()
