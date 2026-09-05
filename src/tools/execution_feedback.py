"""Inert feedback boundary after verified execution outcomes.

This module converts one verified ExecutionOutcome into a provenance-bearing
feedback event. Feedback is evidence for later evaluation; it does not grant
authority, authorize retries, revoke capabilities, execute tools, or write
learning state.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Mapping, Optional

from .execution_outcome import ExecutionOutcome, ExecutionOutcomeStatus


class ExecutionFeedbackError(ValueError):
    """Raised when the feedback boundary contract is invalid."""


class FeedbackKind(str, Enum):
    """Classification of evidence carried by one feedback event."""

    SUCCESS = "success"
    TOOL_FAILURE = "tool_failure"
    EXECUTOR_FAILURE = "executor_failure"


@dataclass(frozen=True)
class ExecutionFeedbackEvent:
    """Immutable feedback evidence bound to one exact execution outcome."""

    feedback_id: str
    execution_id: str
    handoff_id: str
    tool_name: str
    invocation_id: Optional[str]
    kind: FeedbackKind
    payload: Mapping[str, Any]
    provenance: Mapping[str, str]
    reason: Optional[str] = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("feedback_id", self.feedback_id),
            ("execution_id", self.execution_id),
            ("handoff_id", self.handoff_id),
            ("tool_name", self.tool_name),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ExecutionFeedbackError(f"{field_name} must be a non-empty string")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise ExecutionFeedbackError("invocation_id must be a string or None")
        if not isinstance(self.kind, FeedbackKind):
            raise ExecutionFeedbackError("kind must be a FeedbackKind member")
        if not isinstance(self.payload, Mapping):
            raise ExecutionFeedbackError("payload must be a mapping")
        if not isinstance(self.provenance, Mapping):
            raise ExecutionFeedbackError("provenance must be a mapping")
        if not all(
            isinstance(key, str) and key.strip()
            and isinstance(value, str) and value.strip()
            for key, value in self.provenance.items()
        ):
            raise ExecutionFeedbackError("provenance must contain non-empty string keys and values")
        if self.reason is not None and not isinstance(self.reason, str):
            raise ExecutionFeedbackError("reason must be a string or None")
        if self.kind is FeedbackKind.SUCCESS and self.reason is not None:
            raise ExecutionFeedbackError("successful feedback cannot contain a failure reason")
        if self.kind is not FeedbackKind.SUCCESS and (
            self.reason is None or not self.reason.strip()
        ):
            raise ExecutionFeedbackError("failed feedback requires a reason")

    def to_context(self) -> dict[str, object]:
        return {
            "feedback_id": self.feedback_id,
            "execution_id": self.execution_id,
            "handoff_id": self.handoff_id,
            "tool_name": self.tool_name,
            "invocation_id": self.invocation_id,
            "feedback_kind": self.kind.value,
            "payload": dict(self.payload),
            "provenance": dict(self.provenance),
            "feedback_reason": self.reason,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "learning_written": False,
        }


class ExecutionFeedbackService:
    """Convert verified execution outcomes into inert feedback evidence."""

    def from_outcome(self, outcome: ExecutionOutcome) -> ExecutionFeedbackEvent:
        if not isinstance(outcome, ExecutionOutcome):
            raise TypeError("outcome must be an ExecutionOutcome")

        if outcome.status is ExecutionOutcomeStatus.SUCCEEDED:
            kind = FeedbackKind.SUCCESS
            payload = {
                "result": outcome.result.content if outcome.result is not None else None,
                "result_metadata": dict(outcome.result.metadata) if outcome.result is not None else {},
            }
        elif outcome.status is ExecutionOutcomeStatus.TOOL_FAILED:
            kind = FeedbackKind.TOOL_FAILURE
            payload = {
                "result": outcome.result.content if outcome.result is not None else None,
                "error": {
                    "code": outcome.result.error.code if outcome.result and outcome.result.error else None,
                    "message": outcome.result.error.message if outcome.result and outcome.result.error else outcome.reason,
                },
            }
        else:
            kind = FeedbackKind.EXECUTOR_FAILURE
            payload = {"result": None}

        provenance = {
            "source": "execution_outcome",
            "execution_id": outcome.execution_id,
            "handoff_id": outcome.handoff_id,
            "outcome_status": outcome.status.value,
        }
        payload_hash = self._payload_hash(payload)
        provenance = {**provenance, "payload_sha256": payload_hash}
        feedback_id = self._feedback_id(outcome.execution_id, outcome.handoff_id, kind, payload_hash)

        return ExecutionFeedbackEvent(
            feedback_id=feedback_id,
            execution_id=outcome.execution_id,
            handoff_id=outcome.handoff_id,
            tool_name=outcome.tool_name,
            invocation_id=outcome.invocation_id,
            kind=kind,
            payload=payload,
            provenance=provenance,
            reason=outcome.reason if kind is not FeedbackKind.SUCCESS else None,
        )

    @staticmethod
    def _payload_hash(payload: Mapping[str, Any]) -> str:
        encoded = json.dumps(
            payload,
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _feedback_id(
        execution_id: str,
        handoff_id: str,
        kind: FeedbackKind,
        payload_hash: str,
    ) -> str:
        encoded = json.dumps(
            {
                "execution_id": execution_id,
                "handoff_id": handoff_id,
                "kind": kind.value,
                "payload_sha256": payload_hash,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"feedback-{hashlib.sha256(encoded).hexdigest()[:24]}"
