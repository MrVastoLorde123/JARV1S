"""M23.146: establish integrity evidence for semantic-use validation."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_semantic_use_validation import (
    LearningStateExecutionLearningStateSemanticUseValidation,
    LearningStateExecutionLearningStateSemanticUseValidationStatus,
)


class LearningStateExecutionLearningStateSemanticUseValidationIntegrityError(RuntimeError):
    """Raised when semantic-use validation-integrity evidence cannot be formed safely."""


class LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus(str, Enum):
    VALID = "VALID"
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


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_canonical(item) for item in value), key=repr)
    if isinstance(value, Enum):
        return value.value
    return value


def _validation_fingerprint(validation: LearningStateExecutionLearningStateSemanticUseValidation) -> str:
    payload = {
        "validation_id": validation.validation_id,
        "semantic_use_id": validation.semantic_use_id,
        "source_request_id": validation.source_request_id,
        "source_request_lineage_id": validation.source_request_lineage_id,
        "integrity_id": validation.integrity_id,
        "source_validation_id": validation.source_validation_id,
        "interpretation_id": validation.interpretation_id,
        "source_validation_lineage_id": validation.source_validation_lineage_id,
        "read_id": validation.read_id,
        "consumption_request_id": validation.consumption_request_id,
        "requester_id": validation.requester_id,
        "consumer_id": validation.consumer_id,
        "use_purpose": validation.use_purpose,
        "use_rationale": _canonical(validation.use_rationale),
        "requested_use": _canonical(validation.requested_use),
        "semantic_input": _canonical(validation.semantic_input),
        "semantic_output": _canonical(validation.semantic_output),
        "source_status": _canonical(validation.source_status),
        "status": _canonical(validation.status),
        "reasons": _canonical(validation.reasons),
        "lineage": _canonical(validation.lineage),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class LearningStateExecutionLearningStateSemanticUseValidationIntegrity:
    """Immutable integrity evidence for one semantic-use validation artifact."""

    integrity_id: str
    validation_id: str
    semantic_use_id: str
    source_request_id: str
    source_request_lineage_id: str
    source_validation_id: str
    interpretation_id: str
    source_validation_lineage_id: str
    read_id: str
    consumption_request_id: str
    requester_id: str
    consumer_id: str
    use_purpose: str
    validation_status: LearningStateExecutionLearningStateSemanticUseValidationStatus
    validation_fingerprint: str
    computed_validation_fingerprint: str
    status: LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "integrity_id", "validation_id", "semantic_use_id", "source_request_id", "source_request_lineage_id",
            "source_validation_id", "interpretation_id", "source_validation_lineage_id", "read_id",
            "consumption_request_id", "requester_id", "consumer_id", "use_purpose",
            "validation_fingerprint", "computed_validation_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.validation_status, LearningStateExecutionLearningStateSemanticUseValidationStatus):
            raise TypeError("validation_status must be a semantic-use validation status")
        if not isinstance(self.status, LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus):
            raise TypeError("status must be a semantic-use validation integrity status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.status is LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus.VALID:
            if len(self.validation_fingerprint) != 64 or len(self.computed_validation_fingerprint) != 64:
                raise ValueError("validation integrity requires SHA-256 fingerprints")
            if self.validation_fingerprint != self.computed_validation_fingerprint:
                raise ValueError("validation fingerprints must agree for VALID integrity")
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_valid(self) -> bool:
        return self.status is LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus.VALID

    @property
    def is_invalid(self) -> bool:
        return self.status is LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus.INVALID

    @property
    def validates_validation_integrity(self) -> bool:
        return self.is_valid

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


class LearningStateExecutionLearningStateSemanticUseValidationIntegrityService:
    """Form integrity evidence without re-validating, repairing, or executing semantic use."""

    def validate(
        self,
        validation: LearningStateExecutionLearningStateSemanticUseValidation,
        *,
        integrity_id: str,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateSemanticUseValidationIntegrity:
        if type(validation) is not LearningStateExecutionLearningStateSemanticUseValidation:
            raise TypeError("validation must be a semantic-use validation artifact")
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if validation.status is not LearningStateExecutionLearningStateSemanticUseValidationStatus.VALIDATED:
            checks.append("semantic-use validation status must be VALIDATED")
        if integrity_id == validation.validation_id:
            checks.append("integrity identity must be distinct")

        lineage_validation_id = validation.lineage.get("validation_id", validation.validation_id)
        lineage_semantic_use_id = validation.lineage.get("semantic_use_id", validation.semantic_use_id)
        lineage_request_id = validation.lineage.get("request_id", validation.source_request_lineage_id)
        lineage_integrity_id = validation.lineage.get("integrity_id", validation.integrity_id)
        lineage_source_validation_id = validation.lineage.get("source_validation_id", validation.source_validation_lineage_id)
        lineage_interpretation_id = validation.lineage.get("interpretation_id", validation.interpretation_id)
        lineage_source_request_id = validation.lineage.get("source_request_id", validation.source_request_id)
        lineage_source_validation_provenance_id = validation.lineage.get("source_validation_provenance_id", validation.source_validation_id)
        lineage_read_id = validation.lineage.get("read_id", validation.read_id)
        lineage_consumption_request_id = validation.lineage.get("consumption_request_id", validation.consumption_request_id)
        if lineage_validation_id != validation.validation_id:
            checks.append("validation lineage mismatch")
        if lineage_semantic_use_id != validation.semantic_use_id:
            checks.append("semantic-use lineage mismatch")
        if lineage_request_id != validation.source_request_lineage_id:
            checks.append("source request lineage mismatch")
        if lineage_integrity_id != validation.integrity_id:
            checks.append("upstream integrity lineage mismatch")
        if lineage_source_validation_id != validation.source_validation_lineage_id:
            checks.append("source validation lineage mismatch")
        if lineage_interpretation_id != validation.interpretation_id:
            checks.append("interpretation lineage mismatch")
        if lineage_source_request_id != validation.source_request_id:
            checks.append("source request provenance mismatch")
        if lineage_source_validation_provenance_id != validation.source_validation_id:
            checks.append("source validation provenance mismatch")
        if lineage_read_id != validation.read_id:
            checks.append("read lineage mismatch")
        if lineage_consumption_request_id != validation.consumption_request_id:
            checks.append("consumption request lineage mismatch")

        fingerprint = _validation_fingerprint(validation)
        valid = not checks
        final_reasons = reasons if reasons is not None else (("validation structure, lineage, and deterministic integrity checks passed",) if valid else tuple(checks))
        status = LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus.VALID if valid else LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus.INVALID
        return LearningStateExecutionLearningStateSemanticUseValidationIntegrity(
            integrity_id=integrity_id,
            validation_id=validation.validation_id,
            semantic_use_id=validation.semantic_use_id,
            source_request_id=validation.source_request_id,
            source_request_lineage_id=validation.source_request_lineage_id,
            source_validation_id=validation.source_validation_id,
            interpretation_id=validation.interpretation_id,
            source_validation_lineage_id=validation.source_validation_lineage_id,
            read_id=validation.read_id,
            consumption_request_id=validation.consumption_request_id,
            requester_id=validation.requester_id,
            consumer_id=validation.consumer_id,
            use_purpose=validation.use_purpose,
            validation_status=validation.status,
            validation_fingerprint=fingerprint,
            computed_validation_fingerprint=fingerprint,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "integrity_id": integrity_id,
                "validation_id": validation.validation_id,
                "semantic_use_id": validation.semantic_use_id,
                "request_id": validation.source_request_lineage_id,
                "upstream_integrity_id": validation.integrity_id,
                "source_validation_id": validation.source_validation_lineage_id,
                "interpretation_id": validation.interpretation_id,
                "source_request_id": validation.source_request_id,
                "source_validation_provenance_id": validation.source_validation_id,
                "read_id": validation.read_id,
                "consumption_request_id": validation.consumption_request_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateSemanticUseValidationIntegrityError",
    "LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus",
    "LearningStateExecutionLearningStateSemanticUseValidationIntegrity",
    "LearningStateExecutionLearningStateSemanticUseValidationIntegrityService",
]
