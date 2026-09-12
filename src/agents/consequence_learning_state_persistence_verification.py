"""M41 boundary for independently verifying persisted learning state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from src.agents.consequence_learning_state_persistence import (
    ConsequenceLearningStatePersistenceReceipt,
)
from src.agents.consequence_learning_write_request import ConsequenceLearningWriteRequest


class ConsequenceLearningStateReader(Protocol):
    """Explicit read authority for persisted learning state."""

    def read(
        self,
        *,
        request_id: str,
        record_id: str,
    ) -> Mapping[str, Any] | None:
        """Return the persisted record or None when it cannot be observed."""
        ...


@dataclass(frozen=True)
class ConsequenceLearningStatePersistenceVerification:
    """Immutable observation that persisted learning state matches its receipt."""

    verification_id: str
    request_id: str
    record_id: str
    verified: bool
    observed: bool
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("verification_id", self.verification_id),
            ("request_id", self.request_id),
            ("record_id", self.record_id),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        for field_name, value in (("verified", self.verified), ("observed", self.observed)):
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be a bool")
        if self.verified and not self.observed:
            raise ValueError("verified persistence requires an observed record")

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_learning_write_request_id": self.request_id,
            "consequence_learning_persistence_record_id": self.record_id,
            "consequence_learning_persistence_verification_id": self.verification_id,
            "learning_persistence_observed": self.observed,
            "learning_persistence_verified": self.verified,
            "learning_write_requested": True,
            "learning_written": self.observed,
            "learning_write_persisted": self.verified,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "reason": self.reason,
        }


class ConsequenceLearningStatePersistenceVerificationService:
    """Verify one M40 receipt against persisted state observed by an injected reader."""

    def __init__(self, reader: ConsequenceLearningStateReader | None = None) -> None:
        self._reader = reader

    def bind(self, reader: ConsequenceLearningStateReader) -> None:
        if not hasattr(reader, "read") or not callable(reader.read):
            raise TypeError("reader must provide a callable read method")
        self._reader = reader

    def verify(
        self,
        request: ConsequenceLearningWriteRequest,
        receipt: ConsequenceLearningStatePersistenceReceipt,
    ) -> ConsequenceLearningStatePersistenceVerification:
        if not isinstance(request, ConsequenceLearningWriteRequest):
            raise TypeError("request must be a ConsequenceLearningWriteRequest")
        if not isinstance(receipt, ConsequenceLearningStatePersistenceReceipt):
            raise TypeError("receipt must be a ConsequenceLearningStatePersistenceReceipt")
        if request.request_id != receipt.request_id:
            raise ValueError("receipt does not belong to request")
        if self._reader is None:
            raise RuntimeError("learning-state reader is not bound")

        observed = self._reader.read(request_id=request.request_id, record_id=receipt.record_id)
        verified = self._matches(request, receipt, observed)
        reason = (
            "persisted learning state independently matches request and receipt"
            if verified
            else "persisted learning state could not be independently matched to request and receipt"
        )
        return ConsequenceLearningStatePersistenceVerification(
            verification_id=self._verification_id(request.request_id, receipt.record_id),
            request_id=request.request_id,
            record_id=receipt.record_id,
            verified=verified,
            observed=observed is not None,
            reason=reason,
        )

    @staticmethod
    def _matches(
        request: ConsequenceLearningWriteRequest,
        receipt: ConsequenceLearningStatePersistenceReceipt,
        observed: Mapping[str, Any] | None,
    ) -> bool:
        if not isinstance(observed, Mapping):
            return False
        return (
            observed.get("request_id") == request.request_id
            and observed.get("record_id") == receipt.record_id
            and observed.get("payload") == dict(request.learning_payload)
        )

    @staticmethod
    def _verification_id(request_id: str, record_id: str) -> str:
        import hashlib

        return f"consequence-learning-persistence-verification-{hashlib.sha256(f'{request_id}:{record_id}'.encode('utf-8')).hexdigest()[:24]}"


__all__ = [
    "ConsequenceLearningStatePersistenceReader",
    "ConsequenceLearningStatePersistenceVerification",
    "ConsequenceLearningStatePersistenceVerificationService",
    "ConsequenceLearningStateReader",
]
