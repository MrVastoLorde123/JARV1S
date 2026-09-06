"""M23.107: bounded request formation for future learning-state interpretation."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_consumption_read_validation import (
    LearningStateConsumptionReadValidation,
    LearningStateConsumptionReadValidationStatus,
)


class LearningStateInterpretationRequestError(RuntimeError):
    """Raised when an interpretation request cannot be formed safely."""


class LearningStateInterpretationRequestStatus(str, Enum):
    READY = "READY"
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
class LearningStateInterpretationRequest:
    """Immutable declaration of validated learning state offered to a future interpreter."""

    request_id: str
    read_validation_id: str
    read_id: str
    consumption_request_id: str
    source_validation_id: str
    integrity_id: str
    transition_id: str
    evidence_id: str
    application_id: str
    state_key: str
    transition_fingerprint: str
    source_application_fingerprint: str
    computed_application_fingerprint: str
    confidence: float
    state: Mapping[str, Any] | None
    request_status: LearningStateInterpretationRequestStatus
    failure_reason: str | None
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in ("request_id", "read_validation_id", "read_id", "consumption_request_id", "source_validation_id", "integrity_id", "transition_id", "evidence_id", "application_id", "state_key", "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("interpretation request requires SHA-256 fingerprints")
        if not isinstance(self.request_status, LearningStateInterpretationRequestStatus):
            raise TypeError("request_status must be a learning-state interpretation request status")
        if self.request_status is LearningStateInterpretationRequestStatus.READY:
            if not isinstance(self.state, Mapping):
                raise TypeError("READY interpretation request requires a mapping state payload")
            if self.failure_reason is not None:
                raise ValueError("READY interpretation request cannot carry a failure reason")
        elif self.failure_reason is None or not self.failure_reason.strip():
            raise ValueError("REJECTED interpretation request requires a failure reason")
        if self.state is not None:
            object.__setattr__(self, "state", _freeze(self.state))
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_ready(self) -> bool:
        return self.request_status is LearningStateInterpretationRequestStatus.READY

    @property
    def interprets_state(self) -> bool:
        return False

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_correctness(self) -> bool:
        return False

    @property
    def invokes_interpreter(self) -> bool:
        return False

    @property
    def invokes_learner(self) -> bool:
        return False

    @property
    def updates_model(self) -> bool:
        return False

    @property
    def mutates_memory(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def executes_action(self) -> bool:
        return False


class LearningStateInterpretationRequestService:
    """Convert accepted read-validation evidence into a bounded future interpreter handoff."""

    def request(
        self,
        validation: LearningStateConsumptionReadValidation,
        *,
        request_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateInterpretationRequest:
        if type(validation) is not LearningStateConsumptionReadValidation:
            raise TypeError("validation must be a learning-state consumption read validation artifact")
        if not isinstance(request_id, str) or not request_id.strip():
            raise ValueError("request_id must be a non-empty string")
        ready = (
            validation.validation_status is LearningStateConsumptionReadValidationStatus.ACCEPTED
            and isinstance(validation.state, Mapping)
        )
        status = LearningStateInterpretationRequestStatus.READY if ready else LearningStateInterpretationRequestStatus.REJECTED
        failure = None if ready else "learning-state interpretation requires ACCEPTED read validation with a mapping state"
        return LearningStateInterpretationRequest(
            request_id=request_id,
            read_validation_id=validation.validation_id,
            read_id=validation.read_id,
            consumption_request_id=validation.request_id,
            source_validation_id=validation.source_validation_id,
            integrity_id=validation.integrity_id,
            transition_id=validation.transition_id,
            evidence_id=validation.evidence_id,
            application_id=validation.application_id,
            state_key=validation.state_key,
            transition_fingerprint=validation.transition_fingerprint,
            source_application_fingerprint=validation.source_application_fingerprint,
            computed_application_fingerprint=validation.computed_application_fingerprint,
            confidence=validation.confidence,
            state=validation.state,
            request_status=status,
            failure_reason=failure,
            reasons=reasons if reasons is not None else {"request_status": status.value},
            lineage=lineage if lineage is not None else {"request_id": request_id, "read_validation_id": validation.validation_id},
        )


__all__ = [
    "LearningStateInterpretationRequestError",
    "LearningStateInterpretationRequestStatus",
    "LearningStateInterpretationRequest",
    "LearningStateInterpretationRequestService",
]
