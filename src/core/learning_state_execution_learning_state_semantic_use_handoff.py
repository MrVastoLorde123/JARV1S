"""M23.147: hand off integrity-verified semantic-use evidence without granting authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_semantic_use_validation_integrity import (
    LearningStateExecutionLearningStateSemanticUseValidationIntegrity,
    LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus,
)


class LearningStateExecutionLearningStateSemanticUseHandoffError(RuntimeError):
    """Raised when semantic-use handoff evidence cannot be formed safely."""


class LearningStateExecutionLearningStateSemanticUseHandoffStatus(str, Enum):
    HANDED_OFF = "HANDED_OFF"
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
class LearningStateExecutionLearningStateSemanticUseHandoff:
    """Immutable evidence that one integrity-verified semantic-use result was presented downstream."""

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
    handoff_purpose: str
    handoff_rationale: Any
    payload: Any
    status: LearningStateExecutionLearningStateSemanticUseHandoffStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "handoff_id", "integrity_id", "validation_id", "semantic_use_id", "source_request_id",
            "source_request_lineage_id", "source_validation_id", "source_validation_lineage_id",
            "interpretation_id", "read_id", "consumption_request_id", "requester_id", "consumer_id",
            "handoff_target_id", "handoff_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, LearningStateExecutionLearningStateSemanticUseHandoffStatus):
            raise TypeError("status must be a semantic-use handoff status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "handoff_rationale", _freeze(self.handoff_rationale))
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_handed_off(self) -> bool:
        return self.status is LearningStateExecutionLearningStateSemanticUseHandoffStatus.HANDED_OFF

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateSemanticUseHandoffStatus.REJECTED

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


class LearningStateExecutionLearningStateSemanticUseHandoffService:
    """Present integrity-verified semantic-use evidence to a named downstream boundary only."""

    def handoff(
        self,
        integrity: LearningStateExecutionLearningStateSemanticUseValidationIntegrity,
        *,
        handoff_id: str,
        handoff_target_id: str,
        handoff_purpose: str,
        handoff_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateSemanticUseHandoff:
        if type(integrity) is not LearningStateExecutionLearningStateSemanticUseValidationIntegrity:
            raise TypeError("integrity must be a semantic-use validation-integrity artifact")
        for name, value in (
            ("handoff_id", handoff_id),
            ("handoff_target_id", handoff_target_id),
            ("handoff_purpose", handoff_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if handoff_rationale is None:
            raise ValueError("handoff_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if integrity.status is not LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus.VALID:
            checks.append("semantic-use validation integrity status must be VALID")
        if handoff_id == integrity.integrity_id:
            checks.append("handoff identity must be distinct")

        lineage_integrity_id = integrity.lineage.get("integrity_id", integrity.integrity_id)
        lineage_validation_id = integrity.lineage.get("validation_id", integrity.validation_id)
        lineage_semantic_use_id = integrity.lineage.get("semantic_use_id", integrity.semantic_use_id)
        lineage_request_id = integrity.lineage.get("request_id", integrity.source_request_lineage_id)
        lineage_upstream_integrity_id = integrity.lineage.get("upstream_integrity_id")
        lineage_source_validation_id = integrity.lineage.get("source_validation_id", integrity.source_validation_lineage_id)
        lineage_interpretation_id = integrity.lineage.get("interpretation_id", integrity.interpretation_id)
        lineage_source_request_id = integrity.lineage.get("source_request_id", integrity.source_request_id)
        lineage_source_validation_provenance_id = integrity.lineage.get("source_validation_provenance_id", integrity.source_validation_id)
        lineage_read_id = integrity.lineage.get("read_id", integrity.read_id)
        lineage_consumption_request_id = integrity.lineage.get("consumption_request_id", integrity.consumption_request_id)
        expected_upstream_integrity_id = integrity.lineage.get("upstream_integrity_id")

        if lineage_integrity_id != integrity.integrity_id:
            checks.append("integrity lineage mismatch")
        if lineage_validation_id != integrity.validation_id:
            checks.append("validation lineage mismatch")
        if lineage_semantic_use_id != integrity.semantic_use_id:
            checks.append("semantic-use lineage mismatch")
        if lineage_request_id != integrity.source_request_lineage_id:
            checks.append("source request lineage mismatch")
        if lineage_upstream_integrity_id != expected_upstream_integrity_id:
            checks.append("upstream integrity lineage mismatch")
        if lineage_source_validation_id != integrity.source_validation_lineage_id:
            checks.append("source validation lineage mismatch")
        if lineage_interpretation_id != integrity.interpretation_id:
            checks.append("interpretation lineage mismatch")
        if lineage_source_request_id != integrity.source_request_id:
            checks.append("source request provenance mismatch")
        if lineage_source_validation_provenance_id != integrity.source_validation_id:
            checks.append("source validation provenance mismatch")
        if lineage_read_id != integrity.read_id:
            checks.append("read lineage mismatch")
        if lineage_consumption_request_id != integrity.consumption_request_id:
            checks.append("consumption request lineage mismatch")

        valid = not checks
        payload = {"validation_id": integrity.validation_id, "semantic_use_id": integrity.semantic_use_id, "handoff_target_id": handoff_target_id} if valid else {"rejected_integrity": True}
        final_reasons = reasons if reasons is not None else (("integrity-verified semantic use presented to the declared downstream boundary",) if valid else tuple(checks))
        status = LearningStateExecutionLearningStateSemanticUseHandoffStatus.HANDED_OFF if valid else LearningStateExecutionLearningStateSemanticUseHandoffStatus.REJECTED
        return LearningStateExecutionLearningStateSemanticUseHandoff(
            handoff_id=handoff_id,
            integrity_id=integrity.integrity_id,
            validation_id=integrity.validation_id,
            semantic_use_id=integrity.semantic_use_id,
            source_request_id=integrity.source_request_id,
            source_request_lineage_id=integrity.source_request_lineage_id,
            source_validation_id=integrity.source_validation_id,
            source_validation_lineage_id=integrity.source_validation_lineage_id,
            interpretation_id=integrity.interpretation_id,
            read_id=integrity.read_id,
            consumption_request_id=integrity.consumption_request_id,
            requester_id=integrity.requester_id,
            consumer_id=integrity.consumer_id,
            handoff_target_id=handoff_target_id,
            handoff_purpose=handoff_purpose,
            handoff_rationale=handoff_rationale,
            payload=payload,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "handoff_id": handoff_id,
                "integrity_id": integrity.integrity_id,
                "validation_id": integrity.validation_id,
                "semantic_use_id": integrity.semantic_use_id,
                "request_id": integrity.source_request_lineage_id,
                "upstream_integrity_id": integrity.lineage.get("upstream_integrity_id"),
                "source_validation_id": integrity.source_validation_lineage_id,
                "interpretation_id": integrity.interpretation_id,
                "source_request_id": integrity.source_request_id,
                "source_validation_provenance_id": integrity.source_validation_id,
                "read_id": integrity.read_id,
                "consumption_request_id": integrity.consumption_request_id,
                "handoff_target_id": handoff_target_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateSemanticUseHandoffError",
    "LearningStateExecutionLearningStateSemanticUseHandoffStatus",
    "LearningStateExecutionLearningStateSemanticUseHandoff",
    "LearningStateExecutionLearningStateSemanticUseHandoffService",
]
