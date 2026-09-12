"""M47 boundary for evaluating an observed applied learning state."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

from src.agents.consequence_learning_state_application_observation import (
    ConsequenceLearningStateApplicationObservation,
)


class ConsequenceLearningStateApplicationObservationEvaluationStatus:
    """Stable classification values for an observed application state."""

    OBSERVED_APPLIED = "OBSERVED_APPLIED"


@dataclass(frozen=True)
class ConsequenceLearningStateApplicationObservationEvaluation:
    """Immutable evaluation of an M46 application observation."""

    evaluation_id: str
    observation_id: str
    verification_id: str
    application_id: str
    applied_record_id: str
    status: str
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("evaluation_id", self.evaluation_id),
            ("observation_id", self.observation_id),
            ("verification_id", self.verification_id),
            ("application_id", self.application_id),
            ("applied_record_id", self.applied_record_id),
            ("status", self.status),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.status != ConsequenceLearningStateApplicationObservationEvaluationStatus.OBSERVED_APPLIED:
            raise ValueError("unsupported application-observation evaluation status")

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_learning_state_application_observation_evaluation_id": self.evaluation_id,
            "consequence_learning_state_application_observation_id": self.observation_id,
            "consequence_learning_state_application_verification_id": self.verification_id,
            "consequence_learning_state_application_id": self.application_id,
            "consequence_learning_state_applied_record_id": self.applied_record_id,
            "consequence_learning_state_application_observation_evaluation_status": self.status,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "reason": self.reason,
        }


class ConsequenceLearningStateApplicationObservationEvaluationService:
    """Classify exactly one verified M46 observation without granting authority."""

    def evaluate(
        self,
        observation: ConsequenceLearningStateApplicationObservation,
    ) -> ConsequenceLearningStateApplicationObservationEvaluation:
        if not isinstance(observation, ConsequenceLearningStateApplicationObservation):
            raise TypeError("observation must be a ConsequenceLearningStateApplicationObservation")
        if not observation.observed:
            raise ValueError("application-observation evaluation requires an observed application")
        return ConsequenceLearningStateApplicationObservationEvaluation(
            evaluation_id=self._evaluation_id(
                observation.observation_id,
                observation.application_id,
                observation.applied_record_id,
            ),
            observation_id=observation.observation_id,
            verification_id=observation.verification_id,
            application_id=observation.application_id,
            applied_record_id=observation.applied_record_id,
            status=ConsequenceLearningStateApplicationObservationEvaluationStatus.OBSERVED_APPLIED,
            reason="observed applied learning state classified for downstream use without granting authority",
        )

    @staticmethod
    def _evaluation_id(observation_id: str, application_id: str, applied_record_id: str) -> str:
        source = f"{observation_id}:{application_id}:{applied_record_id}".encode("utf-8")
        return f"consequence-learning-state-application-observation-evaluation-{hashlib.sha256(source).hexdigest()[:24]}"


__all__ = [
    "ConsequenceLearningStateApplicationObservationEvaluation",
    "ConsequenceLearningStateApplicationObservationEvaluationService",
    "ConsequenceLearningStateApplicationObservationEvaluationStatus",
]
