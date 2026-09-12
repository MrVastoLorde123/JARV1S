"""M40 boundary from an approved learning-write request into persistence."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Protocol

from src.agents.consequence_learning_write_request import ConsequenceLearningWriteRequest


class ConsequenceLearningStateWriter(Protocol):
    """Explicit persistence authority for learning-state writes."""

    def write(
        self,
        *,
        request_id: str,
        payload: Mapping[str, Any],
        provenance: Mapping[str, str],
    ) -> str:
        """Persist one request and return a stable writer-side record identifier."""
        ...


@dataclass(frozen=True)
class ConsequenceLearningStatePersistenceReceipt:
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
            raise ValueError("a persistence receipt must represent a persisted write")

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_learning_write_request_id": self.request_id,
            "consequence_learning_persistence_receipt_id": self.receipt_id,
            "consequence_learning_record_id": self.record_id,
            "learning_write_requested": True,
            "learning_written": True,
            "learning_write_persisted": True,
            "memory_mutated": True,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "learning_persistence_observed": True,
        }


class ConsequenceLearningStatePersistenceService:
    """Persist exactly one eligible M39 request through an injected writer."""

    def __init__(self, writer: ConsequenceLearningStateWriter | None = None) -> None:
        self._writer = writer

    def bind(self, writer: ConsequenceLearningStateWriter) -> None:
        if not hasattr(writer, "write") or not callable(writer.write):
            raise TypeError("writer must provide a callable write method")
        self._writer = writer

    def persist(
        self,
        request: ConsequenceLearningWriteRequest,
    ) -> ConsequenceLearningStatePersistenceReceipt:
        if not isinstance(request, ConsequenceLearningWriteRequest):
            raise TypeError("request must be a ConsequenceLearningWriteRequest")
        if self._writer is None:
            raise RuntimeError("learning-state writer is not bound")

        payload = dict(request.learning_payload)
        provenance = {
            "request_id": request.request_id,
            "decision_id": request.decision_id,
            "evaluation_id": request.evaluation_id,
            "feedback_id": request.feedback_id,
            "outcome_id": request.outcome_id,
            "attempt_id": request.attempt_id,
            "execution_id": request.execution_id,
            "preparation_id": request.preparation_id,
            "authorization_id": request.authorization_id,
            "handoff_id": request.handoff_id,
            "claim_id": request.claim_id,
            "task_id": request.task_id,
            "consequence_id": request.consequence_id,
        }
        record_id = self._writer.write(
            request_id=request.request_id,
            payload=payload,
            provenance=provenance,
        )
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError("learning-state writer must return a non-empty record identifier")

        return ConsequenceLearningStatePersistenceReceipt(
            receipt_id=self._receipt_id(request.request_id, record_id),
            request_id=request.request_id,
            record_id=record_id,
            persisted=True,
            writer_result=record_id,
        )

    @staticmethod
    def _receipt_id(request_id: str, record_id: str) -> str:
        payload = json.dumps(
            {"request_id": request_id, "record_id": record_id},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"consequence-learning-persistence-{hashlib.sha256(payload).hexdigest()[:24]}"


__all__ = [
    "ConsequenceLearningStatePersistenceReceipt",
    "ConsequenceLearningStatePersistenceService",
    "ConsequenceLearningStateWriter",
]
