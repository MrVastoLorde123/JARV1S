"""M23.124: evaluate execution feedback against an explicit objective."""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_feedback import (
    LearningStateExecutionFeedback,
    LearningStateExecutionFeedbackKind,
)


class LearningStateExecutionEvaluationError(RuntimeError):
    """Raised when bounded execution-feedback evaluation cannot be formed safely."""


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
class LearningStateExecutionEvaluation:
    """Immutable evaluation evidence relating feedback to an explicit objective."""

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
    outcome_status: Any
    feedback_kind: LearningStateExecutionFeedbackKind
    observed_consequence: Any
    executor_output: Any
    failure_type: str | None
    failure_message: str | None
    objective: str
    evaluator_id: str
    evaluation_purpose: str
    evaluation_judgment: Any
    evaluation_context: Mapping[str, Any]
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id", "eligibility_id",
            "handling_id", "consumption_id", "receipt_id", "handoff_id", "integrity_id", "validation_id",
            "use_id", "request_id", "interpretation_id", "source_request_id", "read_validation_id", "read_id",
            "consumption_request_id", "source_validation_id", "source_integrity_id", "transition_id", "evidence_id",
            "application_id", "state_key", "transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "consumer_id", "use_purpose", "downstream_recipient_id",
            "downstream_handler_id", "handling_purpose", "execution_target_id", "execution_purpose", "objective",
            "evaluator_id", "evaluation_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("execution evaluation requires SHA-256 fingerprints")
        if not isinstance(self.feedback_kind, LearningStateExecutionFeedbackKind):
            raise TypeError("feedback_kind must be an execution-feedback kind")
        if not isinstance(self.evaluation_context, Mapping) or not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("evaluation_context, reasons, and lineage must be mappings")
        object.__setattr__(self, "evaluation_judgment", _freeze(self.evaluation_judgment))
        object.__setattr__(self, "evaluation_context", _freeze(self.evaluation_context))
        object.__setattr__(self, "observed_consequence", _freeze(self.observed_consequence))
        object.__setattr__(self, "executor_output", _freeze(self.executor_output))
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
    def authorizes_execution(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def invokes_executor(self) -> bool:
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


class LearningStateExecutionEvaluationService:
    """Create inert evaluation evidence from execution feedback."""

    def evaluate(
        self,
        feedback: LearningStateExecutionFeedback,
        *,
        evaluation_id: str,
        objective: str,
        evaluator_id: str,
        evaluation_purpose: str,
        evaluation_judgment: Any,
        evaluation_context: Mapping[str, Any] | None = None,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionEvaluation:
        if type(feedback) is not LearningStateExecutionFeedback:
            raise TypeError("feedback must be an execution-feedback artifact")
        for name, value in (
            ("evaluation_id", evaluation_id), ("objective", objective),
            ("evaluator_id", evaluator_id), ("evaluation_purpose", evaluation_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        return LearningStateExecutionEvaluation(
            evaluation_id=evaluation_id,
            feedback_id=feedback.feedback_id,
            outcome_id=feedback.outcome_id,
            attempt_id=feedback.attempt_id,
            admission_id=feedback.admission_id,
            eligibility_id=feedback.eligibility_id,
            handling_id=feedback.handling_id,
            consumption_id=feedback.consumption_id,
            receipt_id=feedback.receipt_id,
            handoff_id=feedback.handoff_id,
            integrity_id=feedback.integrity_id,
            validation_id=feedback.validation_id,
            use_id=feedback.use_id,
            request_id=feedback.request_id,
            interpretation_id=feedback.interpretation_id,
            source_request_id=feedback.source_request_id,
            read_validation_id=feedback.read_validation_id,
            read_id=feedback.read_id,
            consumption_request_id=feedback.consumption_request_id,
            source_validation_id=feedback.source_validation_id,
            source_integrity_id=feedback.source_integrity_id,
            transition_id=feedback.transition_id,
            evidence_id=feedback.evidence_id,
            application_id=feedback.application_id,
            state_key=feedback.state_key,
            transition_fingerprint=feedback.transition_fingerprint,
            source_application_fingerprint=feedback.source_application_fingerprint,
            computed_application_fingerprint=feedback.computed_application_fingerprint,
            confidence=feedback.confidence,
            consumer_id=feedback.consumer_id,
            use_purpose=feedback.use_purpose,
            downstream_recipient_id=feedback.downstream_recipient_id,
            downstream_handler_id=feedback.downstream_handler_id,
            handling_purpose=feedback.handling_purpose,
            execution_target_id=feedback.execution_target_id,
            execution_purpose=feedback.execution_purpose,
            outcome_status=feedback.outcome_status,
            feedback_kind=feedback.feedback_kind,
            observed_consequence=feedback.observed_consequence,
            executor_output=feedback.executor_output,
            failure_type=feedback.failure_type,
            failure_message=feedback.failure_message,
            objective=objective,
            evaluator_id=evaluator_id,
            evaluation_purpose=evaluation_purpose,
            evaluation_judgment=evaluation_judgment,
            evaluation_context=evaluation_context if evaluation_context is not None else {"objective": objective},
            reasons=reasons if reasons is not None else {"source_feedback_id": feedback.feedback_id},
            lineage=lineage if lineage is not None else {"evaluation_id": evaluation_id, "feedback_id": feedback.feedback_id},
        )


__all__ = [
    "LearningStateExecutionEvaluationError",
    "LearningStateExecutionEvaluation",
    "LearningStateExecutionEvaluationService",
]
