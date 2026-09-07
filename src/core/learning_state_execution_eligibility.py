"""M23.119: establish execution eligibility without executing downstream work."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_downstream_semantic_handling import (
    LearningStateDownstreamSemanticHandling,
    LearningStateDownstreamSemanticHandlingStatus,
)


class LearningStateExecutionEligibilityError(RuntimeError):
    """Raised when execution eligibility cannot be formed safely."""


class LearningStateExecutionEligibilityStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
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
class LearningStateExecutionEligibility:
    """Immutable evidence that a downstream-handling artifact is execution-eligible."""

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
    handling_status: LearningStateDownstreamSemanticHandlingStatus
    eligibility_status: LearningStateExecutionEligibilityStatus
    result: Mapping[str, Any]
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "eligibility_id", "handling_id", "consumption_id", "receipt_id", "handoff_id", "integrity_id",
            "validation_id", "use_id", "request_id", "interpretation_id", "source_request_id",
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
                raise ValueError("execution eligibility requires SHA-256 fingerprints")
        if not isinstance(self.handling_status, LearningStateDownstreamSemanticHandlingStatus):
            raise TypeError("handling_status must be a downstream semantic-handling status")
        if not isinstance(self.eligibility_status, LearningStateExecutionEligibilityStatus):
            raise TypeError("eligibility_status must be an execution-eligibility status")
        if self.eligibility_status is LearningStateExecutionEligibilityStatus.ELIGIBLE and self.handling_status is not LearningStateDownstreamSemanticHandlingStatus.READY:
            raise ValueError("ELIGIBLE evidence requires READY downstream handling")
        if not isinstance(self.result, Mapping):
            raise TypeError("result must be a mapping")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "result", _freeze(self.result))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_eligible(self) -> bool:
        return self.eligibility_status is LearningStateExecutionEligibilityStatus.ELIGIBLE

    @property
    def invokes_handler(self) -> bool:
        return False

    @property
    def invokes_worker(self) -> bool:
        return False

    @property
    def executes_action(self) -> bool:
        return False

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def grants_permission(self) -> bool:
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
    def establishes_usefulness(self) -> bool:
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


class LearningStateExecutionEligibilityService:
    """Mark READY downstream handling as eligible without granting execution authority."""

    def assess(
        self,
        handling: LearningStateDownstreamSemanticHandling,
        *,
        eligibility_id: str,
        execution_target_id: str,
        execution_purpose: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionEligibility:
        if type(handling) is not LearningStateDownstreamSemanticHandling:
            raise TypeError("handling must be a downstream semantic-handling artifact")
        for name, value in (
            ("eligibility_id", eligibility_id),
            ("execution_target_id", execution_target_id),
            ("execution_purpose", execution_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if handling.handling_status is not LearningStateDownstreamSemanticHandlingStatus.READY or not handling.is_ready:
            raise ValueError("execution eligibility requires READY downstream handling")
        return LearningStateExecutionEligibility(
            eligibility_id=eligibility_id,
            handling_id=handling.handling_id,
            consumption_id=handling.consumption_id,
            receipt_id=handling.receipt_id,
            handoff_id=handling.handoff_id,
            integrity_id=handling.integrity_id,
            validation_id=handling.validation_id,
            use_id=handling.use_id,
            request_id=handling.request_id,
            interpretation_id=handling.interpretation_id,
            source_request_id=handling.source_request_id,
            read_validation_id=handling.read_validation_id,
            read_id=handling.read_id,
            consumption_request_id=handling.consumption_request_id,
            source_validation_id=handling.source_validation_id,
            source_integrity_id=handling.source_integrity_id,
            transition_id=handling.transition_id,
            evidence_id=handling.evidence_id,
            application_id=handling.application_id,
            state_key=handling.state_key,
            transition_fingerprint=handling.transition_fingerprint,
            source_application_fingerprint=handling.source_application_fingerprint,
            computed_application_fingerprint=handling.computed_application_fingerprint,
            confidence=handling.confidence,
            consumer_id=handling.consumer_id,
            use_purpose=handling.use_purpose,
            downstream_recipient_id=handling.downstream_recipient_id,
            downstream_handler_id=handling.downstream_handler_id,
            handling_purpose=handling.handling_purpose,
            execution_target_id=execution_target_id,
            execution_purpose=execution_purpose,
            handling_status=handling.handling_status,
            eligibility_status=LearningStateExecutionEligibilityStatus.ELIGIBLE,
            result=handling.result,
            reasons=reasons if reasons is not None else {"eligibility_status": "ELIGIBLE"},
            lineage=lineage if lineage is not None else {
                "eligibility_id": eligibility_id,
                "handling_id": handling.handling_id,
                "execution_target_id": execution_target_id,
            },
        )


__all__ = [
    "LearningStateExecutionEligibilityError",
    "LearningStateExecutionEligibilityStatus",
    "LearningStateExecutionEligibility",
    "LearningStateExecutionEligibilityService",
]
