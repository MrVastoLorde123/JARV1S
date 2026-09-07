"""M23.144: perform bounded semantic use of a requested learning-state artifact."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_semantic_use_request import (
    LearningStateExecutionLearningStateSemanticUseRequest,
    LearningStateExecutionLearningStateSemanticUseRequestStatus,
)


class LearningStateExecutionLearningStateSemanticUseError(RuntimeError):
    """Raised when semantic-use evidence cannot be formed safely."""


class LearningStateExecutionLearningStateSemanticUseStatus(str, Enum):
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


def _describe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {"kind": "mapping", "keys": tuple(sorted(str(key) for key in value)), "size": len(value)}
    if isinstance(value, (list, tuple)):
        return {"kind": "sequence", "size": len(value), "item_types": tuple(type(item).__name__ for item in value)}
    if isinstance(value, (set, frozenset)):
        return {"kind": "set", "size": len(value), "item_types": tuple(sorted(type(item).__name__ for item in value))}
    if value is None:
        return {"kind": "none"}
    return {"kind": type(value).__name__}


@dataclass(frozen=True)
class LearningStateExecutionLearningStateSemanticUse:
    """Immutable evidence that one requested semantic use was structurally performed."""

    semantic_use_id: str
    source_request_id: str
    integrity_id: str
    validation_id: str
    interpretation_id: str
    source_request_lineage_id: str
    source_validation_id: str
    read_id: str
    consumption_request_id: str
    requester_id: str
    consumer_id: str
    use_purpose: str
    use_rationale: Any
    requested_use: Any
    semantic_input: Any
    semantic_output: Any
    status: LearningStateExecutionLearningStateSemanticUseStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "semantic_use_id", "source_request_id", "integrity_id", "validation_id", "interpretation_id",
            "source_request_lineage_id", "source_validation_id", "read_id", "consumption_request_id",
            "requester_id", "consumer_id", "use_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, LearningStateExecutionLearningStateSemanticUseStatus):
            raise TypeError("status must be a semantic-use status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "use_rationale", _freeze(self.use_rationale))
        object.__setattr__(self, "requested_use", _freeze(self.requested_use))
        object.__setattr__(self, "semantic_input", _freeze(self.semantic_input))
        object.__setattr__(self, "semantic_output", _freeze(self.semantic_output))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_used(self) -> bool:
        return self.status is LearningStateExecutionLearningStateSemanticUseStatus.USED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateSemanticUseStatus.REJECTED

    @property
    def performs_semantic_use(self) -> bool:
        return self.is_used

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


class LearningStateExecutionLearningStateSemanticUseService:
    """Perform only the bounded semantic transformation explicitly requested by M23.143."""

    def use(
        self,
        request: LearningStateExecutionLearningStateSemanticUseRequest,
        *,
        semantic_use_id: str,
        consumer_id: str,
        use_purpose: str,
        use_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateSemanticUse:
        if type(request) is not LearningStateExecutionLearningStateSemanticUseRequest:
            raise TypeError("request must be a semantic-use request artifact")
        for name, value in (("semantic_use_id", semantic_use_id), ("consumer_id", consumer_id), ("use_purpose", use_purpose)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if use_rationale is None:
            raise ValueError("use_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if request.status is not LearningStateExecutionLearningStateSemanticUseRequestStatus.REQUESTED:
            checks.append("semantic-use request is not REQUESTED")
        if semantic_use_id == request.request_id:
            checks.append("semantic-use identity must be distinct from request")
        lineage_request_id = request.lineage.get("request_id", request.request_id)
        lineage_integrity_id = request.lineage.get("integrity_id", request.integrity_id)
        lineage_validation_id = request.lineage.get("validation_id", request.validation_id)
        lineage_interpretation_id = request.lineage.get("interpretation_id", request.interpretation_id)
        lineage_source_request_id = request.lineage.get("source_request_id", request.source_request_id)
        lineage_source_validation_id = request.lineage.get("source_validation_id", request.source_validation_id)
        lineage_read_id = request.lineage.get("read_id", request.read_id)
        lineage_consumption_request_id = request.lineage.get("consumption_request_id", request.consumption_request_id)
        if lineage_request_id != request.request_id:
            checks.append("request lineage mismatch")
        if lineage_integrity_id != request.integrity_id:
            checks.append("integrity lineage mismatch")
        if lineage_validation_id != request.validation_id:
            checks.append("validation lineage mismatch")
        if lineage_interpretation_id != request.interpretation_id:
            checks.append("interpretation lineage mismatch")
        if lineage_source_request_id != request.source_request_id:
            checks.append("source request lineage mismatch")
        if lineage_source_validation_id != request.source_validation_id:
            checks.append("source validation lineage mismatch")
        if lineage_read_id != request.read_id:
            checks.append("read lineage mismatch")
        if lineage_consumption_request_id != request.consumption_request_id:
            checks.append("consumption request lineage mismatch")

        valid = not checks
        if valid:
            semantic_input = {
                "interpretation_id": request.interpretation_id,
                "requested_use": request.requested_use,
                "request_purpose": request.request_purpose,
            }
            semantic_output = {
                "use": _describe(request.requested_use),
                "interpretation_id": request.interpretation_id,
                "purpose": use_purpose,
            }
            final_reasons = reasons if reasons is not None else ("semantic use performed within the bounded request contract",)
        else:
            semantic_input = {"rejected_request": True}
            semantic_output = {"use": "none"}
            final_reasons = reasons if reasons is not None else tuple(checks)

        status = LearningStateExecutionLearningStateSemanticUseStatus.USED if valid else LearningStateExecutionLearningStateSemanticUseStatus.REJECTED
        return LearningStateExecutionLearningStateSemanticUse(
            semantic_use_id=semantic_use_id,
            source_request_id=request.source_request_id,
            integrity_id=request.integrity_id,
            validation_id=request.validation_id,
            interpretation_id=request.interpretation_id,
            source_request_lineage_id=request.request_id,
            source_validation_id=request.source_validation_id,
            read_id=request.read_id,
            consumption_request_id=request.consumption_request_id,
            requester_id=request.requester_id,
            consumer_id=consumer_id,
            use_purpose=use_purpose,
            use_rationale=use_rationale,
            requested_use=request.requested_use,
            semantic_input=semantic_input,
            semantic_output=semantic_output,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "semantic_use_id": semantic_use_id,
                "request_id": request.request_id,
                "integrity_id": request.integrity_id,
                "validation_id": request.validation_id,
                "interpretation_id": request.interpretation_id,
                "source_request_id": request.source_request_id,
                "source_validation_id": request.source_validation_id,
                "read_id": request.read_id,
                "consumption_request_id": request.consumption_request_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateSemanticUseError",
    "LearningStateExecutionLearningStateSemanticUseStatus",
    "LearningStateExecutionLearningStateSemanticUse",
    "LearningStateExecutionLearningStateSemanticUseService",
]
