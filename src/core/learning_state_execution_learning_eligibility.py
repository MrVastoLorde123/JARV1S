"""M23.159: determine bounded learning eligibility without performing learning or granting authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.learning_state_execution_learning_state_execution_learning_signal import (
        LearningStateExecutionLearningSignalKind,
        LearningStateExecutionLearningSignalStatus,
    )
    from src.core.learning_state_execution_learning_state_execution_learning_signal_integrity import (
        LearningStateExecutionLearningSignalIntegrity,
    )


class LearningStateExecutionLearningEligibilityError(RuntimeError):
    """Raised when bounded learning-eligibility evidence cannot be formed safely."""


class LearningStateExecutionLearningEligibilityStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
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
class LearningStateExecutionLearningEligibility:
    """Immutable evidence that one integrity-validated signal may enter a future learning path."""

    eligibility_id: str
    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    attempt_id: str
    admission_id: str
    eligibility_source_id: str
    handling_id: str
    consumption_id: str
    receipt_id: str
    handoff_id: str
    inherited_integrity_id: str
    validation_id: str
    semantic_use_id: str
    source_request_id: str
    source_request_lineage_id: str
    source_validation_id: str
    source_validation_lineage_id: str
    interpretation_id: str
    read_id: str
    consumption_request_id: str
    requester_id: str
    consumer_id: str
    handoff_target_id: str
    recipient_id: str
    handling_target_id: str
    execution_target_id: str
    signal_kind: Any
    signal_purpose: str
    signal_context: Any
    signal_status: Any
    source_signal_fingerprint: str
    computed_signal_fingerprint: str
    learner_id: str
    eligibility_purpose: str
    status: LearningStateExecutionLearningEligibilityStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id",
            "admission_id", "eligibility_source_id", "handling_id", "consumption_id", "receipt_id", "handoff_id",
            "inherited_integrity_id", "validation_id", "semantic_use_id", "source_request_id", "source_request_lineage_id",
            "source_validation_id", "source_validation_lineage_id", "interpretation_id", "read_id", "consumption_request_id",
            "requester_id", "consumer_id", "handoff_target_id", "recipient_id", "handling_target_id", "execution_target_id",
            "signal_purpose", "source_signal_fingerprint", "computed_signal_fingerprint", "learner_id", "eligibility_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if len(self.source_signal_fingerprint) != 64 or len(self.computed_signal_fingerprint) != 64:
            raise ValueError("learning eligibility requires SHA-256 fingerprints")
        if not isinstance(self.status, LearningStateExecutionLearningEligibilityStatus):
            raise TypeError("status must be a learning-eligibility status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "signal_context", _freeze(self.signal_context))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_eligible(self) -> bool:
        return self.status is LearningStateExecutionLearningEligibilityStatus.ELIGIBLE

    @property
    def admits_learning(self) -> bool:
        return self.is_eligible

    @property
    def is_learning(self) -> bool:
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
    def proposes_adaptation(self) -> bool:
        return False

    @property
    def authorizes_learning(self) -> bool:
        return False

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def invokes_learner(self) -> bool:
        return False

    @property
    def invokes_executor(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def plans_work(self) -> bool:
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


class LearningStateExecutionLearningEligibilityService:
    """Gate one integrity-validated learning signal into a future learning path without doing learning."""

    def evaluate(
        self,
        integrity: "LearningStateExecutionLearningSignalIntegrity",
        *,
        eligibility_id: str,
        learner_id: str,
        eligibility_purpose: str,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningEligibility:
        from src.core.learning_state_execution_learning_state_execution_learning_signal_integrity import (
            LearningStateExecutionLearningSignalIntegrity,
            LearningStateExecutionLearningSignalIntegrityStatus,
        )

        if type(integrity) is not LearningStateExecutionLearningSignalIntegrity:
            raise TypeError("integrity must be a learning-signal integrity artifact")
        for name, value in (("eligibility_id", eligibility_id), ("learner_id", learner_id), ("eligibility_purpose", eligibility_purpose)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if eligibility_id == integrity.integrity_id:
            raise ValueError("eligibility identity must be distinct")

        eligible = integrity.status is LearningStateExecutionLearningSignalIntegrityStatus.VALID and integrity.is_valid
        final_reasons = reasons if reasons is not None else (("learning signal integrity is VALID",) if eligible else ("learning signal integrity is not VALID",))
        status = LearningStateExecutionLearningEligibilityStatus.ELIGIBLE if eligible else LearningStateExecutionLearningEligibilityStatus.REJECTED

        return LearningStateExecutionLearningEligibility(
            eligibility_id=eligibility_id,
            integrity_id=integrity.integrity_id,
            signal_id=integrity.signal_id,
            evaluation_id=integrity.evaluation_id,
            feedback_id=integrity.feedback_id,
            outcome_id=integrity.outcome_id,
            attempt_id=integrity.attempt_id,
            admission_id=integrity.admission_id,
            eligibility_source_id=integrity.integrity_id,
            handling_id=integrity.handling_id,
            consumption_id=integrity.consumption_id,
            receipt_id=integrity.receipt_id,
            handoff_id=integrity.handoff_id,
            inherited_integrity_id=integrity.inherited_integrity_id,
            validation_id=integrity.validation_id,
            semantic_use_id=integrity.semantic_use_id,
            source_request_id=integrity.source_request_id,
            source_request_lineage_id=integrity.source_request_lineage_id,
            source_validation_id=integrity.source_validation_id,
            source_validation_lineage_id=integrity.source_validation_lineage_id,
            interpretation_id=integrity.interpretation_id,
            read_id=integrity.read_id,
            consumption_request_id=integrity.consumption_request_id,
            requester_id=integrity.requester_id,
            consumer_id=integrity.consumer_id,
            handoff_target_id=integrity.handoff_target_id,
            recipient_id=integrity.recipient_id,
            handling_target_id=integrity.handling_target_id,
            execution_target_id=integrity.execution_target_id,
            signal_kind=integrity.signal_kind,
            signal_purpose=integrity.signal_purpose,
            signal_context=integrity.signal_context,
            signal_status=integrity.signal_status,
            source_signal_fingerprint=integrity.source_signal_fingerprint,
            computed_signal_fingerprint=integrity.computed_signal_fingerprint,
            learner_id=learner_id,
            eligibility_purpose=eligibility_purpose,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "eligibility_id": eligibility_id,
                "integrity_id": integrity.integrity_id,
                "inherited_integrity_id": integrity.inherited_integrity_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningEligibilityError",
    "LearningStateExecutionLearningEligibilityStatus",
    "LearningStateExecutionLearningEligibility",
    "LearningStateExecutionLearningEligibilityService",
]
