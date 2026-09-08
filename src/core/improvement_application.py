"""M24.4: record bounded improvement application without execution authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.improvement_decision import (
    ImprovementDecision,
    ImprovementDecisionStatus,
)


class ImprovementApplicationError(RuntimeError):
    """Raised when a bounded improvement application cannot be recorded safely."""


class ImprovementApplicationStatus(str, Enum):
    APPLIED = "APPLIED"
    FAILED = "FAILED"
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


@dataclass(frozen=True)
class ImprovementApplication:
    """Immutable record of an externally performed improvement application."""

    application_id: str
    decision_id: str
    evaluation_id: str
    candidate_id: str
    consumption_id: str
    integrity_id: str
    validation_id: str
    transition_id: str
    evidence_id: str
    proposal_id: str
    eligibility_id: str
    source_integrity_id: str
    source_validation_id: str
    state_key: str
    application_scope: str
    applicator_id: str
    application_purpose: str
    application_result: Any
    status: ImprovementApplicationStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]
    source_status: ImprovementDecisionStatus

    def __post_init__(self) -> None:
        for name in (
            "application_id", "decision_id", "evaluation_id", "candidate_id", "consumption_id",
            "integrity_id", "validation_id", "transition_id", "evidence_id", "proposal_id",
            "eligibility_id", "source_integrity_id", "source_validation_id", "state_key",
            "application_scope", "applicator_id", "application_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.source_status, ImprovementDecisionStatus):
            raise TypeError("source_status must be an improvement decision status")
        if not isinstance(self.status, ImprovementApplicationStatus):
            raise TypeError("status must be an improvement application status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(item, str) and item.strip() for item in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.application_result is None:
            raise ValueError("application_result must be provided")
        object.__setattr__(self, "application_result", _freeze(self.application_result))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_applied(self) -> bool:
        return self.status is ImprovementApplicationStatus.APPLIED

    @property
    def is_failed(self) -> bool:
        return self.status is ImprovementApplicationStatus.FAILED

    @property
    def is_invalid(self) -> bool:
        return self.status is ImprovementApplicationStatus.INVALID

    @property
    def executes_improvement(self) -> bool:
        return False

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def mutates_model(self) -> bool:
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
    def learns_from_application(self) -> bool:
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


class ImprovementApplicationService:
    """Record the result of an externally performed application."""

    def apply(
        self,
        decision: ImprovementDecision,
        *,
        applicator_id: str,
        application_scope: str,
        application_purpose: str,
        application_result: Any,
        status: ImprovementApplicationStatus,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> ImprovementApplication:
        if type(decision) is not ImprovementDecision:
            raise TypeError("decision must be an improvement decision")
        for name, value in (
            ("applicator_id", applicator_id),
            ("application_scope", application_scope),
            ("application_purpose", application_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(status, ImprovementApplicationStatus):
            raise TypeError("status must be an improvement application status")
        if application_result is None:
            raise ValueError("application_result must be provided")
        if reasons is not None and (
            not isinstance(reasons, tuple)
            or not all(isinstance(item, str) and item.strip() for item in reasons)
        ):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if decision.status is not ImprovementDecisionStatus.APPROVED:
            checks.append("source decision is not APPROVED")

        anchors = (
            ("decision_id", decision.decision_id),
            ("evaluation_id", decision.evaluation_id),
            ("candidate_id", decision.candidate_id),
            ("consumption_id", decision.consumption_id),
            ("integrity_id", decision.integrity_id),
            ("validation_id", decision.validation_id),
            ("transition_id", decision.transition_id),
            ("evidence_id", decision.evidence_id),
            ("application_id", decision.application_id),
            ("proposal_id", decision.proposal_id),
            ("eligibility_id", decision.eligibility_id),
            ("source_integrity_id", decision.source_integrity_id),
            ("source_validation_id", decision.source_validation_id),
        )
        checks.extend(
            f"{name} lineage mismatch"
            for name, expected in anchors
            if decision.lineage.get(name, expected) != expected
        )

        valid = not checks
        final_status = status if valid else ImprovementApplicationStatus.INVALID
        final_reasons = reasons if reasons is not None else (
            ("approved improvement decision accepted for bounded application recording",)
            if valid
            else tuple(checks)
        )

        return ImprovementApplication(
            application_id=decision.application_id,
            decision_id=decision.decision_id,
            evaluation_id=decision.evaluation_id,
            candidate_id=decision.candidate_id,
            consumption_id=decision.consumption_id,
            integrity_id=decision.integrity_id,
            validation_id=decision.validation_id,
            transition_id=decision.transition_id,
            evidence_id=decision.evidence_id,
            proposal_id=decision.proposal_id,
            eligibility_id=decision.eligibility_id,
            source_integrity_id=decision.source_integrity_id,
            source_validation_id=decision.source_validation_id,
            state_key=decision.state_key,
            application_scope=application_scope,
            applicator_id=applicator_id,
            application_purpose=application_purpose,
            application_result=application_result,
            status=final_status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "application_id": decision.application_id,
                "decision_id": decision.decision_id,
                "evaluation_id": decision.evaluation_id,
                "candidate_id": decision.candidate_id,
                "consumption_id": decision.consumption_id,
                "integrity_id": decision.integrity_id,
                "validation_id": decision.validation_id,
                "transition_id": decision.transition_id,
                "evidence_id": decision.evidence_id,
                "proposal_id": decision.proposal_id,
                "eligibility_id": decision.eligibility_id,
                "source_integrity_id": decision.source_integrity_id,
                "source_validation_id": decision.source_validation_id,
            },
            source_status=decision.status,
        )


__all__ = [
    "ImprovementApplicationError",
    "ImprovementApplicationStatus",
    "ImprovementApplication",
    "ImprovementApplicationService",
]
