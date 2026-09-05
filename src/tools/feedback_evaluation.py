"""Feedback evaluation boundary before any learning decision or write.

This module interprets inert execution feedback into a structured learning
candidate. It does not persist memory, write learning state, authorize
execution, retry requests, or treat feedback as unquestionable truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .execution_feedback import ExecutionFeedbackEvent, FeedbackKind


class FeedbackEvaluationError(ValueError):
    """Raised when the feedback-evaluation contract is invalid."""


class LearningSignalKind(str, Enum):
    """Classified signal for a later learning decision layer."""

    SUCCESS_SIGNAL = "success_signal"
    TOOL_FAILURE_SIGNAL = "tool_failure_signal"
    EXECUTOR_FAILURE_SIGNAL = "executor_failure_signal"


def _freeze(value: Any) -> Any:
    """Recursively freeze common mutable containers into immutable snapshots."""
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
class LearningCandidate:
    """Immutable learning candidate derived from one feedback event."""

    candidate_id: str
    feedback_id: str
    execution_id: str
    handoff_id: str
    tool_name: str
    signal: LearningSignalKind
    confidence: float
    evidence: Mapping[str, Any]
    provenance: Mapping[str, str]
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("candidate_id", self.candidate_id),
            ("feedback_id", self.feedback_id),
            ("execution_id", self.execution_id),
            ("handoff_id", self.handoff_id),
            ("tool_name", self.tool_name),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise FeedbackEvaluationError(f"{field_name} must be a non-empty string")
        if not isinstance(self.signal, LearningSignalKind):
            raise FeedbackEvaluationError("signal must be a LearningSignalKind member")
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise FeedbackEvaluationError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise FeedbackEvaluationError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.evidence, Mapping):
            raise FeedbackEvaluationError("evidence must be a mapping")
        if not isinstance(self.provenance, Mapping):
            raise FeedbackEvaluationError("provenance must be a mapping")
        if not all(
            isinstance(key, str) and key.strip()
            and isinstance(value, str) and value.strip()
            for key, value in self.provenance.items()
        ):
            raise FeedbackEvaluationError(
                "provenance must contain non-empty string keys and values"
            )

        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_candidate_id": self.candidate_id,
            "feedback_id": self.feedback_id,
            "execution_id": self.execution_id,
            "handoff_id": self.handoff_id,
            "tool_name": self.tool_name,
            "learning_signal": self.signal.value,
            "confidence": float(self.confidence),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
            "learning_candidate_reason": self.reason,
            "learning_candidate": True,
            "learning_decision_required": True,
            "learning_written": False,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class FeedbackEvaluationService:
    """Evaluate feedback into an inert learning candidate."""

    _DEFAULT_CONFIDENCE = 0.5

    def evaluate(self, feedback: ExecutionFeedbackEvent) -> LearningCandidate:
        if not isinstance(feedback, ExecutionFeedbackEvent):
            raise TypeError("feedback must be an ExecutionFeedbackEvent")

        if feedback.kind is FeedbackKind.SUCCESS:
            signal = LearningSignalKind.SUCCESS_SIGNAL
            reason = "successful execution provides an observed positive signal"
        elif feedback.kind is FeedbackKind.TOOL_FAILURE:
            signal = LearningSignalKind.TOOL_FAILURE_SIGNAL
            reason = "tool failure provides an observed negative signal requiring evaluation"
        else:
            signal = LearningSignalKind.EXECUTOR_FAILURE_SIGNAL
            reason = "executor failure provides an operational signal requiring evaluation"

        evidence = {
            "feedback_kind": feedback.kind.value,
            "payload": dict(feedback.payload),
            "feedback_reason": feedback.reason,
        }
        provenance = {
            "source": "execution_feedback",
            "feedback_id": feedback.feedback_id,
            "execution_id": feedback.execution_id,
            "handoff_id": feedback.handoff_id,
        }
        candidate_id = self._candidate_id(
            feedback.feedback_id,
            feedback.execution_id,
            signal,
            evidence,
        )

        return LearningCandidate(
            candidate_id=candidate_id,
            feedback_id=feedback.feedback_id,
            execution_id=feedback.execution_id,
            handoff_id=feedback.handoff_id,
            tool_name=feedback.tool_name,
            signal=signal,
            confidence=self._DEFAULT_CONFIDENCE,
            evidence=evidence,
            provenance=provenance,
            reason=reason,
        )

    @staticmethod
    def _candidate_id(
        feedback_id: str,
        execution_id: str,
        signal: LearningSignalKind,
        evidence: Mapping[str, Any],
    ) -> str:
        payload = json.dumps(
            {
                "feedback_id": feedback_id,
                "execution_id": execution_id,
                "signal": signal.value,
                "evidence": evidence,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"learn-candidate-{hashlib.sha256(payload).hexdigest()[:24]}"
