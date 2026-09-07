"""M23.138: validate durable-state read evidence without rereading or interpreting it."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_durable_read_consumption import (
    LearningStateExecutionLearningStateDurableReadConsumption,
    LearningStateExecutionLearningStateDurableReadConsumptionStatus,
)


class LearningStateExecutionLearningStateConsumptionReadValidationError(RuntimeError):
    """Raised when consumption-read validation cannot be formed safely."""


class LearningStateExecutionLearningStateConsumptionReadValidationStatus(str, Enum):
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


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_canonical(item) for item in value), key=repr)
    return value


def _fingerprint(value: Any) -> str:
    encoded = json.dumps(_canonical(value), sort_keys=True, separators=(",", ":"), default=repr).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class LearningStateExecutionLearningStateConsumptionReadValidation:
    """Immutable evidence that a durable-state read artifact passed bounded validation."""

    validation_id: str
    read_id: str
    consumption_request_id: str
    source_validation_id: str
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
    validator_id: str
    validation_purpose: str
    validation_rationale: Any
    status: LearningStateExecutionLearningStateConsumptionReadValidationStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "validation_id", "read_id", "consumption_request_id", "source_validation_id", "integrity_id",
            "transition_id", "evidence_id", "state_key", "read_fingerprint", "computed_read_fingerprint",
            "reader_id", "read_purpose", "validator_id", "validation_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if not isinstance(self.status, LearningStateExecutionLearningStateConsumptionReadValidationStatus):
            raise TypeError("status must be a consumption-read validation status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "requested_scope", _freeze(self.requested_scope))
        object.__setattr__(self, "read_payload", _freeze(self.read_payload))
        object.__setattr__(self, "request_rationale", _freeze(self.request_rationale))
        object.__setattr__(self, "validation_rationale", _freeze(self.validation_rationale))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_validated(self) -> bool:
        return self.status is LearningStateExecutionLearningStateConsumptionReadValidationStatus.VALIDATED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateConsumptionReadValidationStatus.REJECTED

    @property
    def admits_interpretation_request(self) -> bool:
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


class LearningStateExecutionLearningStateConsumptionReadValidationService:
    """Validate M23.137 read evidence without rereading durable state or repairing it."""

    def validate(
        self,
        read: LearningStateExecutionLearningStateDurableReadConsumption,
        *,
        validation_id: str,
        validator_id: str,
        validation_purpose: str,
        validation_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateConsumptionReadValidation:
        if type(read) is not LearningStateExecutionLearningStateDurableReadConsumption:
            raise TypeError("read must be a durable-read consumption artifact")
        for name, value in (("validation_id", validation_id), ("validator_id", validator_id), ("validation_purpose", validation_purpose)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if validation_rationale is None:
            raise ValueError("validation_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if read.status is not LearningStateExecutionLearningStateDurableReadConsumptionStatus.READ:
            checks.append("durable-state read is not READ")
        if validation_id == read.read_id:
            checks.append("validation identity must be distinct from read identity")
        lineage_read_id = read.lineage.get("read_id", read.read_id)
        lineage_request_id = read.lineage.get("consumption_request_id", read.consumption_request_id)
        lineage_validation_id = read.lineage.get("validation_id", read.validation_id)
        if lineage_read_id != read.read_id:
            checks.append("read lineage mismatch")
        if lineage_request_id != read.consumption_request_id:
            checks.append("consumption request lineage mismatch")
        if lineage_validation_id != read.validation_id:
            checks.append("source validation lineage mismatch")
        if read.read_payload is None:
            checks.append("READ evidence requires non-empty payload evidence")
        computed = _fingerprint(read.read_payload)
        if read.read_fingerprint != computed:
            checks.append("read fingerprint mismatch")
        if read.computed_read_fingerprint != computed:
            checks.append("computed read fingerprint mismatch")
        if len(read.read_fingerprint) != 64:
            checks.append("read fingerprint is not SHA-256")
        if len(read.computed_read_fingerprint) != 64:
            checks.append("computed read fingerprint is not SHA-256")

        valid = not checks
        if reasons is not None:
            final_reasons = reasons
        elif valid:
            final_reasons = ("durable-state read evidence passed validation",)
        else:
            final_reasons = tuple(checks)
        status = (
            LearningStateExecutionLearningStateConsumptionReadValidationStatus.VALIDATED
            if valid else LearningStateExecutionLearningStateConsumptionReadValidationStatus.REJECTED
        )
        return LearningStateExecutionLearningStateConsumptionReadValidation(
            validation_id=validation_id,
            read_id=read.read_id,
            consumption_request_id=read.consumption_request_id,
            source_validation_id=read.validation_id,
            integrity_id=read.integrity_id,
            transition_id=read.transition_id,
            evidence_id=read.evidence_id,
            state_key=read.state_key,
            requested_scope=read.requested_scope,
            read_payload=read.read_payload,
            read_fingerprint=read.read_fingerprint,
            computed_read_fingerprint=computed,
            reader_id=read.reader_id,
            read_purpose=read.read_purpose,
            request_rationale=read.request_rationale,
            confidence=read.confidence,
            validator_id=validator_id,
            validation_purpose=validation_purpose,
            validation_rationale=validation_rationale,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "validation_id": validation_id,
                "read_id": read.read_id,
                "consumption_request_id": read.consumption_request_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateConsumptionReadValidationError",
    "LearningStateExecutionLearningStateConsumptionReadValidationStatus",
    "LearningStateExecutionLearningStateConsumptionReadValidation",
    "LearningStateExecutionLearningStateConsumptionReadValidationService",
]
