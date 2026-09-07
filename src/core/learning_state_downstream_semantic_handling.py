"""M23.118: package consumed semantic use for a named downstream handler."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_semantic_use_consumption import (
    LearningStateSemanticUseConsumption,
    LearningStateSemanticUseConsumptionStatus,
)


class LearningStateDownstreamSemanticHandlingError(RuntimeError):
    """Raised when a downstream semantic-handling artifact cannot be formed safely."""


class LearningStateDownstreamSemanticHandlingStatus(str, Enum):
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
class LearningStateDownstreamSemanticHandling:
    """Immutable evidence that consumed semantic use was bound for downstream handling."""

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
    consumption_status: LearningStateSemanticUseConsumptionStatus
    handling_status: LearningStateDownstreamSemanticHandlingStatus
    result: Mapping[str, Any]
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "handling_id", "consumption_id", "receipt_id", "handoff_id", "integrity_id", "validation_id",
            "use_id", "request_id", "interpretation_id", "source_request_id", "read_validation_id",
            "read_id", "consumption_request_id", "source_validation_id", "source_integrity_id",
            "transition_id", "evidence_id", "application_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint", "consumer_id",
            "use_purpose", "downstream_recipient_id", "downstream_handler_id", "handling_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("downstream semantic handling requires SHA-256 fingerprints")
        if not isinstance(self.consumption_status, LearningStateSemanticUseConsumptionStatus):
            raise TypeError("consumption_status must be a semantic-use consumption status")
        if not isinstance(self.handling_status, LearningStateDownstreamSemanticHandlingStatus):
            raise TypeError("handling_status must be a downstream handling status")
        if self.handling_status is LearningStateDownstreamSemanticHandlingStatus.READY and self.consumption_status is not LearningStateSemanticUseConsumptionStatus.CONSUMED:
            raise ValueError("READY handling requires CONSUMED semantic-use evidence")
        if not isinstance(self.result, Mapping):
            raise TypeError("result must be a mapping")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "result", _freeze(self.result))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_ready(self) -> bool:
        return self.handling_status is LearningStateDownstreamSemanticHandlingStatus.READY

    @property
    def invokes_handler(self) -> bool:
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

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def executes_action(self) -> bool:
        return False


class LearningStateDownstreamSemanticHandlingService:
    """Bind consumed semantic use to a named handler without invoking it."""

    def handle(
        self,
        consumption: LearningStateSemanticUseConsumption,
        *,
        handling_id: str,
        downstream_handler_id: str,
        handling_purpose: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateDownstreamSemanticHandling:
        if type(consumption) is not LearningStateSemanticUseConsumption:
            raise TypeError("consumption must be a learning-state semantic-use consumption artifact")
        for name, value in (
            ("handling_id", handling_id),
            ("downstream_handler_id", downstream_handler_id),
            ("handling_purpose", handling_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if consumption.consumption_status is not LearningStateSemanticUseConsumptionStatus.CONSUMED or not consumption.is_consumed:
            raise ValueError("downstream handling requires CONSUMED semantic-use evidence")
        return LearningStateDownstreamSemanticHandling(
            handling_id=handling_id,
            consumption_id=consumption.consumption_id,
            receipt_id=consumption.receipt_id,
            handoff_id=consumption.handoff_id,
            integrity_id=consumption.integrity_id,
            validation_id=consumption.validation_id,
            use_id=consumption.use_id,
            request_id=consumption.request_id,
            interpretation_id=consumption.interpretation_id,
            source_request_id=consumption.source_request_id,
            read_validation_id=consumption.read_validation_id,
            read_id=consumption.read_id,
            consumption_request_id=consumption.consumption_request_id,
            source_validation_id=consumption.source_validation_id,
            source_integrity_id=consumption.source_integrity_id,
            transition_id=consumption.transition_id,
            evidence_id=consumption.evidence_id,
            application_id=consumption.application_id,
            state_key=consumption.state_key,
            transition_fingerprint=consumption.transition_fingerprint,
            source_application_fingerprint=consumption.source_application_fingerprint,
            computed_application_fingerprint=consumption.computed_application_fingerprint,
            confidence=consumption.confidence,
            consumer_id=consumption.consumer_id,
            use_purpose=consumption.use_purpose,
            downstream_recipient_id=consumption.downstream_recipient_id,
            downstream_handler_id=downstream_handler_id,
            handling_purpose=handling_purpose,
            consumption_status=consumption.consumption_status,
            handling_status=LearningStateDownstreamSemanticHandlingStatus.READY,
            result=consumption.result,
            reasons=reasons if reasons is not None else {"handling_status": "READY"},
            lineage=lineage if lineage is not None else {"handling_id": handling_id, "consumption_id": consumption.consumption_id, "downstream_handler_id": downstream_handler_id},
        )


__all__ = [
    "LearningStateDownstreamSemanticHandlingError",
    "LearningStateDownstreamSemanticHandlingStatus",
    "LearningStateDownstreamSemanticHandling",
    "LearningStateDownstreamSemanticHandlingService",
]
