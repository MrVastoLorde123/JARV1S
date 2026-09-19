"""M35 bridge from execution attempts into observable consequence outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json

from src.agents.consequence_execution_attempt import (
    ConsequenceExecutionAttempt,
    ConsequenceExecutionAttemptStatus,
)
from src.tools.models import ToolResult
from src.tools.outcome import (
    ExternalVerificationState,
    ToolOutcome,
)


class ConsequenceExecutionOutcomeStatus(str, Enum):
    COMPLETED_SUCCESS = "COMPLETED_SUCCESS"
    COMPLETED_FAILURE = "COMPLETED_FAILURE"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass(frozen=True)
class ConsequenceExecutionOutcome:
    """Immutable observed consequence outcome preserving execution lineage."""

    outcome_id: str
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
    status: ConsequenceExecutionOutcomeStatus
    authorization_granted: bool
    evidence_refs: tuple[str, ...]
    verification_refs: tuple[str, ...]
    execution_result: ToolResult | None
    verification_state: ExternalVerificationState = ExternalVerificationState.UNVERIFIED
    reason: str | None = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("outcome_id", self.outcome_id), ("attempt_id", self.attempt_id),
            ("preparation_id", self.preparation_id), ("authorization_id", self.authorization_id),
            ("handoff_id", self.handoff_id), ("claim_id", self.claim_id),
            ("task_id", self.task_id), ("consequence_id", self.consequence_id),
            ("tool_name", self.tool_name),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.execution_id is not None and not isinstance(self.execution_id, str):
            raise TypeError("execution_id must be a string or None")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise TypeError("invocation_id must be a string or None")
        if not isinstance(self.status, ConsequenceExecutionOutcomeStatus):
            raise TypeError("status must be a ConsequenceExecutionOutcomeStatus member")
        if not isinstance(self.authorization_granted, bool):
            raise TypeError("authorization_granted must be a bool")
        if any(not isinstance(ref, str) or not ref for ref in self.evidence_refs):
            raise TypeError("evidence_refs must contain non-empty strings")
        if any(not isinstance(ref, str) or not ref for ref in self.verification_refs):
            raise TypeError("verification_refs must contain non-empty strings")
        if self.execution_result is not None and not isinstance(self.execution_result, ToolResult):
            raise TypeError("execution_result must be a ToolResult or None")
        if not isinstance(self.verification_state, ExternalVerificationState):
            raise TypeError("verification_state must be an ExternalVerificationState")
        if self.reason is not None and not isinstance(self.reason, str):
            raise TypeError("reason must be a string or None")
        if self.status is ConsequenceExecutionOutcomeStatus.COMPLETED_SUCCESS:
            if self.execution_id is None or self.execution_result is None or not self.execution_result.success:
                raise ValueError("successful outcome requires a successful execution result")
            if self.reason is not None:
                raise ValueError("successful outcome cannot contain a failure reason")
        elif self.status is ConsequenceExecutionOutcomeStatus.COMPLETED_FAILURE:
            if self.execution_id is None or self.reason is None or not self.reason.strip():
                raise ValueError("failed outcome requires execution identity and reason")
            if self.execution_result is not None and self.execution_result.success:
                raise ValueError("failed outcome cannot wrap a successful result")
        elif self.status is ConsequenceExecutionOutcomeStatus.NOT_EXECUTED:
            if self.execution_id is not None or self.execution_result is not None:
                raise ValueError("not-executed outcome cannot contain execution data")
            if self.reason is None or not self.reason.strip():
                raise ValueError("not-executed outcome requires a reason")

    @property
    def completed(self) -> bool:
        return self.status is not ConsequenceExecutionOutcomeStatus.NOT_EXECUTED

    @property
    def successful(self) -> bool:
        return self.status is ConsequenceExecutionOutcomeStatus.COMPLETED_SUCCESS

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_execution_outcome_id": self.outcome_id,
            "execution_attempt_id": self.attempt_id,
            "execution_id": self.execution_id,
            "preparation_id": self.preparation_id,
            "authorization_id": self.authorization_id,
            "authority_handoff_id": self.handoff_id,
            "claim_id": self.claim_id,
            "task_id": self.task_id,
            "consequence_id": self.consequence_id,
            "tool_name": self.tool_name,
            "invocation_id": self.invocation_id,
            "execution_outcome_status": self.status.value,
            "execution_outcome_observed": True,
            "execution_completed": self.completed,
            "execution_succeeded": self.successful,
            "verification_state": self.verification_state.value,
            "externally_verified": self.verification_state is ExternalVerificationState.VERIFIED,
            "authorization_granted": self.authorization_granted,
            "authority_granted": False,
            "retry_requested": False,
            "learning_write_requested": False,
            "memory_mutated": False,
            "evidence_refs": self.evidence_refs,
            "verification_refs": self.verification_refs,
            "reason": self.reason,
        }


class ConsequenceExecutionOutcomeService:
    """Convert one M34 execution attempt into inert outcome evidence."""

    def evaluate(
        self,
        attempt: ConsequenceExecutionAttempt,
        tool_outcome: ToolOutcome | None = None,
    ) -> ConsequenceExecutionOutcome:
        if not isinstance(attempt, ConsequenceExecutionAttempt):
            raise TypeError("attempt must be a ConsequenceExecutionAttempt")
        if tool_outcome is not None and not isinstance(tool_outcome, ToolOutcome):
            raise TypeError("tool_outcome must be a ToolOutcome or None")
        verification_state = (
            tool_outcome.verification_state
            if tool_outcome is not None
            else ExternalVerificationState.UNVERIFIED
        )
        if tool_outcome is not None and tool_outcome.invocation_id != attempt.invocation_id:
            raise ValueError("tool outcome invocation_id must match execution attempt")
        status = {
            ConsequenceExecutionAttemptStatus.ATTEMPTED_COMPLETED: ConsequenceExecutionOutcomeStatus.COMPLETED_SUCCESS,
            ConsequenceExecutionAttemptStatus.ATTEMPTED_FAILED: ConsequenceExecutionOutcomeStatus.COMPLETED_FAILURE,
            ConsequenceExecutionAttemptStatus.BLOCKED: ConsequenceExecutionOutcomeStatus.NOT_EXECUTED,
        }[attempt.status]
        return ConsequenceExecutionOutcome(
            outcome_id=self._outcome_id(attempt, status),
            attempt_id=attempt.attempt_id,
            execution_id=attempt.execution_id,
            preparation_id=attempt.preparation_id,
            authorization_id=attempt.authorization_id,
            handoff_id=attempt.handoff_id,
            claim_id=attempt.claim_id,
            task_id=attempt.task_id,
            consequence_id=attempt.consequence_id,
            tool_name=attempt.tool_name,
            invocation_id=attempt.invocation_id,
            status=status,
            authorization_granted=attempt.authorization_granted,
            evidence_refs=attempt.evidence_refs,
            verification_refs=attempt.verification_refs,
            execution_result=attempt.execution_result,
            verification_state=verification_state,
            reason=attempt.reason,
        )

    @staticmethod
    def _outcome_id(attempt: ConsequenceExecutionAttempt, status: ConsequenceExecutionOutcomeStatus) -> str:
        payload = json.dumps({
            "attempt_id": attempt.attempt_id,
            "execution_id": attempt.execution_id,
            "preparation_id": attempt.preparation_id,
            "authorization_id": attempt.authorization_id,
            "status": status.value,
        }, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return f"consequence-outcome-{hashlib.sha256(payload).hexdigest()[:24]}"


__all__ = [
    "ConsequenceExecutionOutcome",
    "ConsequenceExecutionOutcomeService",
    "ConsequenceExecutionOutcomeStatus",
]
