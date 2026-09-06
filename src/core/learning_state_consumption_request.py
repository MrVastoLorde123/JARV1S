"""M23.104: bounded learning-state consumption request formation."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_transition_integrity_validation import (
    LearningStateTransitionIntegrityValidation,
    LearningStateTransitionIntegrityValidationStatus,
)


class LearningStateConsumptionRequestError(RuntimeError):
    """Raised when a learning-state consumption request cannot be formed safely."""


class LearningStateConsumptionRequestStatus(str, Enum):
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
class LearningStateConsumptionRequest:
    """Immutable declaration of one accepted learning-state artifact for future read consumption."""

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
    request_status: LearningStateConsumptionRequestStatus
    failure_reason: str | None
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "request_id", "validation_id", "integrity_id", "transition_id", "evidence_id",
            "application_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("consumption request requires SHA-256 fingerprints")
        if not isinstance(self.request_status, LearningStateConsumptionRequestStatus):
            raise TypeError("request_status must be a learning-state consumption request status")
        if self.request_status is LearningStateConsumptionRequestStatus.READY and self.failure_reason is not None:
            raise ValueError("READY request cannot carry a failure reason")
        if self.request_status is LearningStateConsumptionRequestStatus.REJECTED and (self.failure_reason is None or not self.failure_reason.strip()):
            raise ValueError("REJECTED request requires a failure reason")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_readable(self) -> bool:
        return self.request_status is LearningStateConsumptionRequestStatus.READY

    @property
    def reads_durable_state(self) -> bool:
        return False

    @property
    def writes_durable_state(self) -> bool:
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


class LearningStateConsumptionRequestService:
    """Convert accepted validation evidence into a bounded consumer handoff without reading storage."""

    def request(
        self,
        validation: LearningStateTransitionIntegrityValidation,
        *,
        request_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateConsumptionRequest:
        if type(validation) is not LearningStateTransitionIntegrityValidation:
            raise TypeError("validation must be a learning-state transition integrity validation artifact")
        if not isinstance(request_id, str) or not request_id.strip():
            raise ValueError("request_id must be a non-empty string")
        ready = validation.validation_status is LearningStateTransitionIntegrityValidationStatus.ACCEPTED
        status = LearningStateConsumptionRequestStatus.READY if ready else LearningStateConsumptionRequestStatus.REJECTED
        failure = None if ready else "learning-state consumption requires ACCEPTED integrity validation"
        return LearningStateConsumptionRequest(
            request_id=request_id,
            validation_id=validation.validation_id,
            integrity_id=validation.integrity_id,
            transition_id=validation.transition_id,
            evidence_id=validation.evidence_id,
            application_id=validation.application_id,
            state_key=validation.state_key,
            transition_fingerprint=validation.transition_fingerprint,
            source_application_fingerprint=validation.source_application_fingerprint,
            computed_application_fingerprint=validation.computed_application_fingerprint,
            confidence=validation.confidence,
            request_status=status,
            failure_reason=failure,
            reasons=reasons if reasons is not None else {"request_status": status.value},
            lineage=lineage if lineage is not None else {"request_id": request_id, "validation_id": validation.validation_id},
        )


__all__ = [
    "LearningStateConsumptionRequestError",
    "LearningStateConsumptionRequestStatus",
    "LearningStateConsumptionRequest",
    "LearningStateConsumptionRequestService",
]
