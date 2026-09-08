"""M24.3: record a bounded improvement decision without application authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.improvement_evaluation import (
    ImprovementEvaluation,
    ImprovementEvaluationStatus,
)


class ImprovementDecisionError(RuntimeError):
    """Raised when a bounded improvement decision cannot be formed safely."""


class ImprovementDecisionStatus(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"
    INVALID = "INVALID"


class ImprovementDisposition(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    DEFER = "DEFER"


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
class ImprovementDecision:
    """Immutable disposition evidence for one evaluated improvement candidate."""

    decision_id: str
    evaluation_id: str
    candidate_id: str
    consumption_id: str
    integrity_id: str
    validation_id: str
    transition_id: str
    evidence_id: str
    application_id: str
    proposal_id: str
    eligibility_id: str
    source_integrity_id: str
    source_validation_id: str
    state_key: str
    candidate_scope: str
    candidate_source_fingerprint: str
    candidate_computed_fingerprint: str
    source_status: ImprovementEvaluationStatus
    decider_id: str
    decision_purpose: str
    decision_scope: str
    disposition: ImprovementDisposition
    rationale: Any
    factors: Any
    status: ImprovementDecisionStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "decision_id", "evaluation_id", "candidate_id", "consumption_id", "integrity_id",
            "validation_id", "transition_id", "evidence_id", "application_id", "proposal_id",
            "eligibility_id", "source_integrity_id", "source_validation_id", "state_key",
            "candidate_scope", "candidate_source_fingerprint", "candidate_computed_fingerprint",
            "decider_id", "decision_purpose", "decision_scope",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.source_status, ImprovementEvaluationStatus):
            raise TypeError("source_status must be an improvement evaluation status")
        if not isinstance(self.disposition, ImprovementDisposition):
            raise TypeError("disposition must be an improvement disposition")
        if not isinstance(self.status, ImprovementDecisionStatus):
            raise TypeError("status must be an improvement decision status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(item, str) and item.strip() for item in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.rationale is None:
            raise ValueError("rationale must be provided")
        if self.factors is None:
            raise ValueError("factors must be provided")
        object.__setattr__(self, "rationale", _freeze(self.rationale))
        object.__setattr__(self, "factors", _freeze(self.factors))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_approved(self) -> bool:
        return self.status is ImprovementDecisionStatus.APPROVED

    @property
    def is_rejected(self) -> bool:
        return self.status is ImprovementDecisionStatus.REJECTED

    @property
    def is_deferred(self) -> bool:
        return self.status is ImprovementDecisionStatus.DEFERRED

    @property
    def is_invalid(self) -> bool:
        return self.status is ImprovementDecisionStatus.INVALID

    @property
    def approves_candidate(self) -> bool:
        return self.status is ImprovementDecisionStatus.APPROVED

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
    def executes_improvement(self) -> bool:
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


class ImprovementDecisionService:
    """Record one bounded disposition for one evaluated improvement candidate."""

    def decide(
        self,
        evaluation: ImprovementEvaluation,
        *,
        decision_id: str,
        decider_id: str,
        decision_purpose: str,
        decision_scope: str,
        disposition: ImprovementDisposition,
        rationale: Any,
        factors: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> ImprovementDecision:
        if type(evaluation) is not ImprovementEvaluation:
            raise TypeError("evaluation must be an improvement evaluation")
        for name, value in (
            ("decision_id", decision_id),
            ("decider_id", decider_id),
            ("decision_purpose", decision_purpose),
            ("decision_scope", decision_scope),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(disposition, ImprovementDisposition):
            raise TypeError("disposition must be an improvement disposition")
        if rationale is None:
            raise ValueError("rationale must be provided")
        if factors is None:
            raise ValueError("factors must be provided")
        if decision_id in {evaluation.evaluation_id, evaluation.candidate_id}:
            raise ValueError("decision identity must be distinct")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(item, str) and item.strip() for item in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if evaluation.status is not ImprovementEvaluationStatus.EVALUATED:
            checks.append("source evaluation is not EVALUATED")
        anchors = (
            ("evaluation_id", evaluation.evaluation_id),
            ("candidate_id", evaluation.candidate_id),
            ("consumption_id", evaluation.consumption_id),
            ("integrity_id", evaluation.integrity_id),
            ("validation_id", evaluation.validation_id),
            ("transition_id", evaluation.transition_id),
            ("evidence_id", evaluation.evidence_id),
            ("application_id", evaluation.application_id),
            ("source_integrity_id", evaluation.source_integrity_id),
            ("source_validation_id", evaluation.source_validation_id),
        )
        checks.extend(
            f"{name} lineage mismatch"
            for name, expected in anchors
            if evaluation.lineage.get(name, expected) != expected
        )

        valid = not checks
        if not valid:
            status = ImprovementDecisionStatus.INVALID
        elif disposition is ImprovementDisposition.APPROVE:
            status = ImprovementDecisionStatus.APPROVED
        elif disposition is ImprovementDisposition.REJECT:
            status = ImprovementDecisionStatus.REJECTED
        else:
            status = ImprovementDecisionStatus.DEFERRED

        final_reasons = reasons if reasons is not None else (
            ("evaluated improvement candidate received an explicit bounded disposition",)
            if valid else tuple(checks)
        )

        return ImprovementDecision(
            decision_id=decision_id,
            evaluation_id=evaluation.evaluation_id,
            candidate_id=evaluation.candidate_id,
            consumption_id=evaluation.consumption_id,
            integrity_id=evaluation.integrity_id,
            validation_id=evaluation.validation_id,
            transition_id=evaluation.transition_id,
            evidence_id=evaluation.evidence_id,
            application_id=evaluation.application_id,
            proposal_id=evaluation.proposal_id,
            eligibility_id=evaluation.eligibility_id,
            source_integrity_id=evaluation.source_integrity_id,
            source_validation_id=evaluation.source_validation_id,
            state_key=evaluation.state_key,
            candidate_scope=evaluation.candidate_scope,
            candidate_source_fingerprint=evaluation.candidate_source_fingerprint,
            candidate_computed_fingerprint=evaluation.candidate_computed_fingerprint,
            source_status=evaluation.status,
            decider_id=decider_id,
            decision_purpose=decision_purpose,
            decision_scope=decision_scope,
            disposition=disposition,
            rationale=rationale,
            factors=factors,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "decision_id": decision_id,
                "evaluation_id": evaluation.evaluation_id,
                "candidate_id": evaluation.candidate_id,
                "consumption_id": evaluation.consumption_id,
                "integrity_id": evaluation.integrity_id,
                "validation_id": evaluation.validation_id,
                "transition_id": evaluation.transition_id,
                "evidence_id": evaluation.evidence_id,
                "application_id": evaluation.application_id,
                "source_integrity_id": evaluation.source_integrity_id,
                "source_validation_id": evaluation.source_validation_id,
            },
        )


__all__ = [
    "ImprovementDecisionError",
    "ImprovementDecisionStatus",
    "ImprovementDisposition",
    "ImprovementDecision",
    "ImprovementDecisionService",
]
