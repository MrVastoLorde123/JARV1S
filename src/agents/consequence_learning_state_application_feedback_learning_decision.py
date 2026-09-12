"""M50 boundary from application-feedback evaluation into inert learning decision."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json

from src.agents.consequence_learning_state_application_feedback_evaluation import (
    ConsequenceLearningStateApplicationFeedbackEvaluation,
    ConsequenceLearningStateApplicationFeedbackEvaluationSignal,
)


class ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus(str, Enum):
    """Stable classifications for later application-learning consideration."""

    LEARNING_ELIGIBLE = "LEARNING_ELIGIBLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


@dataclass(frozen=True)
class ConsequenceLearningStateApplicationFeedbackLearningDecision:
    """Immutable application-learning decision; no learning write occurs here."""

    decision_id: str
    evaluation_id: str
    feedback_id: str
    observation_evaluation_id: str
    observation_id: str
    verification_id: str
    application_id: str
    applied_record_id: str
    status: ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus
    signal: ConsequenceLearningStateApplicationFeedbackEvaluationSignal
    confidence: float
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("decision_id", self.decision_id),
            ("evaluation_id", self.evaluation_id),
            ("feedback_id", self.feedback_id),
            ("observation_evaluation_id", self.observation_evaluation_id),
            ("observation_id", self.observation_id),
            ("verification_id", self.verification_id),
            ("application_id", self.application_id),
            ("applied_record_id", self.applied_record_id),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if not isinstance(self.status, ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus):
            raise TypeError("status must be a ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus member")
        if not isinstance(self.signal, ConsequenceLearningStateApplicationFeedbackEvaluationSignal):
            raise TypeError("signal must be a ConsequenceLearningStateApplicationFeedbackEvaluationSignal member")
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise TypeError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    @property
    def eligible(self) -> bool:
        return self.status is ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus.LEARNING_ELIGIBLE

    @property
    def requires_review(self) -> bool:
        return self.status is ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus.REVIEW_REQUIRED

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_learning_state_application_feedback_learning_decision_id": self.decision_id,
            "consequence_learning_state_application_feedback_evaluation_id": self.evaluation_id,
            "consequence_learning_state_application_feedback_id": self.feedback_id,
            "consequence_learning_state_application_observation_evaluation_id": self.observation_evaluation_id,
            "consequence_learning_state_application_observation_id": self.observation_id,
            "consequence_learning_state_application_verification_id": self.verification_id,
            "consequence_learning_state_application_id": self.application_id,
            "consequence_learning_state_applied_record_id": self.applied_record_id,
            "consequence_learning_state_application_feedback_learning_decision_status": self.status.value,
            "consequence_learning_state_application_feedback_evaluation_signal": self.signal.value,
            "learning_eligible": self.eligible,
            "learning_review_required": self.requires_review,
            "confidence": float(self.confidence),
            "learning_decision_made": True,
            "application_learning_write_requested": False,
            "application_learning_written": False,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "reason": self.reason,
        }


class ConsequenceLearningStateApplicationFeedbackLearningDecisionService:
    """Classify one M49 evaluation without granting learning or execution authority."""

    def decide(
        self,
        evaluation: ConsequenceLearningStateApplicationFeedbackEvaluation,
    ) -> ConsequenceLearningStateApplicationFeedbackLearningDecision:
        if not isinstance(evaluation, ConsequenceLearningStateApplicationFeedbackEvaluation):
            raise TypeError(
                "evaluation must be a ConsequenceLearningStateApplicationFeedbackEvaluation"
            )

        mapping = {
            ConsequenceLearningStateApplicationFeedbackEvaluationSignal.APPLICATION_CONFIRMED_SIGNAL: (
                ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus.LEARNING_ELIGIBLE,
                "confirmed application feedback is eligible for later application-learning write consideration",
            ),
        }
        status, reason = mapping[evaluation.signal]
        return ConsequenceLearningStateApplicationFeedbackLearningDecision(
            decision_id=self._decision_id(evaluation, status),
            evaluation_id=evaluation.evaluation_id,
            feedback_id=evaluation.feedback_id,
            observation_evaluation_id=evaluation.observation_evaluation_id,
            observation_id=evaluation.observation_id,
            verification_id=evaluation.verification_id,
            application_id=evaluation.application_id,
            applied_record_id=evaluation.applied_record_id,
            status=status,
            signal=evaluation.signal,
            confidence=float(evaluation.confidence),
            reason=reason,
        )

    @staticmethod
    def _decision_id(
        evaluation: ConsequenceLearningStateApplicationFeedbackEvaluation,
        status: ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus,
    ) -> str:
        payload = json.dumps(
            {
                "evaluation_id": evaluation.evaluation_id,
                "feedback_id": evaluation.feedback_id,
                "signal": evaluation.signal.value,
                "status": status.value,
                "confidence": float(evaluation.confidence),
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"consequence-learning-state-application-feedback-learning-decision-{hashlib.sha256(payload).hexdigest()[:24]}"


__all__ = [
    "ConsequenceLearningStateApplicationFeedbackLearningDecision",
    "ConsequenceLearningStateApplicationFeedbackLearningDecisionService",
    "ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus",
]
