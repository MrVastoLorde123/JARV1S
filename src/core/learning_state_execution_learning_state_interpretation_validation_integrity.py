"""M23.142: establish integrity for learning-state interpretation validation evidence."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_interpretation_validation import (
    LearningStateExecutionLearningStateInterpretationValidation,
    LearningStateExecutionLearningStateInterpretationValidationStatus,
)


class LearningStateExecutionLearningStateInterpretationValidationIntegrityError(RuntimeError):
    """Raised when interpretation-validation integrity evidence cannot be formed safely."""


class LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus(str, Enum):
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


def _expected_integrity_fingerprint(validation: LearningStateExecutionLearningStateInterpretationValidation) -> str:
    payload = {
        "validation_id": validation.validation_id,
        "interpretation_id": validation.interpretation_id,
        "source_request_id": validation.source_request_id,
        "source_validation_id": validation.source_validation_id,
        "read_id": validation.read_id,
        "consumption_request_id": validation.consumption_request_id,
        "integrity_id": validation.integrity_id,
        "transition_id": validation.transition_id,
        "evidence_id": validation.evidence_id,
        "state_key": validation.state_key,
        "requested_scope": _canonical(validation.requested_scope),
        "read_payload": _canonical(validation.read_payload),
        "read_fingerprint": validation.read_fingerprint,
        "computed_read_fingerprint": validation.computed_read_fingerprint,
        "interpretation_purpose": validation.interpretation_purpose,
        "interpretation_rationale": _canonical(validation.interpretation_rationale),
        "interpretation": _canonical(validation.interpretation),
        "interpreter_id": validation.interpreter_id,
        "validation_actor_id": validation.validation_actor_id,
        "validation_purpose": validation.validation_purpose,
        "validation_rationale": _canonical(validation.validation_rationale),
        "status": validation.status.value,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class LearningStateExecutionLearningStateInterpretationValidationIntegrity:
    """Immutable integrity evidence for one interpretation-validation artifact."""

    integrity_id: str
    validation_id: str
    interpretation_id: str
    source_request_id: str
    source_validation_id: str
    read_id: str
    consumption_request_id: str
    interpretation: Any
    read_payload: Any
    read_fingerprint: str
    computed_read_fingerprint: str
    validation_actor_id: str
    validation_purpose: str
    status: LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus
    integrity_fingerprint: str
    computed_integrity_fingerprint: str
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "integrity_id", "validation_id", "interpretation_id", "source_request_id", "source_validation_id",
            "read_id", "consumption_request_id", "read_fingerprint", "computed_read_fingerprint",
            "validation_actor_id", "validation_purpose", "integrity_fingerprint", "computed_integrity_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus):
            raise TypeError("status must be an interpretation-validation integrity status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "interpretation", _freeze(self.interpretation))
        object.__setattr__(self, "read_payload", _freeze(self.read_payload))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_valid(self) -> bool:
        return self.status is LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus.VALID

    @property
    def validates_integrity(self) -> bool:
        return self.is_valid

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


class LearningStateExecutionLearningStateInterpretationValidationIntegrityService:
    """Check interpretation-validation identity, lineage, payload and fingerprint without repair."""

    def validate(
        self,
        validation: LearningStateExecutionLearningStateInterpretationValidation,
        *,
        integrity_id: str,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateInterpretationValidationIntegrity:
        if type(validation) is not LearningStateExecutionLearningStateInterpretationValidation:
            raise TypeError("validation must be an interpretation-validation artifact")
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if validation.status is not LearningStateExecutionLearningStateInterpretationValidationStatus.VALIDATED:
            checks.append("interpretation validation is not VALIDATED")
        if integrity_id == validation.validation_id:
            checks.append("integrity identity must be distinct from validation identity")
        lineage_integrity_id = validation.lineage.get("validation_id", validation.validation_id)
        lineage_interpretation_id = validation.lineage.get("interpretation_id", validation.interpretation_id)
        lineage_request_id = validation.lineage.get("request_id", validation.source_request_id)
        lineage_source_validation_id = validation.lineage.get("source_validation_id", validation.source_validation_id)
        lineage_read_id = validation.lineage.get("read_id", validation.read_id)
        lineage_consumption_request_id = validation.lineage.get("consumption_request_id", validation.consumption_request_id)
        if lineage_integrity_id != validation.validation_id:
            checks.append("validation lineage mismatch")
        if lineage_interpretation_id != validation.interpretation_id:
            checks.append("interpretation lineage mismatch")
        if lineage_request_id != validation.source_request_id:
            checks.append("request lineage mismatch")
        if lineage_source_validation_id != validation.source_validation_id:
            checks.append("source validation lineage mismatch")
        if lineage_read_id != validation.read_id:
            checks.append("read lineage mismatch")
        if lineage_consumption_request_id != validation.consumption_request_id:
            checks.append("consumption request lineage mismatch")
        if validation.validation_id == validation.interpretation_id:
            checks.append("validation identity must be distinct from interpretation identity")
        if len(validation.read_fingerprint) != 64 or any(char not in "0123456789abcdef" for char in validation.read_fingerprint):
            checks.append("read fingerprint is not SHA-256")
        if validation.read_fingerprint != validation.computed_read_fingerprint:
            checks.append("read fingerprint mismatch")
        computed = _expected_integrity_fingerprint(validation)
        valid = not checks
        if reasons is not None:
            final_reasons = reasons
        elif valid:
            final_reasons = ("interpretation validation integrity checks passed",)
        else:
            final_reasons = tuple(checks)
        status = LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus.VALID if valid else LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus.INVALID
        return LearningStateExecutionLearningStateInterpretationValidationIntegrity(
            integrity_id=integrity_id,
            validation_id=validation.validation_id,
            interpretation_id=validation.interpretation_id,
            source_request_id=validation.source_request_id,
            source_validation_id=validation.source_validation_id,
            read_id=validation.read_id,
            consumption_request_id=validation.consumption_request_id,
            interpretation=validation.interpretation,
            read_payload=validation.read_payload,
            read_fingerprint=validation.read_fingerprint,
            computed_read_fingerprint=validation.computed_read_fingerprint,
            validation_actor_id=validation.validation_actor_id,
            validation_purpose=validation.validation_purpose,
            status=status,
            integrity_fingerprint=computed,
            computed_integrity_fingerprint=computed,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "integrity_id": integrity_id,
                "validation_id": validation.validation_id,
                "interpretation_id": validation.interpretation_id,
                "request_id": validation.source_request_id,
                "source_validation_id": validation.source_validation_id,
                "read_id": validation.read_id,
                "consumption_request_id": validation.consumption_request_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateInterpretationValidationIntegrityError",
    "LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus",
    "LearningStateExecutionLearningStateInterpretationValidationIntegrity",
    "LearningStateExecutionLearningStateInterpretationValidationIntegrityService",
]
