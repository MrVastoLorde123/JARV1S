"""M46 boundary for observing independently verified applied learning state."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

from src.agents.consequence_learning_state_application_verification import (
    ConsequenceLearningStateApplicationVerification,
)


@dataclass(frozen=True)
class ConsequenceLearningStateApplicationObservation:
    """Immutable admission of a verified applied-learning-state observation."""

    observation_id: str
    verification_id: str
    application_id: str
    application_request_id: str
    request_id: str
    applied_record_id: str
    observed: bool
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("observation_id", self.observation_id),
            ("verification_id", self.verification_id),
            ("application_id", self.application_id),
            ("application_request_id", self.application_request_id),
            ("request_id", self.request_id),
            ("applied_record_id", self.applied_record_id),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if not isinstance(self.observed, bool):
            raise TypeError("observed must be a bool")
        if not self.observed:
            raise ValueError("application observation requires observed=True")

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_learning_state_application_observation_id": self.observation_id,
            "consequence_learning_state_application_verification_id": self.verification_id,
            "consequence_learning_state_application_id": self.application_id,
            "consequence_learning_state_application_request_id": self.application_request_id,
            "consequence_learning_write_request_id": self.request_id,
            "consequence_learning_state_applied_record_id": self.applied_record_id,
            "learning_state_application_verified": True,
            "learning_state_application_observed": self.observed,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "reason": self.reason,
        }


class ConsequenceLearningStateApplicationObservationService:
    """Admit only successful M45 verification into downstream observation."""

    def observe(
        self,
        verification: ConsequenceLearningStateApplicationVerification,
    ) -> ConsequenceLearningStateApplicationObservation:
        if not isinstance(verification, ConsequenceLearningStateApplicationVerification):
            raise TypeError("verification must be a ConsequenceLearningStateApplicationVerification")
        if not verification.verified:
            raise ValueError("application observation requires verified application state")
        return ConsequenceLearningStateApplicationObservation(
            observation_id=self._observation_id(
                verification.verification_id,
                verification.application_id,
                verification.applied_record_id,
            ),
            verification_id=verification.verification_id,
            application_id=verification.application_id,
            application_request_id=verification.application_request_id,
            request_id=verification.request_id,
            applied_record_id=verification.applied_record_id,
            observed=True,
            reason="verified applied learning state admitted as a downstream observation without granting authority",
        )

    @staticmethod
    def _observation_id(verification_id: str, application_id: str, applied_record_id: str) -> str:
        source = f"{verification_id}:{application_id}:{applied_record_id}".encode("utf-8")
        return f"consequence-learning-state-application-observation-{hashlib.sha256(source).hexdigest()[:24]}"


__all__ = [
    "ConsequenceLearningStateApplicationObservation",
    "ConsequenceLearningStateApplicationObservationService",
]
