"""M42 boundary for consuming independently verified learning state."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any, Mapping

from src.agents.consequence_learning_state_persistence_verification import (
    ConsequenceLearningStatePersistenceVerification,
)
from src.agents.consequence_learning_write_request import ConsequenceLearningWriteRequest


@dataclass(frozen=True)
class ConsequenceLearningStateConsumption:
    """Immutable admission of a verified learning-state payload for downstream use."""

    consumption_id: str
    request_id: str
    record_id: str
    source_verification_id: str
    payload: Mapping[str, Any]
    consumed: bool
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("consumption_id", self.consumption_id),
            ("request_id", self.request_id),
            ("record_id", self.record_id),
            ("source_verification_id", self.source_verification_id),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")
        if not isinstance(self.consumed, bool):
            raise TypeError("consumed must be a bool")
        if not self.consumed:
            raise ValueError("consumption result must represent successful consumption")

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_learning_state_consumption_id": self.consumption_id,
            "consequence_learning_write_request_id": self.request_id,
            "consequence_learning_persistence_record_id": self.record_id,
            "consequence_learning_persistence_verification_id": self.source_verification_id,
            "learning_state_consumed": self.consumed,
            "learning_payload": dict(self.payload),
            "learning_write_requested": True,
            "learning_written": True,
            "learning_write_persisted": True,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "reason": self.reason,
        }


class ConsequenceLearningStateConsumptionService:
    """Admit only learning state backed by a successful M41 verification."""

    def consume(
        self,
        request: ConsequenceLearningWriteRequest,
        verification: ConsequenceLearningStatePersistenceVerification,
    ) -> ConsequenceLearningStateConsumption:
        if not isinstance(request, ConsequenceLearningWriteRequest):
            raise TypeError("request must be a ConsequenceLearningWriteRequest")
        if not isinstance(verification, ConsequenceLearningStatePersistenceVerification):
            raise TypeError("verification must be a ConsequenceLearningStatePersistenceVerification")
        if not verification.verified:
            raise ValueError("learning-state consumption requires verified persistence")
        if request.request_id != verification.request_id:
            raise ValueError("verification does not belong to request")
        if not verification.record_id.strip():
            raise ValueError("verification record identity is required")
        payload = dict(request.learning_payload)
        return ConsequenceLearningStateConsumption(
            consumption_id=self._consumption_id(
                request.request_id,
                verification.record_id,
                verification.verification_id,
            ),
            request_id=request.request_id,
            record_id=verification.record_id,
            source_verification_id=verification.verification_id,
            payload=payload,
            consumed=True,
            reason="verified persisted learning state admitted for downstream consumption without granting authority",
        )

    @staticmethod
    def _consumption_id(request_id: str, record_id: str, verification_id: str) -> str:
        source = f"{request_id}:{record_id}:{verification_id}".encode("utf-8")
        return f"consequence-learning-state-consumption-{hashlib.sha256(source).hexdigest()[:24]}"


__all__ = [
    "ConsequenceLearningStateConsumption",
    "ConsequenceLearningStateConsumptionService",
]
