"""M45 boundary for independently verifying applied learning state."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any, Mapping, Protocol

from src.agents.consequence_learning_state_application import (
    ConsequenceLearningStateApplicationReceipt,
)
from src.agents.consequence_learning_state_application_request import (
    ConsequenceLearningStateApplicationRequest,
)


class ConsequenceLearningStateApplicationReader(Protocol):
    """Explicit read authority for independently verifying applied learning state."""

    def read(self, *, applied_record_id: str) -> Mapping[str, Any] | None:
        ...


@dataclass(frozen=True)
class ConsequenceLearningStateApplicationVerification:
    """Immutable observation that an applied learning-state record matches its source contract."""

    verification_id: str
    application_id: str
    application_request_id: str
    request_id: str
    applied_record_id: str
    verified: bool
    observed: bool
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("verification_id", self.verification_id),
            ("application_id", self.application_id),
            ("application_request_id", self.application_request_id),
            ("request_id", self.request_id),
            ("applied_record_id", self.applied_record_id),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        for field_name, value in (("verified", self.verified), ("observed", self.observed)):
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be a bool")
        if self.verified and not self.observed:
            raise ValueError("verified application requires an observed record")

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_learning_state_application_verification_id": self.verification_id,
            "consequence_learning_state_application_id": self.application_id,
            "consequence_learning_state_application_request_id": self.application_request_id,
            "consequence_learning_write_request_id": self.request_id,
            "consequence_learning_state_applied_record_id": self.applied_record_id,
            "learning_state_application_observed": self.observed,
            "learning_state_application_verified": self.verified,
            "learning_state_application_applied": self.verified,
            "memory_mutated": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "reason": self.reason,
        }


class ConsequenceLearningStateApplicationVerificationService:
    """Verify one M44 application receipt against an injected reader."""

    def __init__(self, reader: ConsequenceLearningStateApplicationReader | None = None) -> None:
        self._reader = reader

    def bind(self, reader: ConsequenceLearningStateApplicationReader) -> None:
        if not hasattr(reader, "read") or not callable(reader.read):
            raise TypeError("reader must provide a callable read method")
        self._reader = reader

    def verify(
        self,
        request: ConsequenceLearningStateApplicationRequest,
        receipt: ConsequenceLearningStateApplicationReceipt,
    ) -> ConsequenceLearningStateApplicationVerification:
        if not isinstance(request, ConsequenceLearningStateApplicationRequest):
            raise TypeError("request must be a ConsequenceLearningStateApplicationRequest")
        if not isinstance(receipt, ConsequenceLearningStateApplicationReceipt):
            raise TypeError("receipt must be a ConsequenceLearningStateApplicationReceipt")
        if request.application_request_id != receipt.application_request_id:
            raise ValueError("receipt does not belong to application request")
        if request.request_id != receipt.request_id:
            raise ValueError("receipt does not belong to source request")
        if self._reader is None:
            raise RuntimeError("learning-state application reader is not bound")

        observed = self._reader.read(applied_record_id=receipt.applied_record_id)
        verified = self._matches(request, receipt, observed)
        reason = (
            "applied learning state independently matches application request and receipt"
            if verified
            else "applied learning state could not be independently matched to application request and receipt"
        )
        return ConsequenceLearningStateApplicationVerification(
            verification_id=self._verification_id(receipt.application_id, receipt.applied_record_id),
            application_id=receipt.application_id,
            application_request_id=request.application_request_id,
            request_id=request.request_id,
            applied_record_id=receipt.applied_record_id,
            verified=verified,
            observed=observed is not None,
            reason=reason,
        )

    @staticmethod
    def _matches(
        request: ConsequenceLearningStateApplicationRequest,
        receipt: ConsequenceLearningStateApplicationReceipt,
        observed: Mapping[str, Any] | None,
    ) -> bool:
        if not isinstance(observed, Mapping):
            return False
        return (
            observed.get("application_id") == receipt.application_id
            and observed.get("application_request_id") == request.application_request_id
            and observed.get("request_id") == request.request_id
            and observed.get("source_record_id") == request.record_id
            and observed.get("applied_record_id") == receipt.applied_record_id
            and observed.get("payload") == dict(request.payload)
        )

    @staticmethod
    def _verification_id(application_id: str, applied_record_id: str) -> str:
        source = f"{application_id}:{applied_record_id}".encode("utf-8")
        return f"consequence-learning-state-application-verification-{hashlib.sha256(source).hexdigest()[:24]}"


__all__ = [
    "ConsequenceLearningStateApplicationReader",
    "ConsequenceLearningStateApplicationVerification",
    "ConsequenceLearningStateApplicationVerificationService",
]
