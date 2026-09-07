"""M23.148: acknowledge receipt of a semantic-use handoff without granting authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_semantic_use_handoff import (
    LearningStateExecutionLearningStateSemanticUseHandoff,
    LearningStateExecutionLearningStateSemanticUseHandoffStatus,
)


class LearningStateExecutionLearningStateSemanticUseReceiptError(RuntimeError):
    """Raised when semantic-use receipt evidence cannot be formed safely."""


class LearningStateExecutionLearningStateSemanticUseReceiptStatus(str, Enum):
    RECEIVED = "RECEIVED"
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
class LearningStateExecutionLearningStateSemanticUseReceipt:
    """Immutable evidence that one handed-off semantic-use result was received downstream."""

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
    receipt_purpose: str
    receipt_rationale: Any
    payload: Any
    status: LearningStateExecutionLearningStateSemanticUseReceiptStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "receipt_id", "handoff_id", "integrity_id", "validation_id", "semantic_use_id", "source_request_id",
            "source_request_lineage_id", "source_validation_id", "source_validation_lineage_id", "interpretation_id",
            "read_id", "consumption_request_id", "requester_id", "consumer_id", "handoff_target_id",
            "recipient_id", "receipt_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, LearningStateExecutionLearningStateSemanticUseReceiptStatus):
            raise TypeError("status must be a semantic-use receipt status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "receipt_rationale", _freeze(self.receipt_rationale))
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_received(self) -> bool:
        return self.status is LearningStateExecutionLearningStateSemanticUseReceiptStatus.RECEIVED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateSemanticUseReceiptStatus.REJECTED

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


class LearningStateExecutionLearningStateSemanticUseReceiptService:
    """Acknowledge a handed-off semantic-use result at a named recipient boundary only."""

    def receive(
        self,
        handoff: LearningStateExecutionLearningStateSemanticUseHandoff,
        *,
        receipt_id: str,
        recipient_id: str,
        receipt_purpose: str,
        receipt_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateSemanticUseReceipt:
        if type(handoff) is not LearningStateExecutionLearningStateSemanticUseHandoff:
            raise TypeError("handoff must be a semantic-use handoff artifact")
        for name, value in (
            ("receipt_id", receipt_id),
            ("recipient_id", recipient_id),
            ("receipt_purpose", receipt_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if receipt_rationale is None:
            raise ValueError("receipt_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if handoff.status is not LearningStateExecutionLearningStateSemanticUseHandoffStatus.HANDED_OFF:
            checks.append("semantic-use handoff status must be HANDED_OFF")
        if receipt_id == handoff.handoff_id:
            checks.append("receipt identity must be distinct")

        lineage_handoff_id = handoff.lineage.get("handoff_id", handoff.handoff_id)
        lineage_integrity_id = handoff.lineage.get("integrity_id", handoff.integrity_id)
        lineage_validation_id = handoff.lineage.get("validation_id", handoff.validation_id)
        lineage_semantic_use_id = handoff.lineage.get("semantic_use_id", handoff.semantic_use_id)
        lineage_request_id = handoff.lineage.get("request_id", handoff.source_request_lineage_id)
        lineage_source_validation_id = handoff.lineage.get("source_validation_id", handoff.source_validation_lineage_id)
        lineage_interpretation_id = handoff.lineage.get("interpretation_id", handoff.interpretation_id)
        lineage_source_request_id = handoff.lineage.get("source_request_id", handoff.source_request_id)
        lineage_source_validation_provenance_id = handoff.lineage.get("source_validation_provenance_id", handoff.source_validation_id)
        lineage_read_id = handoff.lineage.get("read_id", handoff.read_id)
        lineage_consumption_request_id = handoff.lineage.get("consumption_request_id", handoff.consumption_request_id)

        if lineage_handoff_id != handoff.handoff_id:
            checks.append("handoff lineage mismatch")
        if lineage_integrity_id != handoff.integrity_id:
            checks.append("integrity lineage mismatch")
        if lineage_validation_id != handoff.validation_id:
            checks.append("validation lineage mismatch")
        if lineage_semantic_use_id != handoff.semantic_use_id:
            checks.append("semantic-use lineage mismatch")
        if lineage_request_id != handoff.source_request_lineage_id:
            checks.append("source request lineage mismatch")
        if lineage_source_validation_id != handoff.source_validation_lineage_id:
            checks.append("source validation lineage mismatch")
        if lineage_interpretation_id != handoff.interpretation_id:
            checks.append("interpretation lineage mismatch")
        if lineage_source_request_id != handoff.source_request_id:
            checks.append("source request provenance mismatch")
        if lineage_source_validation_provenance_id != handoff.source_validation_id:
            checks.append("source validation provenance mismatch")
        if lineage_read_id != handoff.read_id:
            checks.append("read lineage mismatch")
        if lineage_consumption_request_id != handoff.consumption_request_id:
            checks.append("consumption request lineage mismatch")

        valid = not checks
        payload = {"handoff_id": handoff.handoff_id, "recipient_id": recipient_id} if valid else {"rejected_handoff": True}
        final_reasons = reasons if reasons is not None else (("handed-off semantic use received at the declared downstream boundary",) if valid else tuple(checks))
        status = LearningStateExecutionLearningStateSemanticUseReceiptStatus.RECEIVED if valid else LearningStateExecutionLearningStateSemanticUseReceiptStatus.REJECTED
        return LearningStateExecutionLearningStateSemanticUseReceipt(
            receipt_id=receipt_id,
            handoff_id=handoff.handoff_id,
            integrity_id=handoff.integrity_id,
            validation_id=handoff.validation_id,
            semantic_use_id=handoff.semantic_use_id,
            source_request_id=handoff.source_request_id,
            source_request_lineage_id=handoff.source_request_lineage_id,
            source_validation_id=handoff.source_validation_id,
            source_validation_lineage_id=handoff.source_validation_lineage_id,
            interpretation_id=handoff.interpretation_id,
            read_id=handoff.read_id,
            consumption_request_id=handoff.consumption_request_id,
            requester_id=handoff.requester_id,
            consumer_id=handoff.consumer_id,
            handoff_target_id=handoff.handoff_target_id,
            recipient_id=recipient_id,
            receipt_purpose=receipt_purpose,
            receipt_rationale=receipt_rationale,
            payload=payload,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "receipt_id": receipt_id,
                "handoff_id": handoff.handoff_id,
                "integrity_id": handoff.integrity_id,
                "validation_id": handoff.validation_id,
                "semantic_use_id": handoff.semantic_use_id,
                "request_id": handoff.source_request_lineage_id,
                "source_validation_id": handoff.source_validation_lineage_id,
                "interpretation_id": handoff.interpretation_id,
                "source_request_id": handoff.source_request_id,
                "source_validation_provenance_id": handoff.source_validation_id,
                "read_id": handoff.read_id,
                "consumption_request_id": handoff.consumption_request_id,
                "handoff_target_id": handoff.handoff_target_id,
                "recipient_id": recipient_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateSemanticUseReceiptError",
    "LearningStateExecutionLearningStateSemanticUseReceiptStatus",
    "LearningStateExecutionLearningStateSemanticUseReceipt",
    "LearningStateExecutionLearningStateSemanticUseReceiptService",
]
