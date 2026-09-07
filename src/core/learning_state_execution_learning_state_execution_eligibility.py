"""M23.151: determine downstream semantic execution eligibility without granting authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_downstream_semantic_handling import (
    LearningStateExecutionLearningStateDownstreamSemanticHandling,
    LearningStateExecutionLearningStateDownstreamSemanticHandlingStatus,
)


class LearningStateExecutionEligibilityError(RuntimeError):
    """Raised when execution-eligibility evidence cannot be formed safely."""


class LearningStateExecutionEligibilityStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"


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
    """Immutable evidence that one handled semantic result met bounded execution preconditions."""

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
    eligibility_purpose: str
    eligibility_rationale: Any
    payload: Any
    status: LearningStateExecutionEligibilityStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "eligibility_id", "handling_id", "consumption_id", "receipt_id", "handoff_id", "integrity_id",
            "validation_id", "semantic_use_id", "source_request_id", "source_request_lineage_id",
            "source_validation_id", "source_validation_lineage_id", "interpretation_id", "read_id",
            "consumption_request_id", "requester_id", "consumer_id", "handoff_target_id", "recipient_id",
            "handling_target_id", "execution_target_id", "eligibility_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, LearningStateExecutionEligibilityStatus):
            raise TypeError("status must be an execution-eligibility status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "eligibility_rationale", _freeze(self.eligibility_rationale))
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_eligible(self) -> bool:
        return self.status is LearningStateExecutionEligibilityStatus.ELIGIBLE

    @property
    def is_ineligible(self) -> bool:
        return self.status is LearningStateExecutionEligibilityStatus.INELIGIBLE

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


class LearningStateExecutionEligibilityService:
    """Evaluate bounded structural execution preconditions without granting execution authority."""

    def evaluate(
        self,
        handling: LearningStateExecutionLearningStateDownstreamSemanticHandling,
        *,
        eligibility_id: str,
        execution_target_id: str,
        eligibility_purpose: str,
        eligibility_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionEligibility:
        if type(handling) is not LearningStateExecutionLearningStateDownstreamSemanticHandling:
            raise TypeError("handling must be a downstream semantic-handling artifact")
        for name, value in (
            ("eligibility_id", eligibility_id),
            ("execution_target_id", execution_target_id),
            ("eligibility_purpose", eligibility_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if eligibility_rationale is None:
            raise ValueError("eligibility_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if handling.status is not LearningStateExecutionLearningStateDownstreamSemanticHandlingStatus.HANDLED:
            checks.append("downstream semantic handling status must be HANDLED")
        if eligibility_id == handling.handling_id:
            checks.append("eligibility identity must be distinct")

        lineage_handling_id = handling.lineage.get("handling_id", handling.handling_id)
        lineage_consumption_id = handling.lineage.get("consumption_id", handling.consumption_id)
        lineage_receipt_id = handling.lineage.get("receipt_id", handling.receipt_id)
        lineage_handoff_id = handling.lineage.get("handoff_id", handling.handoff_id)
        lineage_integrity_id = handling.lineage.get("integrity_id", handling.integrity_id)
        lineage_validation_id = handling.lineage.get("validation_id", handling.validation_id)
        lineage_semantic_use_id = handling.lineage.get("semantic_use_id", handling.semantic_use_id)
        lineage_request_id = handling.lineage.get("request_id", handling.source_request_lineage_id)
        lineage_source_validation_id = handling.lineage.get("source_validation_id", handling.source_validation_lineage_id)
        lineage_interpretation_id = handling.lineage.get("interpretation_id", handling.interpretation_id)
        lineage_source_request_id = handling.lineage.get("source_request_id", handling.source_request_id)
        lineage_source_validation_provenance_id = handling.lineage.get("source_validation_provenance_id", handling.source_validation_id)
        lineage_read_id = handling.lineage.get("read_id", handling.read_id)
        lineage_consumption_request_id = handling.lineage.get("consumption_request_id", handling.consumption_request_id)

        if lineage_handling_id != handling.handling_id:
            checks.append("handling lineage mismatch")
        if lineage_consumption_id != handling.consumption_id:
            checks.append("consumption lineage mismatch")
        if lineage_receipt_id != handling.receipt_id:
            checks.append("receipt lineage mismatch")
        if lineage_handoff_id != handling.handoff_id:
            checks.append("handoff lineage mismatch")
        if lineage_integrity_id != handling.integrity_id:
            checks.append("integrity lineage mismatch")
        if lineage_validation_id != handling.validation_id:
            checks.append("validation lineage mismatch")
        if lineage_semantic_use_id != handling.semantic_use_id:
            checks.append("semantic-use lineage mismatch")
        if lineage_request_id != handling.source_request_lineage_id:
            checks.append("source request lineage mismatch")
        if lineage_source_validation_id != handling.source_validation_lineage_id:
            checks.append("source validation lineage mismatch")
        if lineage_interpretation_id != handling.interpretation_id:
            checks.append("interpretation lineage mismatch")
        if lineage_source_request_id != handling.source_request_id:
            checks.append("source request provenance mismatch")
        if lineage_source_validation_provenance_id != handling.source_validation_id:
            checks.append("source validation provenance mismatch")
        if lineage_read_id != handling.read_id:
            checks.append("read lineage mismatch")
        if lineage_consumption_request_id != handling.consumption_request_id:
            checks.append("consumption request lineage mismatch")

        valid = not checks
        payload = {"handling_id": handling.handling_id, "execution_target_id": execution_target_id} if valid else {"rejected_handling": True}
        final_reasons = reasons if reasons is not None else (("handled semantic use satisfies bounded execution preconditions",) if valid else tuple(checks))
        status = LearningStateExecutionEligibilityStatus.ELIGIBLE if valid else LearningStateExecutionEligibilityStatus.INELIGIBLE
        return LearningStateExecutionEligibility(
            eligibility_id=eligibility_id,
            handling_id=handling.handling_id,
            consumption_id=handling.consumption_id,
            receipt_id=handling.receipt_id,
            handoff_id=handling.handoff_id,
            integrity_id=handling.integrity_id,
            validation_id=handling.validation_id,
            semantic_use_id=handling.semantic_use_id,
            source_request_id=handling.source_request_id,
            source_request_lineage_id=handling.source_request_lineage_id,
            source_validation_id=handling.source_validation_id,
            source_validation_lineage_id=handling.source_validation_lineage_id,
            interpretation_id=handling.interpretation_id,
            read_id=handling.read_id,
            consumption_request_id=handling.consumption_request_id,
            requester_id=handling.requester_id,
            consumer_id=handling.consumer_id,
            handoff_target_id=handling.handoff_target_id,
            recipient_id=handling.recipient_id,
            handling_target_id=handling.handling_target_id,
            execution_target_id=execution_target_id,
            eligibility_purpose=eligibility_purpose,
            eligibility_rationale=eligibility_rationale,
            payload=payload,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "eligibility_id": eligibility_id,
                "handling_id": handling.handling_id,
                "consumption_id": handling.consumption_id,
                "receipt_id": handling.receipt_id,
                "handoff_id": handling.handoff_id,
                "integrity_id": handling.integrity_id,
                "validation_id": handling.validation_id,
                "semantic_use_id": handling.semantic_use_id,
                "request_id": handling.source_request_lineage_id,
                "source_validation_id": handling.source_validation_lineage_id,
                "interpretation_id": handling.interpretation_id,
                "source_request_id": handling.source_request_id,
                "source_validation_provenance_id": handling.source_validation_id,
                "read_id": handling.read_id,
                "consumption_request_id": handling.consumption_request_id,
                "handling_target_id": handling.handling_target_id,
                "execution_target_id": execution_target_id,
            },
        )


__all__ = [
    "LearningStateExecutionEligibilityError",
    "LearningStateExecutionEligibilityStatus",
    "LearningStateExecutionEligibility",
    "LearningStateExecutionEligibilityService",
]
