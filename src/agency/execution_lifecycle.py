"""Explicit lifecycle and bounded continuation semantics for M8.4."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from src.agency.execution_runtime import ExecutionObservation, ExecutionStatus


class ExecutionLifecycleStatus(str, Enum):
    """Lifecycle state for one execution identity."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    CONTINUATION_REQUIRED = "continuation_required"

    @property
    def terminal(self) -> bool:
        return self in {
            ExecutionLifecycleStatus.SUCCEEDED,
            ExecutionLifecycleStatus.FAILED,
            ExecutionLifecycleStatus.CANCELLED,
        }


@dataclass(frozen=True)
class ContinuationRequest:
    """Explicit data describing why an execution may need continuation.

    A continuation request is not an authorization grant and does not contain
    an executable provider/tool handle. A later action must still traverse the
    normal authority chain.
    """

    execution_id: str
    reason: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValueError("execution_id must be a non-empty string")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")


@dataclass(frozen=True)
class ExecutionLifecycle:
    """Immutable lifecycle state tied to exactly one execution identity."""

    execution_id: str
    status: ExecutionLifecycleStatus = ExecutionLifecycleStatus.PENDING
    observation: ExecutionObservation | None = None
    continuation: ContinuationRequest | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValueError("execution_id must be a non-empty string")
        if not isinstance(self.status, ExecutionLifecycleStatus):
            raise TypeError("status must be an ExecutionLifecycleStatus")
        if self.observation is not None and not isinstance(self.observation, ExecutionObservation):
            raise TypeError("observation must be an ExecutionObservation or None")
        if self.continuation is not None and not isinstance(self.continuation, ContinuationRequest):
            raise TypeError("continuation must be a ContinuationRequest or None")
        if self.continuation is not None and self.continuation.execution_id != self.execution_id:
            raise ValueError("continuation execution_id must match lifecycle execution_id")
        if self.observation is not None and self.observation.execution_id != self.execution_id:
            raise ValueError("observation execution_id must match lifecycle execution_id")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        if self.status is ExecutionLifecycleStatus.CONTINUATION_REQUIRED and self.continuation is None:
            raise ValueError("continuation_required lifecycle state must contain a continuation request")
        if self.status is not ExecutionLifecycleStatus.CONTINUATION_REQUIRED and self.continuation is not None:
            raise ValueError("continuation request is only valid in continuation_required state")

    @property
    def terminal(self) -> bool:
        return self.status.terminal

    @property
    def may_continue(self) -> bool:
        return self.status is ExecutionLifecycleStatus.CONTINUATION_REQUIRED

    @classmethod
    def start(cls, execution_id: str) -> "ExecutionLifecycle":
        return cls(execution_id=execution_id)

    def start_running(self) -> "ExecutionLifecycle":
        self._require_status(ExecutionLifecycleStatus.PENDING)
        return self._replace(status=ExecutionLifecycleStatus.RUNNING)

    def apply_observation(self, observation: ExecutionObservation) -> "ExecutionLifecycle":
        if not isinstance(observation, ExecutionObservation):
            raise TypeError("observation must be an ExecutionObservation")
        if observation.execution_id != self.execution_id:
            raise ValueError("observation execution_id must match lifecycle execution_id")
        self._require_status(ExecutionLifecycleStatus.RUNNING)

        if observation.status is ExecutionStatus.SUCCEEDED:
            status = ExecutionLifecycleStatus.SUCCEEDED
        elif observation.status is ExecutionStatus.FAILED:
            status = ExecutionLifecycleStatus.FAILED
        elif observation.status is ExecutionStatus.NOT_ATTEMPTED:
            status = ExecutionLifecycleStatus.CANCELLED
        else:
            status = ExecutionLifecycleStatus.RUNNING

        return self._replace(status=status, observation=observation)

    def request_continuation(self, reason: str, metadata: Mapping[str, Any] | None = None) -> "ExecutionLifecycle":
        """Represent explicit continuation without authorizing another action."""
        self._require_status(
            ExecutionLifecycleStatus.RUNNING,
            ExecutionLifecycleStatus.FAILED,
        )
        continuation = ContinuationRequest(
            execution_id=self.execution_id,
            reason=reason,
            metadata=dict(metadata or {}),
        )
        return self._replace(
            status=ExecutionLifecycleStatus.CONTINUATION_REQUIRED,
            continuation=continuation,
        )

    def consume_continuation(self) -> "ExecutionLifecycle":
        """Clear a continuation request without authorizing a next execution."""
        self._require_status(ExecutionLifecycleStatus.CONTINUATION_REQUIRED)
        return self._replace(
            status=ExecutionLifecycleStatus.PENDING,
            continuation=None,
            observation=None,
        )

    def cancel(self) -> "ExecutionLifecycle":
        """Cancel a non-terminal lifecycle explicitly."""
        if self.terminal:
            raise ValueError("terminal execution lifecycle cannot be cancelled")
        return self._replace(status=ExecutionLifecycleStatus.CANCELLED, continuation=None)

    def to_context(self) -> dict[str, Any]:
        """Serialize lifecycle state without introducing authority controls."""
        return {
            "execution_id": self.execution_id,
            "status": self.status.value,
            "terminal": self.terminal,
            "may_continue": self.may_continue,
            "observation": None if self.observation is None else self.observation.to_context(),
            "continuation": None
            if self.continuation is None
            else {
                "execution_id": self.continuation.execution_id,
                "reason": self.continuation.reason,
                "metadata": dict(self.continuation.metadata),
            },
            "metadata": dict(self.metadata),
        }

    def _replace(self, **changes: Any) -> "ExecutionLifecycle":
        values = {
            "execution_id": self.execution_id,
            "status": self.status,
            "observation": self.observation,
            "continuation": self.continuation,
            "metadata": dict(self.metadata),
        }
        values.update(changes)
        return ExecutionLifecycle(**values)

    def _require_status(self, *allowed: ExecutionLifecycleStatus) -> None:
        if self.status not in allowed:
            allowed_text = ", ".join(item.value for item in allowed)
            raise ValueError(
                f"lifecycle state '{self.status.value}' does not allow this transition; "
                f"expected one of: {allowed_text}"
            )
