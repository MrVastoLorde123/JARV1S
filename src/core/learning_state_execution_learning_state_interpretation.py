"""M23.140: interpret an explicit interpretation request without granting authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_interpretation_request import (
    LearningStateExecutionLearningStateInterpretationRequest,
    LearningStateExecutionLearningStateInterpretationRequestStatus,
)


class LearningStateExecutionLearningStateInterpretationError(RuntimeError):
    """Raised when a learning-state interpretation cannot be formed safely."""


class LearningStateExecutionLearningStateInterpretationStatus(str, Enum):
    INTERPRETED = "INTERPRETED"
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
    """Produce a deterministic structural interpretation without asserting meaning or truth."""
    if isinstance(payload, Mapping):
        keys = tuple(sorted((str(key) for key in payload.keys())))
        return {
            "kind": "mapping",
            "keys": keys,
            "size": len(payload),
        }
    if isinstance(payload, (list, tuple)):
        return {
            "kind": "sequence",
            "size": len(payload),
            "item_types": tuple(type(item).__name__ for item in payload),
        }
    if isinstance(payload, (set, frozenset)):
        return {
            "kind": "set",
            "size": len(payload),
            "item_types": tuple(sorted(type(item).__name__ for item in payload)),
        }
    if payload is None:
        return {"kind": "none"}
    return {"kind": type(payload).__name__}


@dataclass(frozen=True)
class LearningStateExecutionLearningStateInterpretation:
    """Immutable bounded interpretation evidence derived only from an M23.139 request."""

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
    status: LearningStateExecutionLearningStateInterpretationStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "interpretation_id", "source_request_id", "source_validation_id", "read_id", "consumption_request_id",
            "integrity_id", "transition_id", "evidence_id", "state_key", "read_fingerprint", "computed_read_fingerprint",
            "reader_id", "read_purpose", "requester_id", "interpretation_purpose", "interpreter_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if not isinstance(self.status, LearningStateExecutionLearningStateInterpretationStatus):
            raise TypeError("status must be an interpretation status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "requested_scope", _freeze(self.requested_scope))
        object.__setattr__(self, "read_payload", _freeze(self.read_payload))
        object.__setattr__(self, "request_rationale", _freeze(self.request_rationale))
        object.__setattr__(self, "interpretation_rationale", _freeze(self.interpretation_rationale))
        object.__setattr__(self, "interpretation", _freeze(self.interpretation))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_interpreted(self) -> bool:
        return self.status is LearningStateExecutionLearningStateInterpretationStatus.INTERPRETED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateInterpretationStatus.REJECTED

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
        return self.is_interpreted

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


class LearningStateExecutionLearningStateInterpretationService:
    """Perform bounded interpretation of an M23.139 request without rereading or authorizing."""

    def interpret(
        self,
        request: LearningStateExecutionLearningStateInterpretationRequest,
        *,
        interpretation_id: str,
        interpreter_id: str,
        interpretation_purpose: str,
        interpretation_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateInterpretation:
        if type(request) is not LearningStateExecutionLearningStateInterpretationRequest:
            raise TypeError("request must be an interpretation-request artifact")
        for name, value in (("interpretation_id", interpretation_id), ("interpreter_id", interpreter_id), ("interpretation_purpose", interpretation_purpose)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if interpretation_rationale is None:
            raise ValueError("interpretation_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if request.status is not LearningStateExecutionLearningStateInterpretationRequestStatus.REQUESTED:
            checks.append("interpretation request is not REQUESTED")
        if interpretation_id == request.request_id:
            checks.append("interpretation identity must be distinct from request identity")
        if interpretation_id == request.source_validation_id:
            checks.append("interpretation identity must be distinct from source validation identity")

        lineage_request_id = request.lineage.get("request_id", request.request_id)
        lineage_validation_id = request.lineage.get("validation_id")
        lineage_read_id = request.lineage.get("read_id", request.read_id)
        lineage_consumption_request_id = request.lineage.get("consumption_request_id", request.consumption_request_id)
        if lineage_request_id != request.request_id:
            checks.append("interpretation request lineage mismatch")
        if lineage_validation_id != request.validation_id:
            checks.append("source validation lineage mismatch")
        if lineage_read_id != request.read_id:
            checks.append("read lineage mismatch")
        if lineage_consumption_request_id != request.consumption_request_id:
            checks.append("consumption request lineage mismatch")

        interpretation = _describe_payload(request.read_payload) if not checks else {"kind": "unavailable"}
        valid = not checks
        if reasons is not None:
            final_reasons = reasons
        elif valid:
            final_reasons = ("learning-state interpretation completed",)
        else:
            final_reasons = tuple(checks)
        status = (
            LearningStateExecutionLearningStateInterpretationStatus.INTERPRETED
            if valid else LearningStateExecutionLearningStateInterpretationStatus.REJECTED
        )
        return LearningStateExecutionLearningStateInterpretation(
            interpretation_id=interpretation_id,
            source_request_id=request.request_id,
            source_validation_id=request.source_validation_id,
            read_id=request.read_id,
            consumption_request_id=request.consumption_request_id,
            integrity_id=request.integrity_id,
            transition_id=request.transition_id,
            evidence_id=request.evidence_id,
            state_key=request.state_key,
            requested_scope=request.requested_scope,
            read_payload=request.read_payload,
            read_fingerprint=request.read_fingerprint,
            computed_read_fingerprint=request.computed_read_fingerprint,
            reader_id=request.reader_id,
            read_purpose=request.read_purpose,
            request_rationale=request.request_rationale,
            confidence=request.confidence,
            requester_id=request.requester_id,
            interpretation_purpose=interpretation_purpose,
            interpretation_rationale=interpretation_rationale,
            interpretation=interpretation,
            interpreter_id=interpreter_id,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "interpretation_id": interpretation_id,
                "request_id": request.request_id,
                "validation_id": request.lineage.get("validation_id"),
                "read_id": request.read_id,
                "consumption_request_id": request.consumption_request_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateInterpretationError",
    "LearningStateExecutionLearningStateInterpretationStatus",
    "LearningStateExecutionLearningStateInterpretation",
    "LearningStateExecutionLearningStateInterpretationService",
]
