"""M23.143: request semantic use of validated learning-state evidence without granting authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_interpretation_validation_integrity import (
    LearningStateExecutionLearningStateInterpretationValidationIntegrity,
    LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus,
)


class LearningStateExecutionLearningStateSemanticUseRequestError(RuntimeError):
    """Raised when a semantic-use request cannot be formed safely."""


class LearningStateExecutionLearningStateSemanticUseRequestStatus(str, Enum):
    REQUESTED = "REQUESTED"
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
class LearningStateExecutionLearningStateSemanticUseRequest:
    """Immutable evidence that semantic use was explicitly requested for valid integrity evidence."""

    request_id: str
    integrity_id: str
    validation_id: str
    interpretation_id: str
    source_request_id: str
    source_validation_id: str
    read_id: str
    consumption_request_id: str
    semantic_use_id: str
    requester_id: str
    request_purpose: str
    request_rationale: Any
    requested_use: Any
    status: LearningStateExecutionLearningStateSemanticUseRequestStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "request_id", "integrity_id", "validation_id", "interpretation_id", "source_request_id",
            "source_validation_id", "read_id", "consumption_request_id", "semantic_use_id",
            "requester_id", "request_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, LearningStateExecutionLearningStateSemanticUseRequestStatus):
            raise TypeError("status must be a semantic-use request status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "request_rationale", _freeze(self.request_rationale))
        object.__setattr__(self, "requested_use", _freeze(self.requested_use))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_requested(self) -> bool:
        return self.status is LearningStateExecutionLearningStateSemanticUseRequestStatus.REQUESTED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateSemanticUseRequestStatus.REJECTED

    @property
    def admits_semantic_use(self) -> bool:
        return self.is_requested

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
    def performs_semantic_use(self) -> bool:
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


class LearningStateExecutionLearningStateSemanticUseRequestService:
    """Create semantic-use request evidence without performing semantic use or granting authority."""

    def request(
        self,
        integrity: LearningStateExecutionLearningStateInterpretationValidationIntegrity,
        *,
        request_id: str,
        semantic_use_id: str,
        requester_id: str,
        request_purpose: str,
        request_rationale: Any,
        requested_use: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateSemanticUseRequest:
        if type(integrity) is not LearningStateExecutionLearningStateInterpretationValidationIntegrity:
            raise TypeError("integrity must be an interpretation-validation integrity artifact")
        for name, value in (
            ("request_id", request_id), ("semantic_use_id", semantic_use_id), ("requester_id", requester_id),
            ("request_purpose", request_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if request_rationale is None:
            raise ValueError("request_rationale must be provided")
        if requested_use is None:
            raise ValueError("requested_use must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if integrity.status is not LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus.VALID:
            checks.append("interpretation-validation integrity is not VALID")
        if request_id == semantic_use_id:
            checks.append("request identity must be distinct from semantic-use identity")
        lineage_integrity_id = integrity.lineage.get("integrity_id", integrity.integrity_id)
        lineage_validation_id = integrity.lineage.get("validation_id", integrity.validation_id)
        lineage_interpretation_id = integrity.lineage.get("interpretation_id", integrity.interpretation_id)
        lineage_request_id = integrity.lineage.get("request_id", integrity.source_request_id)
        lineage_source_validation_id = integrity.lineage.get("source_validation_id", integrity.source_validation_id)
        lineage_read_id = integrity.lineage.get("read_id", integrity.read_id)
        lineage_consumption_request_id = integrity.lineage.get("consumption_request_id", integrity.consumption_request_id)
        if lineage_integrity_id != integrity.integrity_id:
            checks.append("integrity lineage mismatch")
        if lineage_validation_id != integrity.validation_id:
            checks.append("validation lineage mismatch")
        if lineage_interpretation_id != integrity.interpretation_id:
            checks.append("interpretation lineage mismatch")
        if lineage_request_id != integrity.source_request_id:
            checks.append("request lineage mismatch")
        if lineage_source_validation_id != integrity.source_validation_id:
            checks.append("source validation lineage mismatch")
        if lineage_read_id != integrity.read_id:
            checks.append("read lineage mismatch")
        if lineage_consumption_request_id != integrity.consumption_request_id:
            checks.append("consumption request lineage mismatch")
        valid = not checks
        if reasons is not None:
            final_reasons = reasons
        elif valid:
            final_reasons = ("semantic-use request accepted for downstream handling",)
        else:
            final_reasons = tuple(checks)
        status = LearningStateExecutionLearningStateSemanticUseRequestStatus.REQUESTED if valid else LearningStateExecutionLearningStateSemanticUseRequestStatus.REJECTED
        return LearningStateExecutionLearningStateSemanticUseRequest(
            request_id=request_id,
            integrity_id=integrity.integrity_id,
            validation_id=integrity.validation_id,
            interpretation_id=integrity.interpretation_id,
            source_request_id=integrity.source_request_id,
            source_validation_id=integrity.source_validation_id,
            read_id=integrity.read_id,
            consumption_request_id=integrity.consumption_request_id,
            semantic_use_id=semantic_use_id,
            requester_id=requester_id,
            request_purpose=request_purpose,
            request_rationale=request_rationale,
            requested_use=requested_use,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "request_id": request_id,
                "integrity_id": integrity.integrity_id,
                "validation_id": integrity.validation_id,
                "interpretation_id": integrity.interpretation_id,
                "source_request_id": integrity.source_request_id,
                "source_validation_id": integrity.source_validation_id,
                "read_id": integrity.read_id,
                "consumption_request_id": integrity.consumption_request_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateSemanticUseRequestError",
    "LearningStateExecutionLearningStateSemanticUseRequestStatus",
    "LearningStateExecutionLearningStateSemanticUseRequest",
    "LearningStateExecutionLearningStateSemanticUseRequestService",
]
