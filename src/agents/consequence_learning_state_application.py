"""M44 boundary for applying an explicit learning-state application request."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any, Mapping, Protocol

from src.agents.consequence_learning_state_application_request import (
    ConsequenceLearningStateApplicationRequest,
)


class ConsequenceLearningStateApplicator(Protocol):
    """Explicit authority to mutate learning state."""

    def apply(self, *, application_request_id: str, request_id: str, record_id: str, payload: Mapping[str, Any]) -> str:
        ...


@dataclass(frozen=True)
class ConsequenceLearningStateApplicationReceipt:
    """Immutable receipt proving an injected applicator returned an application identity."""

    application_id: str
    application_request_id: str
    request_id: str
    source_record_id: str
    applied_record_id: str
    applied: bool
    applicator_result: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("application_id", self.application_id),
            ("application_request_id", self.application_request_id),
            ("request_id", self.request_id),
            ("source_record_id", self.source_record_id),
            ("applied_record_id", self.applied_record_id),
            ("applicator_result", self.applicator_result),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if not isinstance(self.applied, bool):
            raise TypeError("applied must be a bool")
        if not self.applied:
            raise ValueError("application receipt requires applied=True")

    def to_context(self) -> dict[str, object]:
        return {
            "consequence_learning_state_application_id": self.application_id,
            "consequence_learning_state_application_request_id": self.application_request_id,
            "consequence_learning_write_request_id": self.request_id,
            "consequence_learning_persistence_record_id": self.source_record_id,
            "consequence_learning_state_applied_record_id": self.applied_record_id,
            "learning_state_application_applied": True,
            "learning_state_application_observed": True,
            "learning_state_application_requested": True,
            "memory_mutated": True,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "retry_requested": False,
            "revocation_requested": False,
            "reason": "learning state was applied by an explicitly injected applicator",
        }


class ConsequenceLearningStateApplicationService:
    """Apply exactly one M43 request through an explicitly injected applicator."""

    def __init__(self, applicator: ConsequenceLearningStateApplicator | None = None) -> None:
        self._applicator = applicator

    def bind(self, applicator: ConsequenceLearningStateApplicator) -> None:
        if not hasattr(applicator, "apply") or not callable(applicator.apply):
            raise TypeError("applicator must provide a callable apply method")
        self._applicator = applicator

    def apply(self, request: ConsequenceLearningStateApplicationRequest) -> ConsequenceLearningStateApplicationReceipt:
        if not isinstance(request, ConsequenceLearningStateApplicationRequest):
            raise TypeError("request must be a ConsequenceLearningStateApplicationRequest")
        if self._applicator is None:
            raise RuntimeError("learning-state applicator is not bound")
        applied_record_id = self._applicator.apply(
            application_request_id=request.application_request_id,
            request_id=request.request_id,
            record_id=request.record_id,
            payload=request.payload,
        )
        if not isinstance(applied_record_id, str) or not applied_record_id.strip():
            raise ValueError("applicator must return a non-empty record identity")
        return ConsequenceLearningStateApplicationReceipt(
            application_id=self._application_id(request.application_request_id, request.request_id, applied_record_id),
            application_request_id=request.application_request_id,
            request_id=request.request_id,
            source_record_id=request.record_id,
            applied_record_id=applied_record_id,
            applied=True,
            applicator_result=applied_record_id,
        )

    @staticmethod
    def _application_id(application_request_id: str, request_id: str, applied_record_id: str) -> str:
        source = f"{application_request_id}:{request_id}:{applied_record_id}".encode("utf-8")
        return f"consequence-learning-state-application-{hashlib.sha256(source).hexdigest()[:24]}"


__all__ = [
    "ConsequenceLearningStateApplicator",
    "ConsequenceLearningStateApplicationReceipt",
    "ConsequenceLearningStateApplicationService",
]
