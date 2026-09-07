"""M23.120: establish execution admission without executing downstream work."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_eligibility import (
    LearningStateExecutionEligibility,
    LearningStateExecutionEligibilityStatus,
)


class LearningStateExecutionAdmissionError(RuntimeError):
    """Raised when execution admission cannot be formed safely."""


class LearningStateExecutionAdmissionStatus(str, Enum):
    AUTHORIZED = "AUTHORIZED"
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
class LearningStateExecutionAdmission:
    """Immutable evidence that an eligible execution target was admitted or rejected."""

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
    eligibility_status: LearningStateExecutionEligibilityStatus
    admission_status: LearningStateExecutionAdmissionStatus
    result: Mapping[str, Any]
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "admission_id", "eligibility_id", "handling_id", "consumption_id", "receipt_id", "handoff_id",
            "integrity_id", "validation_id", "use_id", "request_id", "interpretation_id", "source_request_id",
            "read_validation_id", "read_id", "consumption_request_id", "source_validation_id",
            "source_integrity_id", "transition_id", "evidence_id", "application_id", "state_key",
            "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint",
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
                raise ValueError("execution admission requires SHA-256 fingerprints")
        if not isinstance(self.eligibility_status, LearningStateExecutionEligibilityStatus):
            raise TypeError("eligibility_status must be an execution-eligibility status")
        if not isinstance(self.admission_status, LearningStateExecutionAdmissionStatus):
            raise TypeError("admission_status must be an execution-admission status")
        if self.admission_status is LearningStateExecutionAdmissionStatus.AUTHORIZED and self.eligibility_status is not LearningStateExecutionEligibilityStatus.ELIGIBLE:
            raise ValueError("AUTHORIZED admission requires ELIGIBLE execution evidence")
        if not isinstance(self.result, Mapping):
            raise TypeError("result must be a mapping")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "result", _freeze(self.result))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_authorized(self) -> bool:
        return self.admission_status is LearningStateExecutionAdmissionStatus.AUTHORIZED

    @property
    def authorizes_execution(self) -> bool:
        return self.is_authorized

    @property
    def invokes_handler(self) -> bool:
        return False

    @property
    def invokes_worker(self) -> bool:
        return False

    @property
    def invokes_executor(self) -> bool:
        return False

    @property
    def executes_action(self) -> bool:
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
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_correctness(self) -> bool:
        return False

    @property
    def establishes_certainty(self) -> bool:
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


class LearningStateExecutionAdmissionService:
    """Admit eligible execution without invoking the future execution mechanism."""

    def admit(
        self,
        eligibility: LearningStateExecutionEligibility,
        *,
        admission_id: str,
        authorization_granted: bool,
        execution_target_id: str,
        execution_purpose: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionAdmission:
        if type(eligibility) is not LearningStateExecutionEligibility:
            raise TypeError("eligibility must be an execution-eligibility artifact")
        for name, value in (
            ("admission_id", admission_id),
            ("execution_target_id", execution_target_id),
            ("execution_purpose", execution_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(authorization_granted, bool):
            raise TypeError("authorization_granted must be boolean")
        if eligibility.eligibility_status is not LearningStateExecutionEligibilityStatus.ELIGIBLE or not eligibility.is_eligible:
            raise ValueError("execution admission requires ELIGIBLE execution evidence")
        if execution_target_id != eligibility.execution_target_id:
            raise ValueError("execution target must match eligibility")
        if execution_purpose != eligibility.execution_purpose:
            raise ValueError("execution purpose must match eligibility")
        status = (
            LearningStateExecutionAdmissionStatus.AUTHORIZED
            if authorization_granted
            else LearningStateExecutionAdmissionStatus.REJECTED
        )
        return LearningStateExecutionAdmission(
            admission_id=admission_id,
            eligibility_id=eligibility.eligibility_id,
            handling_id=eligibility.handling_id,
            consumption_id=eligibility.consumption_id,
            receipt_id=eligibility.receipt_id,
            handoff_id=eligibility.handoff_id,
            integrity_id=eligibility.integrity_id,
            validation_id=eligibility.validation_id,
            use_id=eligibility.use_id,
            request_id=eligibility.request_id,
            interpretation_id=eligibility.interpretation_id,
            source_request_id=eligibility.source_request_id,
            read_validation_id=eligibility.read_validation_id,
            read_id=eligibility.read_id,
            consumption_request_id=eligibility.consumption_request_id,
            source_validation_id=eligibility.source_validation_id,
            source_integrity_id=eligibility.source_integrity_id,
            transition_id=eligibility.transition_id,
            evidence_id=eligibility.evidence_id,
            application_id=eligibility.application_id,
            state_key=eligibility.state_key,
            transition_fingerprint=eligibility.transition_fingerprint,
            source_application_fingerprint=eligibility.source_application_fingerprint,
            computed_application_fingerprint=eligibility.computed_application_fingerprint,
            confidence=eligibility.confidence,
            consumer_id=eligibility.consumer_id,
            use_purpose=eligibility.use_purpose,
            downstream_recipient_id=eligibility.downstream_recipient_id,
            downstream_handler_id=eligibility.downstream_handler_id,
            handling_purpose=eligibility.handling_purpose,
            execution_target_id=execution_target_id,
            execution_purpose=execution_purpose,
            eligibility_status=eligibility.eligibility_status,
            admission_status=status,
            result=eligibility.result,
            reasons=reasons if reasons is not None else {"admission_status": status.value},
            lineage=lineage if lineage is not None else {"admission_id": admission_id, "eligibility_id": eligibility.eligibility_id},
        )


__all__ = [
    "LearningStateExecutionAdmissionError",
    "LearningStateExecutionAdmissionStatus",
    "LearningStateExecutionAdmission",
    "LearningStateExecutionAdmissionService",
]
