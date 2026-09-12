"""M34 bridge from consequence preparation into execution attempts.

M34 accepts only a prepared M33 execution handoff and delegates the actual
attempt to the existing ExecutionAttemptService. It preserves upstream
provenance and never creates authorization, policy, sandbox, or retry logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json

from src.tools.execution_attempt import (
    ExecutionAttemptResult,
    ExecutionAttemptService,
    ExecutionAttemptStatus,
    ToolExecutor,
)
from src.tools.models import ToolResult

from src.agents.consequence_execution_preparation import (
    ConsequenceExecutionPreparation,
    ConsequenceExecutionPreparationStatus,
)


class ConsequenceExecutionAttemptStatus(str, Enum):
    """Outcome of the M33 -> M34 execution-attempt bridge."""

    ATTEMPTED_COMPLETED = "ATTEMPTED_COMPLETED"
    ATTEMPTED_FAILED = "ATTEMPTED_FAILED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class ConsequenceExecutionAttempt:
    """Immutable execution-attempt result preserving the complete lineage."""

    attempt_id: str
    execution_id: str | None
    preparation_id: str
    authorization_id: str
    handoff_id: str
    claim_id: str
    task_id: str
    consequence_id: str
    tool_name: str
    invocation_id: str | None
    status: ConsequenceExecutionAttemptStatus
    authorization_granted: bool
    evidence_refs: tuple[str, ...]
    verification_refs: tuple[str, ...]
    execution_result: ToolResult | None
    underlying_attempt: ExecutionAttemptResult | None
    reason: str | None = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("attempt_id", self.attempt_id),
            ("preparation_id", self.preparation_id),
            ("authorization_id", self.authorization_id),
            ("handoff_id", self.handoff_id),
            ("claim_id", self.claim_id),
            ("task_id", self.task_id),
            ("consequence_id", self.consequence_id),
            ("tool_name", self.tool_name),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.execution_id is not None and not isinstance(self.execution_id, str):
            raise TypeError("execution_id must be a string or None")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise TypeError("invocation_id must be a string or None")
        if not isinstance(self.status, ConsequenceExecutionAttemptStatus):
            raise TypeError("status must be a ConsequenceExecutionAttemptStatus member")
        if not isinstance(self.authorization_granted, bool):
            raise TypeError("authorization_granted must be a bool")
        if any(not isinstance(ref, str) or not ref for ref in self.evidence_refs):
            raise TypeError("evidence_refs must contain non-empty strings")
        if any(not isinstance(ref, str) or not ref for ref in self.verification_refs):
            raise TypeError("verification_refs must contain non-empty strings")
        if self.execution_result is not None and not isinstance(self.execution_result, ToolResult):
            raise TypeError("execution_result must be a ToolResult or None")
        if self.underlying_attempt is not None and not isinstance(
            self.underlying_attempt, ExecutionAttemptResult
        ):
            raise TypeError("underlying_attempt must be an ExecutionAttemptResult or None")
        if self.reason is not None and not isinstance(self.reason, str):
            raise TypeError("reason must be a string or None")

        if self.status is ConsequenceExecutionAttemptStatus.BLOCKED:
            if self.execution_id is not None:
                raise ValueError("BLOCKED cannot contain an execution_id")
            if self.execution_result is not None:
                raise ValueError("BLOCKED cannot contain an execution result")
            if self.underlying_attempt is not None:
                raise ValueError("BLOCKED cannot contain an underlying execution attempt")
            if self.reason is None or not self.reason.strip():
                raise ValueError("BLOCKED requires a reason")
        elif self.status is ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED:
            if not self.authorization_granted:
                raise ValueError("completed attempt requires granted authorization provenance")
            if self.execution_id is None:
                raise ValueError("completed attempt requires an execution_id")
            if self.execution_result is None or not self.execution_result.success:
                raise ValueError("completed attempt requires a successful execution result")
            if self.underlying_attempt is None or not self.underlying_attempt.completed:
                raise ValueError("completed attempt requires a completed underlying attempt")
            if self.reason is not None:
                raise ValueError("completed attempt cannot contain a failure reason")
        elif self.status is ConsequenceExecutionAttemptStatus.ATTEMPTED_FAILED:
            if not self.authorization_granted:
                raise ValueError("failed attempt requires granted authorization provenance")
            if self.execution_id is None:
                raise ValueError("failed attempt requires an execution_id")
            if self.underlying_attempt is None or self.underlying_attempt.status is not ExecutionAttemptStatus.FAILED:
                raise ValueError("failed attempt requires a failed underlying attempt")
            if self.reason is None or not self.reason.strip():
                raise ValueError("failed attempt requires a reason")

    @property
    def attempted(self) -> bool:
        return self.status is not ConsequenceExecutionAttemptStatus.BLOCKED

    @property
    def completed(self) -> bool:
        return self.status is ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED

    def to_context(self) -> dict[str, object]:
        return {
            "attempt_id": self.attempt_id,
            "execution_id": self.execution_id,
            "preparation_id": self.preparation_id,
            "authorization_id": self.authorization_id,
            "authority_handoff_id": self.handoff_id,
            "claim_id": self.claim_id,
            "task_id": self.task_id,
            "consequence_id": self.consequence_id,
            "tool_name": self.tool_name,
            "invocation_id": self.invocation_id,
            "execution_attempt_status": self.status.value,
            "execution_attempted": self.attempted,
            "execution_completed": self.completed,
            "authorization_granted": self.authorization_granted,
            "execution_requested": False,
            "worker_assigned": False,
            "containment_active": False,
            "evidence_refs": self.evidence_refs,
            "verification_refs": self.verification_refs,
            "reason": self.reason,
        }


class ConsequenceExecutionAttemptService:
    """Start one explicit execution attempt from one prepared consequence."""

    def __init__(self, executor: ToolExecutor) -> None:
        self._attempt_service = ExecutionAttemptService(executor)

    def attempt(self, preparation: ConsequenceExecutionPreparation) -> ConsequenceExecutionAttempt:
        if not isinstance(preparation, ConsequenceExecutionPreparation):
            raise TypeError("preparation must be a ConsequenceExecutionPreparation")

        if preparation.status is not ConsequenceExecutionPreparationStatus.PREPARED:
            return self._blocked(preparation, "execution preparation is not ready for an execution attempt")
        if preparation.execution_handoff is None:
            return self._blocked(preparation, "prepared consequence is missing its execution handoff")

        underlying = self._attempt_service.attempt(preparation.execution_handoff)
        status = (
            ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED
            if underlying.status is ExecutionAttemptStatus.COMPLETED
            else ConsequenceExecutionAttemptStatus.ATTEMPTED_FAILED
        )
        reason = None if underlying.status is ExecutionAttemptStatus.COMPLETED else (
            underlying.reason or "execution attempt failed"
        )
        return ConsequenceExecutionAttempt(
            attempt_id=self._attempt_id(preparation, underlying),
            execution_id=underlying.execution_id,
            preparation_id=preparation.preparation_id,
            authorization_id=preparation.authorization_id,
            handoff_id=preparation.handoff_id,
            claim_id=preparation.claim_id,
            task_id=preparation.task_id,
            consequence_id=preparation.consequence_id,
            tool_name=preparation.tool_name,
            invocation_id=preparation.invocation_id,
            status=status,
            authorization_granted=preparation.authorization_granted,
            evidence_refs=preparation.evidence_refs,
            verification_refs=preparation.verification_refs,
            execution_result=underlying.result,
            underlying_attempt=underlying,
            reason=reason,
        )

    @staticmethod
    def _blocked(
        preparation: ConsequenceExecutionPreparation,
        reason: str,
    ) -> ConsequenceExecutionAttempt:
        return ConsequenceExecutionAttempt(
            attempt_id=ConsequenceExecutionAttemptService._blocked_id(preparation, reason),
            execution_id=None,
            preparation_id=preparation.preparation_id,
            authorization_id=preparation.authorization_id,
            handoff_id=preparation.handoff_id,
            claim_id=preparation.claim_id,
            task_id=preparation.task_id,
            consequence_id=preparation.consequence_id,
            tool_name=preparation.tool_name,
            invocation_id=preparation.invocation_id,
            status=ConsequenceExecutionAttemptStatus.BLOCKED,
            authorization_granted=preparation.authorization_granted,
            evidence_refs=preparation.evidence_refs,
            verification_refs=preparation.verification_refs,
            execution_result=None,
            underlying_attempt=None,
            reason=reason,
        )

    @staticmethod
    def _attempt_id(
        preparation: ConsequenceExecutionPreparation,
        attempt: ExecutionAttemptResult,
    ) -> str:
        payload = json.dumps(
            {
                "preparation_id": preparation.preparation_id,
                "authorization_id": preparation.authorization_id,
                "handoff_id": preparation.handoff_id,
                "execution_id": attempt.execution_id,
                "tool_name": preparation.tool_name.strip().lower(),
                "invocation_id": preparation.invocation_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"consequence-attempt-{hashlib.sha256(payload).hexdigest()[:24]}"

    @staticmethod
    def _blocked_id(preparation: ConsequenceExecutionPreparation, reason: str) -> str:
        payload = json.dumps(
            {
                "preparation_id": preparation.preparation_id,
                "authorization_id": preparation.authorization_id,
                "reason": reason,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"consequence-attempt-{hashlib.sha256(payload).hexdigest()[:24]}"


__all__ = [
    "ConsequenceExecutionAttempt",
    "ConsequenceExecutionAttemptService",
    "ConsequenceExecutionAttemptStatus",
]
