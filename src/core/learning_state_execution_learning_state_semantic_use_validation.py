"""M23.145: validate bounded semantic-use evidence without granting authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_semantic_use import (
    LearningStateExecutionLearningStateSemanticUse,
    LearningStateExecutionLearningStateSemanticUseStatus,
)


class LearningStateExecutionLearningStateSemanticUseValidationError(RuntimeError):
    """Raised when semantic-use validation evidence cannot be formed safely."""


class LearningStateExecutionLearningStateSemanticUseValidationStatus(str, Enum):
    VALIDATED = "VALIDATED"
    INVALID = "INVALID"


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


def _structural_use_output(requested_use: Any, interpretation_id: str, purpose: str) -> Any:
    if isinstance(requested_use, Mapping):
        described = {"kind": "mapping", "keys": tuple(sorted(str(key) for key in requested_use)), "size": len(requested_use)}
    elif isinstance(requested_use, (list, tuple)):
        described = {"kind": "sequence", "size": len(requested_use), "item_types": tuple(type(item).__name__ for item in requested_use)}
    elif isinstance(requested_use, (set, frozenset)):
        described = {"kind": "set", "size": len(requested_use), "item_types": tuple(sorted(type(item).__name__ for item in requested_use))}
    elif requested_use is None:
        described = {"kind": "none"}
    else:
        described = {"kind": type(requested_use).__name__}
    return {"use": described, "interpretation_id": interpretation_id, "purpose": purpose}


@dataclass(frozen=True)
class LearningStateExecutionLearningStateSemanticUseValidation:
    """Immutable evidence that one semantic-use artifact satisfied this validation contract."""

    validation_id: str
    semantic_use_id: str
    source_request_id: str
    source_request_lineage_id: str
    integrity_id: str
    source_validation_id: str
    interpretation_id: str
    source_validation_lineage_id: str
    read_id: str
    consumption_request_id: str
    requester_id: str
    consumer_id: str
    use_purpose: str
    use_rationale: Any
    requested_use: Any
    semantic_input: Any
    semantic_output: Any
    source_status: LearningStateExecutionLearningStateSemanticUseStatus
    status: LearningStateExecutionLearningStateSemanticUseValidationStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "validation_id", "semantic_use_id", "source_request_id", "source_request_lineage_id",
            "integrity_id", "source_validation_id", "interpretation_id", "source_validation_lineage_id",
            "read_id", "consumption_request_id", "requester_id", "consumer_id", "use_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.source_status, LearningStateExecutionLearningStateSemanticUseStatus):
            raise TypeError("source_status must be a semantic-use status")
        if not isinstance(self.status, LearningStateExecutionLearningStateSemanticUseValidationStatus):
            raise TypeError("status must be a semantic-use validation status")
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
    def is_validated(self) -> bool:
        return self.status is LearningStateExecutionLearningStateSemanticUseValidationStatus.VALIDATED

    @property
    def is_invalid(self) -> bool:
        return self.status is LearningStateExecutionLearningStateSemanticUseValidationStatus.INVALID

    @property
    def validates_semantic_use(self) -> bool:
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


class LearningStateExecutionLearningStateSemanticUseValidationService:
    """Validate only the bounded structural contract of M23.144 semantic-use evidence."""

    def validate(
        self,
        semantic_use: LearningStateExecutionLearningStateSemanticUse,
        *,
        validation_id: str,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateSemanticUseValidation:
        if type(semantic_use) is not LearningStateExecutionLearningStateSemanticUse:
            raise TypeError("semantic_use must be a semantic-use artifact")
        if not isinstance(validation_id, str) or not validation_id.strip():
            raise ValueError("validation_id must be a non-empty string")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if semantic_use.status is not LearningStateExecutionLearningStateSemanticUseStatus.USED:
            checks.append("semantic-use status must be USED")
        if validation_id == semantic_use.semantic_use_id:
            checks.append("validation identity must be distinct")
        lineage_semantic_use_id = semantic_use.lineage.get("semantic_use_id", semantic_use.semantic_use_id)
        lineage_request_id = semantic_use.lineage.get("request_id", semantic_use.source_request_lineage_id)
        lineage_integrity_id = semantic_use.lineage.get("integrity_id", semantic_use.integrity_id)
        lineage_validation_id = semantic_use.lineage.get("validation_id", semantic_use.validation_id)
        lineage_interpretation_id = semantic_use.lineage.get("interpretation_id", semantic_use.interpretation_id)
        lineage_source_request_id = semantic_use.lineage.get("source_request_id", semantic_use.source_request_id)
        lineage_source_validation_id = semantic_use.lineage.get("source_validation_id", semantic_use.source_validation_id)
        lineage_read_id = semantic_use.lineage.get("read_id", semantic_use.read_id)
        lineage_consumption_request_id = semantic_use.lineage.get("consumption_request_id", semantic_use.consumption_request_id)
        if lineage_semantic_use_id != semantic_use.semantic_use_id:
            checks.append("semantic-use lineage mismatch")
        if lineage_request_id != semantic_use.source_request_lineage_id:
            checks.append("source request lineage mismatch")
        if lineage_integrity_id != semantic_use.integrity_id:
            checks.append("integrity lineage mismatch")
        if lineage_validation_id != semantic_use.validation_id:
            checks.append("source validation lineage mismatch")
        if lineage_interpretation_id != semantic_use.interpretation_id:
            checks.append("interpretation lineage mismatch")
        if lineage_source_request_id != semantic_use.source_request_id:
            checks.append("source request provenance mismatch")
        if lineage_source_validation_id != semantic_use.source_validation_id:
            checks.append("source validation provenance mismatch")
        if lineage_read_id != semantic_use.read_id:
            checks.append("read lineage mismatch")
        if lineage_consumption_request_id != semantic_use.consumption_request_id:
            checks.append("consumption request lineage mismatch")

        actual_input = dict(semantic_use.semantic_input)
        if actual_input.get("interpretation_id") != semantic_use.interpretation_id:
            checks.append("semantic input interpretation mismatch")
        if actual_input.get("requested_use") != semantic_use.requested_use:
            checks.append("semantic input requested-use mismatch")

        expected_output = _structural_use_output(semantic_use.requested_use, semantic_use.interpretation_id, semantic_use.use_purpose)
        actual_output = dict(semantic_use.semantic_output)
        if actual_output != expected_output:
            checks.append("semantic output structural mismatch")

        valid = not checks
        status = LearningStateExecutionLearningStateSemanticUseValidationStatus.VALIDATED if valid else LearningStateExecutionLearningStateSemanticUseValidationStatus.INVALID
        final_reasons = reasons if reasons is not None else (("semantic-use evidence satisfies the bounded validation contract",) if valid else tuple(checks))
        return LearningStateExecutionLearningStateSemanticUseValidation(
            validation_id=validation_id,
            semantic_use_id=semantic_use.semantic_use_id,
            source_request_id=semantic_use.source_request_id,
            source_request_lineage_id=semantic_use.source_request_lineage_id,
            integrity_id=semantic_use.integrity_id,
            source_validation_id=semantic_use.source_validation_id,
            interpretation_id=semantic_use.interpretation_id,
            source_validation_lineage_id=semantic_use.validation_id,
            read_id=semantic_use.read_id,
            consumption_request_id=semantic_use.consumption_request_id,
            requester_id=semantic_use.requester_id,
            consumer_id=semantic_use.consumer_id,
            use_purpose=semantic_use.use_purpose,
            use_rationale=semantic_use.use_rationale,
            requested_use=semantic_use.requested_use,
            semantic_input=semantic_use.semantic_input,
            semantic_output=semantic_use.semantic_output,
            source_status=semantic_use.status,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "validation_id": validation_id,
                "semantic_use_id": semantic_use.semantic_use_id,
                "request_id": semantic_use.source_request_lineage_id,
                "integrity_id": semantic_use.integrity_id,
                "source_validation_id": semantic_use.validation_id,
                "interpretation_id": semantic_use.interpretation_id,
                "source_request_id": semantic_use.source_request_id,
                "source_validation_provenance_id": semantic_use.source_validation_id,
                "read_id": semantic_use.read_id,
                "consumption_request_id": semantic_use.consumption_request_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateSemanticUseValidationError",
    "LearningStateExecutionLearningStateSemanticUseValidationStatus",
    "LearningStateExecutionLearningStateSemanticUseValidation",
    "LearningStateExecutionLearningStateSemanticUseValidationService",
]
