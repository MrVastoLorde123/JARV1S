"""M23.116: acknowledge receipt of a valid semantic-use handoff."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_semantic_use_handoff import (
    LearningStateSemanticUseHandoff,
    LearningStateSemanticUseHandoffStatus,
)


class LearningStateSemanticUseReceiptError(RuntimeError):
    """Raised when a semantic-use receipt cannot be formed safely."""


class LearningStateSemanticUseReceiptStatus(str, Enum):
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
class LearningStateSemanticUseReceipt:
    """Immutable evidence that a named recipient received one valid handoff."""

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
    receipt_status: LearningStateSemanticUseReceiptStatus
    handoff_status: LearningStateSemanticUseHandoffStatus
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "receipt_id", "handoff_id", "integrity_id", "validation_id", "use_id", "request_id",
            "interpretation_id", "source_request_id", "read_validation_id", "read_id",
            "consumption_request_id", "source_validation_id", "source_integrity_id", "transition_id",
            "evidence_id", "application_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint", "consumer_id",
            "use_purpose", "downstream_recipient_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("semantic-use receipt requires SHA-256 fingerprints")
        if not isinstance(self.receipt_status, LearningStateSemanticUseReceiptStatus):
            raise TypeError("receipt_status must be a semantic-use receipt status")
        if not isinstance(self.handoff_status, LearningStateSemanticUseHandoffStatus):
            raise TypeError("handoff_status must be a semantic-use handoff status")
        if self.receipt_status is LearningStateSemanticUseReceiptStatus.RECEIVED:
            if self.handoff_status is not LearningStateSemanticUseHandoffStatus.READY:
                raise ValueError("RECEIVED receipt requires READY handoff")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_received(self) -> bool:
        return self.receipt_status is LearningStateSemanticUseReceiptStatus.RECEIVED

    @property
    def acknowledges_receipt(self) -> bool:
        return self.is_received

    @property
    def reads_semantic_result(self) -> bool:
        return False

    @property
    def transforms_semantic_result(self) -> bool:
        return False

    @property
    def invokes_downstream_recipient(self) -> bool:
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
    def invokes_interpreter(self) -> bool:
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
    def grants_authority(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def executes_action(self) -> bool:
        return False


class LearningStateSemanticUseReceiptService:
    """Acknowledge receipt of a READY handoff without consuming its semantic payload."""

    def receive(
        self,
        handoff: LearningStateSemanticUseHandoff,
        *,
        receipt_id: str,
        recipient_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateSemanticUseReceipt:
        if type(handoff) is not LearningStateSemanticUseHandoff:
            raise TypeError("handoff must be a learning-state semantic-use handoff artifact")
        if not isinstance(receipt_id, str) or not receipt_id.strip():
            raise ValueError("receipt_id must be a non-empty string")
        if not isinstance(recipient_id, str) or not recipient_id.strip():
            raise ValueError("recipient_id must be a non-empty string")
        if handoff.handoff_status is not LearningStateSemanticUseHandoffStatus.READY:
            raise ValueError("semantic-use receipt requires READY semantic-use handoff")
        if recipient_id != handoff.downstream_recipient_id:
            raise ValueError("recipient_id must match the handoff downstream recipient")
        return LearningStateSemanticUseReceipt(
            receipt_id=receipt_id,
            handoff_id=handoff.handoff_id,
            integrity_id=handoff.integrity_id,
            validation_id=handoff.validation_id,
            use_id=handoff.use_id,
            request_id=handoff.request_id,
            interpretation_id=handoff.interpretation_id,
            source_request_id=handoff.source_request_id,
            read_validation_id=handoff.read_validation_id,
            read_id=handoff.read_id,
            consumption_request_id=handoff.consumption_request_id,
            source_validation_id=handoff.source_validation_id,
            source_integrity_id=handoff.source_integrity_id,
            transition_id=handoff.transition_id,
            evidence_id=handoff.evidence_id,
            application_id=handoff.application_id,
            state_key=handoff.state_key,
            transition_fingerprint=handoff.transition_fingerprint,
            source_application_fingerprint=handoff.source_application_fingerprint,
            computed_application_fingerprint=handoff.computed_application_fingerprint,
            confidence=handoff.confidence,
            consumer_id=handoff.consumer_id,
            use_purpose=handoff.use_purpose,
            downstream_recipient_id=handoff.downstream_recipient_id,
            receipt_status=LearningStateSemanticUseReceiptStatus.RECEIVED,
            handoff_status=handoff.handoff_status,
            reasons=reasons if reasons is not None else {"receipt_status": "RECEIVED"},
            lineage=lineage if lineage is not None else {"receipt_id": receipt_id, "handoff_id": handoff.handoff_id},
        )


__all__ = [
    "LearningStateSemanticUseReceiptError",
    "LearningStateSemanticUseReceiptStatus",
    "LearningStateSemanticUseReceipt",
    "LearningStateSemanticUseReceiptService",
]
