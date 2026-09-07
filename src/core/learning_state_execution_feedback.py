"""M23.123: convert execution outcome evidence into bounded feedback."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_outcome import (
    LearningStateExecutionOutcome,
    LearningStateExecutionOutcomeStatus,
)


class LearningStateExecutionFeedbackError(RuntimeError):
    """Raised when execution feedback cannot be formed safely."""


class LearningStateExecutionFeedbackKind(str, Enum):
    SUCCESS_FEEDBACK = "SUCCESS_FEEDBACK"
    FAILURE_FEEDBACK = "FAILURE_FEEDBACK"
    PARTIAL_FEEDBACK = "PARTIAL_FEEDBACK"
    UNKNOWN_FEEDBACK = "UNKNOWN_FEEDBACK"


_KIND_BY_STATUS = {
    LearningStateExecutionOutcomeStatus.SUCCESS: LearningStateExecutionFeedbackKind.SUCCESS_FEEDBACK,
    LearningStateExecutionOutcomeStatus.FAILURE: LearningStateExecutionFeedbackKind.FAILURE_FEEDBACK,
    LearningStateExecutionOutcomeStatus.PARTIAL: LearningStateExecutionFeedbackKind.PARTIAL_FEEDBACK,
    LearningStateExecutionOutcomeStatus.UNKNOWN: LearningStateExecutionFeedbackKind.UNKNOWN_FEEDBACK,
}


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
class LearningStateExecutionFeedback:
    """Immutable feedback evidence derived from one execution outcome."""

    feedback_id: str
    outcome_id: str
    attempt_id: str
    admission_id: str
    eligibility_id: str
    handling_id: str
    consumption_id: str
    receipt_id: str
    handoff_id: str
    integrity_id: str
    validation_id: str
    use_id: str
    request_id: str
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
    downstream_recipient_id: str
    downstream_handler_id: str
    handling_purpose: str
    execution_target_id: str
    execution_purpose: str
    outcome_status: LearningStateExecutionOutcomeStatus
    feedback_kind: LearningStateExecutionFeedbackKind
    observed_consequence: Any
    executor_output: Any
    failure_type: str | None
    failure_message: str | None
    feedback_context: Mapping[str, Any]
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "feedback_id", "outcome_id", "attempt_id", "admission_id", "eligibility_id", "handling_id",
            "consumption_id", "receipt_id", "handoff_id", "integrity_id", "validation_id", "use_id",
            "request_id", "interpretation_id", "source_request_id", "read_validation_id", "read_id",
            "consumption_request_id", "source_validation_id", "source_integrity_id", "transition_id",
            "evidence_id", "application_id", "state_key", "transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "consumer_id", "use_purpose", "downstream_recipient_id",
            "downstream_handler_id", "handling_purpose", "execution_target_id", "execution_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("execution feedback requires SHA-256 fingerprints")
        if not isinstance(self.outcome_status, LearningStateExecutionOutcomeStatus):
            raise TypeError("outcome_status must be an execution-outcome status")
        if not isinstance(self.feedback_kind, LearningStateExecutionFeedbackKind):
            raise TypeError("feedback_kind must be an execution-feedback kind")
        if _KIND_BY_STATUS[self.outcome_status] is not self.feedback_kind:
            raise ValueError("feedback kind must match outcome status")
        if not isinstance(self.feedback_context, Mapping) or not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("feedback_context, reasons, and lineage must be mappings")
        object.__setattr__(self, "observed_consequence", _freeze(self.observed_consequence))
        object.__setattr__(self, "executor_output", _freeze(self.executor_output))
        object.__setattr__(self, "feedback_context", _freeze(self.feedback_context))
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
    def invokes_executor(self) -> bool:
        return False

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def revokes_authority(self) -> bool:
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
    def plans_work(self) -> bool:
        return False


class LearningStateExecutionFeedbackService:
    """Create inert feedback evidence from one execution outcome without acting on it."""

    def record(
        self,
        outcome: LearningStateExecutionOutcome,
        *,
        feedback_id: str,
        feedback_context: Mapping[str, Any] | None = None,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionFeedback:
        if type(outcome) is not LearningStateExecutionOutcome:
            raise TypeError("outcome must be an execution-outcome artifact")
        if not isinstance(feedback_id, str) or not feedback_id.strip():
            raise ValueError("feedback_id must be a non-empty string")
        if not outcome.is_observed:
            raise ValueError("feedback requires an observed execution outcome")
        kind = _KIND_BY_STATUS[outcome.outcome_status]
        return LearningStateExecutionFeedback(
            feedback_id=feedback_id,
            outcome_id=outcome.outcome_id,
            attempt_id=outcome.attempt_id,
            admission_id=outcome.admission_id,
            eligibility_id=outcome.eligibility_id,
            handling_id=outcome.handling_id,
            consumption_id=outcome.consumption_id,
            receipt_id=outcome.receipt_id,
            handoff_id=outcome.handoff_id,
            integrity_id=outcome.integrity_id,
            validation_id=outcome.validation_id,
            use_id=outcome.use_id,
            request_id=outcome.request_id,
            interpretation_id=outcome.interpretation_id,
            source_request_id=outcome.source_request_id,
            read_validation_id=outcome.read_validation_id,
            read_id=outcome.read_id,
            consumption_request_id=outcome.consumption_request_id,
            source_validation_id=outcome.source_validation_id,
            source_integrity_id=outcome.source_integrity_id,
            transition_id=outcome.transition_id,
            evidence_id=outcome.evidence_id,
            application_id=outcome.application_id,
            state_key=outcome.state_key,
            transition_fingerprint=outcome.transition_fingerprint,
            source_application_fingerprint=outcome.source_application_fingerprint,
            computed_application_fingerprint=outcome.computed_application_fingerprint,
            confidence=outcome.confidence,
            consumer_id=outcome.consumer_id,
            use_purpose=outcome.use_purpose,
            downstream_recipient_id=outcome.downstream_recipient_id,
            downstream_handler_id=outcome.downstream_handler_id,
            handling_purpose=outcome.handling_purpose,
            execution_target_id=outcome.execution_target_id,
            execution_purpose=outcome.execution_purpose,
            outcome_status=outcome.outcome_status,
            feedback_kind=kind,
            observed_consequence=outcome.observed_consequence,
            executor_output=outcome.executor_output,
            failure_type=outcome.failure_type,
            failure_message=outcome.failure_message,
            feedback_context=feedback_context if feedback_context is not None else {"feedback_kind": kind.value},
            reasons=reasons if reasons is not None else {"source_outcome_id": outcome.outcome_id},
            lineage=lineage if lineage is not None else {"feedback_id": feedback_id, "outcome_id": outcome.outcome_id},
        )


__all__ = [
    "LearningStateExecutionFeedbackError",
    "LearningStateExecutionFeedbackKind",
    "LearningStateExecutionFeedback",
    "LearningStateExecutionFeedbackService",
]
