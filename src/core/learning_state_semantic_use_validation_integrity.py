"""M23.114: verify structural integrity of semantic-use validation evidence."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_semantic_use_validation import (
    LearningStateSemanticUseValidation,
    LearningStateSemanticUseValidationStatus,
)


class LearningStateSemanticUseIntegrityError(RuntimeError):
    """Raised when semantic-use integrity evidence cannot be formed safely."""


class LearningStateSemanticUseIntegrityStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


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
class LearningStateSemanticUseIntegrity:
    """Immutable integrity evidence for one semantic-use validation artifact."""

    integrity_id: str
    validation_id: str
    use_id: str
    request_id: str
    source_integrity_id: str
    interpretation_id: str
    source_request_id: str
    read_validation_id: str
    read_id: str
    consumption_request_id: str
    source_validation_id: str
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
    request_status: object
    use_status: object
    validation_status: LearningStateSemanticUseValidationStatus
    integrity_status: LearningStateSemanticUseIntegrityStatus
    result: Mapping[str, Any] | None
    failure_reason: str | None
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "integrity_id", "validation_id", "use_id", "request_id", "source_integrity_id",
            "interpretation_id", "source_request_id", "read_validation_id", "read_id",
            "consumption_request_id", "source_validation_id", "transition_id", "evidence_id",
            "application_id", "state_key", "transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "consumer_id", "use_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("semantic-use integrity requires SHA-256 fingerprints")
        if not isinstance(self.validation_status, LearningStateSemanticUseValidationStatus):
            raise TypeError("validation_status must be a semantic-use validation status")
        if not isinstance(self.integrity_status, LearningStateSemanticUseIntegrityStatus):
            raise TypeError("integrity_status must be a semantic-use integrity status")
        if self.integrity_status is LearningStateSemanticUseIntegrityStatus.VALID:
            if self.validation_status is not LearningStateSemanticUseValidationStatus.ACCEPTED:
                raise ValueError("VALID integrity requires ACCEPTED semantic-use validation")
            if not isinstance(self.result, Mapping):
                raise TypeError("VALID integrity requires a mapping semantic-use result")
            if self.failure_reason is not None:
                raise ValueError("VALID integrity cannot carry a failure reason")
        elif self.failure_reason is None or not self.failure_reason.strip():
            raise ValueError("INVALID integrity requires a failure reason")
        if self.result is not None and not isinstance(self.result, Mapping):
            raise TypeError("result must be a mapping when present")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        if self.result is not None:
            object.__setattr__(self, "result", _freeze(self.result))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_valid(self) -> bool:
        return self.integrity_status is LearningStateSemanticUseIntegrityStatus.VALID

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
    def invokes_consumer(self) -> bool:
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


class LearningStateSemanticUseIntegrityService:
    """Verify semantic-use validation structure without semantic judgment."""

    def validate(
        self,
        validation: LearningStateSemanticUseValidation,
        *,
        integrity_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateSemanticUseIntegrity:
        if type(validation) is not LearningStateSemanticUseValidation:
            raise TypeError("validation must be a learning-state semantic-use validation artifact")
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")
        valid = (
            validation.validation_status is LearningStateSemanticUseValidationStatus.ACCEPTED
            and isinstance(validation.result, Mapping)
        )
        status = LearningStateSemanticUseIntegrityStatus.VALID if valid else LearningStateSemanticUseIntegrityStatus.INVALID
        failure = None if valid else "semantic-use integrity requires ACCEPTED validation with a mapping result"
        return LearningStateSemanticUseIntegrity(
            integrity_id=integrity_id,
            validation_id=validation.validation_id,
            use_id=validation.use_id,
            request_id=validation.request_id,
            source_integrity_id=validation.integrity_id,
            interpretation_id=validation.interpretation_id,
            source_request_id=validation.source_request_id,
            read_validation_id=validation.read_validation_id,
            read_id=validation.read_id,
            consumption_request_id=validation.consumption_request_id,
            source_validation_id=validation.source_validation_id,
            transition_id=validation.transition_id,
            evidence_id=validation.evidence_id,
            application_id=validation.application_id,
            state_key=validation.state_key,
            transition_fingerprint=validation.transition_fingerprint,
            source_application_fingerprint=validation.source_application_fingerprint,
            computed_application_fingerprint=validation.computed_application_fingerprint,
            confidence=validation.confidence,
            consumer_id=validation.consumer_id,
            use_purpose=validation.use_purpose,
            request_status=validation.request_status,
            use_status=validation.use_status,
            validation_status=validation.validation_status,
            integrity_status=status,
            result=validation.result,
            failure_reason=failure,
            reasons=reasons if reasons is not None else {"integrity_status": status.value},
            lineage=lineage if lineage is not None else {"integrity_id": integrity_id, "validation_id": validation.validation_id},
        )


__all__ = [
    "LearningStateSemanticUseIntegrityError",
    "LearningStateSemanticUseIntegrityStatus",
    "LearningStateSemanticUseIntegrity",
    "LearningStateSemanticUseIntegrityService",
]
