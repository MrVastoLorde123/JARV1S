"""M23.106: validate a learning-state consumption read event without asserting state truth."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_consumption_read import (
    LearningStateConsumptionRead,
    LearningStateConsumptionReadStatus,
)


class LearningStateConsumptionReadValidationError(RuntimeError):
    """Raised when a read-validation artifact cannot be formed safely."""


class LearningStateConsumptionReadValidationStatus(str, Enum):
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
class LearningStateConsumptionReadValidation:
    """Immutable validation evidence for one bounded learning-state read event."""

    validation_id: str
    read_id: str
    request_id: str
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
    read_status: LearningStateConsumptionReadStatus
    state: Mapping[str, Any] | None
    validation_status: LearningStateConsumptionReadValidationStatus
    failure_reason: str | None
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "validation_id", "read_id", "request_id", "source_validation_id", "integrity_id",
            "transition_id", "evidence_id", "application_id", "state_key",
            "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("read validation requires SHA-256 fingerprints")
        if not isinstance(self.read_status, LearningStateConsumptionReadStatus):
            raise TypeError("read_status must be a learning-state consumption read status")
        if not isinstance(self.validation_status, LearningStateConsumptionReadValidationStatus):
            raise TypeError("validation_status must be a learning-state consumption read validation status")
        if self.validation_status is LearningStateConsumptionReadValidationStatus.ACCEPTED:
            if self.read_status is not LearningStateConsumptionReadStatus.CONSUMED:
                raise ValueError("ACCEPTED read validation requires a CONSUMED read")
            if not isinstance(self.state, Mapping):
                raise TypeError("ACCEPTED read validation requires a mapping state payload")
            if self.failure_reason is not None:
                raise ValueError("ACCEPTED read validation cannot carry a failure reason")
        elif self.failure_reason is None or not self.failure_reason.strip():
            raise ValueError("REJECTED read validation requires a failure reason")
        if self.state is not None:
            object.__setattr__(self, "state", _freeze(self.state))
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


class LearningStateConsumptionReadValidationService:
    """Validate the read artifact contract without interpreting consumed-state semantics."""

    def validate(
        self,
        read: LearningStateConsumptionRead,
        *,
        validation_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateConsumptionReadValidation:
        if type(read) is not LearningStateConsumptionRead:
            raise TypeError("read must be a learning-state consumption read artifact")
        if not isinstance(validation_id, str) or not validation_id.strip():
            raise ValueError("validation_id must be a non-empty string")

        accepted = (
            read.read_status is LearningStateConsumptionReadStatus.CONSUMED
            and isinstance(read.state, Mapping)
        )
        status = (
            LearningStateConsumptionReadValidationStatus.ACCEPTED
            if accepted else LearningStateConsumptionReadValidationStatus.REJECTED
        )
        failure = None if accepted else "learning-state read validation requires a CONSUMED mapping read"
        return LearningStateConsumptionReadValidation(
            validation_id=validation_id,
            read_id=read.read_id,
            request_id=read.request_id,
            source_validation_id=read.validation_id,
            integrity_id=read.integrity_id,
            transition_id=read.transition_id,
            evidence_id=read.evidence_id,
            application_id=read.application_id,
            state_key=read.state_key,
            transition_fingerprint=read.transition_fingerprint,
            source_application_fingerprint=read.source_application_fingerprint,
            computed_application_fingerprint=read.computed_application_fingerprint,
            confidence=read.confidence,
            read_status=read.read_status,
            state=read.state,
            validation_status=status,
            failure_reason=failure,
            reasons=reasons if reasons is not None else {"validation_status": status.value},
            lineage=lineage if lineage is not None else {"validation_id": validation_id, "read_id": read.read_id},
        )


__all__ = [
    "LearningStateConsumptionReadValidationError",
    "LearningStateConsumptionReadValidationStatus",
    "LearningStateConsumptionReadValidation",
    "LearningStateConsumptionReadValidationService",
]
