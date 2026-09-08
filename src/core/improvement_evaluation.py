"""M24.2: evaluate one continuous-self-improvement candidate without authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.continuous_self_improvement_candidate import (
    ContinuousSelfImprovementCandidate,
    ContinuousSelfImprovementCandidateStatus,
)


class ImprovementEvaluationError(RuntimeError):
    """Raised when bounded improvement evaluation cannot be formed safely."""


class ImprovementEvaluationStatus(str, Enum):
    EVALUATED = "EVALUATED"
    REJECTED = "REJECTED"


class ImprovementAssessment(str, Enum):
    SUPPORTIVE = "SUPPORTIVE"
    CONCERNING = "CONCERNING"
    MIXED = "MIXED"
    INCONCLUSIVE = "INCONCLUSIVE"


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
class ImprovementEvaluation:
    """Immutable evidence describing an evaluation of one proposed improvement."""

    evaluation_id: str
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
    candidate_scope: str
    candidate_source_fingerprint: str
    candidate_computed_fingerprint: str
    source_status: ContinuousSelfImprovementCandidateStatus
    evaluator_id: str
    evaluation_purpose: str
    evaluation_scope: str
    criteria: tuple[str, ...]
    observations: Any
    assessment: ImprovementAssessment
    status: ImprovementEvaluationStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "evaluation_id", "candidate_id", "consumption_id", "integrity_id", "validation_id",
            "transition_id", "evidence_id", "application_id", "decision_id", "proposal_id",
            "eligibility_id", "source_integrity_id", "source_validation_id", "state_key",
            "candidate_scope", "candidate_source_fingerprint", "candidate_computed_fingerprint",
            "evaluator_id", "evaluation_purpose", "evaluation_scope",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.source_status, ContinuousSelfImprovementCandidateStatus):
            raise TypeError("source_status must be a continuous-self-improvement candidate status")
        if not isinstance(self.assessment, ImprovementAssessment):
            raise TypeError("assessment must be an improvement assessment")
        if not isinstance(self.status, ImprovementEvaluationStatus):
            raise TypeError("status must be an improvement evaluation status")
        if not isinstance(self.criteria, tuple) or not all(isinstance(item, str) and item.strip() for item in self.criteria):
            raise TypeError("criteria must be a tuple of non-empty strings")
        if not self.criteria:
            raise ValueError("criteria must not be empty")
        if not isinstance(self.reasons, tuple) or not all(isinstance(item, str) and item.strip() for item in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.observations is None:
            raise ValueError("observations must be provided")
        object.__setattr__(self, "criteria", tuple(self.criteria))
        object.__setattr__(self, "observations", _freeze(self.observations))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_evaluated(self) -> bool:
        return self.status is ImprovementEvaluationStatus.EVALUATED

    @property
    def is_rejected(self) -> bool:
        return self.status is ImprovementEvaluationStatus.REJECTED

    @property
    def authorizes_application(self) -> bool:
        return False

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def applies_improvement(self) -> bool:
        return False

    @property
    def decides_improvement(self) -> bool:
        return False

    @property
    def is_learning(self) -> bool:
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


class ImprovementEvaluationService:
    """Evaluate one proposed candidate against explicit criteria and observations."""

    def evaluate(
        self,
        candidate: ContinuousSelfImprovementCandidate,
        *,
        evaluation_id: str,
        evaluator_id: str,
        evaluation_purpose: str,
        evaluation_scope: str,
        criteria: tuple[str, ...],
        observations: Any,
        assessment: ImprovementAssessment,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> ImprovementEvaluation:
        if type(candidate) is not ContinuousSelfImprovementCandidate:
            raise TypeError("candidate must be a continuous-self-improvement candidate")
        for name, value in (
            ("evaluation_id", evaluation_id),
            ("evaluator_id", evaluator_id),
            ("evaluation_purpose", evaluation_purpose),
            ("evaluation_scope", evaluation_scope),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(criteria, tuple) or not all(isinstance(item, str) and item.strip() for item in criteria):
            raise TypeError("criteria must be a tuple of non-empty strings")
        if not criteria:
            raise ValueError("criteria must not be empty")
        if observations is None:
            raise ValueError("observations must be provided")
        if not isinstance(assessment, ImprovementAssessment):
            raise TypeError("assessment must be an improvement assessment")
        if evaluation_id in {candidate.candidate_id, candidate.consumption_id}:
            raise ValueError("evaluation identity must be distinct")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(item, str) and item.strip() for item in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if candidate.status is not ContinuousSelfImprovementCandidateStatus.PROPOSED:
            checks.append("source candidate is not PROPOSED")
        anchors = (
            ("candidate_id", candidate.candidate_id),
            ("consumption_id", candidate.consumption_id),
            ("integrity_id", candidate.integrity_id),
            ("validation_id", candidate.validation_id),
            ("transition_id", candidate.transition_id),
            ("evidence_id", candidate.evidence_id),
            ("application_id", candidate.application_id),
            ("source_integrity_id", candidate.source_integrity_id),
            ("source_validation_id", candidate.source_validation_id),
        )
        checks.extend(
            f"{name} lineage mismatch"
            for name, expected in anchors
            if candidate.lineage.get(name, expected) != expected
        )

        valid = not checks
        status = ImprovementEvaluationStatus.EVALUATED if valid else ImprovementEvaluationStatus.REJECTED
        final_reasons = reasons if reasons is not None else (
            ("proposed improvement candidate evaluated against declared criteria",)
            if valid else tuple(checks)
        )

        return ImprovementEvaluation(
            evaluation_id=evaluation_id,
            candidate_id=candidate.candidate_id,
            consumption_id=candidate.consumption_id,
            integrity_id=candidate.integrity_id,
            validation_id=candidate.validation_id,
            transition_id=candidate.transition_id,
            evidence_id=candidate.evidence_id,
            application_id=candidate.application_id,
            decision_id=candidate.decision_id,
            proposal_id=candidate.proposal_id,
            eligibility_id=candidate.eligibility_id,
            source_integrity_id=candidate.source_integrity_id,
            source_validation_id=candidate.source_validation_id,
            state_key=candidate.state_key,
            candidate_scope=candidate.improvement_scope,
            candidate_source_fingerprint=candidate.source_integrity_fingerprint,
            candidate_computed_fingerprint=candidate.computed_integrity_fingerprint,
            source_status=candidate.status,
            evaluator_id=evaluator_id,
            evaluation_purpose=evaluation_purpose,
            evaluation_scope=evaluation_scope,
            criteria=tuple(criteria),
            observations=observations,
            assessment=assessment,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "evaluation_id": evaluation_id,
                "candidate_id": candidate.candidate_id,
                "consumption_id": candidate.consumption_id,
                "integrity_id": candidate.integrity_id,
                "validation_id": candidate.validation_id,
                "transition_id": candidate.transition_id,
                "evidence_id": candidate.evidence_id,
                "application_id": candidate.application_id,
                "source_integrity_id": candidate.source_integrity_id,
                "source_validation_id": candidate.source_validation_id,
            },
        )


__all__ = [
    "ImprovementEvaluationError",
    "ImprovementEvaluationStatus",
    "ImprovementAssessment",
    "ImprovementEvaluation",
    "ImprovementEvaluationService",
]
