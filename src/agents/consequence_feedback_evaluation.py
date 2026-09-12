"""M37 bridge from consequence feedback into inert evaluation signals."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from src.agents.consequence_execution_feedback import (
    ConsequenceExecutionFeedback,
    ConsequenceExecutionFeedbackKind,
)


class ConsequenceFeedbackEvaluationSignal(str, Enum):
    """Classification produced by evaluating one observed feedback event."""

    SUCCESS_SIGNAL = "SUCCESS_SIGNAL"
    FAILURE_SIGNAL = "FAILURE_SIGNAL"
    NOT_EXECUTED_SIGNAL = "NOT_EXECUTED_SIGNAL"


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
class ConsequenceFeedbackEvaluation:
    """Immutable evaluation signal preserving complete consequence provenance."""

    evaluation_id: str
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
    signal: ConsequenceFeedbackEvaluationSignal
    confidence: float
    evidence: Mapping[str, Any]
    authorization_granted: bool
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("evaluation_id", self.evaluation_id),
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
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.execution_id is not None and (not isinstance(self.execution_id, str) or not self.execution_id.strip()):
            raise ValueError("execution_id must be a non-empty string or None")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise TypeError("invocation_id must be a string or None")
        if not isinstance(self.signal, ConsequenceFeedbackEvaluationSignal):
            raise TypeError("signal must be a ConsequenceFeedbackEvaluationSignal member")
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise TypeError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.evidence, Mapping):
            raise TypeError("evidence must be a mapping")
        if not isinstance(self.authorization_granted, bool):
            raise TypeError("authorization_granted must be a bool")

        if self.signal is ConsequenceFeedbackEvaluationSignal.NOT_EXECUTED_SIGNAL and self.execution_id is not None:
            raise ValueError("not-executed evaluation cannot contain execution identity")
        if self.signal is not ConsequenceFeedbackEvaluationSignal.NOT_EXECUTED_SIGNAL and self.execution_id is None:
            raise ValueError("executed evaluation requires execution identity")

        object.__setattr__(self, "evidence", _freeze(self.evidence))

    def to_context(self) -> dict[str, object]:
        return {
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
            "consequence_feedback_evaluation_signal": self.signal.value,
            "confidence": float(self.confidence),
            "evidence": dict(self.evidence),
            "authorization_granted": False,
            "authority_granted": False,
            "evaluation_observed": True,
            "learning_decision_required": True,
            "learning_write_requested": False,
            "memory_mutated": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "reason": self.reason,
        }


class ConsequenceFeedbackEvaluationService:
    """Evaluate one M36 feedback event into an inert signal."""

    _DEFAULT_CONFIDENCE = 0.5

    def evaluate(self, feedback: ConsequenceExecutionFeedback) -> ConsequenceFeedbackEvaluation:
        if not isinstance(feedback, ConsequenceExecutionFeedback):
            raise TypeError("feedback must be a ConsequenceExecutionFeedback")

        mapping = {
            ConsequenceExecutionFeedbackKind.SUCCESS: (
                ConsequenceFeedbackEvaluationSignal.SUCCESS_SIGNAL,
                "successful consequence execution provides an observed positive signal",
            ),
            ConsequenceExecutionFeedbackKind.FAILURE: (
                ConsequenceFeedbackEvaluationSignal.FAILURE_SIGNAL,
                "failed consequence execution provides an observed negative signal requiring a later decision",
            ),
            ConsequenceExecutionFeedbackKind.NOT_EXECUTED: (
                ConsequenceFeedbackEvaluationSignal.NOT_EXECUTED_SIGNAL,
                "not-executed consequence provides an operational signal requiring a later decision",
            ),
        }
        signal, reason = mapping[feedback.kind]
        evidence = {
            "feedback_kind": feedback.kind.value,
            "payload": dict(feedback.payload),
            "feedback_reason": feedback.reason,
        }

        return ConsequenceFeedbackEvaluation(
            evaluation_id=self._evaluation_id(feedback, signal, evidence),
            feedback_id=feedback.feedback_id,
            outcome_id=feedback.outcome_id,
            attempt_id=feedback.attempt_id,
            execution_id=feedback.execution_id,
            preparation_id=feedback.preparation_id,
            authorization_id=feedback.authorization_id,
            handoff_id=feedback.handoff_id,
            claim_id=feedback.claim_id,
            task_id=feedback.task_id,
            consequence_id=feedback.consequence_id,
            tool_name=feedback.tool_name,
            invocation_id=feedback.invocation_id,
            signal=signal,
            confidence=self._DEFAULT_CONFIDENCE,
            evidence=evidence,
            authorization_granted=feedback.authorization_granted,
            reason=reason,
        )

    @staticmethod
    def _evaluation_id(
        feedback: ConsequenceExecutionFeedback,
        signal: ConsequenceFeedbackEvaluationSignal,
        evidence: Mapping[str, Any],
    ) -> str:
        payload = json.dumps(
            {
                "feedback_id": feedback.feedback_id,
                "outcome_id": feedback.outcome_id,
                "signal": signal.value,
                "evidence": evidence,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"consequence-feedback-evaluation-{hashlib.sha256(payload).hexdigest()[:24]}"


__all__ = [
    "ConsequenceFeedbackEvaluation",
    "ConsequenceFeedbackEvaluationService",
    "ConsequenceFeedbackEvaluationSignal",
]
