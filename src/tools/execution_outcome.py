"""Outcome and result-integrity boundary after an execution attempt.

This module interprets one execution-attempt result against the exact
ExecutionHandoff that produced it. It verifies lifecycle and identity
consistency, distinguishes executor failure from tool-declared failure, and
creates an immutable outcome record for later feedback without authorizing,
retrying, revoking, persisting, or learning from the result.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .execution_attempt import ExecutionAttemptResult, ExecutionAttemptStatus
from .execution_preparation import ExecutionHandoff
from .models import ToolResult


class ExecutionOutcomeError(ValueError):
    """Raised when an execution outcome contract is invalid."""


class ExecutionOutcomeStatus(str, Enum):
    """Normalized outcome classification for one execution attempt."""

    SUCCEEDED = "succeeded"
    TOOL_FAILED = "tool_failed"
    EXECUTOR_FAILED = "executor_failed"


@dataclass(frozen=True)
class ExecutionOutcome:
    """Immutable, inspectable outcome bound to one exact execution attempt."""

    execution_id: str
    handoff_id: str
    tool_name: str
    invocation_id: Optional[str]
    status: ExecutionOutcomeStatus
    result: Optional[ToolResult] = None
    reason: Optional[str] = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("execution_id", self.execution_id),
            ("handoff_id", self.handoff_id),
            ("tool_name", self.tool_name),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ExecutionOutcomeError(f"{field_name} must be a non-empty string")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise ExecutionOutcomeError("invocation_id must be a string or None")
        if not isinstance(self.status, ExecutionOutcomeStatus):
            raise ExecutionOutcomeError("status must be an ExecutionOutcomeStatus member")
        if self.result is not None and not isinstance(self.result, ToolResult):
            raise ExecutionOutcomeError("result must be a ToolResult or None")
        if self.reason is not None and not isinstance(self.reason, str):
            raise ExecutionOutcomeError("reason must be a string or None")

        if self.status is ExecutionOutcomeStatus.SUCCEEDED:
            if self.result is None or not self.result.success:
                raise ExecutionOutcomeError("a succeeded outcome requires a successful ToolResult")
            if self.reason is not None:
                raise ExecutionOutcomeError("a succeeded outcome cannot contain a reason")
        elif self.status is ExecutionOutcomeStatus.TOOL_FAILED:
            if self.result is None or self.result.success:
                raise ExecutionOutcomeError("a tool-failed outcome requires a failed ToolResult")
            if self.reason is None or not self.reason.strip():
                raise ExecutionOutcomeError("a tool-failed outcome requires a reason")
        elif self.status is ExecutionOutcomeStatus.EXECUTOR_FAILED:
            if self.result is not None:
                raise ExecutionOutcomeError("an executor-failed outcome cannot contain a ToolResult")
            if self.reason is None or not self.reason.strip():
                raise ExecutionOutcomeError("an executor-failed outcome requires a reason")

    @property
    def succeeded(self) -> bool:
        return self.status is ExecutionOutcomeStatus.SUCCEEDED

    def to_context(self) -> dict[str, object]:
        return {
            "execution_id": self.execution_id,
            "handoff_id": self.handoff_id,
            "tool_name": self.tool_name,
            "invocation_id": self.invocation_id,
            "execution_outcome_status": self.status.value,
            "execution_succeeded": self.succeeded,
            "outcome_reason": self.reason,
            "authority_granted": False,
            "permission_granted": False,
            "authorization_granted": False,
            "learning_written": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class ExecutionOutcomeService:
    """Validate an execution attempt against its exact handoff and normalize its outcome."""

    def interpret(
        self,
        attempt: ExecutionAttemptResult,
        handoff: ExecutionHandoff,
    ) -> ExecutionOutcome:
        if not isinstance(attempt, ExecutionAttemptResult):
            raise TypeError("attempt must be an ExecutionAttemptResult")
        if not isinstance(handoff, ExecutionHandoff):
            raise TypeError("handoff must be an ExecutionHandoff")

        tool_name = handoff.tool_name.strip().lower()
        if attempt.execution_id.strip() != self._expected_execution_id(handoff):
            raise ExecutionOutcomeError("execution identity does not match handoff")
        if attempt.handoff_id != handoff.handoff_id:
            raise ExecutionOutcomeError("attempt handoff identity does not match handoff")
        if attempt.tool_name.strip().lower() != tool_name:
            raise ExecutionOutcomeError("attempt tool identity does not match handoff")
        if attempt.invocation_id != handoff.invocation_id:
            raise ExecutionOutcomeError("attempt invocation identity does not match handoff")

        if attempt.status is ExecutionAttemptStatus.COMPLETED:
            if attempt.result is None or not attempt.result.success:
                raise ExecutionOutcomeError(
                    "completed execution attempt must contain a successful ToolResult"
                )
            if attempt.result.tool_name.strip().lower() != tool_name:
                raise ExecutionOutcomeError("result tool identity does not match handoff")
            if attempt.result.invocation_id != handoff.invocation_id:
                raise ExecutionOutcomeError("result invocation identity does not match handoff")
            return ExecutionOutcome(
                execution_id=attempt.execution_id,
                handoff_id=handoff.handoff_id,
                tool_name=handoff.tool_name,
                invocation_id=handoff.invocation_id,
                status=ExecutionOutcomeStatus.SUCCEEDED,
                result=attempt.result,
            )

        if attempt.result is not None:
            if attempt.result.tool_name.strip().lower() != tool_name:
                raise ExecutionOutcomeError("failed result tool identity does not match handoff")
            if attempt.result.invocation_id != handoff.invocation_id:
                raise ExecutionOutcomeError("failed result invocation identity does not match handoff")
            if attempt.result.success:
                raise ExecutionOutcomeError("failed execution attempt cannot contain a successful ToolResult")
            return ExecutionOutcome(
                execution_id=attempt.execution_id,
                handoff_id=handoff.handoff_id,
                tool_name=handoff.tool_name,
                invocation_id=handoff.invocation_id,
                status=ExecutionOutcomeStatus.TOOL_FAILED,
                result=attempt.result,
                reason=attempt.reason
                or (attempt.result.error.message if attempt.result.error is not None else "tool execution failed"),
            )

        return ExecutionOutcome(
            execution_id=attempt.execution_id,
            handoff_id=handoff.handoff_id,
            tool_name=handoff.tool_name,
            invocation_id=handoff.invocation_id,
            status=ExecutionOutcomeStatus.EXECUTOR_FAILED,
            reason=attempt.reason or "executor failed without a ToolResult",
        )

    @staticmethod
    def _expected_execution_id(handoff: ExecutionHandoff) -> str:
        import hashlib
        import json

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
