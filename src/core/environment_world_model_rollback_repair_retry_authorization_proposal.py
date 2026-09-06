"""M23.49: advisory authorization proposal from retry re-eligibility assessment.

The proposal converts one bounded M23.48 assessment into non-authorizing
proposal evidence for a separate authorization decision. It never grants
permission, schedules retry, executes retry, or mutates state.

The upstream assessment type is imported lazily inside runtime validation so
this module remains a leaf dependency from the authorization-decision layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from src.core.environment_world_model_rollback_repair_retry_reeligibility_assessment import (
        EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessment,
        EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus,
    )


class EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalError(RuntimeError):
    """Raised when a retry authorization proposal cannot be formed safely."""


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


def _validate_aware_datetime(value: datetime, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal:
    """Immutable advisory evidence proposing a separate retry authorization decision."""

    proposal_id: str
    assessment_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    assessment_status: "EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus"
    requested_action: str
    retry_count: int
    max_retries: int
    evaluated_at: datetime
    next_eligible_at: datetime | None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        from src.core.environment_world_model_rollback_repair_retry_reeligibility_assessment import (
            EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus,
        )

        for name in (
            "proposal_id",
            "assessment_id",
            "evaluation_id",
            "feedback_id",
            "outcome_id",
            "environment_id",
            "expected_model_id",
            "observed_model_id",
            "requested_action",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(
            self.assessment_status,
            EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus,
        ):
            raise TypeError("assessment_status must be a re-eligibility assessment status")
        if self.requested_action not in {"RETRY_REPAIR", "NO_AUTHORIZATION"}:
            raise ValueError("requested_action must be RETRY_REPAIR or NO_AUTHORIZATION")
        if isinstance(self.retry_count, bool) or not isinstance(self.retry_count, int):
            raise TypeError("retry_count must be an integer")
        if self.retry_count < 0:
            raise ValueError("retry_count must be >= 0")
        if isinstance(self.max_retries, bool) or not isinstance(self.max_retries, int):
            raise TypeError("max_retries must be an integer")
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        _validate_aware_datetime(self.evaluated_at, "evaluated_at")
        if self.next_eligible_at is not None:
            _validate_aware_datetime(self.next_eligible_at, "next_eligible_at")
        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def executes_retry(self) -> bool:
        return False

    @property
    def schedules_retry(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalService:
    """Convert M23.48 assessment evidence into non-authorizing proposal evidence."""

    def propose(
        self,
        assessment: "EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessment",
        *,
        proposal_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal:
        from src.core.environment_world_model_rollback_repair_retry_reeligibility_assessment import (
            EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessment,
            EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus,
        )

        if type(assessment) is not EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessment:
            raise TypeError(
                "assessment must be EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessment"
            )
        if not isinstance(proposal_id, str) or not proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string")

        if assessment.status is EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.ELIGIBLE:
            requested_action = "RETRY_REPAIR"
            default_reason = "eligible retry re-eligibility evidence requests a separate authorization decision"
        elif assessment.status in {
            EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.WAITING,
            EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.NOT_ELIGIBLE,
        }:
            requested_action = "NO_AUTHORIZATION"
            default_reason = "retry re-eligibility evidence does not support requesting retry authorization"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalError(
                "unsupported re-eligibility assessment status"
            )

        return EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal(
            proposal_id=proposal_id,
            assessment_id=assessment.assessment_id,
            evaluation_id=assessment.evaluation_id,
            feedback_id=assessment.feedback_id,
            outcome_id=assessment.outcome_id,
            environment_id=assessment.environment_id,
            expected_model_id=assessment.expected_model_id,
            observed_model_id=assessment.observed_model_id,
            assessment_status=assessment.status,
            requested_action=requested_action,
            retry_count=assessment.retry_count,
            max_retries=assessment.max_retries,
            evaluated_at=assessment.evaluated_at,
            next_eligible_at=assessment.next_eligible_at,
            reasons=reasons or {"status": default_reason},
            lineage=lineage or {
                "assessment_id": assessment.assessment_id,
                "evaluation_id": assessment.evaluation_id,
                "feedback_id": assessment.feedback_id,
                "outcome_id": assessment.outcome_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalError",
    "EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal",
    "EnvironmentWorldModelRollbackRepairRetryAuthorizationProposalService",
]
