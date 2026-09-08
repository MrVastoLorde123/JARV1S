"""M24.1: form a bounded continuous-self-improvement candidate from consumed evidence."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_validation_integrity_consumption import (
    LearningStateExecutionLearningStateValidationIntegrityConsumption,
    LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus,
)


class ContinuousSelfImprovementCandidateError(RuntimeError):
    """Raised when a bounded improvement candidate cannot be formed safely."""


class ContinuousSelfImprovementCandidateStatus(str, Enum):
    PROPOSED = "PROPOSED"
    REJECTED = "REJECTED"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, tuple):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, set):
        return frozenset(_freeze(v) for v in value)
    return value


@dataclass(frozen=True)
class ContinuousSelfImprovementCandidate:
    """Immutable candidate change derived from consumed learning-state evidence."""

    candidate_id: str
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
    source_integrity_fingerprint: str
    computed_integrity_fingerprint: str
    source_status: LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus
    proposer_id: str
    candidate_purpose: str
    improvement_scope: str
    proposed_improvement: Any
    rationale: Any
    status: ContinuousSelfImprovementCandidateStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "candidate_id", "consumption_id", "integrity_id", "validation_id", "transition_id", "evidence_id",
            "application_id", "decision_id", "proposal_id", "eligibility_id", "source_integrity_id",
            "source_validation_id", "state_key", "source_integrity_fingerprint", "computed_integrity_fingerprint",
            "proposer_id", "candidate_purpose", "improvement_scope",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.source_status, LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus):
            raise TypeError("source_status must be a validation-integrity consumption status")
        if not isinstance(self.status, ContinuousSelfImprovementCandidateStatus):
            raise TypeError("status must be a continuous-self-improvement candidate status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(r, str) and r.strip() for r in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.proposed_improvement is None:
            raise ValueError("proposed_improvement must be provided")
        if self.rationale is None:
            raise ValueError("rationale must be provided")
        object.__setattr__(self, "proposed_improvement", _freeze(self.proposed_improvement))
        object.__setattr__(self, "rationale", _freeze(self.rationale))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_proposed(self) -> bool:
        return self.status is ContinuousSelfImprovementCandidateStatus.PROPOSED

    @property
    def is_rejected(self) -> bool:
        return self.status is ContinuousSelfImprovementCandidateStatus.REJECTED

    @property
    def is_learning(self) -> bool: return False
    @property
    def applies_learning(self) -> bool: return False
    @property
    def proposes_adaptation(self) -> bool: return self.is_proposed
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
    def updates_model(self) -> bool: return False
    @property
    def mutates_memory(self) -> bool: return False
    @property
    def mutates_policy(self) -> bool: return False
    @property
    def mutates_state(self) -> bool: return False
    @property
    def persists_state(self) -> bool: return False
    @property
    def schedules_work(self) -> bool: return False
    @property
    def plans_work(self) -> bool: return False
    @property
    def establishes_truth(self) -> bool: return False
    @property
    def establishes_correctness(self) -> bool: return False
    @property
    def establishes_certainty(self) -> bool: return False
    @property
    def establishes_usefulness(self) -> bool: return False


class ContinuousSelfImprovementCandidateService:
    """Form one bounded improvement candidate from one consumed evidence artifact."""

    def propose(
        self,
        consumption: LearningStateExecutionLearningStateValidationIntegrityConsumption,
        *,
        candidate_id: str,
        proposer_id: str,
        candidate_purpose: str,
        improvement_scope: str,
        proposed_improvement: Any,
        rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> ContinuousSelfImprovementCandidate:
        if type(consumption) is not LearningStateExecutionLearningStateValidationIntegrityConsumption:
            raise TypeError("consumption must be a validation-integrity consumption artifact")
        for name, value in (
            ("candidate_id", candidate_id),
            ("proposer_id", proposer_id),
            ("candidate_purpose", candidate_purpose),
            ("improvement_scope", improvement_scope),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if proposed_improvement is None:
            raise ValueError("proposed_improvement must be provided")
        if rationale is None:
            raise ValueError("rationale must be provided")
        if candidate_id in {consumption.consumption_id, consumption.integrity_id}:
            raise ValueError("candidate identity must be distinct")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(r, str) and r.strip() for r in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if consumption.status is not LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus.CONSUMED:
            checks.append("source consumption is not CONSUMED")
        anchors = (
            ("consumption_id", consumption.consumption_id),
            ("integrity_id", consumption.integrity_id),
            ("validation_id", consumption.validation_id),
            ("transition_id", consumption.transition_id),
            ("evidence_id", consumption.evidence_id),
            ("application_id", consumption.application_id),
            ("source_integrity_id", consumption.source_integrity_id),
            ("source_validation_id", consumption.source_validation_id),
        )
        checks.extend(f"{name} lineage mismatch" for name, expected in anchors if consumption.lineage.get(name, expected) != expected)
        valid = not checks
        status = ContinuousSelfImprovementCandidateStatus.PROPOSED if valid else ContinuousSelfImprovementCandidateStatus.REJECTED
        final_reasons = reasons if reasons is not None else (("consumed learning-state evidence accepted for improvement candidacy",) if valid else tuple(checks))
        return ContinuousSelfImprovementCandidate(
            candidate_id=candidate_id,
            consumption_id=consumption.consumption_id,
            integrity_id=consumption.integrity_id,
            validation_id=consumption.validation_id,
            transition_id=consumption.transition_id,
            evidence_id=consumption.evidence_id,
            application_id=consumption.application_id,
            decision_id=consumption.decision_id,
            proposal_id=consumption.proposal_id,
            eligibility_id=consumption.eligibility_id,
            source_integrity_id=consumption.source_integrity_id,
            source_validation_id=consumption.source_validation_id,
            state_key=consumption.state_key,
            source_integrity_fingerprint=consumption.integrity_fingerprint,
            computed_integrity_fingerprint=consumption.computed_integrity_fingerprint,
            source_status=consumption.status,
            proposer_id=proposer_id,
            candidate_purpose=candidate_purpose,
            improvement_scope=improvement_scope,
            proposed_improvement=proposed_improvement,
            rationale=rationale,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "candidate_id": candidate_id,
                "consumption_id": consumption.consumption_id,
                "integrity_id": consumption.integrity_id,
                "validation_id": consumption.validation_id,
                "transition_id": consumption.transition_id,
                "evidence_id": consumption.evidence_id,
                "application_id": consumption.application_id,
                "source_integrity_id": consumption.source_integrity_id,
                "source_validation_id": consumption.source_validation_id,
            },
        )


__all__ = [
    "ContinuousSelfImprovementCandidateError",
    "ContinuousSelfImprovementCandidateStatus",
    "ContinuousSelfImprovementCandidate",
    "ContinuousSelfImprovementCandidateService",
]
