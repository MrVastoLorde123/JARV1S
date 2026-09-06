"""M23.109: validate a learning-state interpretation artifact without judging semantics."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_interpretation import (
    LearningStateInterpretation,
    LearningStateInterpretationStatus,
)


class LearningStateInterpretationValidationError(RuntimeError):
    """Raised when an interpretation-validation artifact cannot be formed safely."""


class LearningStateInterpretationValidationStatus(str, Enum):
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
class LearningStateInterpretationValidation:
    """Immutable contract-validation evidence for one learning-state interpretation."""

    validation_id: str
    interpretation_id: str
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
    interpretation_status: LearningStateInterpretationStatus
    interpretation: Mapping[str, Any] | None
    validation_status: LearningStateInterpretationValidationStatus
    failure_reason: str | None
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "validation_id", "interpretation_id", "request_id", "read_validation_id", "read_id",
            "consumption_request_id", "source_validation_id", "integrity_id", "transition_id",
            "evidence_id", "application_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("interpretation validation requires SHA-256 fingerprints")
        if not isinstance(self.interpretation_status, LearningStateInterpretationStatus):
            raise TypeError("interpretation_status must be a learning-state interpretation status")
        if not isinstance(self.validation_status, LearningStateInterpretationValidationStatus):
            raise TypeError("validation_status must be a learning-state interpretation validation status")
        if self.validation_status is LearningStateInterpretationValidationStatus.ACCEPTED:
            if self.interpretation_status is not LearningStateInterpretationStatus.INTERPRETED:
                raise ValueError("ACCEPTED interpretation validation requires an INTERPRETED source")
            if not isinstance(self.interpretation, Mapping):
                raise TypeError("ACCEPTED interpretation validation requires a mapping interpretation")
            if self.failure_reason is not None:
                raise ValueError("ACCEPTED interpretation validation cannot carry a failure reason")
        elif self.failure_reason is None or not self.failure_reason.strip():
            raise ValueError("REJECTED interpretation validation requires a failure reason")
        if self.interpretation is not None:
            object.__setattr__(self, "interpretation", _freeze(self.interpretation))
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

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


class LearningStateInterpretationValidationService:
    """Validate the interpretation artifact contract without evaluating semantic content."""

    def validate(
        self,
        interpretation: LearningStateInterpretation,
        *,
        validation_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateInterpretationValidation:
        if type(interpretation) is not LearningStateInterpretation:
            raise TypeError("interpretation must be a learning-state interpretation artifact")
        if not isinstance(validation_id, str) or not validation_id.strip():
            raise ValueError("validation_id must be a non-empty string")

        accepted = (
            interpretation.interpretation_status is LearningStateInterpretationStatus.INTERPRETED
            and isinstance(interpretation.interpretation, Mapping)
        )
        status = (
            LearningStateInterpretationValidationStatus.ACCEPTED
            if accepted else LearningStateInterpretationValidationStatus.REJECTED
        )
        failure = None if accepted else "learning-state interpretation validation requires an INTERPRETED mapping result"
        return LearningStateInterpretationValidation(
            validation_id=validation_id,
            interpretation_id=interpretation.interpretation_id,
            request_id=interpretation.request_id,
            read_validation_id=interpretation.read_validation_id,
            read_id=interpretation.read_id,
            consumption_request_id=interpretation.consumption_request_id,
            source_validation_id=interpretation.source_validation_id,
            integrity_id=interpretation.integrity_id,
            transition_id=interpretation.transition_id,
            evidence_id=interpretation.evidence_id,
            application_id=interpretation.application_id,
            state_key=interpretation.state_key,
            transition_fingerprint=interpretation.transition_fingerprint,
            source_application_fingerprint=interpretation.source_application_fingerprint,
            computed_application_fingerprint=interpretation.computed_application_fingerprint,
            confidence=interpretation.confidence,
            interpretation_status=interpretation.interpretation_status,
            interpretation=interpretation.interpretation if accepted else None,
            validation_status=status,
            failure_reason=failure,
            reasons=reasons if reasons is not None else {"validation_status": status.value},
            lineage=lineage if lineage is not None else {"validation_id": validation_id, "interpretation_id": interpretation.interpretation_id},
        )


__all__ = [
    "LearningStateInterpretationValidationError",
    "LearningStateInterpretationValidationStatus",
    "LearningStateInterpretationValidation",
    "LearningStateInterpretationValidationService",
]
