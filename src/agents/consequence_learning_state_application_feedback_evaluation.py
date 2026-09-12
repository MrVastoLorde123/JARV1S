"""M49 boundary for evaluating post-application learning-state feedback."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib

from src.agents.consequence_learning_state_application_feedback import (
    ConsequenceLearningStateApplicationFeedback,
)


class ConsequenceLearningStateApplicationFeedbackEvaluationSignal(str, Enum):
    """Stable advisory signals for M48 application feedback."""

    APPLICATION_CONFIRMED_SIGNAL = "APPLICATION_CONFIRMED_SIGNAL"


@dataclass(frozen=True)
class ConsequenceLearningStateApplicationFeedbackEvaluation:
    """Immutable evaluation preserving the complete M48 feedback lineage."""

    evaluation_id: str
    feedback_id: str
    observation_evaluation_id: str
    observation_id: str
    verification_id: str
    application_id: str
    applied_record_id: str
    signal: ConsequenceLearningStateApplicationFeedbackEvaluationSignal
    confidence: float
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
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
        if not isinstance(self.signal, ConsequenceLearningStateApplicationFeedbackEvaluationSignal):
            raise TypeError("signal must be a ConsequenceLearningStateApplicationFeedbackEvaluationSignal member")
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise TypeError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_learning_state_application_feedback_evaluation_id": self.evaluation_id,
            "consequence_learning_state_application_feedback_id": self.feedback_id,
            "consequence_learning_state_application_observation_evaluation_id": self.observation_evaluation_id,
            "consequence_learning_state_application_observation_id": self.observation_id,
            "consequence_learning_state_application_verification_id": self.verification_id,
            "consequence_learning_state_application_id": self.application_id,
            "consequence_learning_state_applied_record_id": self.applied_record_id,
            "consequence_learning_state_application_feedback_evaluation_signal": self.signal.value,
            "confidence": float(self.confidence),
            "learning_decision_required": True,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "reason": self.reason,
        }


class ConsequenceLearningStateApplicationFeedbackEvaluationService:
    """Evaluate one M48 application feedback event without granting authority."""

    _DEFAULT_CONFIDENCE = 0.5

    def evaluate(
        self,
        feedback: ConsequenceLearningStateApplicationFeedback,
    ) -> ConsequenceLearningStateApplicationFeedbackEvaluation:
        if not isinstance(feedback, ConsequenceLearningStateApplicationFeedback):
            raise TypeError("feedback must be a ConsequenceLearningStateApplicationFeedback")
        return ConsequenceLearningStateApplicationFeedbackEvaluation(
            evaluation_id=self._evaluation_id(feedback),
            feedback_id=feedback.feedback_id,
            observation_evaluation_id=feedback.evaluation_id,
            observation_id=feedback.observation_id,
            verification_id=feedback.verification_id,
            application_id=feedback.application_id,
            applied_record_id=feedback.applied_record_id,
            signal=ConsequenceLearningStateApplicationFeedbackEvaluationSignal.APPLICATION_CONFIRMED_SIGNAL,
            confidence=self._DEFAULT_CONFIDENCE,
            reason="application feedback confirms an observed applied learning-state event for later learning decision use",
        )

    @staticmethod
    def _evaluation_id(feedback: ConsequenceLearningStateApplicationFeedback) -> str:
        source = f"{feedback.feedback_id}:{feedback.evaluation_id}:{feedback.application_id}:{feedback.applied_record_id}".encode("utf-8")
        return f"consequence-learning-state-application-feedback-evaluation-{hashlib.sha256(source).hexdigest()[:24]}"


__all__ = [
    "ConsequenceLearningStateApplicationFeedbackEvaluation",
    "ConsequenceLearningStateApplicationFeedbackEvaluationService",
    "ConsequenceLearningStateApplicationFeedbackEvaluationSignal",
]
