"""M23.139: form an explicit interpretation request from validated read evidence."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_consumption_read_validation import (
    LearningStateExecutionLearningStateConsumptionReadValidation,
    LearningStateExecutionLearningStateConsumptionReadValidationStatus,
)


class LearningStateExecutionLearningStateInterpretationRequestError(RuntimeError):
    """Raised when an interpretation request cannot be formed safely."""


class LearningStateExecutionLearningStateInterpretationRequestStatus(str, Enum):
    REQUESTED = "REQUESTED"
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
class LearningStateExecutionLearningStateInterpretationRequest:
    """Immutable evidence that interpretation was explicitly requested for validated read evidence."""

    request_id: str
    source_validation_id: str
    read_id: str
    consumption_request_id: str
    integrity_id: str
    transition_id: str
    evidence_id: str
    state_key: str
    requested_scope: Any
    read_payload: Any
    read_fingerprint: str
    computed_read_fingerprint: str
    reader_id: str
    read_purpose: str
    request_rationale: Any
    confidence: float
    requester_id: str
    interpretation_purpose: str
    interpretation_rationale: Any
    status: LearningStateExecutionLearningStateInterpretationRequestStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "request_id", "source_validation_id", "read_id", "consumption_request_id", "integrity_id",
            "transition_id", "evidence_id", "state_key", "read_fingerprint", "computed_read_fingerprint",
            "reader_id", "read_purpose", "requester_id", "interpretation_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if not isinstance(self.status, LearningStateExecutionLearningStateInterpretationRequestStatus):
            raise TypeError("status must be an interpretation-request status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "requested_scope", _freeze(self.requested_scope))
        object.__setattr__(self, "read_payload", _freeze(self.read_payload))
        object.__setattr__(self, "request_rationale", _freeze(self.request_rationale))
        object.__setattr__(self, "interpretation_rationale", _freeze(self.interpretation_rationale))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_requested(self) -> bool:
        return self.status is LearningStateExecutionLearningStateInterpretationRequestStatus.REQUESTED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateInterpretationRequestStatus.REJECTED

    @property
    def admits_interpretation(self) -> bool:
        return self.is_requested

    @property
    def has_interpreted_payload(self) -> bool:
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


class LearningStateExecutionLearningStateInterpretationRequestService:
    """Request interpretation of validated read evidence without interpreting it."""

    def request(
        self,
        validation: LearningStateExecutionLearningStateConsumptionReadValidation,
        *,
        request_id: str,
        requester_id: str,
        interpretation_purpose: str,
        interpretation_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateInterpretationRequest:
        if type(validation) is not LearningStateExecutionLearningStateConsumptionReadValidation:
            raise TypeError("validation must be a consumption-read validation artifact")
        for name, value in (("request_id", request_id), ("requester_id", requester_id), ("interpretation_purpose", interpretation_purpose)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if interpretation_rationale is None:
            raise ValueError("interpretation_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if validation.status is not LearningStateExecutionLearningStateConsumptionReadValidationStatus.VALIDATED:
            checks.append("consumption read validation is not VALIDATED")
        if request_id == validation.validation_id:
            checks.append("interpretation request identity must be distinct from validation identity")
        if request_id == validation.read_id:
            checks.append("interpretation request identity must be distinct from read identity")

        lineage_validation_id = validation.lineage.get("validation_id", validation.validation_id)
        lineage_read_id = validation.lineage.get("read_id", validation.read_id)
        lineage_request_id = validation.lineage.get("consumption_request_id", validation.consumption_request_id)
        if lineage_validation_id != validation.validation_id:
            checks.append("source validation lineage mismatch")
        if lineage_read_id != validation.read_id:
            checks.append("read lineage mismatch")
        if lineage_request_id != validation.consumption_request_id:
            checks.append("consumption request lineage mismatch")

        valid = not checks
        if reasons is not None:
            final_reasons = reasons
        elif valid:
            final_reasons = ("interpretation request accepted",)
        else:
            final_reasons = tuple(checks)
        status = (
            LearningStateExecutionLearningStateInterpretationRequestStatus.REQUESTED
            if valid else LearningStateExecutionLearningStateInterpretationRequestStatus.REJECTED
        )
        return LearningStateExecutionLearningStateInterpretationRequest(
            request_id=request_id,
            source_validation_id=validation.source_validation_id,
            read_id=validation.read_id,
            consumption_request_id=validation.consumption_request_id,
            integrity_id=validation.integrity_id,
            transition_id=validation.transition_id,
            evidence_id=validation.evidence_id,
            state_key=validation.state_key,
            requested_scope=validation.requested_scope,
            read_payload=validation.read_payload,
            read_fingerprint=validation.read_fingerprint,
            computed_read_fingerprint=validation.computed_read_fingerprint,
            reader_id=validation.reader_id,
            read_purpose=validation.read_purpose,
            request_rationale=validation.request_rationale,
            confidence=validation.confidence,
            requester_id=requester_id,
            interpretation_purpose=interpretation_purpose,
            interpretation_rationale=interpretation_rationale,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "request_id": request_id,
                "validation_id": validation.validation_id,
                "read_id": validation.read_id,
                "consumption_request_id": validation.consumption_request_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateInterpretationRequestError",
    "LearningStateExecutionLearningStateInterpretationRequestStatus",
    "LearningStateExecutionLearningStateInterpretationRequest",
    "LearningStateExecutionLearningStateInterpretationRequestService",
]
