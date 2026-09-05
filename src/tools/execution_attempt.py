"""Provider-neutral execution-attempt boundary after preparation.

The execution-attempt layer accepts only a structurally valid ExecutionHandoff
and delegates execution to a replaceable ToolExecutor. It records an explicit
execution identity and lifecycle outcome while keeping authorization,
permission, worker assignment, and successful completion distinct concepts.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Optional, Protocol

from .execution_preparation import ExecutionHandoff
from .models import ToolResult


class ExecutionAttemptError(ValueError):
    """Raised when the execution-attempt contract is invalid."""


class ExecutionAttemptStatus(str, Enum):
    """Lifecycle outcome of one execution attempt."""

    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class ExecutionAttemptResult:
    """Immutable execution-attempt outcome for one prepared handoff."""

    execution_id: str
    handoff_id: str
    tool_name: str
    invocation_id: Optional[str]
    status: ExecutionAttemptStatus
    worker_id: Optional[str] = None
    result: Optional[ToolResult] = None
    reason: Optional[str] = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("execution_id", self.execution_id),
            ("handoff_id", self.handoff_id),
            ("tool_name", self.tool_name),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ExecutionAttemptError(f"{field_name} must be a non-empty string")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise ExecutionAttemptError("invocation_id must be a string or None")
        if not isinstance(self.status, ExecutionAttemptStatus):
            raise ExecutionAttemptError("status must be an ExecutionAttemptStatus member")
        if self.worker_id is not None and (
            not isinstance(self.worker_id, str) or not self.worker_id.strip()
        ):
            raise ExecutionAttemptError("worker_id must be a non-empty string or None")
        if self.result is not None and not isinstance(self.result, ToolResult):
            raise ExecutionAttemptError("result must be a ToolResult or None")
        if self.reason is not None and not isinstance(self.reason, str):
            raise ExecutionAttemptError("reason must be a string or None")
        if self.status is ExecutionAttemptStatus.COMPLETED:
            if self.result is None:
                raise ExecutionAttemptError("a completed attempt requires a result")
            if self.reason is not None:
                raise ExecutionAttemptError("a completed attempt cannot contain a failure reason")
        if self.status is ExecutionAttemptStatus.FAILED and (
            self.reason is None or not self.reason.strip()
        ):
            raise ExecutionAttemptError("a failed attempt requires a reason")

    @property
    def completed(self) -> bool:
        return self.status is ExecutionAttemptStatus.COMPLETED

    def to_context(self) -> dict[str, object]:
        return {
            "execution_id": self.execution_id,
            "handoff_id": self.handoff_id,
            "tool_name": self.tool_name,
            "invocation_id": self.invocation_id,
            "execution_attempt_status": self.status.value,
            "worker_id": self.worker_id,
            "execution_attempted": True,
            "execution_completed": self.completed,
            "authority_granted": False,
            "permission_granted": False,
            "authorization_granted": False,
        }


class ToolExecutor(Protocol):
    """Replaceable execution provider behind the attempt boundary."""

    def execute(self, handoff: ExecutionHandoff) -> ToolResult:
        """Execute the exact prepared handoff and return its tool outcome."""


class ExecutionAttemptService:
    """Turn one prepared handoff into one explicit execution attempt."""

    def __init__(self, executor: ToolExecutor) -> None:
        if not callable(getattr(executor, "execute", None)):
            raise TypeError("executor must provide an execute(handoff) method")
        self._executor = executor

    def attempt(self, handoff: ExecutionHandoff) -> ExecutionAttemptResult:
        if not isinstance(handoff, ExecutionHandoff):
            raise TypeError("handoff must be an ExecutionHandoff")

        execution_id = self._execution_id(handoff)
        try:
            result = self._executor.execute(handoff)
        except Exception as exc:  # noqa: BLE001 - executor boundary converts execution failures to data
            return ExecutionAttemptResult(
                execution_id=execution_id,
                handoff_id=handoff.handoff_id,
                tool_name=handoff.tool_name,
                invocation_id=handoff.invocation_id,
                status=ExecutionAttemptStatus.FAILED,
                worker_id=None,
                result=None,
                reason=str(exc) or exc.__class__.__name__,
            )

        if not isinstance(result, ToolResult):
            return self._failed(handoff, execution_id, "executor returned an invalid result type")

        if result.tool_name.strip().lower() != handoff.tool_name.strip().lower():
            return self._failed(
                handoff,
                execution_id,
                "executor result tool identity does not match handoff",
            )
        if result.invocation_id != handoff.invocation_id:
            return self._failed(
                handoff,
                execution_id,
                "executor result invocation identity does not match handoff",
            )

        status = (
            ExecutionAttemptStatus.COMPLETED
            if result.success
            else ExecutionAttemptStatus.FAILED
        )
        return ExecutionAttemptResult(
            execution_id=execution_id,
            handoff_id=handoff.handoff_id,
            tool_name=handoff.tool_name,
            invocation_id=handoff.invocation_id,
            status=status,
            result=result,
            reason=None if result.success else (
                result.error.message if result.error is not None else "tool execution failed"
            ),
        )

    @staticmethod
    def _failed(
        handoff: ExecutionHandoff,
        execution_id: str,
        reason: str,
    ) -> ExecutionAttemptResult:
        return ExecutionAttemptResult(
            execution_id=execution_id,
            handoff_id=handoff.handoff_id,
            tool_name=handoff.tool_name,
            invocation_id=handoff.invocation_id,
            status=ExecutionAttemptStatus.FAILED,
            reason=reason,
        )

    @staticmethod
    def _execution_id(handoff: ExecutionHandoff) -> str:
        payload = json.dumps(
            {
                "handoff_id": handoff.handoff_id,
                "tool_name": handoff.tool_name.strip().lower(),
                "invocation_id": handoff.invocation_id,
                "arguments": dict(handoff.arguments),
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"exec-{hashlib.sha256(payload).hexdigest()[:24]}"
