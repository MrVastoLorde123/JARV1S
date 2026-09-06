"""M23.111: bounded request for downstream semantic use of validated learning-state evidence."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_interpretation_validation import (
    LearningStateInterpretationValidationStatus,
)
from src.core.learning_state_interpretation_validation_integrity import (
    LearningStateInterpretationValidationIntegrity,
    LearningStateInterpretationValidationIntegrityStatus,
)


class LearningStateSemanticUseRequestError(RuntimeError):
    """Raised when a semantic-use request cannot be formed safely."""


class LearningStateSemanticUseRequestStatus(str, Enum):
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
class LearningStateSemanticUseRequest:
    """Immutable request authorizing no action and performing no semantic use."""

    request_id: str
    integrity_id: str
    validation_id: str
    interpretation_id: str
    source_request_id: str
    read_validation_id: str
    read_id: str
    consumption_request_id: str
    source_validation_id: str
    source_integrity_id: str
    transition_id: str
    evidence_id: str
    application_id: str
    state_key: str
    transition_fingerprint: str
    source_application_fingerprint: str
    computed_application_fingerprint: str
    confidence: float
    consumer_id: str
    use_purpose: str
    request_status: LearningStateSemanticUseRequestStatus
    validation_status: LearningStateInterpretationValidationStatus
    integrity_status: LearningStateInterpretationValidationIntegrityStatus
    interpretation: Mapping[str, Any]
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "request_id", "integrity_id", "validation_id", "interpretation_id", "source_request_id",
            "read_validation_id", "read_id", "consumption_request_id", "source_validation_id",
            "source_integrity_id", "transition_id", "evidence_id", "application_id", "state_key",
            "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint",
            "consumer_id", "use_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("semantic-use request requires SHA-256 fingerprints")
        if not isinstance(self.request_status, LearningStateSemanticUseRequestStatus):
            raise TypeError("request_status must be a semantic-use request status")
        if not isinstance(self.validation_status, LearningStateInterpretationValidationStatus):
            raise TypeError("validation_status must be an interpretation validation status")
        if not isinstance(self.integrity_status, LearningStateInterpretationValidationIntegrityStatus):
            raise TypeError("integrity_status must be an interpretation-validation integrity status")
        if self.request_status is LearningStateSemanticUseRequestStatus.READY:
            if self.integrity_status is not LearningStateInterpretationValidationIntegrityStatus.VALID:
                raise ValueError("READY semantic-use request requires VALID integrity")
            if self.validation_status is not LearningStateInterpretationValidationStatus.ACCEPTED:
                raise ValueError("READY semantic-use request requires ACCEPTED validation")
            if not isinstance(self.interpretation, Mapping):
                raise TypeError("READY semantic-use request requires mapping interpretation evidence")
        if not isinstance(self.interpretation, Mapping):
            raise TypeError("interpretation must be a mapping")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "interpretation", _freeze(self.interpretation))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_ready(self) -> bool:
        return self.request_status is LearningStateSemanticUseRequestStatus.READY

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
    def establishes_certainty(self) -> bool:
        return False

    @property
    def establishes_usefulness(self) -> bool:
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
    def schedules_work(self) -> bool:
        return False

    @property
    def executes_action(self) -> bool:
        return False


class LearningStateSemanticUseRequestService:
    """Create an immutable semantic-use request without performing semantic use."""

    def request(
        self,
        integrity: LearningStateInterpretationValidationIntegrity,
        *,
        request_id: str,
        consumer_id: str,
        use_purpose: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateSemanticUseRequest:
        if type(integrity) is not LearningStateInterpretationValidationIntegrity:
            raise TypeError("integrity must be a learning-state interpretation validation integrity artifact")
        for name, value in (("request_id", request_id), ("consumer_id", consumer_id), ("use_purpose", use_purpose)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if integrity.integrity_status is not LearningStateInterpretationValidationIntegrityStatus.VALID:
            raise LearningStateSemanticUseRequestError("semantic-use request requires VALID interpretation-validation integrity")
        if integrity.validation_status is not LearningStateInterpretationValidationStatus.ACCEPTED:
            raise LearningStateSemanticUseRequestError("semantic-use request requires ACCEPTED interpretation validation")
        if not isinstance(integrity.interpretation, Mapping):
            raise LearningStateSemanticUseRequestError("semantic-use request requires mapping interpretation evidence")
        return LearningStateSemanticUseRequest(
            request_id=request_id,
            integrity_id=integrity.integrity_id,
            validation_id=integrity.validation_id,
            interpretation_id=integrity.interpretation_id,
            source_request_id=integrity.request_id,
            read_validation_id=integrity.read_validation_id,
            read_id=integrity.read_id,
            consumption_request_id=integrity.consumption_request_id,
            source_validation_id=integrity.source_validation_id,
            source_integrity_id=integrity.source_integrity_id,
            transition_id=integrity.transition_id,
            evidence_id=integrity.evidence_id,
            application_id=integrity.application_id,
            state_key=integrity.state_key,
            transition_fingerprint=integrity.transition_fingerprint,
            source_application_fingerprint=integrity.source_application_fingerprint,
            computed_application_fingerprint=integrity.computed_application_fingerprint,
            confidence=integrity.confidence,
            consumer_id=consumer_id,
            use_purpose=use_purpose,
            request_status=LearningStateSemanticUseRequestStatus.READY,
            validation_status=integrity.validation_status,
            integrity_status=integrity.integrity_status,
            interpretation=integrity.interpretation,
            reasons=reasons if reasons is not None else {"request_status": "READY"},
            lineage=lineage if lineage is not None else {"request_id": request_id, "integrity_id": integrity.integrity_id},
        )


__all__ = [
    "LearningStateSemanticUseRequestError",
    "LearningStateSemanticUseRequestStatus",
    "LearningStateSemanticUseRequest",
    "LearningStateSemanticUseRequestService",
]
