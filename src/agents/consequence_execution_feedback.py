"""M36 bridge from observed consequence outcomes into inert feedback."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from src.agents.consequence_execution_outcome import (
    ConsequenceExecutionOutcome,
    ConsequenceExecutionOutcomeStatus,
)


class ConsequenceExecutionFeedbackKind(str, Enum):
    """Classification of one observed consequence outcome as feedback."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    NOT_EXECUTED = "NOT_EXECUTED"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class ConsequenceExecutionFeedback:
    """Immutable feedback evidence preserving the complete consequence lineage."""

    feedback_id: str
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
    kind: ConsequenceExecutionFeedbackKind
    payload: Mapping[str, Any]
    authorization_granted: bool
    evidence_refs: tuple[str, ...]
    verification_refs: tuple[str, ...]
    reason: str | None = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("feedback_id", self.feedback_id),
            ("outcome_id", self.outcome_id),
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
        if self.execution_id is not None and (not isinstance(self.execution_id, str) or not self.execution_id.strip()):
            raise ValueError("execution_id must be a non-empty string or None")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise TypeError("invocation_id must be a string or None")
        if not isinstance(self.kind, ConsequenceExecutionFeedbackKind):
            raise TypeError("kind must be a ConsequenceExecutionFeedbackKind member")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")
        if not isinstance(self.authorization_granted, bool):
            raise TypeError("authorization_granted must be a bool")
        if any(not isinstance(ref, str) or not ref.strip() for ref in self.evidence_refs):
            raise TypeError("evidence_refs must contain non-empty strings")
        if any(not isinstance(ref, str) or not ref.strip() for ref in self.verification_refs):
            raise TypeError("verification_refs must contain non-empty strings")
        if self.reason is not None and not isinstance(self.reason, str):
            raise TypeError("reason must be a string or None")

        if self.kind is ConsequenceExecutionFeedbackKind.SUCCESS:
            if self.execution_id is None:
                raise ValueError("success feedback requires execution identity")
            if self.reason is not None:
                raise ValueError("success feedback cannot contain a reason")
        elif self.kind is ConsequenceExecutionFeedbackKind.FAILURE:
            if self.execution_id is None:
                raise ValueError("failure feedback requires execution identity")
            if self.reason is None or not self.reason.strip():
                raise ValueError("failure feedback requires a reason")
        elif self.kind is ConsequenceExecutionFeedbackKind.NOT_EXECUTED:
            if self.execution_id is not None:
                raise ValueError("not-executed feedback cannot contain execution identity")
            if self.reason is None or not self.reason.strip():
                raise ValueError("not-executed feedback requires a reason")

        object.__setattr__(self, "payload", _freeze(self.payload))

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_execution_feedback_id": self.feedback_id,
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
            "consequence_feedback_kind": self.kind.value,
            "payload": dict(self.payload),
            "authorization_granted": self.authorization_granted,
            "evidence_refs": self.evidence_refs,
            "verification_refs": self.verification_refs,
            "reason": self.reason,
            "feedback_observed": True,
            "learning_decision_required": False,
            "learning_write_requested": False,
            "memory_mutated": False,
            "retry_requested": False,
            "authority_granted": False,
            "execution_requested": False,
            "revocation_requested": False,
        }


class ConsequenceExecutionFeedbackService:
    """Convert one M35 observed outcome into inert feedback evidence."""

    def evaluate(self, outcome: ConsequenceExecutionOutcome) -> ConsequenceExecutionFeedback:
        if not isinstance(outcome, ConsequenceExecutionOutcome):
            raise TypeError("outcome must be a ConsequenceExecutionOutcome")

        if outcome.status is ConsequenceExecutionOutcomeStatus.COMPLETED_SUCCESS:
            kind = ConsequenceExecutionFeedbackKind.SUCCESS
            payload = self._success_payload(outcome)
            reason = None
        elif outcome.status is ConsequenceExecutionOutcomeStatus.COMPLETED_FAILURE:
            kind = ConsequenceExecutionFeedbackKind.FAILURE
            payload = self._failure_payload(outcome)
            reason = outcome.reason
        else:
            kind = ConsequenceExecutionFeedbackKind.NOT_EXECUTED
            payload = {"execution_result": None}
            reason = outcome.reason

        return ConsequenceExecutionFeedback(
            feedback_id=self._feedback_id(outcome, kind, payload),
            outcome_id=outcome.outcome_id,
            attempt_id=outcome.attempt_id,
            execution_id=outcome.execution_id,
            preparation_id=outcome.preparation_id,
            authorization_id=outcome.authorization_id,
            handoff_id=outcome.handoff_id,
            claim_id=outcome.claim_id,
            task_id=outcome.task_id,
            consequence_id=outcome.consequence_id,
            tool_name=outcome.tool_name,
            invocation_id=outcome.invocation_id,
            kind=kind,
            payload=payload,
            authorization_granted=outcome.authorization_granted,
            evidence_refs=outcome.evidence_refs,
            verification_refs=outcome.verification_refs,
            reason=reason,
        )

    @staticmethod
    def _success_payload(outcome: ConsequenceExecutionOutcome) -> dict[str, Any]:
        result = outcome.execution_result
        return {
            "execution_outcome_status": outcome.status.value,
            "result": result.content if result is not None else None,
            "result_metadata": dict(result.metadata) if result is not None else {},
        }

    @staticmethod
    def _failure_payload(outcome: ConsequenceExecutionOutcome) -> dict[str, Any]:
        result = outcome.execution_result
        return {
            "execution_outcome_status": outcome.status.value,
            "result": result.content if result is not None else None,
            "result_metadata": dict(result.metadata) if result is not None else {},
        }

    @staticmethod
    def _feedback_id(
        outcome: ConsequenceExecutionOutcome,
        kind: ConsequenceExecutionFeedbackKind,
        payload: Mapping[str, Any],
    ) -> str:
        encoded = json.dumps(
            {
                "outcome_id": outcome.outcome_id,
                "kind": kind.value,
                "payload": payload,
                "reason": outcome.reason,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"consequence-feedback-{hashlib.sha256(encoded).hexdigest()[:24]}"


__all__ = [
    "ConsequenceExecutionFeedback",
    "ConsequenceExecutionFeedbackKind",
    "ConsequenceExecutionFeedbackService",
]
