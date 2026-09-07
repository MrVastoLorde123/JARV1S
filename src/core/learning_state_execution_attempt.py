"""M23.121: attempt authorized execution through an injected executor."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping

from src.core.learning_state_execution_admission import (
    LearningStateExecutionAdmission,
    LearningStateExecutionAdmissionStatus,
)


class LearningStateExecutionAttemptError(RuntimeError):
    """Raised when an execution attempt cannot be formed safely."""


class LearningStateExecutionAttemptStatus(str, Enum):
    ATTEMPTED = "ATTEMPTED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


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
class LearningStateExecutionAttempt:
    """Immutable evidence that authorized execution was attempted."""

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
    executor_output: Any
    failure_type: str | None
    failure_message: str | None
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "attempt_id", "admission_id", "eligibility_id", "handling_id", "consumption_id", "receipt_id",
            "handoff_id", "integrity_id", "validation_id", "use_id", "request_id", "interpretation_id",
            "source_request_id", "read_validation_id", "read_id", "consumption_request_id",
            "source_validation_id", "source_integrity_id", "transition_id", "evidence_id", "application_id",
            "state_key", "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint",
            "consumer_id", "use_purpose", "downstream_recipient_id", "downstream_handler_id",
            "handling_purpose", "execution_target_id", "execution_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("execution attempt requires SHA-256 fingerprints")
        if not isinstance(self.admission_status, LearningStateExecutionAdmissionStatus):
            raise TypeError("admission_status must be an execution-admission status")
        if not isinstance(self.attempt_status, LearningStateExecutionAttemptStatus):
            raise TypeError("attempt_status must be an execution-attempt status")
        if self.attempt_status is LearningStateExecutionAttemptStatus.ATTEMPTED and self.admission_status is not LearningStateExecutionAdmissionStatus.AUTHORIZED:
            raise ValueError("ATTEMPTED evidence requires AUTHORIZED admission")
        if self.attempt_status is LearningStateExecutionAttemptStatus.FAILED and self.admission_status is not LearningStateExecutionAdmissionStatus.AUTHORIZED:
            raise ValueError("FAILED evidence requires AUTHORIZED admission")
        if self.failure_type is not None and (not isinstance(self.failure_type, str) or not self.failure_type.strip()):
            raise ValueError("failure_type must be a non-empty string when provided")
        if self.failure_message is not None and not isinstance(self.failure_message, str):
            raise TypeError("failure_message must be a string when provided")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "executor_output", _freeze(self.executor_output))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_attempted(self) -> bool:
        return self.attempt_status is LearningStateExecutionAttemptStatus.ATTEMPTED

    @property
    def is_failed(self) -> bool:
        return self.attempt_status is LearningStateExecutionAttemptStatus.FAILED

    @property
    def invokes_executor(self) -> bool:
        return self.is_attempted or self.is_failed

    @property
    def establishes_outcome(self) -> bool:
        return False

    @property
    def establishes_success(self) -> bool:
        return False

    @property
    def establishes_failure_truth(self) -> bool:
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

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def plans_work(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False


Executor = Callable[[Mapping[str, Any], str, str], Any]


class LearningStateExecutionAttemptService:
    """Attempt authorized execution once and record only bounded attempt evidence."""

    def attempt(
        self,
        admission: LearningStateExecutionAdmission,
        executor: Executor,
        *,
        attempt_id: str,
        execution_target_id: str,
        execution_purpose: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionAttempt:
        if type(admission) is not LearningStateExecutionAdmission:
            raise TypeError("admission must be an execution-admission artifact")
        if not isinstance(attempt_id, str) or not attempt_id.strip():
            raise ValueError("attempt_id must be a non-empty string")
        if not callable(executor):
            raise TypeError("executor must be callable")
        for name, value in (("execution_target_id", execution_target_id), ("execution_purpose", execution_purpose)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if admission.admission_status is not LearningStateExecutionAdmissionStatus.AUTHORIZED or not admission.is_authorized:
            raise ValueError("execution attempt requires AUTHORIZED admission")
        if execution_target_id != admission.execution_target_id:
            raise ValueError("execution target must match admission")
        if execution_purpose != admission.execution_purpose:
            raise ValueError("execution purpose must match admission")
        try:
            output = executor(
                admission.result,
                execution_target_id,
                execution_purpose,
            )
            return LearningStateExecutionAttempt(
                attempt_id=attempt_id,
                admission_id=admission.admission_id,
                eligibility_id=admission.eligibility_id,
                handling_id=admission.handling_id,
                consumption_id=admission.consumption_id,
                receipt_id=admission.receipt_id,
                handoff_id=admission.handoff_id,
                integrity_id=admission.integrity_id,
                validation_id=admission.validation_id,
                use_id=admission.use_id,
                request_id=admission.request_id,
                interpretation_id=admission.interpretation_id,
                source_request_id=admission.source_request_id,
                read_validation_id=admission.read_validation_id,
                read_id=admission.read_id,
                consumption_request_id=admission.consumption_request_id,
                source_validation_id=admission.source_validation_id,
                source_integrity_id=admission.source_integrity_id,
                transition_id=admission.transition_id,
                evidence_id=admission.evidence_id,
                application_id=admission.application_id,
                state_key=admission.state_key,
                transition_fingerprint=admission.transition_fingerprint,
                source_application_fingerprint=admission.source_application_fingerprint,
                computed_application_fingerprint=admission.computed_application_fingerprint,
                confidence=admission.confidence,
                consumer_id=admission.consumer_id,
                use_purpose=admission.use_purpose,
                downstream_recipient_id=admission.downstream_recipient_id,
                downstream_handler_id=admission.downstream_handler_id,
                handling_purpose=admission.handling_purpose,
                execution_target_id=execution_target_id,
                execution_purpose=execution_purpose,
                admission_status=admission.admission_status,
                attempt_status=LearningStateExecutionAttemptStatus.ATTEMPTED,
                executor_output=output,
                failure_type=None,
                failure_message=None,
                reasons=reasons if reasons is not None else {"attempt_status": "ATTEMPTED"},
                lineage=lineage if lineage is not None else {"attempt_id": attempt_id, "admission_id": admission.admission_id},
            )
        except Exception as exc:
            return LearningStateExecutionAttempt(
                attempt_id=attempt_id,
                admission_id=admission.admission_id,
                eligibility_id=admission.eligibility_id,
                handling_id=admission.handling_id,
                consumption_id=admission.consumption_id,
                receipt_id=admission.receipt_id,
                handoff_id=admission.handoff_id,
                integrity_id=admission.integrity_id,
                validation_id=admission.validation_id,
                use_id=admission.use_id,
                request_id=admission.request_id,
                interpretation_id=admission.interpretation_id,
                source_request_id=admission.source_request_id,
                read_validation_id=admission.read_validation_id,
                read_id=admission.read_id,
                consumption_request_id=admission.consumption_request_id,
                source_validation_id=admission.source_validation_id,
                source_integrity_id=admission.source_integrity_id,
                transition_id=admission.transition_id,
                evidence_id=admission.evidence_id,
                application_id=admission.application_id,
                state_key=admission.state_key,
                transition_fingerprint=admission.transition_fingerprint,
                source_application_fingerprint=admission.source_application_fingerprint,
                computed_application_fingerprint=admission.computed_application_fingerprint,
                confidence=admission.confidence,
                consumer_id=admission.consumer_id,
                use_purpose=admission.use_purpose,
                downstream_recipient_id=admission.downstream_recipient_id,
                downstream_handler_id=admission.downstream_handler_id,
                handling_purpose=admission.handling_purpose,
                execution_target_id=execution_target_id,
                execution_purpose=execution_purpose,
                admission_status=admission.admission_status,
                attempt_status=LearningStateExecutionAttemptStatus.FAILED,
                executor_output=None,
                failure_type=type(exc).__name__,
                failure_message=str(exc),
                reasons=reasons if reasons is not None else {"attempt_status": "FAILED"},
                lineage=lineage if lineage is not None else {"attempt_id": attempt_id, "admission_id": admission.admission_id},
            )


__all__ = [
    "LearningStateExecutionAttemptError",
    "LearningStateExecutionAttemptStatus",
    "LearningStateExecutionAttempt",
    "LearningStateExecutionAttemptService",
]
