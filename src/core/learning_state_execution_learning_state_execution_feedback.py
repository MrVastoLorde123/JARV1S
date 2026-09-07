"""M23.155: record bounded feedback from an observed execution outcome without granting authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_execution_outcome import (
    LearningStateExecutionOutcome,
    LearningStateExecutionOutcomeStatus,
)


class LearningStateExecutionFeedbackError(RuntimeError):
    """Raised when execution-feedback evidence cannot be formed safely."""


class LearningStateExecutionFeedbackStatus(str, Enum):
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
class LearningStateExecutionFeedback:
    """Immutable feedback evidence derived from one observed execution outcome."""

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
    outcome_status: LearningStateExecutionOutcomeStatus
    outcome_observation: Any
    feedback_signal: Any
    feedback_purpose: str
    feedback_rationale: Any
    payload: Any
    status: LearningStateExecutionFeedbackStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "feedback_id", "outcome_id", "attempt_id", "admission_id", "eligibility_id", "handling_id",
            "consumption_id", "receipt_id", "handoff_id", "integrity_id", "validation_id", "semantic_use_id",
            "source_request_id", "source_request_lineage_id", "source_validation_id", "source_validation_lineage_id",
            "interpretation_id", "read_id", "consumption_request_id", "requester_id", "consumer_id",
            "handoff_target_id", "recipient_id", "handling_target_id", "execution_target_id", "feedback_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.outcome_status, LearningStateExecutionOutcomeStatus):
            raise TypeError("outcome_status must be an execution-outcome status")
        if not isinstance(self.status, LearningStateExecutionFeedbackStatus):
            raise TypeError("status must be an execution-feedback status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "authorization_scope", _freeze(self.authorization_scope))
        object.__setattr__(self, "outcome_observation", _freeze(self.outcome_observation))
        object.__setattr__(self, "feedback_signal", _freeze(self.feedback_signal))
        object.__setattr__(self, "feedback_rationale", _freeze(self.feedback_rationale))
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_recorded(self) -> bool:
        return self.status is LearningStateExecutionFeedbackStatus.RECORDED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionFeedbackStatus.REJECTED

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


class LearningStateExecutionFeedbackService:
    """Record structured feedback from one terminal execution outcome only."""

    def record(
        self,
        outcome: LearningStateExecutionOutcome,
        *,
        feedback_id: str,
        feedback_signal: Any,
        feedback_purpose: str,
        feedback_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionFeedback:
        if type(outcome) is not LearningStateExecutionOutcome:
            raise TypeError("outcome must be an execution-outcome artifact")
        if not isinstance(feedback_id, str) or not feedback_id.strip():
            raise ValueError("feedback_id must be a non-empty string")
        if feedback_signal is None:
            raise ValueError("feedback_signal must be provided")
        if not isinstance(feedback_purpose, str) or not feedback_purpose.strip():
            raise ValueError("feedback_purpose must be a non-empty string")
        if feedback_rationale is None:
            raise ValueError("feedback_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if outcome.status not in (LearningStateExecutionOutcomeStatus.SUCCEEDED, LearningStateExecutionOutcomeStatus.FAILED):
            checks.append("execution outcome status must be SUCCEEDED or FAILED")
        if feedback_id == outcome.outcome_id:
            checks.append("feedback identity must be distinct")

        lineage_outcome_id = outcome.lineage.get("outcome_id", outcome.outcome_id)
        lineage_attempt_id = outcome.lineage.get("attempt_id", outcome.attempt_id)
        lineage_admission_id = outcome.lineage.get("admission_id", outcome.admission_id)
        lineage_eligibility_id = outcome.lineage.get("eligibility_id", outcome.eligibility_id)
        lineage_handling_id = outcome.lineage.get("handling_id", outcome.handling_id)
        lineage_consumption_id = outcome.lineage.get("consumption_id", outcome.consumption_id)
        lineage_receipt_id = outcome.lineage.get("receipt_id", outcome.receipt_id)
        lineage_handoff_id = outcome.lineage.get("handoff_id", outcome.handoff_id)
        lineage_integrity_id = outcome.lineage.get("integrity_id", outcome.integrity_id)
        lineage_validation_id = outcome.lineage.get("validation_id", outcome.validation_id)
        lineage_semantic_use_id = outcome.lineage.get("semantic_use_id", outcome.semantic_use_id)
        lineage_request_id = outcome.lineage.get("request_id", outcome.source_request_lineage_id)
        lineage_source_validation_id = outcome.lineage.get("source_validation_id", outcome.source_validation_lineage_id)
        lineage_interpretation_id = outcome.lineage.get("interpretation_id", outcome.interpretation_id)
        lineage_source_request_id = outcome.lineage.get("source_request_id", outcome.source_request_id)
        lineage_source_validation_provenance_id = outcome.lineage.get("source_validation_provenance_id", outcome.source_validation_id)
        lineage_read_id = outcome.lineage.get("read_id", outcome.read_id)
        lineage_consumption_request_id = outcome.lineage.get("consumption_request_id", outcome.consumption_request_id)

        checks.extend(
            message for actual, expected, message in (
                (lineage_outcome_id, outcome.outcome_id, "outcome lineage mismatch"),
                (lineage_attempt_id, outcome.attempt_id, "attempt lineage mismatch"),
                (lineage_admission_id, outcome.admission_id, "admission lineage mismatch"),
                (lineage_eligibility_id, outcome.eligibility_id, "eligibility lineage mismatch"),
                (lineage_handling_id, outcome.handling_id, "handling lineage mismatch"),
                (lineage_consumption_id, outcome.consumption_id, "consumption lineage mismatch"),
                (lineage_receipt_id, outcome.receipt_id, "receipt lineage mismatch"),
                (lineage_handoff_id, outcome.handoff_id, "handoff lineage mismatch"),
                (lineage_integrity_id, outcome.integrity_id, "integrity lineage mismatch"),
                (lineage_validation_id, outcome.validation_id, "validation lineage mismatch"),
                (lineage_semantic_use_id, outcome.semantic_use_id, "semantic-use lineage mismatch"),
                (lineage_request_id, outcome.source_request_lineage_id, "source request lineage mismatch"),
                (lineage_source_validation_id, outcome.source_validation_lineage_id, "source validation lineage mismatch"),
                (lineage_interpretation_id, outcome.interpretation_id, "interpretation lineage mismatch"),
                (lineage_source_request_id, outcome.source_request_id, "source request provenance mismatch"),
                (lineage_source_validation_provenance_id, outcome.source_validation_id, "source validation provenance mismatch"),
                (lineage_read_id, outcome.read_id, "read lineage mismatch"),
                (lineage_consumption_request_id, outcome.consumption_request_id, "consumption request lineage mismatch"),
            ) if actual != expected
        )

        valid = not checks
        payload = {"outcome_id": outcome.outcome_id, "feedback_signal": feedback_signal} if valid else {"rejected_outcome": True}
        final_reasons = reasons if reasons is not None else (("execution feedback recorded from observed outcome",) if valid else tuple(checks))
        status = LearningStateExecutionFeedbackStatus.RECORDED if valid else LearningStateExecutionFeedbackStatus.REJECTED
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
            semantic_use_id=outcome.semantic_use_id,
            source_request_id=outcome.source_request_id,
            source_request_lineage_id=outcome.source_request_lineage_id,
            source_validation_id=outcome.source_validation_id,
            source_validation_lineage_id=outcome.source_validation_lineage_id,
            interpretation_id=outcome.interpretation_id,
            read_id=outcome.read_id,
            consumption_request_id=outcome.consumption_request_id,
            requester_id=outcome.requester_id,
            consumer_id=outcome.consumer_id,
            handoff_target_id=outcome.handoff_target_id,
            recipient_id=outcome.recipient_id,
            handling_target_id=outcome.handling_target_id,
            execution_target_id=outcome.execution_target_id,
            authorization_scope=outcome.authorization_scope,
            outcome_status=outcome.outcome_status,
            outcome_observation=outcome.outcome_observation,
            feedback_signal=feedback_signal,
            feedback_purpose=feedback_purpose,
            feedback_rationale=feedback_rationale,
            payload=payload,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "feedback_id": feedback_id,
                "outcome_id": outcome.outcome_id,
                "attempt_id": outcome.attempt_id,
                "admission_id": outcome.admission_id,
                "eligibility_id": outcome.eligibility_id,
                "handling_id": outcome.handling_id,
                "consumption_id": outcome.consumption_id,
                "receipt_id": outcome.receipt_id,
                "handoff_id": outcome.handoff_id,
                "integrity_id": outcome.integrity_id,
                "validation_id": outcome.validation_id,
                "semantic_use_id": outcome.semantic_use_id,
                "request_id": outcome.source_request_lineage_id,
                "source_validation_id": outcome.source_validation_lineage_id,
                "interpretation_id": outcome.interpretation_id,
                "source_request_id": outcome.source_request_id,
                "source_validation_provenance_id": outcome.source_validation_id,
                "read_id": outcome.read_id,
                "consumption_request_id": outcome.consumption_request_id,
                "execution_target_id": outcome.execution_target_id,
            },
        )


__all__ = [
    "LearningStateExecutionFeedbackError",
    "LearningStateExecutionFeedbackStatus",
    "LearningStateExecutionFeedback",
    "LearningStateExecutionFeedbackService",
]
