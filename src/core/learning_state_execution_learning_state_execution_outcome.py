"""M23.154: record one observed execution outcome without granting downstream authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_execution_attempt import (
    LearningStateExecutionAttempt,
    LearningStateExecutionAttemptStatus,
)


class LearningStateExecutionOutcomeError(RuntimeError):
    """Raised when execution-outcome evidence cannot be formed safely."""


class LearningStateExecutionOutcomeStatus(str, Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
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
class LearningStateExecutionOutcome:
    """Immutable evidence describing one observed result of a bounded execution attempt."""

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
    authority_basis: Any
    outcome_status: LearningStateExecutionOutcomeStatus
    outcome_observation: Any
    outcome_purpose: str
    outcome_rationale: Any
    payload: Any
    status: LearningStateExecutionOutcomeStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "outcome_id", "attempt_id", "admission_id", "eligibility_id", "handling_id", "consumption_id",
            "receipt_id", "handoff_id", "integrity_id", "validation_id", "semantic_use_id", "source_request_id",
            "source_request_lineage_id", "source_validation_id", "source_validation_lineage_id", "interpretation_id",
            "read_id", "consumption_request_id", "requester_id", "consumer_id", "handoff_target_id", "recipient_id",
            "handling_target_id", "execution_target_id", "outcome_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.outcome_status, LearningStateExecutionOutcomeStatus):
            raise TypeError("outcome_status must be an execution-outcome status")
        if not isinstance(self.status, LearningStateExecutionOutcomeStatus):
            raise TypeError("status must be an execution-outcome status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "authorization_scope", _freeze(self.authorization_scope))
        object.__setattr__(self, "authority_basis", _freeze(self.authority_basis))
        object.__setattr__(self, "outcome_observation", _freeze(self.outcome_observation))
        object.__setattr__(self, "outcome_rationale", _freeze(self.outcome_rationale))
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_succeeded(self) -> bool:
        return self.status is LearningStateExecutionOutcomeStatus.SUCCEEDED

    @property
    def is_failed(self) -> bool:
        return self.status is LearningStateExecutionOutcomeStatus.FAILED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionOutcomeStatus.REJECTED

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


class LearningStateExecutionOutcomeService:
    """Record an observed result of one admitted execution attempt without adding authority."""

    def record(
        self,
        attempt: LearningStateExecutionAttempt,
        *,
        outcome_id: str,
        execution_target_id: str,
        outcome_status: LearningStateExecutionOutcomeStatus,
        outcome_observation: Any,
        outcome_purpose: str,
        outcome_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionOutcome:
        if type(attempt) is not LearningStateExecutionAttempt:
            raise TypeError("attempt must be an execution-attempt artifact")
        for name, value in (
            ("outcome_id", outcome_id),
            ("execution_target_id", execution_target_id),
            ("outcome_purpose", outcome_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(outcome_status, LearningStateExecutionOutcomeStatus):
            raise TypeError("outcome_status must be an execution-outcome status")
        if outcome_observation is None:
            raise ValueError("outcome_observation must be provided")
        if outcome_rationale is None:
            raise ValueError("outcome_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if attempt.status is not LearningStateExecutionAttemptStatus.ATTEMPTED:
            checks.append("execution attempt status must be ATTEMPTED")
        if outcome_id == attempt.attempt_id:
            checks.append("outcome identity must be distinct")
        if execution_target_id != attempt.execution_target_id:
            checks.append("execution target must match attempt")

        lineage_attempt_id = attempt.lineage.get("attempt_id", attempt.attempt_id)
        lineage_admission_id = attempt.lineage.get("admission_id", attempt.admission_id)
        lineage_eligibility_id = attempt.lineage.get("eligibility_id", attempt.eligibility_id)
        lineage_handling_id = attempt.lineage.get("handling_id", attempt.handling_id)
        lineage_consumption_id = attempt.lineage.get("consumption_id", attempt.consumption_id)
        lineage_receipt_id = attempt.lineage.get("receipt_id", attempt.receipt_id)
        lineage_handoff_id = attempt.lineage.get("handoff_id", attempt.handoff_id)
        lineage_integrity_id = attempt.lineage.get("integrity_id", attempt.integrity_id)
        lineage_validation_id = attempt.lineage.get("validation_id", attempt.validation_id)
        lineage_semantic_use_id = attempt.lineage.get("semantic_use_id", attempt.semantic_use_id)
        lineage_request_id = attempt.lineage.get("request_id", attempt.source_request_lineage_id)
        lineage_source_validation_id = attempt.lineage.get("source_validation_id", attempt.source_validation_lineage_id)
        lineage_interpretation_id = attempt.lineage.get("interpretation_id", attempt.interpretation_id)
        lineage_source_request_id = attempt.lineage.get("source_request_id", attempt.source_request_id)
        lineage_source_validation_provenance_id = attempt.lineage.get("source_validation_provenance_id", attempt.source_validation_id)
        lineage_read_id = attempt.lineage.get("read_id", attempt.read_id)
        lineage_consumption_request_id = attempt.lineage.get("consumption_request_id", attempt.consumption_request_id)

        if lineage_attempt_id != attempt.attempt_id:
            checks.append("attempt lineage mismatch")
        if lineage_admission_id != attempt.admission_id:
            checks.append("admission lineage mismatch")
        if lineage_eligibility_id != attempt.eligibility_id:
            checks.append("eligibility lineage mismatch")
        if lineage_handling_id != attempt.handling_id:
            checks.append("handling lineage mismatch")
        if lineage_consumption_id != attempt.consumption_id:
            checks.append("consumption lineage mismatch")
        if lineage_receipt_id != attempt.receipt_id:
            checks.append("receipt lineage mismatch")
        if lineage_handoff_id != attempt.handoff_id:
            checks.append("handoff lineage mismatch")
        if lineage_integrity_id != attempt.integrity_id:
            checks.append("integrity lineage mismatch")
        if lineage_validation_id != attempt.validation_id:
            checks.append("validation lineage mismatch")
        if lineage_semantic_use_id != attempt.semantic_use_id:
            checks.append("semantic-use lineage mismatch")
        if lineage_request_id != attempt.source_request_lineage_id:
            checks.append("source request lineage mismatch")
        if lineage_source_validation_id != attempt.source_validation_lineage_id:
            checks.append("source validation lineage mismatch")
        if lineage_interpretation_id != attempt.interpretation_id:
            checks.append("interpretation lineage mismatch")
        if lineage_source_request_id != attempt.source_request_id:
            checks.append("source request provenance mismatch")
        if lineage_source_validation_provenance_id != attempt.source_validation_id:
            checks.append("source validation provenance mismatch")
        if lineage_read_id != attempt.read_id:
            checks.append("read lineage mismatch")
        if lineage_consumption_request_id != attempt.consumption_request_id:
            checks.append("consumption request lineage mismatch")

        valid = not checks
        effective_status = outcome_status if valid else LearningStateExecutionOutcomeStatus.REJECTED
        payload = (
            {"attempt_id": attempt.attempt_id, "execution_target_id": execution_target_id, "outcome_status": outcome_status.value}
            if valid else {"rejected_attempt": True}
        )
        final_reasons = reasons if reasons is not None else (("observed execution outcome recorded for declared attempt",) if valid else tuple(checks))
        return LearningStateExecutionOutcome(
            outcome_id=outcome_id,
            attempt_id=attempt.attempt_id,
            admission_id=attempt.admission_id,
            eligibility_id=attempt.eligibility_id,
            handling_id=attempt.handling_id,
            consumption_id=attempt.consumption_id,
            receipt_id=attempt.receipt_id,
            handoff_id=attempt.handoff_id,
            integrity_id=attempt.integrity_id,
            validation_id=attempt.validation_id,
            semantic_use_id=attempt.semantic_use_id,
            source_request_id=attempt.source_request_id,
            source_request_lineage_id=attempt.source_request_lineage_id,
            source_validation_id=attempt.source_validation_id,
            source_validation_lineage_id=attempt.source_validation_lineage_id,
            interpretation_id=attempt.interpretation_id,
            read_id=attempt.read_id,
            consumption_request_id=attempt.consumption_request_id,
            requester_id=attempt.requester_id,
            consumer_id=attempt.consumer_id,
            handoff_target_id=attempt.handoff_target_id,
            recipient_id=attempt.recipient_id,
            handling_target_id=attempt.handling_target_id,
            execution_target_id=execution_target_id,
            authorization_scope=attempt.authorization_scope,
            authority_basis=attempt.authority_basis,
            outcome_status=effective_status,
            outcome_observation=outcome_observation,
            outcome_purpose=outcome_purpose,
            outcome_rationale=outcome_rationale,
            payload=payload,
            status=effective_status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "outcome_id": outcome_id,
                "attempt_id": attempt.attempt_id,
                "admission_id": attempt.admission_id,
                "eligibility_id": attempt.eligibility_id,
                "handling_id": attempt.handling_id,
                "consumption_id": attempt.consumption_id,
                "receipt_id": attempt.receipt_id,
                "handoff_id": attempt.handoff_id,
                "integrity_id": attempt.integrity_id,
                "validation_id": attempt.validation_id,
                "semantic_use_id": attempt.semantic_use_id,
                "request_id": attempt.source_request_lineage_id,
                "source_validation_id": attempt.source_validation_lineage_id,
                "interpretation_id": attempt.interpretation_id,
                "source_request_id": attempt.source_request_id,
                "source_validation_provenance_id": attempt.source_validation_id,
                "read_id": attempt.read_id,
                "consumption_request_id": attempt.consumption_request_id,
                "execution_target_id": execution_target_id,
            },
        )


__all__ = [
    "LearningStateExecutionOutcomeError",
    "LearningStateExecutionOutcomeStatus",
    "LearningStateExecutionOutcome",
    "LearningStateExecutionOutcomeService",
]
