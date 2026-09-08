"""M23.168: establish integrity for learning-state validation evidence."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_validation import (
    LearningStateExecutionLearningStateValidation,
    LearningStateExecutionLearningStateValidationStatus,
)


class LearningStateExecutionLearningStateValidationIntegrityError(RuntimeError):
    """Raised when learning-state validation-integrity evidence cannot be formed safely."""


class LearningStateExecutionLearningStateValidationIntegrityStatus(str, Enum):
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


def _validation_integrity_fingerprint(validation: LearningStateExecutionLearningStateValidation) -> str:
    payload = {name: _canonical(getattr(validation, name)) for name in (
        "validation_id", "integrity_id", "transition_id", "transition_status", "evidence_id", "state_key",
        "state_before", "state_after", "proposed_change", "transition_fingerprint",
        "computed_transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint",
        "application_id", "decision_id", "proposal_id", "eligibility_id", "source_integrity_id", "signal_id",
        "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id", "source_validation_id",
        "use_id", "request_id", "interpretation_id", "source_request_id", "read_validation_id", "read_id",
        "consumption_request_id", "confidence", "consumer_id", "execution_target_id", "execution_purpose",
        "objective", "evaluator_id", "evaluation_purpose", "signal_kind", "signal_purpose", "learner_id",
        "eligibility_purpose", "proposer_id", "proposal_purpose", "proposal_rationale", "decision_maker_id",
        "decision_purpose", "decision_rationale", "applier_id", "application_purpose", "application_rationale",
        "application_evidence", "application_status", "evidence_collector_id", "evidence_purpose",
        "evidence_rationale", "evidence_payload", "transition_actor_id", "transition_purpose",
        "transition_rationale", "validator_id", "validation_purpose", "validation_rationale", "status",
        "reasons", "lineage",
    )}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class LearningStateExecutionLearningStateValidationIntegrity:
    """Immutable integrity evidence for one learning-state validation artifact."""

    integrity_id: str
    validation_id: str
    integrity_source_status: LearningStateExecutionLearningStateValidationStatus
    transition_id: str
    evidence_id: str
    application_id: str
    decision_id: str
    proposal_id: str
    eligibility_id: str
    source_integrity_id: str
    source_validation_id: str
    state_key: str
    state_before: Any
    state_after: Any
    proposed_change: Any
    transition_fingerprint: str
    computed_transition_fingerprint: str
    source_application_fingerprint: str
    computed_application_fingerprint: str
    confidence: float
    validation_purpose: str
    validator_id: str
    integrity_fingerprint: str
    computed_integrity_fingerprint: str
    status: LearningStateExecutionLearningStateValidationIntegrityStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "integrity_id", "validation_id", "transition_id", "evidence_id", "application_id", "decision_id",
            "proposal_id", "eligibility_id", "source_integrity_id", "source_validation_id", "state_key",
            "transition_fingerprint", "computed_transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "validation_purpose", "validator_id", "integrity_fingerprint",
            "computed_integrity_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.integrity_source_status, LearningStateExecutionLearningStateValidationStatus):
            raise TypeError("integrity_source_status must be a learning-state validation status")
        if not isinstance(self.status, LearningStateExecutionLearningStateValidationIntegrityStatus):
            raise TypeError("status must be a learning-state validation integrity status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.status is LearningStateExecutionLearningStateValidationIntegrityStatus.VALID:
            for name in (
                "transition_fingerprint", "computed_transition_fingerprint", "source_application_fingerprint",
                "computed_application_fingerprint", "integrity_fingerprint", "computed_integrity_fingerprint",
            ):
                value = getattr(self, name)
                if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                    raise ValueError("VALID learning-state validation integrity requires SHA-256 fingerprints")
            if self.integrity_fingerprint != self.computed_integrity_fingerprint:
                raise ValueError("VALID integrity requires matching integrity fingerprints")
            if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
                raise ValueError("VALID integrity requires confidence between 0.0 and 1.0")
        object.__setattr__(self, "state_before", _freeze(self.state_before))
        object.__setattr__(self, "state_after", _freeze(self.state_after))
        object.__setattr__(self, "proposed_change", _freeze(self.proposed_change))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_valid(self) -> bool:
        return self.status is LearningStateExecutionLearningStateValidationIntegrityStatus.VALID

    @property
    def is_invalid(self) -> bool:
        return self.status is LearningStateExecutionLearningStateValidationIntegrityStatus.INVALID

    @property
    def validates_integrity(self) -> bool:
        return self.is_valid

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


class LearningStateExecutionLearningStateValidationIntegrityService:
    """Form deterministic integrity evidence without repairing or executing validation."""

    def validate(
        self,
        validation: LearningStateExecutionLearningStateValidation,
        *,
        integrity_id: str,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateValidationIntegrity:
        if type(validation) is not LearningStateExecutionLearningStateValidation:
            raise TypeError("validation must be a learning-state validation artifact")
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if validation.status is not LearningStateExecutionLearningStateValidationStatus.VALIDATED:
            checks.append("learning-state validation is not VALIDATED")
        if integrity_id == validation.validation_id:
            checks.append("integrity identity must be distinct from validation identity")
        expected_lineage = (
            ("validation_id", validation.validation_id, "validation lineage mismatch"),
            ("integrity_id", validation.integrity_id, "integrity lineage mismatch"),
            ("transition_id", validation.transition_id, "transition lineage mismatch"),
            ("evidence_id", validation.evidence_id, "evidence lineage mismatch"),
            ("application_id", validation.application_id, "application lineage mismatch"),
            ("source_integrity_id", validation.source_integrity_id, "source integrity lineage mismatch"),
            ("source_validation_id", validation.source_validation_id, "source validation lineage mismatch"),
        )
        for name, expected, reason in expected_lineage:
            if validation.lineage.get(name, expected) != expected:
                checks.append(reason)

        for name in (
            "transition_fingerprint", "computed_transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint",
        ):
            value = getattr(validation, name)
            if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                checks.append(f"{name} is not SHA-256")
        if validation.transition_fingerprint != validation.computed_transition_fingerprint:
            checks.append("transition fingerprint mismatch")
        if validation.source_application_fingerprint != validation.computed_application_fingerprint:
            checks.append("application fingerprint mismatch")
        if validation.state_before == validation.state_after:
            checks.append("state before and after are identical")
        if isinstance(validation.confidence, bool) or not isinstance(validation.confidence, (int, float)) or not 0.0 <= float(validation.confidence) <= 1.0:
            checks.append("confidence is outside bounds")

        fingerprint = _validation_integrity_fingerprint(validation)
        valid = not checks
        final_reasons = reasons if reasons is not None else (
            ("learning-state validation integrity checks passed",) if valid else tuple(checks)
        )
        status = LearningStateExecutionLearningStateValidationIntegrityStatus.VALID if valid else LearningStateExecutionLearningStateValidationIntegrityStatus.INVALID
        return LearningStateExecutionLearningStateValidationIntegrity(
            integrity_id=integrity_id,
            validation_id=validation.validation_id,
            integrity_source_status=validation.status,
            transition_id=validation.transition_id,
            evidence_id=validation.evidence_id,
            application_id=validation.application_id,
            decision_id=validation.decision_id,
            proposal_id=validation.proposal_id,
            eligibility_id=validation.eligibility_id,
            source_integrity_id=validation.source_integrity_id,
            source_validation_id=validation.source_validation_id,
            state_key=validation.state_key,
            state_before=validation.state_before,
            state_after=validation.state_after,
            proposed_change=validation.proposed_change,
            transition_fingerprint=validation.transition_fingerprint,
            computed_transition_fingerprint=validation.computed_transition_fingerprint,
            source_application_fingerprint=validation.source_application_fingerprint,
            computed_application_fingerprint=validation.computed_application_fingerprint,
            confidence=validation.confidence,
            validation_purpose=validation.validation_purpose,
            validator_id=validation.validator_id,
            integrity_fingerprint=fingerprint,
            computed_integrity_fingerprint=fingerprint,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "integrity_id": integrity_id,
                "validation_id": validation.validation_id,
                "transition_id": validation.transition_id,
                "evidence_id": validation.evidence_id,
                "application_id": validation.application_id,
                "source_integrity_id": validation.source_integrity_id,
                "source_validation_id": validation.source_validation_id,
            },
        )


__all__ = [
    "LearningStateExecutionLearningStateValidationIntegrityError",
    "LearningStateExecutionLearningStateValidationIntegrityStatus",
    "LearningStateExecutionLearningStateValidationIntegrity",
    "LearningStateExecutionLearningStateValidationIntegrityService",
]
