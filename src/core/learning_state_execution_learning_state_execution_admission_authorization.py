"""M23.152: admit and authorize one eligible execution target without executing it."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_execution_eligibility import (
    LearningStateExecutionEligibility,
    LearningStateExecutionEligibilityStatus,
)


class LearningStateExecutionAdmissionAuthorizationError(RuntimeError):
    """Raised when bounded execution admission evidence cannot be formed safely."""


class LearningStateExecutionAdmissionAuthorizationStatus(str, Enum):
    ADMITTED = "ADMITTED"
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
class LearningStateExecutionAdmissionAuthorization:
    """Immutable evidence that one eligible execution target was admitted within a declared scope."""

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
    admission_purpose: str
    admission_rationale: Any
    payload: Any
    status: LearningStateExecutionAdmissionAuthorizationStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "admission_id", "eligibility_id", "handling_id", "consumption_id", "receipt_id", "handoff_id",
            "integrity_id", "validation_id", "semantic_use_id", "source_request_id", "source_request_lineage_id",
            "source_validation_id", "source_validation_lineage_id", "interpretation_id", "read_id",
            "consumption_request_id", "requester_id", "consumer_id", "handoff_target_id", "recipient_id",
            "handling_target_id", "execution_target_id", "admission_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, LearningStateExecutionAdmissionAuthorizationStatus):
            raise TypeError("status must be an execution admission / authorization status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "authorization_scope", _freeze(self.authorization_scope))
        object.__setattr__(self, "authority_basis", _freeze(self.authority_basis))
        object.__setattr__(self, "admission_rationale", _freeze(self.admission_rationale))
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_admitted(self) -> bool:
        return self.status is LearningStateExecutionAdmissionAuthorizationStatus.ADMITTED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionAdmissionAuthorizationStatus.REJECTED

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
        return self.is_admitted

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


class LearningStateExecutionAdmissionAuthorizationService:
    """Admit and authorize one eligible execution target within an explicit scope only."""

    def admit(
        self,
        eligibility: LearningStateExecutionEligibility,
        *,
        admission_id: str,
        execution_target_id: str,
        authorization_scope: Any,
        authority_basis: Any,
        admission_purpose: str,
        admission_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionAdmissionAuthorization:
        if type(eligibility) is not LearningStateExecutionEligibility:
            raise TypeError("eligibility must be an execution-eligibility artifact")
        for name, value in (
            ("admission_id", admission_id),
            ("execution_target_id", execution_target_id),
            ("admission_purpose", admission_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if authorization_scope is None:
            raise ValueError("authorization_scope must be provided")
        if authority_basis is None:
            raise ValueError("authority_basis must be provided")
        if admission_rationale is None:
            raise ValueError("admission_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if eligibility.status is not LearningStateExecutionEligibilityStatus.ELIGIBLE:
            checks.append("execution eligibility status must be ELIGIBLE")
        if admission_id == eligibility.eligibility_id:
            checks.append("admission identity must be distinct")
        if execution_target_id != eligibility.execution_target_id:
            checks.append("execution target must match eligibility")

        lineage_eligibility_id = eligibility.lineage.get("eligibility_id", eligibility.eligibility_id)
        lineage_handling_id = eligibility.lineage.get("handling_id", eligibility.handling_id)
        lineage_consumption_id = eligibility.lineage.get("consumption_id", eligibility.consumption_id)
        lineage_receipt_id = eligibility.lineage.get("receipt_id", eligibility.receipt_id)
        lineage_handoff_id = eligibility.lineage.get("handoff_id", eligibility.handoff_id)
        lineage_integrity_id = eligibility.lineage.get("integrity_id", eligibility.integrity_id)
        lineage_validation_id = eligibility.lineage.get("validation_id", eligibility.validation_id)
        lineage_semantic_use_id = eligibility.lineage.get("semantic_use_id", eligibility.semantic_use_id)
        lineage_request_id = eligibility.lineage.get("request_id", eligibility.source_request_lineage_id)
        lineage_source_validation_id = eligibility.lineage.get("source_validation_id", eligibility.source_validation_lineage_id)
        lineage_interpretation_id = eligibility.lineage.get("interpretation_id", eligibility.interpretation_id)
        lineage_source_request_id = eligibility.lineage.get("source_request_id", eligibility.source_request_id)
        lineage_source_validation_provenance_id = eligibility.lineage.get("source_validation_provenance_id", eligibility.source_validation_id)
        lineage_read_id = eligibility.lineage.get("read_id", eligibility.read_id)
        lineage_consumption_request_id = eligibility.lineage.get("consumption_request_id", eligibility.consumption_request_id)

        if lineage_eligibility_id != eligibility.eligibility_id:
            checks.append("eligibility lineage mismatch")
        if lineage_handling_id != eligibility.handling_id:
            checks.append("handling lineage mismatch")
        if lineage_consumption_id != eligibility.consumption_id:
            checks.append("consumption lineage mismatch")
        if lineage_receipt_id != eligibility.receipt_id:
            checks.append("receipt lineage mismatch")
        if lineage_handoff_id != eligibility.handoff_id:
            checks.append("handoff lineage mismatch")
        if lineage_integrity_id != eligibility.integrity_id:
            checks.append("integrity lineage mismatch")
        if lineage_validation_id != eligibility.validation_id:
            checks.append("validation lineage mismatch")
        if lineage_semantic_use_id != eligibility.semantic_use_id:
            checks.append("semantic-use lineage mismatch")
        if lineage_request_id != eligibility.source_request_lineage_id:
            checks.append("source request lineage mismatch")
        if lineage_source_validation_id != eligibility.source_validation_lineage_id:
            checks.append("source validation lineage mismatch")
        if lineage_interpretation_id != eligibility.interpretation_id:
            checks.append("interpretation lineage mismatch")
        if lineage_source_request_id != eligibility.source_request_id:
            checks.append("source request provenance mismatch")
        if lineage_source_validation_provenance_id != eligibility.source_validation_id:
            checks.append("source validation provenance mismatch")
        if lineage_read_id != eligibility.read_id:
            checks.append("read lineage mismatch")
        if lineage_consumption_request_id != eligibility.consumption_request_id:
            checks.append("consumption request lineage mismatch")

        valid = not checks
        payload = (
            {"eligibility_id": eligibility.eligibility_id, "execution_target_id": execution_target_id, "authorization_scope": authorization_scope}
            if valid else {"rejected_eligibility": True}
        )
        final_reasons = reasons if reasons is not None else (("eligible execution target admitted within the declared authorization scope",) if valid else tuple(checks))
        status = LearningStateExecutionAdmissionAuthorizationStatus.ADMITTED if valid else LearningStateExecutionAdmissionAuthorizationStatus.REJECTED
        return LearningStateExecutionAdmissionAuthorization(
            admission_id=admission_id,
            eligibility_id=eligibility.eligibility_id,
            handling_id=eligibility.handling_id,
            consumption_id=eligibility.consumption_id,
            receipt_id=eligibility.receipt_id,
            handoff_id=eligibility.handoff_id,
            integrity_id=eligibility.integrity_id,
            validation_id=eligibility.validation_id,
            semantic_use_id=eligibility.semantic_use_id,
            source_request_id=eligibility.source_request_id,
            source_request_lineage_id=eligibility.source_request_lineage_id,
            source_validation_id=eligibility.source_validation_id,
            source_validation_lineage_id=eligibility.source_validation_lineage_id,
            interpretation_id=eligibility.interpretation_id,
            read_id=eligibility.read_id,
            consumption_request_id=eligibility.consumption_request_id,
            requester_id=eligibility.requester_id,
            consumer_id=eligibility.consumer_id,
            handoff_target_id=eligibility.handoff_target_id,
            recipient_id=eligibility.recipient_id,
            handling_target_id=eligibility.handling_target_id,
            execution_target_id=execution_target_id,
            authorization_scope=authorization_scope,
            authority_basis=authority_basis,
            admission_purpose=admission_purpose,
            admission_rationale=admission_rationale,
            payload=payload,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "admission_id": admission_id,
                "eligibility_id": eligibility.eligibility_id,
                "handling_id": eligibility.handling_id,
                "consumption_id": eligibility.consumption_id,
                "receipt_id": eligibility.receipt_id,
                "handoff_id": eligibility.handoff_id,
                "integrity_id": eligibility.integrity_id,
                "validation_id": eligibility.validation_id,
                "semantic_use_id": eligibility.semantic_use_id,
                "request_id": eligibility.source_request_lineage_id,
                "source_validation_id": eligibility.source_validation_lineage_id,
                "interpretation_id": eligibility.interpretation_id,
                "source_request_id": eligibility.source_request_id,
                "source_validation_provenance_id": eligibility.source_validation_id,
                "read_id": eligibility.read_id,
                "consumption_request_id": eligibility.consumption_request_id,
                "execution_target_id": execution_target_id,
            },
        )


__all__ = [
    "LearningStateExecutionAdmissionAuthorizationError",
    "LearningStateExecutionAdmissionAuthorizationStatus",
    "LearningStateExecutionAdmissionAuthorization",
    "LearningStateExecutionAdmissionAuthorizationService",
]
