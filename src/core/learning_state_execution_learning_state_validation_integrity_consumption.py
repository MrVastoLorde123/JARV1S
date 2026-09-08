"""M23.169: consume one valid learning-state validation-integrity artifact safely."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_validation_integrity import (
    LearningStateExecutionLearningStateValidationIntegrity,
    LearningStateExecutionLearningStateValidationIntegrityStatus,
)


class LearningStateExecutionLearningStateValidationIntegrityConsumptionError(RuntimeError):
    """Raised when validation-integrity consumption evidence cannot be formed safely."""


class LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus(str, Enum):
    CONSUMED = "CONSUMED"
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
class LearningStateExecutionLearningStateValidationIntegrityConsumption:
    """Immutable evidence that one valid validation-integrity artifact was consumed."""

    consumption_id: str
    integrity_id: str
    validation_id: str
    transition_id: str
    evidence_id: str
    application_id: str
    decision_id: str
    proposal_id: str
    eligibility_id: str
    source_integrity_id: str
    source_validation_id: str
    state_key: str
    validation_purpose: str
    validator_id: str
    integrity_fingerprint: str
    computed_integrity_fingerprint: str
    source_status: LearningStateExecutionLearningStateValidationIntegrityStatus
    consumer_id: str
    consumption_purpose: str
    consumption_rationale: Any
    consumed_metadata: Mapping[str, Any]
    status: LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "consumption_id", "integrity_id", "validation_id", "transition_id", "evidence_id",
            "application_id", "decision_id", "proposal_id", "eligibility_id", "source_integrity_id",
            "source_validation_id", "state_key", "validation_purpose", "validator_id",
            "integrity_fingerprint", "computed_integrity_fingerprint", "consumer_id", "consumption_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.source_status, LearningStateExecutionLearningStateValidationIntegrityStatus):
            raise TypeError("source_status must be a learning-state validation-integrity status")
        if not isinstance(self.status, LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus):
            raise TypeError("status must be a validation-integrity consumption status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.consumed_metadata, Mapping):
            raise TypeError("consumed_metadata must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.status is LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus.CONSUMED:
            for name in ("integrity_fingerprint", "computed_integrity_fingerprint"):
                value = getattr(self, name)
                if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                    raise ValueError("CONSUMED validation-integrity evidence requires SHA-256 fingerprints")
            if self.integrity_fingerprint != self.computed_integrity_fingerprint:
                raise ValueError("CONSUMED validation-integrity evidence requires matching fingerprints")
            if self.source_status is not LearningStateExecutionLearningStateValidationIntegrityStatus.VALID:
                raise ValueError("CONSUMED validation-integrity evidence requires VALID source status")
        object.__setattr__(self, "consumption_rationale", _freeze(self.consumption_rationale))
        object.__setattr__(self, "consumed_metadata", _freeze(self.consumed_metadata))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_consumed(self) -> bool:
        return self.status is LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus.CONSUMED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus.REJECTED

    @property
    def consumes_validation_integrity(self) -> bool:
        return self.is_consumed

    @property
    def mutates_state(self) -> bool: return False
    @property
    def persists_state(self) -> bool: return False
    @property
    def consumes_state(self) -> bool: return False
    @property
    def is_learning(self) -> bool: return False
    @property
    def applies_learning(self) -> bool: return False
    @property
    def authorizes_learning(self) -> bool: return False
    @property
    def authorizes_execution(self) -> bool: return False
    @property
    def authorizes_retry(self) -> bool: return False
    @property
    def invokes_learner(self) -> bool: return False
    @property
    def invokes_executor(self) -> bool: return False
    @property
    def schedules_work(self) -> bool: return False
    @property
    def plans_work(self) -> bool: return False
    @property
    def updates_model(self) -> bool: return False
    @property
    def mutates_memory(self) -> bool: return False
    @property
    def mutates_policy(self) -> bool: return False
    @property
    def establishes_truth(self) -> bool: return False
    @property
    def establishes_correctness(self) -> bool: return False
    @property
    def establishes_certainty(self) -> bool: return False
    @property
    def establishes_usefulness(self) -> bool: return False


class LearningStateExecutionLearningStateValidationIntegrityConsumptionService:
    """Consume only the bounded integrity evidence explicitly presented to this boundary."""

    def consume(
        self,
        integrity: LearningStateExecutionLearningStateValidationIntegrity,
        *,
        consumption_id: str,
        consumer_id: str,
        consumption_purpose: str,
        consumption_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateValidationIntegrityConsumption:
        if type(integrity) is not LearningStateExecutionLearningStateValidationIntegrity:
            raise TypeError("integrity must be a learning-state validation-integrity artifact")
        for name, value in (
            ("consumption_id", consumption_id),
            ("consumer_id", consumer_id),
            ("consumption_purpose", consumption_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if consumption_rationale is None:
            raise ValueError("consumption_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if integrity.status is not LearningStateExecutionLearningStateValidationIntegrityStatus.VALID:
            checks.append("learning-state validation integrity is not VALID")
        if consumption_id == integrity.integrity_id:
            checks.append("consumption identity must be distinct from integrity identity")
        expected_lineage = (
            ("integrity_id", integrity.integrity_id, "integrity lineage mismatch"),
            ("validation_id", integrity.validation_id, "validation lineage mismatch"),
            ("transition_id", integrity.transition_id, "transition lineage mismatch"),
            ("evidence_id", integrity.evidence_id, "evidence lineage mismatch"),
            ("application_id", integrity.application_id, "application lineage mismatch"),
            ("source_integrity_id", integrity.source_integrity_id, "source integrity lineage mismatch"),
            ("source_validation_id", integrity.source_validation_id, "source validation lineage mismatch"),
        )
        for name, expected, reason in expected_lineage:
            if integrity.lineage.get(name, expected) != expected:
                checks.append(reason)

        for name in ("integrity_fingerprint", "computed_integrity_fingerprint"):
            value = getattr(integrity, name)
            if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                checks.append(f"{name} is not SHA-256")
        if integrity.integrity_fingerprint != integrity.computed_integrity_fingerprint:
            checks.append("integrity fingerprint mismatch")

        valid = not checks
        status = (
            LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus.CONSUMED
            if valid
            else LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus.REJECTED
        )
        final_reasons = reasons if reasons is not None else (
            ("learning-state validation-integrity artifact consumed at the declared boundary",)
            if valid else tuple(checks)
        )
        metadata = {
            "integrity_id": integrity.integrity_id,
            "validation_id": integrity.validation_id,
            "transition_id": integrity.transition_id,
            "evidence_id": integrity.evidence_id,
            "application_id": integrity.application_id,
            "decision_id": integrity.decision_id,
            "proposal_id": integrity.proposal_id,
            "eligibility_id": integrity.eligibility_id,
            "source_integrity_id": integrity.source_integrity_id,
            "source_validation_id": integrity.source_validation_id,
            "state_key": integrity.state_key,
            "validation_purpose": integrity.validation_purpose,
            "validator_id": integrity.validator_id,
            "integrity_fingerprint": integrity.integrity_fingerprint,
        } if valid else {"rejected_integrity": True}
        return LearningStateExecutionLearningStateValidationIntegrityConsumption(
            consumption_id=consumption_id,
            integrity_id=integrity.integrity_id,
            validation_id=integrity.validation_id,
            transition_id=integrity.transition_id,
            evidence_id=integrity.evidence_id,
            application_id=integrity.application_id,
            decision_id=integrity.decision_id,
            proposal_id=integrity.proposal_id,
            eligibility_id=integrity.eligibility_id,
            source_integrity_id=integrity.source_integrity_id,
            source_validation_id=integrity.source_validation_id,
            state_key=integrity.state_key,
            validation_purpose=integrity.validation_purpose,
            validator_id=integrity.validator_id,
            integrity_fingerprint=integrity.integrity_fingerprint,
            computed_integrity_fingerprint=integrity.computed_integrity_fingerprint,
            source_status=integrity.status,
            consumer_id=consumer_id,
            consumption_purpose=consumption_purpose,
            consumption_rationale=consumption_rationale,
            consumed_metadata=metadata,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "consumption_id": consumption_id,
                "integrity_id": integrity.integrity_id,
                "validation_id": integrity.validation_id,
                "transition_id": integrity.transition_id,
                "evidence_id": integrity.evidence_id,
                "application_id": integrity.application_id,
                "source_integrity_id": integrity.source_integrity_id,
                "source_validation_id": integrity.source_validation_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateValidationIntegrityConsumptionError",
    "LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus",
    "LearningStateExecutionLearningStateValidationIntegrityConsumption",
    "LearningStateExecutionLearningStateValidationIntegrityConsumptionService",
]
