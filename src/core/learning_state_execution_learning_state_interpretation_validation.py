"""M23.141: validate learning-state interpretation evidence without adding authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_interpretation import (
    LearningStateExecutionLearningStateInterpretation,
    LearningStateExecutionLearningStateInterpretationStatus,
)


class LearningStateExecutionLearningStateInterpretationValidationError(RuntimeError):
    """Raised when interpretation validation evidence cannot be formed safely."""


class LearningStateExecutionLearningStateInterpretationValidationStatus(str, Enum):
    VALIDATED = "VALIDATED"
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


def _describe_payload(payload: Any) -> Any:
    if isinstance(payload, Mapping):
        return {"kind": "mapping", "keys": tuple(sorted(str(key) for key in payload.keys())), "size": len(payload)}
    if isinstance(payload, (list, tuple)):
        return {"kind": "sequence", "size": len(payload), "item_types": tuple(type(item).__name__ for item in payload)}
    if isinstance(payload, (set, frozenset)):
        return {"kind": "set", "size": len(payload), "item_types": tuple(sorted(type(item).__name__ for item in payload))}
    if payload is None:
        return {"kind": "none"}
    return {"kind": type(payload).__name__}


@dataclass(frozen=True)
class LearningStateExecutionLearningStateInterpretationValidation:
    """Immutable evidence that one M23.140 interpretation satisfied the validation contract."""

    validation_id: str
    interpretation_id: str
    source_request_id: str
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
    interpretation: Any
    interpreter_id: str
    validation_actor_id: str
    validation_purpose: str
    validation_rationale: Any
    status: LearningStateExecutionLearningStateInterpretationValidationStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        required = (
            "validation_id", "interpretation_id", "source_request_id", "source_validation_id", "read_id",
            "consumption_request_id", "integrity_id", "transition_id", "evidence_id", "state_key",
            "read_fingerprint", "computed_read_fingerprint", "reader_id", "read_purpose", "requester_id",
            "interpretation_purpose", "interpreter_id", "validation_actor_id", "validation_purpose",
        )
        for name in required:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if not isinstance(self.status, LearningStateExecutionLearningStateInterpretationValidationStatus):
            raise TypeError("status must be an interpretation validation status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "requested_scope", _freeze(self.requested_scope))
        object.__setattr__(self, "read_payload", _freeze(self.read_payload))
        object.__setattr__(self, "request_rationale", _freeze(self.request_rationale))
        object.__setattr__(self, "interpretation_rationale", _freeze(self.interpretation_rationale))
        object.__setattr__(self, "interpretation", _freeze(self.interpretation))
        object.__setattr__(self, "validation_rationale", _freeze(self.validation_rationale))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_validated(self) -> bool:
        return self.status is LearningStateExecutionLearningStateInterpretationValidationStatus.VALIDATED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateInterpretationValidationStatus.REJECTED

    @property
    def admits_interpretation_validation_integrity(self) -> bool:
        return self.is_validated

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


class LearningStateExecutionLearningStateInterpretationValidationService:
    """Validate M23.140 interpretation evidence without reinterpreting or consuming it."""

    def validate(
        self,
        interpretation: LearningStateExecutionLearningStateInterpretation,
        *,
        validation_id: str,
        validation_actor_id: str,
        validation_purpose: str,
        validation_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateInterpretationValidation:
        if type(interpretation) is not LearningStateExecutionLearningStateInterpretation:
            raise TypeError("interpretation must be a learning-state interpretation artifact")
        for name, value in (("validation_id", validation_id), ("validation_actor_id", validation_actor_id), ("validation_purpose", validation_purpose)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if validation_rationale is None:
            raise ValueError("validation_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if interpretation.status is not LearningStateExecutionLearningStateInterpretationStatus.INTERPRETED:
            checks.append("learning-state interpretation is not INTERPRETED")
        if validation_id == interpretation.interpretation_id:
            checks.append("validation identity must be distinct from interpretation identity")
        if interpretation.lineage.get("interpretation_id", interpretation.interpretation_id) != interpretation.interpretation_id:
            checks.append("interpretation lineage mismatch")
        if interpretation.lineage.get("request_id", interpretation.source_request_id) != interpretation.source_request_id:
            checks.append("request lineage mismatch")
        direct_validation_id = interpretation.lineage.get("validation_id")
        if not isinstance(direct_validation_id, str) or not direct_validation_id.strip():
            checks.append("source validation lineage mismatch")
        if interpretation.lineage.get("read_id", interpretation.read_id) != interpretation.read_id:
            checks.append("read lineage mismatch")
        if interpretation.lineage.get("consumption_request_id", interpretation.consumption_request_id) != interpretation.consumption_request_id:
            checks.append("consumption request lineage mismatch")
        if interpretation.source_validation_id == interpretation.interpretation_id:
            checks.append("source validation identity must be distinct from interpretation identity")
        if interpretation.read_fingerprint != interpretation.computed_read_fingerprint:
            checks.append("read fingerprint mismatch")
        if len(interpretation.read_fingerprint) != 64:
            checks.append("read fingerprint is not SHA-256")
        if _describe_payload(interpretation.read_payload) != interpretation.interpretation:
            checks.append("interpretation is inconsistent with supplied read payload")
        if isinstance(interpretation.confidence, bool) or not isinstance(interpretation.confidence, (int, float)) or not 0.0 <= float(interpretation.confidence) <= 1.0:
            checks.append("confidence is outside bounds")

        valid = not checks
        if reasons is not None:
            final_reasons = reasons
        elif valid:
            final_reasons = ("learning-state interpretation passed validation",)
        else:
            final_reasons = tuple(checks)
        status = (
            LearningStateExecutionLearningStateInterpretationValidationStatus.VALIDATED
            if valid else LearningStateExecutionLearningStateInterpretationValidationStatus.REJECTED
        )
        return LearningStateExecutionLearningStateInterpretationValidation(
            validation_id=validation_id,
            interpretation_id=interpretation.interpretation_id,
            source_request_id=interpretation.source_request_id,
            source_validation_id=interpretation.source_validation_id,
            read_id=interpretation.read_id,
            consumption_request_id=interpretation.consumption_request_id,
            integrity_id=interpretation.integrity_id,
            transition_id=interpretation.transition_id,
            evidence_id=interpretation.evidence_id,
            state_key=interpretation.state_key,
            requested_scope=interpretation.requested_scope,
            read_payload=interpretation.read_payload,
            read_fingerprint=interpretation.read_fingerprint,
            computed_read_fingerprint=interpretation.computed_read_fingerprint,
            reader_id=interpretation.reader_id,
            read_purpose=interpretation.read_purpose,
            request_rationale=interpretation.request_rationale,
            confidence=interpretation.confidence,
            requester_id=interpretation.requester_id,
            interpretation_purpose=interpretation.interpretation_purpose,
            interpretation_rationale=interpretation.interpretation_rationale,
            interpretation=interpretation.interpretation,
            interpreter_id=interpretation.interpreter_id,
            validation_actor_id=validation_actor_id,
            validation_purpose=validation_purpose,
            validation_rationale=validation_rationale,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "validation_id": validation_id,
                "interpretation_id": interpretation.interpretation_id,
                "request_id": interpretation.source_request_id,
                "source_validation_id": interpretation.source_validation_id,
                "read_id": interpretation.read_id,
                "consumption_request_id": interpretation.consumption_request_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateInterpretationValidationError",
    "LearningStateExecutionLearningStateInterpretationValidationStatus",
    "LearningStateExecutionLearningStateInterpretationValidation",
    "LearningStateExecutionLearningStateInterpretationValidationService",
]
