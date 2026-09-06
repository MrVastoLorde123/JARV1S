"""M23.108: bounded semantic interpretation of learning-state requests."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping

from src.core.learning_state_interpretation_request import (
    LearningStateInterpretationRequest,
    LearningStateInterpretationRequestStatus,
)


class LearningStateInterpretationError(RuntimeError):
    """Raised when a learning-state interpretation boundary cannot be formed safely."""


class LearningStateInterpretationStatus(str, Enum):
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


@dataclass(frozen=True)
class LearningStateInterpretation:
    """Immutable semantic result produced by one bounded interpreter invocation."""

    interpretation_id: str
    request_id: str
    read_validation_id: str
    read_id: str
    consumption_request_id: str
    source_validation_id: str
    integrity_id: str
    transition_id: str
    evidence_id: str
    application_id: str
    state_key: str
    transition_fingerprint: str
    source_application_fingerprint: str
    computed_application_fingerprint: str
    confidence: float
    interpretation_status: LearningStateInterpretationStatus
    interpretation: Mapping[str, Any] | None
    failure_reason: str | None
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "interpretation_id", "request_id", "read_validation_id", "read_id",
            "consumption_request_id", "source_validation_id", "integrity_id",
            "transition_id", "evidence_id", "application_id", "state_key",
            "transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("learning-state interpretation requires SHA-256 fingerprints")
        if not isinstance(self.interpretation_status, LearningStateInterpretationStatus):
            raise TypeError("interpretation_status must be a learning-state interpretation status")
        if self.interpretation_status is LearningStateInterpretationStatus.INTERPRETED:
            if not isinstance(self.interpretation, Mapping):
                raise TypeError("INTERPRETED result requires a mapping interpretation")
            if self.failure_reason is not None:
                raise ValueError("INTERPRETED result cannot carry a failure reason")
        elif self.failure_reason is None or not self.failure_reason.strip():
            raise ValueError("REJECTED interpretation requires a failure reason")
        if self.interpretation is not None:
            object.__setattr__(self, "interpretation", _freeze(self.interpretation))
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_interpreted(self) -> bool:
        return self.interpretation_status is LearningStateInterpretationStatus.INTERPRETED

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


class LearningStateInterpretationService:
    """Apply exactly one caller-supplied interpreter to a ready interpretation request."""

    def interpret(
        self,
        request: LearningStateInterpretationRequest,
        *,
        interpretation_id: str,
        interpreter: Callable[[Mapping[str, Any]], object] | None,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateInterpretation:
        if type(request) is not LearningStateInterpretationRequest:
            raise TypeError("request must be a learning-state interpretation request artifact")
        if not isinstance(interpretation_id, str) or not interpretation_id.strip():
            raise ValueError("interpretation_id must be a non-empty string")

        interpreted = False
        result: Mapping[str, Any] | None = None
        failure: str | None = None
        if request.request_status is not LearningStateInterpretationRequestStatus.READY:
            failure = "learning-state interpretation requires a READY interpretation request"
        elif not callable(interpreter):
            failure = "learning-state interpretation requires a callable interpreter"
        else:
            try:
                candidate = interpreter(request.state)
                if isinstance(candidate, Mapping):
                    result = candidate
                    interpreted = True
                else:
                    failure = "learning-state interpreter returned a non-mapping result"
            except Exception:
                failure = "learning-state interpreter raised an exception"

        status = LearningStateInterpretationStatus.INTERPRETED if interpreted else LearningStateInterpretationStatus.REJECTED
        return LearningStateInterpretation(
            interpretation_id=interpretation_id,
            request_id=request.request_id,
            read_validation_id=request.read_validation_id,
            read_id=request.read_id,
            consumption_request_id=request.consumption_request_id,
            source_validation_id=request.source_validation_id,
            integrity_id=request.integrity_id,
            transition_id=request.transition_id,
            evidence_id=request.evidence_id,
            application_id=request.application_id,
            state_key=request.state_key,
            transition_fingerprint=request.transition_fingerprint,
            source_application_fingerprint=request.source_application_fingerprint,
            computed_application_fingerprint=request.computed_application_fingerprint,
            confidence=request.confidence,
            interpretation_status=status,
            interpretation=result,
            failure_reason=None if interpreted else failure,
            reasons=reasons if reasons is not None else {"interpretation_status": status.value},
            lineage=lineage if lineage is not None else {"interpretation_id": interpretation_id, "request_id": request.request_id},
        )


__all__ = [
    "LearningStateInterpretationError",
    "LearningStateInterpretationStatus",
    "LearningStateInterpretation",
    "LearningStateInterpretationService",
]
