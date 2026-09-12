"""M39 boundary from learning eligibility into an inert learning-write request."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from src.agents.consequence_learning_decision import (
    ConsequenceLearningDecision,
    ConsequenceLearningDecisionStatus,
)


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
class ConsequenceLearningWriteRequest:
    """Immutable request for a later learning-state writer; not persisted here."""

    request_id: str
    decision_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    attempt_id: str
    execution_id: str
    preparation_id: str
    authorization_id: str
    handoff_id: str
    claim_id: str
    task_id: str
    consequence_id: str
    tool_name: str
    invocation_id: str | None
    confidence: float
    learning_payload: Mapping[str, Any]
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("request_id", self.request_id),
            ("decision_id", self.decision_id),
            ("evaluation_id", self.evaluation_id),
            ("feedback_id", self.feedback_id),
            ("outcome_id", self.outcome_id),
            ("attempt_id", self.attempt_id),
            ("execution_id", self.execution_id),
            ("preparation_id", self.preparation_id),
            ("authorization_id", self.authorization_id),
            ("handoff_id", self.handoff_id),
            ("claim_id", self.claim_id),
            ("task_id", self.task_id),
            ("consequence_id", self.consequence_id),
            ("tool_name", self.tool_name),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise TypeError("invocation_id must be a string or None")
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise TypeError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.learning_payload, Mapping):
            raise TypeError("learning_payload must be a mapping")
        object.__setattr__(self, "learning_payload", _freeze(self.learning_payload))

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_learning_write_request_id": self.request_id,
            "consequence_learning_decision_id": self.decision_id,
            "consequence_feedback_evaluation_id": self.evaluation_id,
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
            "confidence": float(self.confidence),
            "learning_payload": dict(self.learning_payload),
            "learning_write_requested": True,
            "learning_written": False,
            "learning_write_persisted": False,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "reason": self.reason,
        }


class ConsequenceLearningWriteRequestService:
    """Convert only an eligible M38 learning decision into a write request."""

    def create(self, decision: ConsequenceLearningDecision) -> ConsequenceLearningWriteRequest:
        if not isinstance(decision, ConsequenceLearningDecision):
            raise TypeError("decision must be a ConsequenceLearningDecision")
        if decision.status is not ConsequenceLearningDecisionStatus.LEARNING_ELIGIBLE:
            raise ValueError(
                "learning write request requires a LEARNING_ELIGIBLE decision"
            )
        if decision.execution_id is None:
            raise ValueError("learning write request requires an execution identity")

        payload = {
            "decision_status": decision.status.value,
            "signal_evidence": dict(decision.evidence),
            "decision_reason": decision.reason,
        }
        return ConsequenceLearningWriteRequest(
            request_id=self._request_id(decision, payload),
            decision_id=decision.decision_id,
            evaluation_id=decision.evaluation_id,
            feedback_id=decision.feedback_id,
            outcome_id=decision.outcome_id,
            attempt_id=decision.attempt_id,
            execution_id=decision.execution_id,
            preparation_id=decision.preparation_id,
            authorization_id=decision.authorization_id,
            handoff_id=decision.handoff_id,
            claim_id=decision.claim_id,
            task_id=decision.task_id,
            consequence_id=decision.consequence_id,
            tool_name=decision.tool_name,
            invocation_id=decision.invocation_id,
            confidence=float(decision.confidence),
            learning_payload=payload,
            reason="learning eligibility permits a later learning-state writer to consider this request",
        )

    @staticmethod
    def _request_id(
        decision: ConsequenceLearningDecision,
        payload: Mapping[str, Any],
    ) -> str:
        encoded = json.dumps(
            {
                "decision_id": decision.decision_id,
                "evaluation_id": decision.evaluation_id,
                "outcome_id": decision.outcome_id,
                "payload": payload,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"consequence-learning-write-request-{hashlib.sha256(encoded).hexdigest()[:24]}"


__all__ = [
    "ConsequenceLearningWriteRequest",
    "ConsequenceLearningWriteRequestService",
]
