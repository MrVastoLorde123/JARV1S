"""M23.115: package integrity-valid semantic-use evidence for downstream receipt."""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping
from enum import Enum

from src.core.learning_state_semantic_use_validation_integrity import (
    LearningStateSemanticUseIntegrity,
    LearningStateSemanticUseIntegrityStatus,
)


class LearningStateSemanticUseHandoffError(RuntimeError):
    """Raised when a semantic-use handoff cannot be formed safely."""


class LearningStateSemanticUseHandoffStatus(str, Enum):
    READY = "READY"
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
class LearningStateSemanticUseHandoff:
    """Immutable sealed package for bounded downstream receipt of semantic-use evidence."""

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
    handoff_status: LearningStateSemanticUseHandoffStatus
    integrity_status: LearningStateSemanticUseIntegrityStatus
    result: Mapping[str, Any]
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "handoff_id", "integrity_id", "validation_id", "use_id", "request_id", "interpretation_id",
            "source_request_id", "read_validation_id", "read_id", "consumption_request_id",
            "source_validation_id", "source_integrity_id", "transition_id", "evidence_id", "application_id",
            "state_key", "transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "consumer_id", "use_purpose", "downstream_recipient_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("semantic-use handoff requires SHA-256 fingerprints")
        if not isinstance(self.handoff_status, LearningStateSemanticUseHandoffStatus):
            raise TypeError("handoff_status must be a semantic-use handoff status")
        if not isinstance(self.integrity_status, LearningStateSemanticUseIntegrityStatus):
            raise TypeError("integrity_status must be a semantic-use integrity status")
        if self.handoff_status is LearningStateSemanticUseHandoffStatus.READY:
            if self.integrity_status is not LearningStateSemanticUseIntegrityStatus.VALID:
                raise ValueError("READY handoff requires VALID semantic-use integrity")
            if not isinstance(self.result, Mapping):
                raise TypeError("READY handoff requires a mapping result")
        if not isinstance(self.result, Mapping):
            raise TypeError("result must be a mapping")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "result", _freeze(self.result))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_ready(self) -> bool:
        return self.handoff_status is LearningStateSemanticUseHandoffStatus.READY

    @property
    def invokes_downstream_recipient(self) -> bool:
        return False

    @property
    def transforms_semantic_result(self) -> bool:
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


class LearningStateSemanticUseHandoffService:
    """Seal integrity-valid semantic-use evidence for downstream receipt without invoking it."""

    def handoff(
        self,
        integrity: LearningStateSemanticUseIntegrity,
        *,
        handoff_id: str,
        downstream_recipient_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateSemanticUseHandoff:
        if type(integrity) is not LearningStateSemanticUseIntegrity:
            raise TypeError("integrity must be a learning-state semantic-use integrity artifact")
        if not isinstance(handoff_id, str) or not handoff_id.strip():
            raise ValueError("handoff_id must be a non-empty string")
        if not isinstance(downstream_recipient_id, str) or not downstream_recipient_id.strip():
            raise ValueError("downstream_recipient_id must be a non-empty string")
        ready = integrity.integrity_status is LearningStateSemanticUseIntegrityStatus.VALID
        status = LearningStateSemanticUseHandoffStatus.READY if ready else LearningStateSemanticUseHandoffStatus.REJECTED
        if not ready:
            raise ValueError("semantic-use handoff requires VALID semantic-use integrity")
        return LearningStateSemanticUseHandoff(
            handoff_id=handoff_id,
            integrity_id=integrity.integrity_id,
            validation_id=integrity.validation_id,
            use_id=integrity.use_id,
            request_id=integrity.request_id,
            interpretation_id=integrity.interpretation_id,
            source_request_id=integrity.source_request_id,
            read_validation_id=integrity.read_validation_id,
            read_id=integrity.read_id,
            consumption_request_id=integrity.consumption_request_id,
            source_validation_id=integrity.source_validation_id,
            source_integrity_id=integrity.source_integrity_id,
            transition_id=integrity.transition_id,
            evidence_id=integrity.evidence_id,
            application_id=integrity.application_id,
            state_key=integrity.state_key,
            transition_fingerprint=integrity.transition_fingerprint,
            source_application_fingerprint=integrity.source_application_fingerprint,
            computed_application_fingerprint=integrity.computed_application_fingerprint,
            confidence=integrity.confidence,
            consumer_id=integrity.consumer_id,
            use_purpose=integrity.use_purpose,
            downstream_recipient_id=downstream_recipient_id,
            handoff_status=status,
            integrity_status=integrity.integrity_status,
            result=integrity.result,
            reasons=reasons if reasons is not None else {"handoff_status": status.value},
            lineage=lineage if lineage is not None else {"handoff_id": handoff_id, "integrity_id": integrity.integrity_id},
        )


__all__ = [
    "LearningStateSemanticUseHandoffError",
    "LearningStateSemanticUseHandoffStatus",
    "LearningStateSemanticUseHandoff",
    "LearningStateSemanticUseHandoffService",
]
