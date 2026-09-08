"""M24.5: verify an application outcome and record bounded rollback evidence."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.improvement_application import (
    ImprovementApplication,
    ImprovementApplicationStatus,
)


class ImprovementVerificationError(RuntimeError):
    """Raised when a bounded verification result cannot be recorded safely."""


class ImprovementVerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    INVALID = "INVALID"


class ImprovementRollbackStatus(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    REQUIRED = "REQUIRED"
    RECORDED = "RECORDED"
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
class ImprovementVerification:
    """Immutable verification and bounded rollback evidence for one application."""

    verification_id: str
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
    verifier_id: str
    verification_purpose: str
    verification_scope: str
    observed_result: Any
    expected_result: Any
    verification_status: ImprovementVerificationStatus
    rollback_status: ImprovementRollbackStatus
    rollback_result: Any
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]
    source_status: ImprovementApplicationStatus

    def __post_init__(self) -> None:
        for name in (
            "verification_id", "application_id", "decision_id", "evaluation_id", "candidate_id",
            "consumption_id", "integrity_id", "validation_id", "transition_id", "evidence_id",
            "proposal_id", "eligibility_id", "source_integrity_id", "source_validation_id",
            "state_key", "verifier_id", "verification_purpose", "verification_scope",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.source_status, ImprovementApplicationStatus):
            raise TypeError("source_status must be an improvement application status")
        if not isinstance(self.verification_status, ImprovementVerificationStatus):
            raise TypeError("verification_status must be an improvement verification status")
        if not isinstance(self.rollback_status, ImprovementRollbackStatus):
            raise TypeError("rollback_status must be an improvement rollback status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(item, str) and item.strip() for item in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.observed_result is None:
            raise ValueError("observed_result must be provided")
        if self.expected_result is None:
            raise ValueError("expected_result must be provided")
        if self.rollback_result is None:
            raise ValueError("rollback_result must be provided")
        object.__setattr__(self, "observed_result", _freeze(self.observed_result))
        object.__setattr__(self, "expected_result", _freeze(self.expected_result))
        object.__setattr__(self, "rollback_result", _freeze(self.rollback_result))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_verified(self) -> bool:
        return self.verification_status is ImprovementVerificationStatus.VERIFIED

    @property
    def is_failed(self) -> bool:
        return self.verification_status is ImprovementVerificationStatus.FAILED

    @property
    def is_invalid(self) -> bool:
        return self.verification_status is ImprovementVerificationStatus.INVALID

    @property
    def requires_rollback(self) -> bool:
        return self.rollback_status is ImprovementRollbackStatus.REQUIRED

    @property
    def rollback_recorded(self) -> bool:
        return self.rollback_status is ImprovementRollbackStatus.RECORDED

    @property
    def executes_rollback(self) -> bool:
        return False

    @property
    def authorizes_rollback(self) -> bool:
        return False

    @property
    def executes_improvement(self) -> bool:
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
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_correctness(self) -> bool:
        return self.is_verified

    @property
    def establishes_certainty(self) -> bool:
        return False


class ImprovementVerificationService:
    """Record verification and externally supplied rollback evidence for an application."""

    def verify(
        self,
        application: ImprovementApplication,
        *,
        verification_id: str,
        verifier_id: str,
        verification_purpose: str,
        verification_scope: str,
        observed_result: Any,
        expected_result: Any,
        verification_status: ImprovementVerificationStatus,
        rollback_status: ImprovementRollbackStatus,
        rollback_result: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> ImprovementVerification:
        if type(application) is not ImprovementApplication:
            raise TypeError("application must be an improvement application")
        for name, value in (
            ("verification_id", verification_id),
            ("verifier_id", verifier_id),
            ("verification_purpose", verification_purpose),
            ("verification_scope", verification_scope),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(verification_status, ImprovementVerificationStatus):
            raise TypeError("verification_status must be an improvement verification status")
        if not isinstance(rollback_status, ImprovementRollbackStatus):
            raise TypeError("rollback_status must be an improvement rollback status")
        if observed_result is None:
            raise ValueError("observed_result must be provided")
        if expected_result is None:
            raise ValueError("expected_result must be provided")
        if rollback_result is None:
            raise ValueError("rollback_result must be provided")
        if verification_id in {application.application_id, application.decision_id, application.evaluation_id, application.candidate_id}:
            raise ValueError("verification identity must be distinct")
        if reasons is not None and (
            not isinstance(reasons, tuple)
            or not all(isinstance(item, str) and item.strip() for item in reasons)
        ):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if application.status is not ImprovementApplicationStatus.APPLIED:
            checks.append("source application is not APPLIED")

        anchors = (
            ("application_id", application.application_id),
            ("decision_id", application.decision_id),
            ("evaluation_id", application.evaluation_id),
            ("candidate_id", application.candidate_id),
            ("consumption_id", application.consumption_id),
            ("integrity_id", application.integrity_id),
            ("validation_id", application.validation_id),
            ("transition_id", application.transition_id),
            ("evidence_id", application.evidence_id),
            ("proposal_id", application.proposal_id),
            ("eligibility_id", application.eligibility_id),
            ("source_integrity_id", application.source_integrity_id),
            ("source_validation_id", application.source_validation_id),
        )
        checks.extend(
            f"{name} lineage mismatch"
            for name, expected in anchors
            if application.lineage.get(name, expected) != expected
        )

        valid = not checks
        final_verification_status = verification_status if valid else ImprovementVerificationStatus.INVALID
        final_rollback_status = rollback_status if valid else ImprovementRollbackStatus.INVALID
        final_reasons = reasons if reasons is not None else (
            ("application outcome accepted for bounded verification",) if valid else tuple(checks)
        )

        return ImprovementVerification(
            verification_id=verification_id,
            application_id=application.application_id,
            decision_id=application.decision_id,
            evaluation_id=application.evaluation_id,
            candidate_id=application.candidate_id,
            consumption_id=application.consumption_id,
            integrity_id=application.integrity_id,
            validation_id=application.validation_id,
            transition_id=application.transition_id,
            evidence_id=application.evidence_id,
            proposal_id=application.proposal_id,
            eligibility_id=application.eligibility_id,
            source_integrity_id=application.source_integrity_id,
            source_validation_id=application.source_validation_id,
            state_key=application.state_key,
            verifier_id=verifier_id,
            verification_purpose=verification_purpose,
            verification_scope=verification_scope,
            observed_result=observed_result,
            expected_result=expected_result,
            verification_status=final_verification_status,
            rollback_status=final_rollback_status,
            rollback_result=rollback_result,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {
                "verification_id": verification_id,
                "application_id": application.application_id,
                "decision_id": application.decision_id,
                "evaluation_id": application.evaluation_id,
                "candidate_id": application.candidate_id,
                "consumption_id": application.consumption_id,
                "integrity_id": application.integrity_id,
                "validation_id": application.validation_id,
                "transition_id": application.transition_id,
                "evidence_id": application.evidence_id,
                "proposal_id": application.proposal_id,
                "eligibility_id": application.eligibility_id,
                "source_integrity_id": application.source_integrity_id,
                "source_validation_id": application.source_validation_id,
            },
            source_status=application.status,
        )


__all__ = [
    "ImprovementVerificationError",
    "ImprovementVerificationStatus",
    "ImprovementRollbackStatus",
    "ImprovementVerification",
    "ImprovementVerificationService",
]