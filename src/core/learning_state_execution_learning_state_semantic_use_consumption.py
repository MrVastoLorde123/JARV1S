"""M23.149: consume a received semantic-use receipt without granting authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_semantic_use_receipt import (
    LearningStateExecutionLearningStateSemanticUseReceipt,
    LearningStateExecutionLearningStateSemanticUseReceiptStatus,
)


class LearningStateExecutionLearningStateSemanticUseConsumptionError(RuntimeError):
    """Raised when semantic-use consumption evidence cannot be formed safely."""


class LearningStateExecutionLearningStateSemanticUseConsumptionStatus(str, Enum):
    CONSUMED = "CONSUMED"
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
class LearningStateExecutionLearningStateSemanticUseConsumption:
    """Immutable evidence that one received semantic-use handoff was consumed downstream."""

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
    consumption_purpose: str
    consumption_rationale: Any
    payload: Any
    status: LearningStateExecutionLearningStateSemanticUseConsumptionStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "consumption_id", "receipt_id", "handoff_id", "integrity_id", "validation_id", "semantic_use_id",
            "source_request_id", "source_request_lineage_id", "source_validation_id", "source_validation_lineage_id",
            "interpretation_id", "read_id", "consumption_request_id", "requester_id", "consumer_id",
            "handoff_target_id", "recipient_id", "consumption_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, LearningStateExecutionLearningStateSemanticUseConsumptionStatus):
            raise TypeError("status must be a semantic-use consumption status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "consumption_rationale", _freeze(self.consumption_rationale))
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_consumed(self) -> bool:
        return self.status is LearningStateExecutionLearningStateSemanticUseConsumptionStatus.CONSUMED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateSemanticUseConsumptionStatus.REJECTED

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


class LearningStateExecutionLearningStateSemanticUseConsumptionService:
    """Consume a received semantic-use receipt at a named downstream boundary only."""

    def consume(
        self,
        receipt: LearningStateExecutionLearningStateSemanticUseReceipt,
        *,
        consumption_id: str,
        consumer_id: str,
        consumption_purpose: str,
        consumption_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateSemanticUseConsumption:
        if type(receipt) is not LearningStateExecutionLearningStateSemanticUseReceipt:
            raise TypeError("receipt must be a semantic-use receipt artifact")
        for name, value in (
            ("consumption_id", consumption_id),
            ("consumer_id", consumer_id),
            ("consumption_purpose", consumption_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if consumption_rationale is None:
            raise ValueError("consumption_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if receipt.status is not LearningStateExecutionLearningStateSemanticUseReceiptStatus.RECEIVED:
            checks.append("semantic-use receipt status must be RECEIVED")
        if consumption_id == receipt.receipt_id:
            checks.append("consumption identity must be distinct")

        lineage_receipt_id = receipt.lineage.get("receipt_id", receipt.receipt_id)
        lineage_handoff_id = receipt.lineage.get("handoff_id", receipt.handoff_id)
        lineage_integrity_id = receipt.lineage.get("integrity_id", receipt.integrity_id)
        lineage_validation_id = receipt.lineage.get("validation_id", receipt.validation_id)
        lineage_semantic_use_id = receipt.lineage.get("semantic_use_id", receipt.semantic_use_id)
        lineage_request_id = receipt.lineage.get("request_id", receipt.source_request_lineage_id)
        lineage_source_validation_id = receipt.lineage.get("source_validation_id", receipt.source_validation_lineage_id)
        lineage_interpretation_id = receipt.lineage.get("interpretation_id", receipt.interpretation_id)
        lineage_source_request_id = receipt.lineage.get("source_request_id", receipt.source_request_id)
        lineage_source_validation_provenance_id = receipt.lineage.get("source_validation_provenance_id", receipt.source_validation_id)
        lineage_read_id = receipt.lineage.get("read_id", receipt.read_id)
        lineage_consumption_request_id = receipt.lineage.get("consumption_request_id", receipt.consumption_request_id)

        if lineage_receipt_id != receipt.receipt_id:
            checks.append("receipt lineage mismatch")
        if lineage_handoff_id != receipt.handoff_id:
            checks.append("handoff lineage mismatch")
        if lineage_integrity_id != receipt.integrity_id:
            checks.append("integrity lineage mismatch")
        if lineage_validation_id != receipt.validation_id:
            checks.append("validation lineage mismatch")
        if lineage_semantic_use_id != receipt.semantic_use_id:
            checks.append("semantic-use lineage mismatch")
        if lineage_request_id != receipt.source_request_lineage_id:
            checks.append("source request lineage mismatch")
        if lineage_source_validation_id != receipt.source_validation_lineage_id:
            checks.append("source validation lineage mismatch")
        if lineage_interpretation_id != receipt.interpretation_id:
            checks.append("interpretation lineage mismatch")
        if lineage_source_request_id != receipt.source_request_id:
            checks.append("source request provenance mismatch")
        if lineage_source_validation_provenance_id != receipt.source_validation_id:
            checks.append("source validation provenance mismatch")
        if lineage_read_id != receipt.read_id:
            checks.append("read lineage mismatch")
        if lineage_consumption_request_id != receipt.consumption_request_id:
            checks.append("consumption request lineage mismatch")

        valid = not checks
        payload = {"receipt_id": receipt.receipt_id, "consumer_id": consumer_id} if valid else {"rejected_receipt": True}
        final_reasons = reasons if reasons is not None else (("received semantic use consumed at the declared downstream boundary",) if valid else tuple(checks))
        status = LearningStateExecutionLearningStateSemanticUseConsumptionStatus.CONSUMED if valid else LearningStateExecutionLearningStateSemanticUseConsumptionStatus.REJECTED
        return LearningStateExecutionLearningStateSemanticUseConsumption(
            consumption_id=consumption_id,
            receipt_id=receipt.receipt_id,
            handoff_id=receipt.handoff_id,
            integrity_id=receipt.integrity_id,
            validation_id=receipt.validation_id,
            semantic_use_id=receipt.semantic_use_id,
            source_request_id=receipt.source_request_id,
            source_request_lineage_id=receipt.source_request_lineage_id,
            source_validation_id=receipt.source_validation_id,
            source_validation_lineage_id=receipt.source_validation_lineage_id,
            interpretation_id=receipt.interpretation_id,
            read_id=receipt.read_id,
            consumption_request_id=receipt.consumption_request_id,
            requester_id=receipt.requester_id,
            consumer_id=consumer_id,
            handoff_target_id=receipt.handoff_target_id,
            recipient_id=receipt.recipient_id,
            consumption_purpose=consumption_purpose,
            consumption_rationale=consumption_rationale,
            payload=payload,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "consumption_id": consumption_id,
                "receipt_id": receipt.receipt_id,
                "handoff_id": receipt.handoff_id,
                "integrity_id": receipt.integrity_id,
                "validation_id": receipt.validation_id,
                "semantic_use_id": receipt.semantic_use_id,
                "request_id": receipt.source_request_lineage_id,
                "source_validation_id": receipt.source_validation_lineage_id,
                "interpretation_id": receipt.interpretation_id,
                "source_request_id": receipt.source_request_id,
                "source_validation_provenance_id": receipt.source_validation_id,
                "read_id": receipt.read_id,
                "consumption_request_id": receipt.consumption_request_id,
                "handoff_target_id": receipt.handoff_target_id,
                "recipient_id": receipt.recipient_id,
                "consumer_id": consumer_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateSemanticUseConsumptionError",
    "LearningStateExecutionLearningStateSemanticUseConsumptionStatus",
    "LearningStateExecutionLearningStateSemanticUseConsumption",
    "LearningStateExecutionLearningStateSemanticUseConsumptionService",
]
