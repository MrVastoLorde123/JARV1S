"""M23.153: record a bounded execution attempt after explicit admission and authorization."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_execution_admission_authorization import (
    LearningStateExecutionAdmissionAuthorization,
    LearningStateExecutionAdmissionAuthorizationStatus,
)


class LearningStateExecutionAttemptError(RuntimeError):
    """Raised when execution-attempt evidence cannot be formed safely."""


class LearningStateExecutionAttemptStatus(str, Enum):
    ATTEMPTED = "ATTEMPTED"
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
class LearningStateExecutionAttempt:
    """Immutable evidence that one admitted execution boundary was entered for a declared attempt."""

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
    attempt_purpose: str
    attempt_rationale: Any
    payload: Any
    status: LearningStateExecutionAttemptStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "attempt_id", "admission_id", "eligibility_id", "handling_id", "consumption_id", "receipt_id",
            "handoff_id", "integrity_id", "validation_id", "semantic_use_id", "source_request_id",
            "source_request_lineage_id", "source_validation_id", "source_validation_lineage_id", "interpretation_id",
            "read_id", "consumption_request_id", "requester_id", "consumer_id", "handoff_target_id", "recipient_id",
            "handling_target_id", "execution_target_id", "attempt_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, LearningStateExecutionAttemptStatus):
            raise TypeError("status must be an execution-attempt status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "authorization_scope", _freeze(self.authorization_scope))
        object.__setattr__(self, "authority_basis", _freeze(self.authority_basis))
        object.__setattr__(self, "attempt_rationale", _freeze(self.attempt_rationale))
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_attempted(self) -> bool:
        return self.status is LearningStateExecutionAttemptStatus.ATTEMPTED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionAttemptStatus.REJECTED

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


class LearningStateExecutionAttemptService:
    """Record entry to an explicitly admitted execution boundary without invoking execution itself."""

    def attempt(
        self,
        admission: LearningStateExecutionAdmissionAuthorization,
        *,
        attempt_id: str,
        execution_target_id: str,
        attempt_purpose: str,
        attempt_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionAttempt:
        if type(admission) is not LearningStateExecutionAdmissionAuthorization:
            raise TypeError("admission must be an execution admission / authorization artifact")
        for name, value in (
            ("attempt_id", attempt_id),
            ("execution_target_id", execution_target_id),
            ("attempt_purpose", attempt_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if attempt_rationale is None:
            raise ValueError("attempt_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if admission.status is not LearningStateExecutionAdmissionAuthorizationStatus.ADMITTED:
            checks.append("execution admission status must be ADMITTED")
        if attempt_id == admission.admission_id:
            checks.append("attempt identity must be distinct")
        if execution_target_id != admission.execution_target_id:
            checks.append("execution target must match admission")

        lineage_admission_id = admission.lineage.get("admission_id", admission.admission_id)
        lineage_eligibility_id = admission.lineage.get("eligibility_id", admission.eligibility_id)
        lineage_handling_id = admission.lineage.get("handling_id", admission.handling_id)
        lineage_consumption_id = admission.lineage.get("consumption_id", admission.consumption_id)
        lineage_receipt_id = admission.lineage.get("receipt_id", admission.receipt_id)
        lineage_handoff_id = admission.lineage.get("handoff_id", admission.handoff_id)
        lineage_integrity_id = admission.lineage.get("integrity_id", admission.integrity_id)
        lineage_validation_id = admission.lineage.get("validation_id", admission.validation_id)
        lineage_semantic_use_id = admission.lineage.get("semantic_use_id", admission.semantic_use_id)
        lineage_request_id = admission.lineage.get("request_id", admission.source_request_lineage_id)
        lineage_source_validation_id = admission.lineage.get("source_validation_id", admission.source_validation_lineage_id)
        lineage_interpretation_id = admission.lineage.get("interpretation_id", admission.interpretation_id)
        lineage_source_request_id = admission.lineage.get("source_request_id", admission.source_request_id)
        lineage_source_validation_provenance_id = admission.lineage.get("source_validation_provenance_id", admission.source_validation_id)
        lineage_read_id = admission.lineage.get("read_id", admission.read_id)
        lineage_consumption_request_id = admission.lineage.get("consumption_request_id", admission.consumption_request_id)

        if lineage_admission_id != admission.admission_id:
            checks.append("admission lineage mismatch")
        if lineage_eligibility_id != admission.eligibility_id:
            checks.append("eligibility lineage mismatch")
        if lineage_handling_id != admission.handling_id:
            checks.append("handling lineage mismatch")
        if lineage_consumption_id != admission.consumption_id:
            checks.append("consumption lineage mismatch")
        if lineage_receipt_id != admission.receipt_id:
            checks.append("receipt lineage mismatch")
        if lineage_handoff_id != admission.handoff_id:
            checks.append("handoff lineage mismatch")
        if lineage_integrity_id != admission.integrity_id:
            checks.append("integrity lineage mismatch")
        if lineage_validation_id != admission.validation_id:
            checks.append("validation lineage mismatch")
        if lineage_semantic_use_id != admission.semantic_use_id:
            checks.append("semantic-use lineage mismatch")
        if lineage_request_id != admission.source_request_lineage_id:
            checks.append("source request lineage mismatch")
        if lineage_source_validation_id != admission.source_validation_lineage_id:
            checks.append("source validation lineage mismatch")
        if lineage_interpretation_id != admission.interpretation_id:
            checks.append("interpretation lineage mismatch")
        if lineage_source_request_id != admission.source_request_id:
            checks.append("source request provenance mismatch")
        if lineage_source_validation_provenance_id != admission.source_validation_id:
            checks.append("source validation provenance mismatch")
        if lineage_read_id != admission.read_id:
            checks.append("read lineage mismatch")
        if lineage_consumption_request_id != admission.consumption_request_id:
            checks.append("consumption request lineage mismatch")

        valid = not checks
        payload = {"admission_id": admission.admission_id, "execution_target_id": execution_target_id} if valid else {"rejected_admission": True}
        final_reasons = reasons if reasons is not None else (("admitted execution boundary entered for declared attempt",) if valid else tuple(checks))
        status = LearningStateExecutionAttemptStatus.ATTEMPTED if valid else LearningStateExecutionAttemptStatus.REJECTED
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
            semantic_use_id=admission.semantic_use_id,
            source_request_id=admission.source_request_id,
            source_request_lineage_id=admission.source_request_lineage_id,
            source_validation_id=admission.source_validation_id,
            source_validation_lineage_id=admission.source_validation_lineage_id,
            interpretation_id=admission.interpretation_id,
            read_id=admission.read_id,
            consumption_request_id=admission.consumption_request_id,
            requester_id=admission.requester_id,
            consumer_id=admission.consumer_id,
            handoff_target_id=admission.handoff_target_id,
            recipient_id=admission.recipient_id,
            handling_target_id=admission.handling_target_id,
            execution_target_id=execution_target_id,
            authorization_scope=admission.authorization_scope,
            authority_basis=admission.authority_basis,
            attempt_purpose=attempt_purpose,
            attempt_rationale=attempt_rationale,
            payload=payload,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "attempt_id": attempt_id,
                "admission_id": admission.admission_id,
                "eligibility_id": admission.eligibility_id,
                "handling_id": admission.handling_id,
                "consumption_id": admission.consumption_id,
                "receipt_id": admission.receipt_id,
                "handoff_id": admission.handoff_id,
                "integrity_id": admission.integrity_id,
                "validation_id": admission.validation_id,
                "semantic_use_id": admission.semantic_use_id,
                "request_id": admission.source_request_lineage_id,
                "source_validation_id": admission.source_validation_lineage_id,
                "interpretation_id": admission.interpretation_id,
                "source_request_id": admission.source_request_id,
                "source_validation_provenance_id": admission.source_validation_id,
                "read_id": admission.read_id,
                "consumption_request_id": admission.consumption_request_id,
                "execution_target_id": execution_target_id,
            },
        )


__all__ = [
    "LearningStateExecutionAttemptError",
    "LearningStateExecutionAttemptStatus",
    "LearningStateExecutionAttempt",
    "LearningStateExecutionAttemptService",
]
