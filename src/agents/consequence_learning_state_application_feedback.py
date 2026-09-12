"""M48 boundary for creating feedback from an evaluated learning-state application."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

from src.agents.consequence_learning_state_application_observation_evaluation import (
    ConsequenceLearningStateApplicationObservationEvaluation,
    ConsequenceLearningStateApplicationObservationEvaluationStatus,
)


@dataclass(frozen=True)
class ConsequenceLearningStateApplicationFeedback:
    """Immutable downstream feedback derived from one M47 evaluation."""

    feedback_id: str
    evaluation_id: str
    observation_id: str
    verification_id: str
    application_id: str
    applied_record_id: str
    status: str
    feedback: str
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("feedback_id", self.feedback_id),
            ("evaluation_id", self.evaluation_id),
            ("observation_id", self.observation_id),
            ("verification_id", self.verification_id),
            ("application_id", self.application_id),
            ("applied_record_id", self.applied_record_id),
            ("status", self.status),
            ("feedback", self.feedback),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.status != ConsequenceLearningStateApplicationObservationEvaluationStatus.OBSERVED_APPLIED:
            raise ValueError("unsupported application-feedback status")

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_learning_state_application_feedback_id": self.feedback_id,
            "consequence_learning_state_application_observation_evaluation_id": self.evaluation_id,
            "consequence_learning_state_application_observation_id": self.observation_id,
            "consequence_learning_state_application_verification_id": self.verification_id,
            "consequence_learning_state_application_id": self.application_id,
            "consequence_learning_state_applied_record_id": self.applied_record_id,
            "consequence_learning_state_application_feedback_status": self.status,
            "consequence_learning_state_application_feedback": self.feedback,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "reason": self.reason,
        }


class ConsequenceLearningStateApplicationFeedbackService:
    """Create feedback from exactly one M47 evaluation without granting authority."""

    def create(
        self,
        evaluation: ConsequenceLearningStateApplicationObservationEvaluation,
    ) -> ConsequenceLearningStateApplicationFeedback:
        if not isinstance(evaluation, ConsequenceLearningStateApplicationObservationEvaluation):
            raise TypeError(
                "evaluation must be a ConsequenceLearningStateApplicationObservationEvaluation"
            )
        if evaluation.status != ConsequenceLearningStateApplicationObservationEvaluationStatus.OBSERVED_APPLIED:
            raise ValueError("application feedback requires an observed-applied evaluation")
        return ConsequenceLearningStateApplicationFeedback(
            feedback_id=self._feedback_id(
                evaluation.evaluation_id,
                evaluation.observation_id,
                evaluation.application_id,
                evaluation.applied_record_id,
            ),
            evaluation_id=evaluation.evaluation_id,
            observation_id=evaluation.observation_id,
            verification_id=evaluation.verification_id,
            application_id=evaluation.application_id,
            applied_record_id=evaluation.applied_record_id,
            status=evaluation.status,
            feedback="observed applied learning state is available as downstream feedback for later evaluation without granting authority",
            reason="M47 application-observation evaluation admitted as feedback without reinterpretation or mutation",
        )

    @staticmethod
    def _feedback_id(
        evaluation_id: str,
        observation_id: str,
        application_id: str,
        applied_record_id: str,
    ) -> str:
        source = f"{evaluation_id}:{observation_id}:{application_id}:{applied_record_id}".encode("utf-8")
        return f"consequence-learning-state-application-feedback-{hashlib.sha256(source).hexdigest()[:24]}"


__all__ = [
    "ConsequenceLearningStateApplicationFeedback",
    "ConsequenceLearningStateApplicationFeedbackService",
]
