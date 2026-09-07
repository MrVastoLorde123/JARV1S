"""M23.126: validate learning-signal integrity without mutating or learning from it."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_signal import (
    LearningStateExecutionLearningSignal,
    LearningStateExecutionLearningSignalKind,
)


class LearningStateExecutionLearningSignalIntegrityError(RuntimeError):
    """Raised when learning-signal integrity evidence cannot be formed safely."""


class LearningStateExecutionLearningSignalIntegrityStatus(str, Enum):
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
class LearningStateExecutionLearningSignalIntegrity:
    """Immutable evidence about the structural integrity of one learning signal."""

    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    attempt_id: str
    admission_id: str
    eligibility_id: str
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
    downstream_recipient_id: str
    downstream_handler_id: str
    execution_target_id: str
    execution_purpose: str
    objective: str
    evaluator_id: str
    evaluation_purpose: str
    evaluation_judgment: Any
    outcome_status: Any
    feedback_kind: Any
    observed_consequence: Any
    executor_output: Any
    signal_kind: LearningStateExecutionLearningSignalKind
    signal_purpose: str
    status: LearningStateExecutionLearningSignalIntegrityStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id",
            "admission_id", "eligibility_id", "handling_id", "consumption_id", "receipt_id", "handoff_id",
            "source_integrity_id", "validation_id", "use_id", "request_id", "interpretation_id",
            "source_request_id", "read_validation_id", "read_id", "consumption_request_id", "source_validation_id",
            "transition_id", "evidence_id", "application_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint", "consumer_id",
            "downstream_recipient_id", "downstream_handler_id", "execution_target_id", "execution_purpose",
            "objective", "evaluator_id", "evaluation_purpose", "signal_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            value = getattr(self, name)
            if len(value) != 64:
                raise ValueError("learning signal integrity requires SHA-256 fingerprints")
        if not isinstance(self.signal_kind, LearningStateExecutionLearningSignalKind):
            raise TypeError("signal_kind must be a learning-signal kind")
        if not isinstance(self.status, LearningStateExecutionLearningSignalIntegrityStatus):
            raise TypeError("status must be a learning-signal integrity status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "evaluation_judgment", _freeze(self.evaluation_judgment))
        object.__setattr__(self, "observed_consequence", _freeze(self.observed_consequence))
        object.__setattr__(self, "executor_output", _freeze(self.executor_output))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_valid(self) -> bool:
        return self.status is LearningStateExecutionLearningSignalIntegrityStatus.VALID

    @property
    def validates_signal(self) -> bool:
        return self.is_valid

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
    def is_learning(self) -> bool:
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
    def invokes_executor(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def plans_work(self) -> bool:
        return False


class LearningStateExecutionLearningSignalIntegrityService:
    """Validate learning-signal structure and provenance without repairing or consuming it."""

    def validate(
        self,
        signal: LearningStateExecutionLearningSignal,
        *,
        integrity_id: str,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningSignalIntegrity:
        if type(signal) is not LearningStateExecutionLearningSignal:
            raise TypeError("signal must be a learning-signal artifact")
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        checks.append("signal_id" if signal.signal_id.strip() else "missing signal_id")
        checks.append("evaluation_id" if signal.evaluation_id == signal.lineage.get("evaluation_id", signal.evaluation_id) else "evaluation lineage mismatch")
        checks.append("feedback_id" if signal.feedback_id.strip() else "missing feedback_id")
        checks.append("outcome_id" if signal.outcome_id.strip() else "missing outcome_id")
        checks.append("signal_kind" if isinstance(signal.signal_kind, LearningStateExecutionLearningSignalKind) else "invalid signal_kind")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(signal, name)) != 64:
                checks.append(f"invalid {name}")
        valid = not any(check.startswith("missing") or check.startswith("invalid") or check.endswith("mismatch") for check in checks)
        if reasons is not None:
            final_reasons = reasons
        elif valid:
            final_reasons = ("signal structure and provenance checks passed",)
        else:
            final_reasons = tuple(check for check in checks if check.startswith("missing") or check.startswith("invalid") or check.endswith("mismatch"))

        status = LearningStateExecutionLearningSignalIntegrityStatus.VALID if valid else LearningStateExecutionLearningSignalIntegrityStatus.INVALID
        return LearningStateExecutionLearningSignalIntegrity(
            integrity_id=integrity_id,
            signal_id=signal.signal_id,
            evaluation_id=signal.evaluation_id,
            feedback_id=signal.feedback_id,
            outcome_id=signal.outcome_id,
            attempt_id=signal.attempt_id,
            admission_id=signal.admission_id,
            eligibility_id=signal.eligibility_id,
            handling_id=signal.handling_id,
            consumption_id=signal.consumption_id,
            receipt_id=signal.receipt_id,
            handoff_id=signal.handoff_id,
            source_integrity_id=signal.source_integrity_id,
            validation_id=signal.validation_id,
            use_id=signal.use_id,
            request_id=signal.request_id,
            interpretation_id=signal.interpretation_id,
            source_request_id=signal.source_request_id,
            read_validation_id=signal.read_validation_id,
            read_id=signal.read_id,
            consumption_request_id=signal.consumption_request_id,
            source_validation_id=signal.source_validation_id,
            transition_id=signal.transition_id,
            evidence_id=signal.evidence_id,
            application_id=signal.application_id,
            state_key=signal.state_key,
            transition_fingerprint=signal.transition_fingerprint,
            source_application_fingerprint=signal.source_application_fingerprint,
            computed_application_fingerprint=signal.computed_application_fingerprint,
            confidence=signal.confidence,
            consumer_id=signal.consumer_id,
            downstream_recipient_id=signal.downstream_recipient_id,
            downstream_handler_id=signal.downstream_handler_id,
            execution_target_id=signal.execution_target_id,
            execution_purpose=signal.execution_purpose,
            objective=signal.objective,
            evaluator_id=signal.evaluator_id,
            evaluation_purpose=signal.evaluation_purpose,
            evaluation_judgment=signal.evaluation_judgment,
            outcome_status=signal.outcome_status,
            feedback_kind=signal.feedback_kind,
            observed_consequence=signal.observed_consequence,
            executor_output=signal.executor_output,
            signal_kind=signal.signal_kind,
            signal_purpose=signal.signal_purpose,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {"integrity_id": integrity_id, "signal_id": signal.signal_id},
        )


__all__ = [
    "LearningStateExecutionLearningSignalIntegrityError",
    "LearningStateExecutionLearningSignalIntegrityStatus",
    "LearningStateExecutionLearningSignalIntegrity",
    "LearningStateExecutionLearningSignalIntegrityService",
]
