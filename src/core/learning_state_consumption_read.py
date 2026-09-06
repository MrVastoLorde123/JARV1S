"""M23.105: bounded caller-owned read consumption of learning state."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping

from src.core.learning_state_consumption_request import LearningStateConsumptionRequest, LearningStateConsumptionRequestStatus

class LearningStateConsumptionReadError(RuntimeError):
    """Raised when a learning-state read boundary cannot be formed safely."""

class LearningStateConsumptionReadStatus(str, Enum):
    CONSUMED = "CONSUMED"
    REJECTED = "REJECTED"

def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value

@dataclass(frozen=True)
class LearningStateConsumptionRead:
    """Immutable evidence of one bounded learning-state storage read attempt."""
    read_id: str
    request_id: str
    validation_id: str
    integrity_id: str
    transition_id: str
    evidence_id: str
    application_id: str
    state_key: str
    transition_fingerprint: str
    source_application_fingerprint: str
    computed_application_fingerprint: str
    confidence: float
    read_status: LearningStateConsumptionReadStatus
    state: Mapping[str, Any] | None
    failure_reason: str | None
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in ("read_id", "request_id", "validation_id", "integrity_id", "transition_id", "evidence_id", "application_id", "state_key", "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("consumption read requires SHA-256 fingerprints")
        if not isinstance(self.read_status, LearningStateConsumptionReadStatus):
            raise TypeError("read_status must be a learning-state consumption read status")
        if self.read_status is LearningStateConsumptionReadStatus.CONSUMED:
            if not isinstance(self.state, Mapping):
                raise TypeError("CONSUMED read requires a mapping state payload")
            if self.failure_reason is not None:
                raise ValueError("CONSUMED read cannot carry a failure reason")
        elif self.failure_reason is None or not self.failure_reason.strip():
            raise ValueError("REJECTED read requires a failure reason")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        if self.state is not None:
            object.__setattr__(self, "state", _freeze(self.state))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def read_only(self) -> bool: return True
    @property
    def writes_durable_state(self) -> bool: return False
    @property
    def retries(self) -> bool: return False
    @property
    def invokes_learner(self) -> bool: return False
    @property
    def updates_model(self) -> bool: return False
    @property
    def mutates_memory(self) -> bool: return False
    @property
    def mutates_policy(self) -> bool: return False
    @property
    def grants_authority(self) -> bool: return False
    @property
    def executes_action(self) -> bool: return False

class LearningStateConsumptionReadService:
    """Perform one caller-owned read attempt from an accepted consumption request."""
    def consume(self, request: LearningStateConsumptionRequest, *, read_id: str, reader: Callable[[Mapping[str, str]], object] | None, reasons: Mapping[str, Any] | None = None, lineage: Mapping[str, Any] | None = None) -> LearningStateConsumptionRead:
        if type(request) is not LearningStateConsumptionRequest:
            raise TypeError("request must be a learning-state consumption request artifact")
        if not isinstance(read_id, str) or not read_id.strip():
            raise ValueError("read_id must be a non-empty string")
        metadata = {"request_id": request.request_id, "validation_id": request.validation_id, "integrity_id": request.integrity_id, "transition_id": request.transition_id, "state_key": request.state_key}
        state = None
        reason = None
        consumed = request.request_status is LearningStateConsumptionRequestStatus.READY and callable(reader)
        if consumed:
            try:
                result = reader(metadata)
                if isinstance(result, Mapping):
                    state = result
                else:
                    consumed = False
                    reason = "learning-state reader returned a non-mapping result"
            except Exception:
                consumed = False
                reason = "learning-state reader raised an exception"
        elif request.request_status is not LearningStateConsumptionRequestStatus.READY:
            reason = "learning-state consumption requires a READY request"
        else:
            reason = "learning-state consumption requires a callable read adapter"
        status = LearningStateConsumptionReadStatus.CONSUMED if consumed else LearningStateConsumptionReadStatus.REJECTED
        return LearningStateConsumptionRead(read_id=read_id, request_id=request.request_id, validation_id=request.validation_id, integrity_id=request.integrity_id, transition_id=request.transition_id, evidence_id=request.evidence_id, application_id=request.application_id, state_key=request.state_key, transition_fingerprint=request.transition_fingerprint, source_application_fingerprint=request.source_application_fingerprint, computed_application_fingerprint=request.computed_application_fingerprint, confidence=request.confidence, read_status=status, state=state, failure_reason=None if consumed else reason, reasons=reasons if reasons is not None else {"read_status": status.value}, lineage=lineage if lineage is not None else {"read_id": read_id, "request_id": request.request_id})

__all__ = ["LearningStateConsumptionReadError", "LearningStateConsumptionReadStatus", "LearningStateConsumptionRead", "LearningStateConsumptionReadService"]
