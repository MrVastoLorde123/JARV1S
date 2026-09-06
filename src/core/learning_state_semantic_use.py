"""M23.112: bounded semantic use of a ready learning-state semantic-use request."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping

from src.core.learning_state_semantic_use_request import LearningStateSemanticUseRequest, LearningStateSemanticUseRequestStatus


class LearningStateSemanticUseError(RuntimeError):
    """Raised when bounded semantic-use evidence cannot be formed safely."""


class LearningStateSemanticUseStatus(str, Enum):
    USED = "USED"
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
class LearningStateSemanticUse:
    """Immutable evidence produced by one bounded semantic-use invocation."""

    use_id: str
    request_id: str
    integrity_id: str
    validation_id: str
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
    request_status: LearningStateSemanticUseRequestStatus
    use_status: LearningStateSemanticUseStatus
    result: Mapping[str, Any] | None
    failure_reason: str | None
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "use_id", "request_id", "integrity_id", "validation_id", "interpretation_id", "source_request_id",
            "read_validation_id", "read_id", "consumption_request_id", "source_validation_id", "source_integrity_id",
            "transition_id", "evidence_id", "application_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint", "consumer_id", "use_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("semantic-use evidence requires SHA-256 fingerprints")
        if not isinstance(self.request_status, LearningStateSemanticUseRequestStatus):
            raise TypeError("request_status must be a semantic-use request status")
        if not isinstance(self.use_status, LearningStateSemanticUseStatus):
            raise TypeError("use_status must be a semantic-use status")
        if self.use_status is LearningStateSemanticUseStatus.USED:
            if self.request_status is not LearningStateSemanticUseRequestStatus.READY:
                raise ValueError("USED semantic-use evidence requires a READY request")
            if not isinstance(self.result, Mapping):
                raise TypeError("USED semantic-use evidence requires a mapping result")
            if self.failure_reason is not None:
                raise ValueError("USED semantic-use evidence cannot carry a failure reason")
        elif self.failure_reason is None or not self.failure_reason.strip():
            raise ValueError("REJECTED semantic-use evidence requires a failure reason")
        if self.result is not None:
            object.__setattr__(self, "result", _freeze(self.result))
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_used(self) -> bool:
        return self.use_status is LearningStateSemanticUseStatus.USED

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


class LearningStateSemanticUseService:
    """Invoke exactly one caller-supplied semantic consumer without granting authority."""

    def use(self, request: LearningStateSemanticUseRequest, *, use_id: str, consumer: Callable[[Mapping[str, Any]], object] | None,
            reasons: Mapping[str, Any] | None = None, lineage: Mapping[str, Any] | None = None) -> LearningStateSemanticUse:
        if type(request) is not LearningStateSemanticUseRequest:
            raise TypeError("request must be a learning-state semantic-use request artifact")
        if not isinstance(use_id, str) or not use_id.strip():
            raise ValueError("use_id must be a non-empty string")
        used = False
        result: Mapping[str, Any] | None = None
        failure: str | None = None
        if request.request_status is not LearningStateSemanticUseRequestStatus.READY:
            failure = "learning-state semantic use requires a READY semantic-use request"
        elif not callable(consumer):
            failure = "learning-state semantic use requires a callable consumer"
        else:
            try:
                candidate = consumer(request.interpretation)
                if isinstance(candidate, Mapping):
                    result = candidate
                    used = True
                else:
                    failure = "learning-state semantic-use consumer returned a non-mapping result"
            except Exception:
                failure = "learning-state semantic-use consumer raised an exception"
        status = LearningStateSemanticUseStatus.USED if used else LearningStateSemanticUseStatus.REJECTED
        return LearningStateSemanticUse(
            use_id=use_id, request_id=request.request_id, integrity_id=request.integrity_id,
            validation_id=request.validation_id, interpretation_id=request.interpretation_id,
            source_request_id=request.source_request_id, read_validation_id=request.read_validation_id,
            read_id=request.read_id, consumption_request_id=request.consumption_request_id,
            source_validation_id=request.source_validation_id, source_integrity_id=request.source_integrity_id,
            transition_id=request.transition_id, evidence_id=request.evidence_id, application_id=request.application_id,
            state_key=request.state_key, transition_fingerprint=request.transition_fingerprint,
            source_application_fingerprint=request.source_application_fingerprint,
            computed_application_fingerprint=request.computed_application_fingerprint, confidence=request.confidence,
            consumer_id=request.consumer_id, use_purpose=request.use_purpose, request_status=request.request_status,
            use_status=status, result=result, failure_reason=None if used else failure,
            reasons=reasons if reasons is not None else {"use_status": status.value},
            lineage=lineage if lineage is not None else {"use_id": use_id, "request_id": request.request_id},
        )


__all__ = ["LearningStateSemanticUseError", "LearningStateSemanticUseStatus", "LearningStateSemanticUse", "LearningStateSemanticUseService"]
