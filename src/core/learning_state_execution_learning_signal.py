"""M23.125: convert bounded evaluation evidence into a learning signal."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_evaluation import LearningStateExecutionEvaluation
from src.core.learning_state_execution_feedback import LearningStateExecutionFeedbackKind


class LearningStateExecutionLearningSignalError(RuntimeError):
    """Raised when a bounded learning signal cannot be formed safely."""


class LearningStateExecutionLearningSignalKind(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


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
class LearningStateExecutionLearningSignal:
    """Immutable signal evidence for a later learning mechanism."""

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
    signal_kind: LearningStateExecutionLearningSignalKind
    signal_purpose: str
    signal_context: Mapping[str, Any]
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id",
            "eligibility_id", "handling_id", "consumption_id", "receipt_id", "handoff_id", "integrity_id",
            "validation_id", "use_id", "request_id", "interpretation_id", "source_request_id",
            "read_validation_id", "read_id", "consumption_request_id", "source_validation_id", "source_integrity_id",
            "transition_id", "evidence_id", "application_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint", "consumer_id", "use_purpose",
            "downstream_recipient_id", "downstream_handler_id", "handling_purpose", "execution_target_id",
            "execution_purpose", "objective", "evaluator_id", "evaluation_purpose", "signal_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("learning signal requires SHA-256 fingerprints")
        if not isinstance(self.feedback_kind, LearningStateExecutionFeedbackKind):
            raise TypeError("feedback_kind must be an execution-feedback kind")
        if not isinstance(self.signal_kind, LearningStateExecutionLearningSignalKind):
            raise TypeError("signal_kind must be a learning-signal kind")
        if not isinstance(self.evaluation_context, Mapping) or not isinstance(self.signal_context, Mapping):
            raise TypeError("evaluation_context and signal_context must be mappings")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "evaluation_judgment", _freeze(self.evaluation_judgment))
        object.__setattr__(self, "evaluation_context", _freeze(self.evaluation_context))
        object.__setattr__(self, "observed_consequence", _freeze(self.observed_consequence))
        object.__setattr__(self, "executor_output", _freeze(self.executor_output))
        object.__setattr__(self, "signal_context", _freeze(self.signal_context))
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


class LearningStateExecutionLearningSignalService:
    """Create inert learning-signal evidence from one explicit evaluation."""

    def create(
        self,
        evaluation: LearningStateExecutionEvaluation,
        *,
        signal_id: str,
        signal_kind: LearningStateExecutionLearningSignalKind,
        signal_purpose: str,
        evaluation_context: Mapping[str, Any] | None = None,
        signal_context: Mapping[str, Any] | None = None,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningSignal:
        if type(evaluation) is not LearningStateExecutionEvaluation:
            raise TypeError("evaluation must be an execution-evaluation artifact")
        if not isinstance(signal_kind, LearningStateExecutionLearningSignalKind):
            raise TypeError("signal_kind must be a learning-signal kind")
        for name, value in (("signal_id", signal_id), ("signal_purpose", signal_purpose)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        return LearningStateExecutionLearningSignal(
            signal_id=signal_id,
            evaluation_id=evaluation.evaluation_id,
            feedback_id=evaluation.feedback_id,
            outcome_id=evaluation.outcome_id,
            attempt_id=evaluation.attempt_id,
            admission_id=evaluation.admission_id,
            eligibility_id=evaluation.eligibility_id,
            handling_id=evaluation.handling_id,
            consumption_id=evaluation.consumption_id,
            receipt_id=evaluation.receipt_id,
            handoff_id=evaluation.handoff_id,
            integrity_id=evaluation.integrity_id,
            validation_id=evaluation.validation_id,
            use_id=evaluation.use_id,
            request_id=evaluation.request_id,
            interpretation_id=evaluation.interpretation_id,
            source_request_id=evaluation.source_request_id,
            read_validation_id=evaluation.read_validation_id,
            read_id=evaluation.read_id,
            consumption_request_id=evaluation.consumption_request_id,
            source_validation_id=evaluation.source_validation_id,
            source_integrity_id=evaluation.source_integrity_id,
            transition_id=evaluation.transition_id,
            evidence_id=evaluation.evidence_id,
            application_id=evaluation.application_id,
            state_key=evaluation.state_key,
            transition_fingerprint=evaluation.transition_fingerprint,
            source_application_fingerprint=evaluation.source_application_fingerprint,
            computed_application_fingerprint=evaluation.computed_application_fingerprint,
            confidence=evaluation.confidence,
            consumer_id=evaluation.consumer_id,
            use_purpose=evaluation.use_purpose,
            downstream_recipient_id=evaluation.downstream_recipient_id,
            downstream_handler_id=evaluation.downstream_handler_id,
            handling_purpose=evaluation.handling_purpose,
            execution_target_id=evaluation.execution_target_id,
            execution_purpose=evaluation.execution_purpose,
            outcome_status=evaluation.outcome_status,
            feedback_kind=evaluation.feedback_kind,
            observed_consequence=evaluation.observed_consequence,
            executor_output=evaluation.executor_output,
            failure_type=evaluation.failure_type,
            failure_message=evaluation.failure_message,
            objective=evaluation.objective,
            evaluator_id=evaluation.evaluator_id,
            evaluation_purpose=evaluation.evaluation_purpose,
            evaluation_judgment=evaluation.evaluation_judgment,
            evaluation_context=evaluation_context if evaluation_context is not None else evaluation.evaluation_context,
            signal_kind=signal_kind,
            signal_purpose=signal_purpose,
            signal_context=signal_context if signal_context is not None else {"signal_kind": signal_kind.value},
            reasons=reasons if reasons is not None else {"source_evaluation_id": evaluation.evaluation_id},
            lineage=lineage if lineage is not None else {"signal_id": signal_id, "evaluation_id": evaluation.evaluation_id},
        )


__all__ = [
    "LearningStateExecutionLearningSignalError",
    "LearningStateExecutionLearningSignalKind",
    "LearningStateExecutionLearningSignal",
    "LearningStateExecutionLearningSignalService",
]
