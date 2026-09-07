"""M23.150: handle consumed semantic-use evidence within a bounded downstream semantic boundary."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_semantic_use_consumption import (
    LearningStateExecutionLearningStateSemanticUseConsumption,
    LearningStateExecutionLearningStateSemanticUseConsumptionStatus,
)


class LearningStateExecutionLearningStateDownstreamSemanticHandlingError(RuntimeError):
    """Raised when downstream semantic-handling evidence cannot be formed safely."""


class LearningStateExecutionLearningStateDownstreamSemanticHandlingStatus(str, Enum):
    HANDLED = "HANDLED"
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
class LearningStateExecutionLearningStateDownstreamSemanticHandling:
    """Immutable evidence that one consumed semantic-use result was handled downstream."""

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
    handling_purpose: str
    handling_rationale: Any
    payload: Any
    status: LearningStateExecutionLearningStateDownstreamSemanticHandlingStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "handling_id", "consumption_id", "receipt_id", "handoff_id", "integrity_id", "validation_id",
            "semantic_use_id", "source_request_id", "source_request_lineage_id", "source_validation_id",
            "source_validation_lineage_id", "interpretation_id", "read_id", "consumption_request_id",
            "requester_id", "consumer_id", "handoff_target_id", "recipient_id", "handling_target_id",
            "handling_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, LearningStateExecutionLearningStateDownstreamSemanticHandlingStatus):
            raise TypeError("status must be a downstream semantic-handling status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "handling_rationale", _freeze(self.handling_rationale))
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_handled(self) -> bool:
        return self.status is LearningStateExecutionLearningStateDownstreamSemanticHandlingStatus.HANDLED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateDownstreamSemanticHandlingStatus.REJECTED

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


class LearningStateExecutionLearningStateDownstreamSemanticHandlingService:
    """Handle one consumed semantic-use result at a declared downstream boundary only."""

    def handle(
        self,
        consumption: LearningStateExecutionLearningStateSemanticUseConsumption,
        *,
        handling_id: str,
        handling_target_id: str,
        handling_purpose: str,
        handling_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateDownstreamSemanticHandling:
        if type(consumption) is not LearningStateExecutionLearningStateSemanticUseConsumption:
            raise TypeError("consumption must be a semantic-use consumption artifact")
        for name, value in (
            ("handling_id", handling_id),
            ("handling_target_id", handling_target_id),
            ("handling_purpose", handling_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if handling_rationale is None:
            raise ValueError("handling_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if consumption.status is not LearningStateExecutionLearningStateSemanticUseConsumptionStatus.CONSUMED:
            checks.append("semantic-use consumption status must be CONSUMED")
        if handling_id == consumption.consumption_id:
            checks.append("handling identity must be distinct")

        lineage_consumption_id = consumption.lineage.get("consumption_id", consumption.consumption_id)
        lineage_receipt_id = consumption.lineage.get("receipt_id", consumption.receipt_id)
        lineage_handoff_id = consumption.lineage.get("handoff_id", consumption.handoff_id)
        lineage_integrity_id = consumption.lineage.get("integrity_id", consumption.integrity_id)
        lineage_validation_id = consumption.lineage.get("validation_id", consumption.validation_id)
        lineage_semantic_use_id = consumption.lineage.get("semantic_use_id", consumption.semantic_use_id)
        lineage_request_id = consumption.lineage.get("request_id", consumption.source_request_lineage_id)
        lineage_source_validation_id = consumption.lineage.get("source_validation_id", consumption.source_validation_lineage_id)
        lineage_interpretation_id = consumption.lineage.get("interpretation_id", consumption.interpretation_id)
        lineage_source_request_id = consumption.lineage.get("source_request_id", consumption.source_request_id)
        lineage_source_validation_provenance_id = consumption.lineage.get("source_validation_provenance_id", consumption.source_validation_id)
        lineage_read_id = consumption.lineage.get("read_id", consumption.read_id)
        lineage_consumption_request_id = consumption.lineage.get("consumption_request_id", consumption.consumption_request_id)

        if lineage_consumption_id != consumption.consumption_id:
            checks.append("consumption lineage mismatch")
        if lineage_receipt_id != consumption.receipt_id:
            checks.append("receipt lineage mismatch")
        if lineage_handoff_id != consumption.handoff_id:
            checks.append("handoff lineage mismatch")
        if lineage_integrity_id != consumption.integrity_id:
            checks.append("integrity lineage mismatch")
        if lineage_validation_id != consumption.validation_id:
            checks.append("validation lineage mismatch")
        if lineage_semantic_use_id != consumption.semantic_use_id:
            checks.append("semantic-use lineage mismatch")
        if lineage_request_id != consumption.source_request_lineage_id:
            checks.append("source request lineage mismatch")
        if lineage_source_validation_id != consumption.source_validation_lineage_id:
            checks.append("source validation lineage mismatch")
        if lineage_interpretation_id != consumption.interpretation_id:
            checks.append("interpretation lineage mismatch")
        if lineage_source_request_id != consumption.source_request_id:
            checks.append("source request provenance mismatch")
        if lineage_source_validation_provenance_id != consumption.source_validation_id:
            checks.append("source validation provenance mismatch")
        if lineage_read_id != consumption.read_id:
            checks.append("read lineage mismatch")
        if lineage_consumption_request_id != consumption.consumption_request_id:
            checks.append("consumption request lineage mismatch")

        valid = not checks
        payload = {"consumption_id": consumption.consumption_id, "handling_target_id": handling_target_id} if valid else {"rejected_consumption": True}
        final_reasons = reasons if reasons is not None else (("consumed semantic use handled at the declared downstream semantic boundary",) if valid else tuple(checks))
        status = LearningStateExecutionLearningStateDownstreamSemanticHandlingStatus.HANDLED if valid else LearningStateExecutionLearningStateDownstreamSemanticHandlingStatus.REJECTED
        return LearningStateExecutionLearningStateDownstreamSemanticHandling(
            handling_id=handling_id,
            consumption_id=consumption.consumption_id,
            receipt_id=consumption.receipt_id,
            handoff_id=consumption.handoff_id,
            integrity_id=consumption.integrity_id,
            validation_id=consumption.validation_id,
            semantic_use_id=consumption.semantic_use_id,
            source_request_id=consumption.source_request_id,
            source_request_lineage_id=consumption.source_request_lineage_id,
            source_validation_id=consumption.source_validation_id,
            source_validation_lineage_id=consumption.source_validation_lineage_id,
            interpretation_id=consumption.interpretation_id,
            read_id=consumption.read_id,
            consumption_request_id=consumption.consumption_request_id,
            requester_id=consumption.requester_id,
            consumer_id=consumption.consumer_id,
            handoff_target_id=consumption.handoff_target_id,
            recipient_id=consumption.recipient_id,
            handling_target_id=handling_target_id,
            handling_purpose=handling_purpose,
            handling_rationale=handling_rationale,
            payload=payload,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "handling_id": handling_id,
                "consumption_id": consumption.consumption_id,
                "receipt_id": consumption.receipt_id,
                "handoff_id": consumption.handoff_id,
                "integrity_id": consumption.integrity_id,
                "validation_id": consumption.validation_id,
                "semantic_use_id": consumption.semantic_use_id,
                "request_id": consumption.source_request_lineage_id,
                "source_validation_id": consumption.source_validation_lineage_id,
                "interpretation_id": consumption.interpretation_id,
                "source_request_id": consumption.source_request_id,
                "source_validation_provenance_id": consumption.source_validation_id,
                "read_id": consumption.read_id,
                "consumption_request_id": consumption.consumption_request_id,
                "handoff_target_id": consumption.handoff_target_id,
                "recipient_id": consumption.recipient_id,
                "handling_target_id": handling_target_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateDownstreamSemanticHandlingError",
    "LearningStateExecutionLearningStateDownstreamSemanticHandlingStatus",
    "LearningStateExecutionLearningStateDownstreamSemanticHandling",
    "LearningStateExecutionLearningStateDownstreamSemanticHandlingService",
]
