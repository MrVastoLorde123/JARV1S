"""M52 boundary from application-learning write request into explicit persistence."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Protocol

from src.agents.consequence_learning_state_application_learning_write_request import (
    ConsequenceLearningStateApplicationLearningWriteRequest,
)


class ConsequenceLearningStateApplicationLearningWriter(Protocol):
    """Explicit persistence authority for application-learning state."""

    def write(
        self,
        *,
        request_id: str,
        payload: Mapping[str, Any],
        provenance: Mapping[str, str],
    ) -> str:
        """Persist one application-learning request and return a stable record identifier."""
        ...


@dataclass(frozen=True)
class ConsequenceLearningStateApplicationLearningPersistenceReceipt:
    """Immutable receipt proving that the injected writer accepted the write."""

    receipt_id: str
    request_id: str
    record_id: str
    persisted: bool
    writer_result: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("receipt_id", self.receipt_id),
            ("request_id", self.request_id),
            ("record_id", self.record_id),
            ("writer_result", self.writer_result),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if not isinstance(self.persisted, bool):
            raise TypeError("persisted must be a bool")
        if not self.persisted:
            raise ValueError("a persistence receipt must represent a persisted application-learning write")

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_learning_state_application_learning_write_request_id": self.request_id,
            "consequence_learning_state_application_learning_persistence_receipt_id": self.receipt_id,
            "consequence_learning_state_application_learning_record_id": self.record_id,
            "application_learning_write_requested": True,
            "application_learning_written": True,
            "application_learning_persisted": True,
            "memory_mutated": True,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "application_learning_persistence_observed": True,
        }


class ConsequenceLearningStateApplicationLearningPersistenceService:
    """Persist exactly one M51 request through an explicitly injected writer."""

    def __init__(self, writer: ConsequenceLearningStateApplicationLearningWriter | None = None) -> None:
        self._writer = writer

    def bind(self, writer: ConsequenceLearningStateApplicationLearningWriter) -> None:
        if not hasattr(writer, "write") or not callable(writer.write):
            raise TypeError("writer must provide a callable write method")
        self._writer = writer

    def persist(
        self,
        request: ConsequenceLearningStateApplicationLearningWriteRequest,
    ) -> ConsequenceLearningStateApplicationLearningPersistenceReceipt:
        if not isinstance(request, ConsequenceLearningStateApplicationLearningWriteRequest):
            raise TypeError(
                "request must be a ConsequenceLearningStateApplicationLearningWriteRequest"
            )
        if self._writer is None:
            raise RuntimeError("application-learning writer is not bound")

        payload = dict(request.learning_payload)
        provenance = {
            "request_id": request.request_id,
            "decision_id": request.decision_id,
            "evaluation_id": request.evaluation_id,
            "feedback_id": request.feedback_id,
            "observation_evaluation_id": request.observation_evaluation_id,
            "observation_id": request.observation_id,
            "verification_id": request.verification_id,
            "application_id": request.application_id,
            "applied_record_id": request.applied_record_id,
        }
        record_id = self._writer.write(
            request_id=request.request_id,
            payload=payload,
            provenance=provenance,
        )
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError(
                "application-learning writer must return a non-empty record identifier"
            )

        return ConsequenceLearningStateApplicationLearningPersistenceReceipt(
            receipt_id=self._receipt_id(request.request_id, record_id),
            request_id=request.request_id,
            record_id=record_id,
            persisted=True,
            writer_result=record_id,
        )

    @staticmethod
    def _receipt_id(request_id: str, record_id: str) -> str:
        encoded = json.dumps(
            {"request_id": request_id, "record_id": record_id},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"consequence-learning-state-application-learning-persistence-{hashlib.sha256(encoded).hexdigest()[:24]}"


__all__ = [
    "ConsequenceLearningStateApplicationLearningPersistenceReceipt",
    "ConsequenceLearningStateApplicationLearningPersistenceService",
    "ConsequenceLearningStateApplicationLearningWriter",
]
