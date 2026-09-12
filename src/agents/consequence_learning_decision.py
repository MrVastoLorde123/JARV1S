"""M38 boundary from feedback evaluation into inert learning eligibility decisions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from src.agents.consequence_feedback_evaluation import (
    ConsequenceFeedbackEvaluation,
    ConsequenceFeedbackEvaluationSignal,
)


class ConsequenceLearningDecisionStatus(str, Enum):
    """Deterministic classification for later learning-write consideration."""

    LEARNING_ELIGIBLE = "LEARNING_ELIGIBLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


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
class ConsequenceLearningDecision:
    """Immutable learning eligibility decision; no learning write occurs here."""

    decision_id: str
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
    status: ConsequenceLearningDecisionStatus
    confidence: float
    evidence: Mapping[str, Any]
    authorization_granted: bool
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("decision_id", self.decision_id),
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
        if not isinstance(self.status, ConsequenceLearningDecisionStatus):
            raise TypeError("status must be a ConsequenceLearningDecisionStatus member")
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise TypeError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.evidence, Mapping):
            raise TypeError("evidence must be a mapping")
        if not isinstance(self.authorization_granted, bool):
            raise TypeError("authorization_granted must be a bool")
        if self.status is ConsequenceLearningDecisionStatus.NOT_ELIGIBLE and self.execution_id is not None:
            raise ValueError("not-eligible decision for a not-executed signal cannot invent execution identity")
        object.__setattr__(self, "evidence", _freeze(self.evidence))

    @property
    def eligible(self) -> bool:
        return self.status is ConsequenceLearningDecisionStatus.LEARNING_ELIGIBLE

    @property
    def requires_review(self) -> bool:
        return self.status is ConsequenceLearningDecisionStatus.REVIEW_REQUIRED

    def to_context(self) -> dict[str, object]:
        return {
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
            "consequence_learning_decision_status": self.status.value,
            "learning_eligible": self.eligible,
            "learning_review_required": self.requires_review,
            "confidence": float(self.confidence),
            "evidence": dict(self.evidence),
            "authorization_granted": False,
            "authority_granted": False,
            "learning_decision_made": True,
            "learning_write_requested": False,
            "learning_written": False,
            "memory_mutated": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "reason": self.reason,
        }


class ConsequenceLearningDecisionService:
    """Convert one M37 evaluation into an inert learning decision."""

    def decide(self, evaluation: ConsequenceFeedbackEvaluation) -> ConsequenceLearningDecision:
        if not isinstance(evaluation, ConsequenceFeedbackEvaluation):
            raise TypeError("evaluation must be a ConsequenceFeedbackEvaluation")

        mapping = {
            ConsequenceFeedbackEvaluationSignal.SUCCESS_SIGNAL: (
                ConsequenceLearningDecisionStatus.LEARNING_ELIGIBLE,
                "successful execution is eligible for a later learning-write decision",
            ),
            ConsequenceFeedbackEvaluationSignal.FAILURE_SIGNAL: (
                ConsequenceLearningDecisionStatus.REVIEW_REQUIRED,
                "failed execution requires review before any learning write",
            ),
            ConsequenceFeedbackEvaluationSignal.NOT_EXECUTED_SIGNAL: (
                ConsequenceLearningDecisionStatus.NOT_ELIGIBLE,
                "not-executed consequence is not eligible for direct learning write",
            ),
        }
        status, reason = mapping[evaluation.signal]
        evidence = {
            "evaluation_signal": evaluation.signal.value,
            "evaluation_confidence": float(evaluation.confidence),
            "evaluation_evidence": dict(evaluation.evidence),
            "evaluation_reason": evaluation.reason,
        }

        return ConsequenceLearningDecision(
            decision_id=self._decision_id(evaluation, status, evidence),
            evaluation_id=evaluation.evaluation_id,
            feedback_id=evaluation.feedback_id,
            outcome_id=evaluation.outcome_id,
            attempt_id=evaluation.attempt_id,
            execution_id=evaluation.execution_id,
            preparation_id=evaluation.preparation_id,
            authorization_id=evaluation.authorization_id,
            handoff_id=evaluation.handoff_id,
            claim_id=evaluation.claim_id,
            task_id=evaluation.task_id,
            consequence_id=evaluation.consequence_id,
            tool_name=evaluation.tool_name,
            invocation_id=evaluation.invocation_id,
            status=status,
            confidence=float(evaluation.confidence),
            evidence=evidence,
            authorization_granted=evaluation.authorization_granted,
            reason=reason,
        )

    @staticmethod
    def _decision_id(
        evaluation: ConsequenceFeedbackEvaluation,
        status: ConsequenceLearningDecisionStatus,
        evidence: Mapping[str, Any],
    ) -> str:
        payload = json.dumps(
            {
                "evaluation_id": evaluation.evaluation_id,
                "feedback_id": evaluation.feedback_id,
                "status": status.value,
                "evidence": evidence,
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"consequence-learning-decision-{hashlib.sha256(payload).hexdigest()[:24]}"


__all__ = [
    "ConsequenceLearningDecision",
    "ConsequenceLearningDecisionService",
    "ConsequenceLearningDecisionStatus",
]
