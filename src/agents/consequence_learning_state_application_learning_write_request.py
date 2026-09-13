"""M51 boundary from application-learning eligibility into an inert write request."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from src.agents.consequence_learning_state_application_feedback_learning_decision import (
    ConsequenceLearningStateApplicationFeedbackLearningDecision,
    ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus,
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
class ConsequenceLearningStateApplicationLearningWriteRequest:
    """Immutable request for later application-learning persistence; not persisted here."""

    request_id: str
    decision_id: str
    evaluation_id: str
    feedback_id: str
    observation_evaluation_id: str
    observation_id: str
    verification_id: str
    application_id: str
    applied_record_id: str
    signal: str
    confidence: float
    learning_payload: Mapping[str, Any]
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("request_id", self.request_id),
            ("decision_id", self.decision_id),
            ("evaluation_id", self.evaluation_id),
            ("feedback_id", self.feedback_id),
            ("observation_evaluation_id", self.observation_evaluation_id),
            ("observation_id", self.observation_id),
            ("verification_id", self.verification_id),
            ("application_id", self.application_id),
            ("applied_record_id", self.applied_record_id),
            ("signal", self.signal),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise TypeError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.learning_payload, Mapping):
            raise TypeError("learning_payload must be a mapping")
        object.__setattr__(self, "learning_payload", _freeze(self.learning_payload))

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_learning_state_application_learning_write_request_id": self.request_id,
            "consequence_learning_state_application_feedback_learning_decision_id": self.decision_id,
            "consequence_learning_state_application_feedback_evaluation_id": self.evaluation_id,
            "consequence_learning_state_application_feedback_id": self.feedback_id,
            "consequence_learning_state_application_observation_evaluation_id": self.observation_evaluation_id,
            "consequence_learning_state_application_observation_id": self.observation_id,
            "consequence_learning_state_application_verification_id": self.verification_id,
            "consequence_learning_state_application_id": self.application_id,
            "consequence_learning_state_applied_record_id": self.applied_record_id,
            "consequence_learning_state_application_feedback_evaluation_signal": self.signal,
            "confidence": float(self.confidence),
            "learning_payload": dict(self.learning_payload),
            "application_learning_write_requested": True,
            "application_learning_written": False,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "reason": self.reason,
        }


class ConsequenceLearningStateApplicationLearningWriteRequestService:
    """Convert only an eligible M50 decision into an inert application-learning write request."""

    def create(
        self,
        decision: ConsequenceLearningStateApplicationFeedbackLearningDecision,
    ) -> ConsequenceLearningStateApplicationLearningWriteRequest:
        if not isinstance(decision, ConsequenceLearningStateApplicationFeedbackLearningDecision):
            raise TypeError(
                "decision must be a ConsequenceLearningStateApplicationFeedbackLearningDecision"
            )
        if decision.status is not ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus.LEARNING_ELIGIBLE:
            raise ValueError(
                "application-learning write request requires a LEARNING_ELIGIBLE decision"
            )

        payload = {
            "decision_status": decision.status.value,
            "evaluation_signal": decision.signal.value,
            "confidence": float(decision.confidence),
            "decision_id": decision.decision_id,
            "evaluation_id": decision.evaluation_id,
            "feedback_id": decision.feedback_id,
        }
        return ConsequenceLearningStateApplicationLearningWriteRequest(
            request_id=self._request_id(decision, payload),
            decision_id=decision.decision_id,
            evaluation_id=decision.evaluation_id,
            feedback_id=decision.feedback_id,
            observation_evaluation_id=decision.observation_evaluation_id,
            observation_id=decision.observation_id,
            verification_id=decision.verification_id,
            application_id=decision.application_id,
            applied_record_id=decision.applied_record_id,
            signal=decision.signal.value,
            confidence=float(decision.confidence),
            learning_payload=payload,
            reason="application-learning eligibility permits a later persistence boundary to consider this write request",
        )

    @staticmethod
    def _request_id(
        decision: ConsequenceLearningStateApplicationFeedbackLearningDecision,
        payload: Mapping[str, Any],
    ) -> str:
        encoded = json.dumps(
            {
                "decision_id": decision.decision_id,
                "evaluation_id": decision.evaluation_id,
                "feedback_id": decision.feedback_id,
                "payload": payload,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"consequence-learning-state-application-learning-write-request-{hashlib.sha256(encoded).hexdigest()[:24]}"


__all__ = [
    "ConsequenceLearningStateApplicationLearningWriteRequest",
    "ConsequenceLearningStateApplicationLearningWriteRequestService",
]
