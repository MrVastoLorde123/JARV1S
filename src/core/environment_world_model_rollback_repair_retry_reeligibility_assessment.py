"""M23.48: bounded re-eligibility assessment from retry feedback evaluation.

The assessment consumes one verified M23.47 evaluation plus an explicit retry
state and immutable policy snapshot. It is observational only: it does not
reuse prior authorization, mutate policy, schedule retry, authorize retry, or
execute corrective work.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_feedback_evaluation import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluation,
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus,
)


class EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentError(RuntimeError):
    """Raised when retry re-eligibility assessment cannot be formed safely."""


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
class EnvironmentWorldModelRollbackRepairRetryReeligibilityPolicy:
    """Immutable bounds for deciding whether another retry may be considered."""

    max_retries: int
    backoff_seconds: float = 0.0

    def __post_init__(self) -> None:
        if isinstance(self.max_retries, bool) or not isinstance(self.max_retries, int):
            raise TypeError("max_retries must be an integer")
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if isinstance(self.backoff_seconds, bool) or not isinstance(self.backoff_seconds, (int, float)):
            raise TypeError("backoff_seconds must be a number")
        if self.backoff_seconds < 0:
            raise ValueError("backoff_seconds must be >= 0")


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryState:
    """Immutable observational snapshot of retry history relevant to assessment."""

    retry_count: int
    last_attempt_at: datetime | None = None

    def __post_init__(self) -> None:
        if isinstance(self.retry_count, bool) or not isinstance(self.retry_count, int):
            raise TypeError("retry_count must be an integer")
        if self.retry_count < 0:
            raise ValueError("retry_count must be >= 0")
        if self.last_attempt_at is not None:
            _validate_aware_datetime(self.last_attempt_at, "last_attempt_at")


class EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    WAITING = "WAITING"


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessment:
    """Immutable advisory assessment of whether another retry may be considered."""

    assessment_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    evaluation_status: EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus
    retry_count: int
    max_retries: int
    evaluated_at: datetime
    next_eligible_at: datetime | None
    status: EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "assessment_id",
            "evaluation_id",
            "feedback_id",
            "outcome_id",
            "environment_id",
            "expected_model_id",
            "observed_model_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.evaluation_status, EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus):
            raise TypeError("evaluation_status must be a feedback-evaluation status")
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
        if not isinstance(self.status, EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus):
            raise TypeError("status must be a re-eligibility assessment status")
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
    def requests_retry(self) -> bool:
        return False

    @property
    def schedules_retry(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentService:
    """Assess retry re-eligibility without granting permission or causing action."""

    def assess(
        self,
        evaluation: EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluation,
        policy: EnvironmentWorldModelRollbackRepairRetryReeligibilityPolicy,
        state: EnvironmentWorldModelRollbackRepairRetryState,
        *,
        assessment_id: str,
        evaluated_at: datetime,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessment:
        if type(evaluation) is not EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluation:
            raise TypeError(
                "evaluation must be EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluation"
            )
        if type(policy) is not EnvironmentWorldModelRollbackRepairRetryReeligibilityPolicy:
            raise TypeError(
                "policy must be EnvironmentWorldModelRollbackRepairRetryReeligibilityPolicy"
            )
        if type(state) is not EnvironmentWorldModelRollbackRepairRetryState:
            raise TypeError("state must be EnvironmentWorldModelRollbackRepairRetryState")
        if not isinstance(assessment_id, str) or not assessment_id.strip():
            raise ValueError("assessment_id must be a non-empty string")
        _validate_aware_datetime(evaluated_at, "evaluated_at")

        if evaluation.evaluation_status is EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus.FAILURE_EVALUATION:
            if state.retry_count >= policy.max_retries:
                status = EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.NOT_ELIGIBLE
                next_eligible_at = None
                default_reason = "failure evaluation observed after the configured retry limit was exhausted"
            elif state.last_attempt_at is not None:
                candidate = state.last_attempt_at + timedelta(seconds=policy.backoff_seconds)
                if evaluated_at < candidate:
                    status = EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.WAITING
                    next_eligible_at = candidate
                    default_reason = "failure evaluation observed while configured retry backoff remains active"
                else:
                    status = EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.ELIGIBLE
                    next_eligible_at = candidate
                    default_reason = "failure evaluation observed and retry is within configured bounds"
            else:
                status = EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.ELIGIBLE
                next_eligible_at = evaluated_at + timedelta(seconds=policy.backoff_seconds)
                default_reason = "failure evaluation observed and retry is within configured bounds"
        elif evaluation.evaluation_status is EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationStatus.SUCCESS_EVALUATION:
            status = EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus.NOT_ELIGIBLE
            next_eligible_at = None
            default_reason = "successful evaluation does not automatically re-open retry eligibility"
        else:
            raise EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentError(
                "unsupported evaluation status"
            )

        return EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessment(
            assessment_id=assessment_id,
            evaluation_id=evaluation.evaluation_id,
            feedback_id=evaluation.feedback_id,
            outcome_id=evaluation.outcome_id,
            environment_id=evaluation.environment_id,
            expected_model_id=evaluation.expected_model_id,
            observed_model_id=evaluation.observed_model_id,
            evaluation_status=evaluation.evaluation_status,
            retry_count=state.retry_count,
            max_retries=policy.max_retries,
            evaluated_at=evaluated_at,
            next_eligible_at=next_eligible_at,
            status=status,
            reasons=reasons or {"status": default_reason},
            lineage=lineage
            or {
                "evaluation_id": evaluation.evaluation_id,
                "feedback_id": evaluation.feedback_id,
                "outcome_id": evaluation.outcome_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentError",
    "EnvironmentWorldModelRollbackRepairRetryReeligibilityPolicy",
    "EnvironmentWorldModelRollbackRepairRetryState",
    "EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentStatus",
    "EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessment",
    "EnvironmentWorldModelRollbackRepairRetryReeligibilityAssessmentService",
]
