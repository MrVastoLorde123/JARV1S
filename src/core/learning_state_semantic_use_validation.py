"""M23.113: validate a completed semantic-use artifact structurally."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_semantic_use import (
    LearningStateSemanticUse,
    LearningStateSemanticUseStatus,
)


class LearningStateSemanticUseValidationError(RuntimeError):
    """Raised when semantic-use validation cannot be formed safely."""


class LearningStateSemanticUseValidationStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
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
class LearningStateSemanticUseValidation:
    """Immutable structural validation evidence for one semantic-use artifact."""

    validation_id: str
    use_id: str
    request_id: str
    integrity_id: str
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
    request_status: object
    use_status: LearningStateSemanticUseStatus
    result: Mapping[str, Any] | None
    validation_status: LearningStateSemanticUseValidationStatus
    failure_reason: str | None
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "validation_id", "use_id", "request_id", "integrity_id", "interpretation_id", "source_request_id",
            "read_validation_id", "read_id", "consumption_request_id", "source_validation_id", "source_integrity_id",
            "transition_id", "evidence_id", "application_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint", "consumer_id", "use_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("semantic-use validation requires SHA-256 fingerprints")
        if not isinstance(self.use_status, LearningStateSemanticUseStatus):
            raise TypeError("use_status must be a semantic-use status")
        if not isinstance(self.validation_status, LearningStateSemanticUseValidationStatus):
            raise TypeError("validation_status must be a semantic-use validation status")
        if self.validation_status is LearningStateSemanticUseValidationStatus.ACCEPTED:
            if self.use_status is not LearningStateSemanticUseStatus.USED:
                raise ValueError("ACCEPTED validation requires USED semantic use")
            if not isinstance(self.result, Mapping):
                raise TypeError("ACCEPTED validation requires a mapping semantic-use result")
            if self.failure_reason is not None:
                raise ValueError("ACCEPTED validation cannot carry a failure reason")
        elif self.failure_reason is None or not self.failure_reason.strip():
            raise ValueError("REJECTED validation requires a failure reason")
        if self.result is not None and not isinstance(self.result, Mapping):
            raise TypeError("result must be a mapping when present")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        if self.result is not None:
            object.__setattr__(self, "result", _freeze(self.result))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_accepted(self) -> bool:
        return self.validation_status is LearningStateSemanticUseValidationStatus.ACCEPTED

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


class LearningStateSemanticUseValidationService:
    """Validate semantic-use structure without inspecting semantic values."""

    def validate(
        self,
        use: LearningStateSemanticUse,
        *,
        validation_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateSemanticUseValidation:
        if type(use) is not LearningStateSemanticUse:
            raise TypeError("use must be a learning-state semantic-use artifact")
        if not isinstance(validation_id, str) or not validation_id.strip():
            raise ValueError("validation_id must be a non-empty string")
        accepted = use.use_status is LearningStateSemanticUseStatus.USED and isinstance(use.result, Mapping)
        status = LearningStateSemanticUseValidationStatus.ACCEPTED if accepted else LearningStateSemanticUseValidationStatus.REJECTED
        failure = None if accepted else "learning-state semantic-use validation requires USED status with a mapping result"
        return LearningStateSemanticUseValidation(
            validation_id=validation_id,
            use_id=use.use_id,
            request_id=use.request_id,
            integrity_id=use.integrity_id,
            interpretation_id=use.interpretation_id,
            source_request_id=use.source_request_id,
            read_validation_id=use.read_validation_id,
            read_id=use.read_id,
            consumption_request_id=use.consumption_request_id,
            source_validation_id=use.source_validation_id,
            source_integrity_id=use.source_integrity_id,
            transition_id=use.transition_id,
            evidence_id=use.evidence_id,
            application_id=use.application_id,
            state_key=use.state_key,
            transition_fingerprint=use.transition_fingerprint,
            source_application_fingerprint=use.source_application_fingerprint,
            computed_application_fingerprint=use.computed_application_fingerprint,
            confidence=use.confidence,
            consumer_id=use.consumer_id,
            use_purpose=use.use_purpose,
            request_status=use.request_status,
            use_status=use.use_status,
            result=use.result if accepted else None,
            validation_status=status,
            failure_reason=failure,
            reasons=reasons if reasons is not None else {"validation_status": status.value},
            lineage=lineage if lineage is not None else {"validation_id": validation_id, "use_id": use.use_id},
        )


__all__ = [
    "LearningStateSemanticUseValidationError",
    "LearningStateSemanticUseValidationStatus",
    "LearningStateSemanticUseValidation",
    "LearningStateSemanticUseValidationService",
]
