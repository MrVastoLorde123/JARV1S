"""M23.127: gate integrity-valid learning signals for a future learner."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_signal import LearningStateExecutionLearningSignalKind
from src.core.learning_state_execution_learning_signal_integrity import (
    LearningStateExecutionLearningSignalIntegrity,
    LearningStateExecutionLearningSignalIntegrityStatus,
)


class LearningStateExecutionLearningEligibilityError(RuntimeError):
    """Raised when learning eligibility evidence cannot be formed safely."""


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
    """Immutable gate evidence for whether a learning signal may enter learning."""

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
    source_integrity_id: str
    validation_id: str
    use_id: str
    request_id: str
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
    execution_target_id: str
    execution_purpose: str
    objective: str
    evaluator_id: str
    evaluation_purpose: str
    signal_kind: LearningStateExecutionLearningSignalKind
    signal_purpose: str
    learner_id: str
    eligibility_purpose: str
    status: LearningStateExecutionLearningEligibilityStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id",
            "attempt_id", "admission_id", "eligibility_source_id", "handling_id", "consumption_id", "receipt_id",
            "handoff_id", "source_integrity_id", "validation_id", "use_id", "request_id", "interpretation_id",
            "source_request_id", "read_validation_id", "read_id", "consumption_request_id", "source_validation_id",
            "transition_id", "evidence_id", "application_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint", "consumer_id", "execution_target_id",
            "execution_purpose", "objective", "evaluator_id", "evaluation_purpose", "signal_purpose", "learner_id",
            "eligibility_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("learning eligibility requires SHA-256 fingerprints")
        if not isinstance(self.signal_kind, LearningStateExecutionLearningSignalKind):
            raise TypeError("signal_kind must be a learning-signal kind")
        if not isinstance(self.status, LearningStateExecutionLearningEligibilityStatus):
            raise TypeError("status must be a learning-eligibility status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
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
    def authorizes_execution(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
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


class LearningStateExecutionLearningEligibilityService:
    """Admit only integrity-valid learning signals into a future learner boundary."""

    def evaluate(
        self,
        integrity: LearningStateExecutionLearningSignalIntegrity,
        *,
        eligibility_id: str,
        learner_id: str,
        eligibility_purpose: str,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningEligibility:
        if type(integrity) is not LearningStateExecutionLearningSignalIntegrity:
            raise TypeError("integrity must be a learning-signal integrity artifact")
        for name, value in (
            ("eligibility_id", eligibility_id), ("learner_id", learner_id), ("eligibility_purpose", eligibility_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        valid = integrity.status is LearningStateExecutionLearningSignalIntegrityStatus.VALID and integrity.is_valid
        final_reasons = reasons if reasons is not None else (("integrity status is VALID",) if valid else ("integrity status is not VALID",))
        status = LearningStateExecutionLearningEligibilityStatus.ELIGIBLE if valid else LearningStateExecutionLearningEligibilityStatus.REJECTED
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
            source_integrity_id=integrity.source_integrity_id,
            validation_id=integrity.validation_id,
            use_id=integrity.use_id,
            request_id=integrity.request_id,
            interpretation_id=integrity.interpretation_id,
            source_request_id=integrity.source_request_id,
            read_validation_id=integrity.read_validation_id,
            read_id=integrity.read_id,
            consumption_request_id=integrity.consumption_request_id,
            source_validation_id=integrity.source_validation_id,
            transition_id=integrity.transition_id,
            evidence_id=integrity.evidence_id,
            application_id=integrity.application_id,
            state_key=integrity.state_key,
            transition_fingerprint=integrity.transition_fingerprint,
            source_application_fingerprint=integrity.source_application_fingerprint,
            computed_application_fingerprint=integrity.computed_application_fingerprint,
            confidence=integrity.confidence,
            consumer_id=integrity.consumer_id,
            execution_target_id=integrity.execution_target_id,
            execution_purpose=integrity.execution_purpose,
            objective=integrity.objective,
            evaluator_id=integrity.evaluator_id,
            evaluation_purpose=integrity.evaluation_purpose,
            signal_kind=integrity.signal_kind,
            signal_purpose=integrity.signal_purpose,
            learner_id=learner_id,
            eligibility_purpose=eligibility_purpose,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {"eligibility_id": eligibility_id, "integrity_id": integrity.integrity_id},
        )


__all__ = [
    "LearningStateExecutionLearningEligibilityError",
    "LearningStateExecutionLearningEligibilityStatus",
    "LearningStateExecutionLearningEligibility",
    "LearningStateExecutionLearningEligibilityService",
]
