"""M43 boundary for requesting later application of consumed learning state."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any, Mapping

from src.agents.consequence_learning_state_consumption import ConsequenceLearningStateConsumption


@dataclass(frozen=True)
class ConsequenceLearningStateApplicationRequest:
    """Immutable request for a later learning-state application stage."""

    application_request_id: str
    consumption_id: str
    request_id: str
    record_id: str
    verification_id: str
    payload: Mapping[str, Any]
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("application_request_id", self.application_request_id),
            ("consumption_id", self.consumption_id),
            ("request_id", self.request_id),
            ("record_id", self.record_id),
            ("verification_id", self.verification_id),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_learning_state_application_request_id": self.application_request_id,
            "consequence_learning_state_consumption_id": self.consumption_id,
            "consequence_learning_write_request_id": self.request_id,
            "consequence_learning_persistence_record_id": self.record_id,
            "consequence_learning_persistence_verification_id": self.verification_id,
            "learning_payload": dict(self.payload),
            "learning_state_consumed": True,
            "learning_state_application_requested": True,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "reason": self.reason,
        }


class ConsequenceLearningStateApplicationRequestService:
    """Create an inert application request only from consumed learning state."""

    def create(self, consumption: ConsequenceLearningStateConsumption) -> ConsequenceLearningStateApplicationRequest:
        if not isinstance(consumption, ConsequenceLearningStateConsumption):
            raise TypeError("consumption must be a ConsequenceLearningStateConsumption")
        return ConsequenceLearningStateApplicationRequest(
            application_request_id=self._application_request_id(
                consumption.consumption_id,
                consumption.request_id,
                consumption.record_id,
                consumption.source_verification_id,
            ),
            consumption_id=consumption.consumption_id,
            request_id=consumption.request_id,
            record_id=consumption.record_id,
            verification_id=consumption.source_verification_id,
            payload=consumption.payload,
            reason="consumed verified learning state admitted as an inert application request; no mutation performed",
        )

    @staticmethod
    def _application_request_id(consumption_id: str, request_id: str, record_id: str, verification_id: str) -> str:
        source = f"{consumption_id}:{request_id}:{record_id}:{verification_id}".encode("utf-8")
        return f"consequence-learning-state-application-request-{hashlib.sha256(source).hexdigest()[:24]}"


__all__ = [
    "ConsequenceLearningStateApplicationRequest",
    "ConsequenceLearningStateApplicationRequestService",
]
