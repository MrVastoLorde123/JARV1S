"""M23.156: evaluate one recorded execution-feedback artifact against an explicit objective."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_execution_feedback import (
    LearningStateExecutionFeedback,
    LearningStateExecutionFeedbackStatus,
)


class LearningStateExecutionEvaluationError(RuntimeError):
    """Raised when bounded evaluation evidence cannot be formed safely."""


class LearningStateExecutionEvaluationStatus(str, Enum):
    EVALUATED = "EVALUATED"
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
class LearningStateExecutionEvaluation:
    """Immutable evaluation evidence derived from one recorded execution feedback artifact."""

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
    payload: Any
    status: LearningStateExecutionEvaluationStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id", "eligibility_id",
            "handling_id", "consumption_id", "receipt_id", "handoff_id", "integrity_id", "validation_id",
            "semantic_use_id", "source_request_id", "source_request_lineage_id", "source_validation_id",
            "source_validation_lineage_id", "interpretation_id", "read_id", "consumption_request_id",
            "requester_id", "consumer_id", "handoff_target_id", "recipient_id", "handling_target_id",
            "execution_target_id", "feedback_purpose", "objective", "evaluator_id", "evaluation_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, LearningStateExecutionEvaluationStatus):
            raise TypeError("status must be an execution-evaluation status")
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
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_evaluated(self) -> bool:
        return self.status is LearningStateExecutionEvaluationStatus.EVALUATED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionEvaluationStatus.REJECTED

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
    def is_learning(self) -> bool:
        return False

    @property
    def applies_learning(self) -> bool:
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


class LearningStateExecutionEvaluationService:
    """Evaluate exactly one recorded execution-feedback artifact without granting downstream authority."""

    def evaluate(
        self,
        feedback: LearningStateExecutionFeedback,
        *,
        evaluation_id: str,
        objective: str,
        evaluator_id: str,
        evaluation_purpose: str,
        evaluation_judgment: Any,
        evaluation_context: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionEvaluation:
        if type(feedback) is not LearningStateExecutionFeedback:
            raise TypeError("feedback must be an execution-feedback artifact")
        for name, value in (
            ("evaluation_id", evaluation_id),
            ("objective", objective),
            ("evaluator_id", evaluator_id),
            ("evaluation_purpose", evaluation_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if evaluation_judgment is None:
            raise ValueError("evaluation_judgment must be provided")
        if evaluation_context is None:
            raise ValueError("evaluation_context must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if feedback.status is not LearningStateExecutionFeedbackStatus.RECORDED:
            checks.append("execution feedback status must be RECORDED")
        if evaluation_id == feedback.feedback_id:
            checks.append("evaluation identity must be distinct")

        anchored = (
            ("feedback_id", feedback.feedback_id, "feedback lineage mismatch"),
            ("outcome_id", feedback.outcome_id, "outcome lineage mismatch"),
            ("attempt_id", feedback.attempt_id, "attempt lineage mismatch"),
            ("admission_id", feedback.admission_id, "admission lineage mismatch"),
            ("eligibility_id", feedback.eligibility_id, "eligibility lineage mismatch"),
            ("handling_id", feedback.handling_id, "handling lineage mismatch"),
            ("consumption_id", feedback.consumption_id, "consumption lineage mismatch"),
            ("receipt_id", feedback.receipt_id, "receipt lineage mismatch"),
            ("handoff_id", feedback.handoff_id, "handoff lineage mismatch"),
            ("integrity_id", feedback.integrity_id, "integrity lineage mismatch"),
            ("validation_id", feedback.validation_id, "validation lineage mismatch"),
            ("semantic_use_id", feedback.semantic_use_id, "semantic-use lineage mismatch"),
            ("request_id", feedback.source_request_lineage_id, "source request lineage mismatch"),
            ("source_validation_id", feedback.source_validation_lineage_id, "source validation lineage mismatch"),
            ("interpretation_id", feedback.interpretation_id, "interpretation lineage mismatch"),
            ("source_request_id", feedback.source_request_id, "source request provenance mismatch"),
            ("source_validation_provenance_id", feedback.source_validation_id, "source validation provenance mismatch"),
            ("read_id", feedback.read_id, "read lineage mismatch"),
            ("consumption_request_id", feedback.consumption_request_id, "consumption request lineage mismatch"),
        )
        checks.extend(
            message
            for key, expected, message in anchored
            if feedback.lineage.get(key, expected) != expected
        )

        valid = not checks
        status = LearningStateExecutionEvaluationStatus.EVALUATED if valid else LearningStateExecutionEvaluationStatus.REJECTED
        final_reasons = reasons if reasons is not None else (("execution feedback evaluated against explicit objective",) if valid else tuple(checks))
        payload = {"feedback_id": feedback.feedback_id, "objective": objective, "evaluation_judgment": evaluation_judgment} if valid else {"rejected_feedback": True}
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
            semantic_use_id=feedback.semantic_use_id,
            source_request_id=feedback.source_request_id,
            source_request_lineage_id=feedback.source_request_lineage_id,
            source_validation_id=feedback.source_validation_id,
            source_validation_lineage_id=feedback.source_validation_lineage_id,
            interpretation_id=feedback.interpretation_id,
            read_id=feedback.read_id,
            consumption_request_id=feedback.consumption_request_id,
            requester_id=feedback.requester_id,
            consumer_id=feedback.consumer_id,
            handoff_target_id=feedback.handoff_target_id,
            recipient_id=feedback.recipient_id,
            handling_target_id=feedback.handling_target_id,
            execution_target_id=feedback.execution_target_id,
            authorization_scope=feedback.authorization_scope,
            outcome_status=feedback.outcome_status,
            outcome_observation=feedback.outcome_observation,
            feedback_signal=feedback.feedback_signal,
            feedback_purpose=feedback.feedback_purpose,
            feedback_rationale=feedback.feedback_rationale,
            objective=objective,
            evaluator_id=evaluator_id,
            evaluation_purpose=evaluation_purpose,
            evaluation_judgment=evaluation_judgment,
            evaluation_context=evaluation_context,
            payload=payload,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "evaluation_id": evaluation_id,
                "feedback_id": feedback.feedback_id,
                "outcome_id": feedback.outcome_id,
                "attempt_id": feedback.attempt_id,
                "admission_id": feedback.admission_id,
                "eligibility_id": feedback.eligibility_id,
                "handling_id": feedback.handling_id,
                "consumption_id": feedback.consumption_id,
                "receipt_id": feedback.receipt_id,
                "handoff_id": feedback.handoff_id,
                "integrity_id": feedback.integrity_id,
                "validation_id": feedback.validation_id,
                "semantic_use_id": feedback.semantic_use_id,
                "request_id": feedback.source_request_lineage_id,
                "source_validation_id": feedback.source_validation_lineage_id,
                "interpretation_id": feedback.interpretation_id,
                "source_request_provenance_id": feedback.source_request_id,
                "source_validation_provenance_id": feedback.source_validation_id,
                "read_id": feedback.read_id,
                "consumption_request_id": feedback.consumption_request_id,
            },
        )


__all__ = [
    "LearningStateExecutionEvaluationError",
    "LearningStateExecutionEvaluationStatus",
    "LearningStateExecutionEvaluation",
    "LearningStateExecutionEvaluationService",
]
