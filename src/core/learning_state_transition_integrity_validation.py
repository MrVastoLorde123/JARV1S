"""M23.103: bounded validation of learning-state transition integrity evidence."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_transition_integrity import (
    LearningStateTransitionIntegrity,
    LearningStateTransitionIntegrityStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_learning_state_transition_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Status as TransitionStatus,
)


class LearningStateTransitionIntegrityValidationError(RuntimeError):
    """Raised when learning-state integrity validation cannot be formed safely."""


class LearningStateTransitionIntegrityValidationStatus(str, Enum):
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
class LearningStateTransitionIntegrityValidation:
    """Immutable decision on whether transition integrity evidence is consumable."""

    validation_id: str
    integrity_id: str
    transition_id: str
    evidence_id: str
    application_id: str
    state_key: str
    transition_status: TransitionStatus
    integrity_status: LearningStateTransitionIntegrityStatus
    transition_fingerprint: str
    source_application_fingerprint: str
    computed_application_fingerprint: str
    confidence: float
    validation_status: LearningStateTransitionIntegrityValidationStatus
    failure_reason: str | None
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "validation_id", "integrity_id", "transition_id", "evidence_id", "application_id",
            "state_key", "transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("validation requires SHA-256 fingerprints")
        if not isinstance(self.transition_status, TransitionStatus):
            raise TypeError("transition_status must be a learning-state transition status")
        if not isinstance(self.integrity_status, LearningStateTransitionIntegrityStatus):
            raise TypeError("integrity_status must be a learning-state transition integrity status")
        if not isinstance(self.validation_status, LearningStateTransitionIntegrityValidationStatus):
            raise TypeError("validation_status must be a learning-state integrity validation status")
        if self.validation_status is LearningStateTransitionIntegrityValidationStatus.ACCEPTED and self.failure_reason is not None:
            raise ValueError("ACCEPTED validation cannot carry a failure reason")
        if self.validation_status is LearningStateTransitionIntegrityValidationStatus.REJECTED and (self.failure_reason is None or not self.failure_reason.strip()):
            raise ValueError("REJECTED validation requires a failure reason")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_consumable(self) -> bool:
        return self.validation_status is LearningStateTransitionIntegrityValidationStatus.ACCEPTED

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_correctness(self) -> bool:
        return False

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
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
    def schedules_work(self) -> bool:
        return False

    @property
    def executes_action(self) -> bool:
        return False


class LearningStateTransitionIntegrityValidationService:
    """Validate transition integrity evidence without persistence, learning, or authority mutation."""

    def validate(
        self,
        integrity: LearningStateTransitionIntegrity,
        *,
        validation_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateTransitionIntegrityValidation:
        if type(integrity) is not LearningStateTransitionIntegrity:
            raise TypeError("integrity must be a learning-state transition integrity artifact")
        if not isinstance(validation_id, str) or not validation_id.strip():
            raise ValueError("validation_id must be a non-empty string")

        accepted = (
            integrity.integrity_status is LearningStateTransitionIntegrityStatus.VALID
            and integrity.transition_status is TransitionStatus.PERSISTED
        )
        status = (
            LearningStateTransitionIntegrityValidationStatus.ACCEPTED
            if accepted
            else LearningStateTransitionIntegrityValidationStatus.REJECTED
        )
        reason = None if accepted else (
            "learning-state integrity is not consumable: requires VALID integrity over a PERSISTED transition"
        )
        return LearningStateTransitionIntegrityValidation(
            validation_id=validation_id,
            integrity_id=integrity.integrity_id,
            transition_id=integrity.transition_id,
            evidence_id=integrity.evidence_id,
            application_id=integrity.application_id,
            state_key=integrity.state_key,
            transition_status=integrity.transition_status,
            integrity_status=integrity.integrity_status,
            transition_fingerprint=integrity.computed_transition_fingerprint,
            source_application_fingerprint=integrity.source_application_fingerprint,
            computed_application_fingerprint=integrity.computed_application_fingerprint,
            confidence=integrity.confidence,
            validation_status=status,
            failure_reason=reason,
            reasons=reasons if reasons is not None else {"validation_status": status.value},
            lineage=lineage if lineage is not None else {"validation_id": validation_id, "integrity_id": integrity.integrity_id},
        )


__all__ = [
    "LearningStateTransitionIntegrityValidationError",
    "LearningStateTransitionIntegrityValidationStatus",
    "LearningStateTransitionIntegrityValidation",
    "LearningStateTransitionIntegrityValidationService",
]
