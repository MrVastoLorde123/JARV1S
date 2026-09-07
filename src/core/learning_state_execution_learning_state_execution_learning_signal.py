"""M23.157: convert one evaluated execution-feedback artifact into bounded learning-signal evidence."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_execution_evaluation import (
    LearningStateExecutionEvaluation,
    LearningStateExecutionEvaluationStatus,
)


class LearningStateExecutionLearningSignalError(RuntimeError):
    """Raised when a bounded learning signal cannot be formed safely."""


class LearningStateExecutionLearningSignalKind(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class LearningStateExecutionLearningSignalStatus(str, Enum):
    RECORDED = "RECORDED"
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
class LearningStateExecutionLearningSignal:
    """Immutable learning-signal evidence for a later learning mechanism."""

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
    authorization_scope: Any
    outcome_status: Any
    outcome_observation: Any
    feedback_signal: Any
    feedback_purpose: str
    feedback_rationale: Any
    objective: str
    evaluator_id: str
    evaluation_purpose: str
    evaluation_judgment: Any
    evaluation_context: Any
    signal_kind: LearningStateExecutionLearningSignalKind
    signal_purpose: str
    signal_context: Any
    payload: Any
    status: LearningStateExecutionLearningSignalStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id",
            "eligibility_id", "handling_id", "consumption_id", "receipt_id", "handoff_id", "integrity_id",
            "validation_id", "semantic_use_id", "source_request_id", "source_request_lineage_id",
            "source_validation_id", "source_validation_lineage_id", "interpretation_id", "read_id",
            "consumption_request_id", "requester_id", "consumer_id", "handoff_target_id", "recipient_id",
            "handling_target_id", "execution_target_id", "feedback_purpose", "objective", "evaluator_id",
            "evaluation_purpose", "signal_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.signal_kind, LearningStateExecutionLearningSignalKind):
            raise TypeError("signal_kind must be a learning-signal kind")
        if not isinstance(self.status, LearningStateExecutionLearningSignalStatus):
            raise TypeError("status must be a learning-signal status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "authorization_scope", _freeze(self.authorization_scope))
        object.__setattr__(self, "outcome_observation", _freeze(self.outcome_observation))
        object.__setattr__(self, "feedback_signal", _freeze(self.feedback_signal))
        object.__setattr__(self, "feedback_rationale", _freeze(self.feedback_rationale))
        object.__setattr__(self, "evaluation_judgment", _freeze(self.evaluation_judgment))
        object.__setattr__(self, "evaluation_context", _freeze(self.evaluation_context))
        object.__setattr__(self, "signal_context", _freeze(self.signal_context))
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_recorded(self) -> bool:
        return self.status is LearningStateExecutionLearningSignalStatus.RECORDED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningSignalStatus.REJECTED

    @property
    def mutates_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
        return False

    @property
    def reads_durable_state(self) -> bool:
        return False

    @property
    def rereads_durable_state(self) -> bool:
        return False

    @property
    def interprets_state(self) -> bool:
        return False

    @property
    def is_learning(self) -> bool:
        return False

    @property
    def applies_learning(self) -> bool:
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


class LearningStateExecutionLearningSignalService:
    """Create inert learning-signal evidence from one evaluated execution-feedback evaluation."""

    def create(
        self,
        evaluation: LearningStateExecutionEvaluation,
        *,
        signal_id: str,
        signal_kind: LearningStateExecutionLearningSignalKind,
        signal_purpose: str,
        signal_context: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningSignal:
        if type(evaluation) is not LearningStateExecutionEvaluation:
            raise TypeError("evaluation must be an execution-evaluation artifact")
        if not isinstance(signal_kind, LearningStateExecutionLearningSignalKind):
            raise TypeError("signal_kind must be a learning-signal kind")
        for name, value in (("signal_id", signal_id), ("signal_purpose", signal_purpose)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if signal_context is None:
            raise ValueError("signal_context must be provided")

        checks: list[str] = []
        if evaluation.status is not LearningStateExecutionEvaluationStatus.EVALUATED:
            checks.append("execution evaluation status must be EVALUATED")
        if signal_id == evaluation.evaluation_id:
            checks.append("signal identity must be distinct")

        anchored = (
            ("evaluation_id", evaluation.evaluation_id, "evaluation lineage mismatch"),
            ("feedback_id", evaluation.feedback_id, "feedback lineage mismatch"),
            ("outcome_id", evaluation.outcome_id, "outcome lineage mismatch"),
            ("attempt_id", evaluation.attempt_id, "attempt lineage mismatch"),
            ("admission_id", evaluation.admission_id, "admission lineage mismatch"),
            ("eligibility_id", evaluation.eligibility_id, "eligibility lineage mismatch"),
            ("handling_id", evaluation.handling_id, "handling lineage mismatch"),
            ("consumption_id", evaluation.consumption_id, "consumption lineage mismatch"),
            ("receipt_id", evaluation.receipt_id, "receipt lineage mismatch"),
            ("handoff_id", evaluation.handoff_id, "handoff lineage mismatch"),
            ("integrity_id", evaluation.integrity_id, "integrity lineage mismatch"),
            ("validation_id", evaluation.validation_id, "validation lineage mismatch"),
            ("semantic_use_id", evaluation.semantic_use_id, "semantic-use lineage mismatch"),
            ("request_id", evaluation.source_request_lineage_id, "source request lineage mismatch"),
            ("source_validation_id", evaluation.source_validation_lineage_id, "source validation lineage mismatch"),
            ("interpretation_id", evaluation.interpretation_id, "interpretation lineage mismatch"),
            ("source_request_provenance_id", evaluation.source_request_id, "source request provenance mismatch"),
            ("source_validation_provenance_id", evaluation.source_validation_id, "source validation provenance mismatch"),
            ("read_id", evaluation.read_id, "read lineage mismatch"),
            ("consumption_request_id", evaluation.consumption_request_id, "consumption request lineage mismatch"),
        )
        checks.extend(
            message
            for key, expected, message in anchored
            if evaluation.lineage.get(key, expected) != expected
        )

        valid = not checks
        status = LearningStateExecutionLearningSignalStatus.RECORDED if valid else LearningStateExecutionLearningSignalStatus.REJECTED
        final_reasons = reasons if reasons is not None else (("learning signal recorded from evaluated execution feedback",) if valid else tuple(checks))
        payload = (
            {"evaluation_id": evaluation.evaluation_id, "signal_kind": signal_kind.value, "signal_context": signal_context}
            if valid else {"rejected_evaluation": True}
        )
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
            semantic_use_id=evaluation.semantic_use_id,
            source_request_id=evaluation.source_request_id,
            source_request_lineage_id=evaluation.source_request_lineage_id,
            source_validation_id=evaluation.source_validation_id,
            source_validation_lineage_id=evaluation.source_validation_lineage_id,
            interpretation_id=evaluation.interpretation_id,
            read_id=evaluation.read_id,
            consumption_request_id=evaluation.consumption_request_id,
            requester_id=evaluation.requester_id,
            consumer_id=evaluation.consumer_id,
            handoff_target_id=evaluation.handoff_target_id,
            recipient_id=evaluation.recipient_id,
            handling_target_id=evaluation.handling_target_id,
            execution_target_id=evaluation.execution_target_id,
            authorization_scope=evaluation.authorization_scope,
            outcome_status=evaluation.outcome_status,
            outcome_observation=evaluation.outcome_observation,
            feedback_signal=evaluation.feedback_signal,
            feedback_purpose=evaluation.feedback_purpose,
            feedback_rationale=evaluation.feedback_rationale,
            objective=evaluation.objective,
            evaluator_id=evaluation.evaluator_id,
            evaluation_purpose=evaluation.evaluation_purpose,
            evaluation_judgment=evaluation.evaluation_judgment,
            evaluation_context=evaluation.evaluation_context,
            signal_kind=signal_kind,
            signal_purpose=signal_purpose,
            signal_context=signal_context,
            payload=payload,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "signal_id": signal_id,
                "evaluation_id": evaluation.evaluation_id,
                "feedback_id": evaluation.feedback_id,
                "outcome_id": evaluation.outcome_id,
                "attempt_id": evaluation.attempt_id,
                "admission_id": evaluation.admission_id,
                "eligibility_id": evaluation.eligibility_id,
                "handling_id": evaluation.handling_id,
                "consumption_id": evaluation.consumption_id,
                "receipt_id": evaluation.receipt_id,
                "handoff_id": evaluation.handoff_id,
                "integrity_id": evaluation.integrity_id,
                "validation_id": evaluation.validation_id,
                "semantic_use_id": evaluation.semantic_use_id,
                "request_id": evaluation.source_request_lineage_id,
                "source_validation_id": evaluation.source_validation_lineage_id,
                "interpretation_id": evaluation.interpretation_id,
                "source_request_provenance_id": evaluation.source_request_id,
                "source_validation_provenance_id": evaluation.source_validation_id,
                "read_id": evaluation.read_id,
                "consumption_request_id": evaluation.consumption_request_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningSignalError",
    "LearningStateExecutionLearningSignalKind",
    "LearningStateExecutionLearningSignalStatus",
    "LearningStateExecutionLearningSignal",
    "LearningStateExecutionLearningSignalService",
]
