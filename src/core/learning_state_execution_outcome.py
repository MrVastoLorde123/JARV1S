"""M23.122: record explicit observed consequences of execution attempts."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_admission import LearningStateExecutionAdmissionStatus
from src.core.learning_state_execution_attempt import (
    LearningStateExecutionAttempt,
    LearningStateExecutionAttemptStatus,
)


class LearningStateExecutionOutcomeError(RuntimeError):
    """Raised when execution outcome evidence cannot be formed safely."""


class LearningStateExecutionOutcomeStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PARTIAL = "PARTIAL"
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
class LearningStateExecutionOutcome:
    """Immutable evidence of an explicitly observed consequence after attempted execution."""

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
    admission_status: LearningStateExecutionAdmissionStatus
    attempt_status: LearningStateExecutionAttemptStatus
    outcome_status: LearningStateExecutionOutcomeStatus
    executor_output: Any
    failure_type: str | None
    failure_message: str | None
    observed_consequence: Any
    observation_source_id: str
    observation_purpose: str
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "outcome_id", "attempt_id", "admission_id", "eligibility_id", "handling_id", "consumption_id",
            "receipt_id", "handoff_id", "integrity_id", "validation_id", "use_id", "request_id",
            "interpretation_id", "source_request_id", "read_validation_id", "read_id", "consumption_request_id",
            "source_validation_id", "source_integrity_id", "transition_id", "evidence_id", "application_id",
            "state_key", "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint",
            "consumer_id", "use_purpose", "downstream_recipient_id", "downstream_handler_id",
            "handling_purpose", "execution_target_id", "execution_purpose", "observation_source_id",
            "observation_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("execution outcome requires SHA-256 fingerprints")
        if not isinstance(self.admission_status, LearningStateExecutionAdmissionStatus):
            raise TypeError("admission_status must be an execution-admission status")
        if not isinstance(self.attempt_status, LearningStateExecutionAttemptStatus):
            raise TypeError("attempt_status must be an execution-attempt status")
        if not isinstance(self.outcome_status, LearningStateExecutionOutcomeStatus):
            raise TypeError("outcome_status must be an execution-outcome status")
        if self.attempt_status is LearningStateExecutionAttemptStatus.REJECTED:
            raise ValueError("an execution outcome requires an attempt that invoked the executor")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "executor_output", _freeze(self.executor_output))
        object.__setattr__(self, "observed_consequence", _freeze(self.observed_consequence))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_observed(self) -> bool:
        return True

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
    def schedules_work(self) -> bool:
        return False

    @property
    def plans_work(self) -> bool:
        return False

    @property
    def transforms_semantic_result(self) -> bool:
        return False

    @property
    def interprets_semantic_result(self) -> bool:
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


class LearningStateExecutionOutcomeService:
    """Record explicit observation evidence after an execution attempt without interpreting it."""

    def observe(
        self,
        attempt: LearningStateExecutionAttempt,
        *,
        outcome_id: str,
        outcome_status: LearningStateExecutionOutcomeStatus,
        observed_consequence: Any,
        observation_source_id: str,
        observation_purpose: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionOutcome:
        if type(attempt) is not LearningStateExecutionAttempt:
            raise TypeError("attempt must be an execution-attempt artifact")
        if not isinstance(outcome_status, LearningStateExecutionOutcomeStatus):
            raise TypeError("outcome_status must be an execution-outcome status")
        for name, value in (
            ("outcome_id", outcome_id),
            ("observation_source_id", observation_source_id),
            ("observation_purpose", observation_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if attempt.attempt_status is LearningStateExecutionAttemptStatus.REJECTED or not attempt.invokes_executor:
            raise ValueError("execution outcome requires an attempt that invoked the executor")
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
            use_id=attempt.use_id,
            request_id=attempt.request_id,
            interpretation_id=attempt.interpretation_id,
            source_request_id=attempt.source_request_id,
            read_validation_id=attempt.read_validation_id,
            read_id=attempt.read_id,
            consumption_request_id=attempt.consumption_request_id,
            source_validation_id=attempt.source_validation_id,
            source_integrity_id=attempt.source_integrity_id,
            transition_id=attempt.transition_id,
            evidence_id=attempt.evidence_id,
            application_id=attempt.application_id,
            state_key=attempt.state_key,
            transition_fingerprint=attempt.transition_fingerprint,
            source_application_fingerprint=attempt.source_application_fingerprint,
            computed_application_fingerprint=attempt.computed_application_fingerprint,
            confidence=attempt.confidence,
            consumer_id=attempt.consumer_id,
            use_purpose=attempt.use_purpose,
            downstream_recipient_id=attempt.downstream_recipient_id,
            downstream_handler_id=attempt.downstream_handler_id,
            handling_purpose=attempt.handling_purpose,
            execution_target_id=attempt.execution_target_id,
            execution_purpose=attempt.execution_purpose,
            admission_status=attempt.admission_status,
            attempt_status=attempt.attempt_status,
            outcome_status=outcome_status,
            executor_output=attempt.executor_output,
            failure_type=attempt.failure_type,
            failure_message=attempt.failure_message,
            observed_consequence=observed_consequence,
            observation_source_id=observation_source_id,
            observation_purpose=observation_purpose,
            reasons=reasons if reasons is not None else {"outcome_status": outcome_status.value},
            lineage=lineage if lineage is not None else {"outcome_id": outcome_id, "attempt_id": attempt.attempt_id},
        )


__all__ = [
    "LearningStateExecutionOutcomeError",
    "LearningStateExecutionOutcomeStatus",
    "LearningStateExecutionOutcome",
    "LearningStateExecutionOutcomeService",
]
