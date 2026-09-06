"""M23.52: inert execution preparation / handoff for retry authorization v2.

Consumes one exact M23.50 authorization decision and one exact M23.51
authorization-decision integrity artifact. Produces provider-neutral immutable
handoff evidence without executing, scheduling, re-authorizing, or persisting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_authorization_decision_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2,
)
from src.core.environment_world_model_rollback_repair_retry_authorization_decision_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2,
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status,
)


class EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2Error(RuntimeError):
    """Raised when v2 retry execution preparation evidence is unsafe."""


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
class EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2:
    """Immutable, non-executing retry preparation / handoff evidence."""

    preparation_id: str
    decision_id: str
    integrity_id: str
    proposal_id: str
    assessment_id: str | None
    evaluation_id: str | None
    feedback_id: str | None
    outcome_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    requested_action: str
    decision: str
    assessment_status: str | None
    eligible: bool
    retry_count: int | None
    max_retries: int | None
    evaluated_at: datetime
    next_eligible_at: datetime | None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "preparation_id",
            "decision_id",
            "integrity_id",
            "proposal_id",
            "environment_id",
            "expected_model_id",
            "observed_model_id",
            "requested_action",
            "decision",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("assessment_id", "evaluation_id", "feedback_id", "outcome_id", "assessment_status"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if self.requested_action != "RETRY_REPAIR":
            raise ValueError("requested_action must be RETRY_REPAIR")
        if self.decision != "ACCEPT":
            raise ValueError("decision must be ACCEPT")
        if not isinstance(self.eligible, bool) or not self.eligible:
            raise ValueError("eligible must be True for retry execution preparation")
        for name in ("retry_count", "max_retries"):
            value = getattr(self, name)
            if value is not None:
                if isinstance(value, bool) or not isinstance(value, int):
                    raise TypeError(f"{name} must be an integer or None")
                if value < 0:
                    raise ValueError(f"{name} must be >= 0")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        _validate_aware_datetime(self.evaluated_at, "evaluated_at")
        if self.next_eligible_at is not None:
            _validate_aware_datetime(self.next_eligible_at, "next_eligible_at")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_non_executing(self) -> bool:
        return True

    @property
    def execution_started(self) -> bool:
        return False

    @property
    def grants_execution_authority(self) -> bool:
        return False

    @property
    def schedules_retry(self) -> bool:
        return False

    @property
    def reauthorizes_retry(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2Service:
    """Prepare an inert retry handoff from exact v2 authorization evidence."""

    def prepare(
        self,
        decision: EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2,
        integrity: EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2,
        *,
        preparation_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2:
        if type(decision) is not EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2:
            raise TypeError(
                "decision must be EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionV2"
            )
        if type(integrity) is not EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2:
            raise TypeError(
                "integrity must be EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2"
            )
        if not isinstance(preparation_id, str) or not preparation_id.strip():
            raise ValueError("preparation_id must be a non-empty string")
        if integrity.status is not EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionIntegrityV2Status.VALID:
            raise EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2Error(
                "authorization decision integrity must be VALID before retry execution preparation"
            )
        if decision.decision != "ACCEPT":
            raise EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2Error(
                "retry execution preparation requires an ACCEPT decision"
            )
        if decision.requested_action != "RETRY_REPAIR" or decision.eligible is not True:
            raise EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2Error(
                "retry execution preparation requires eligible RETRY_REPAIR evidence"
            )
        if integrity.proposal_id != decision.proposal_id or integrity.decision_id != decision.decision_id:
            raise EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2Error(
                "integrity artifact does not bind to the exact authorization decision"
            )
        return EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2(
            preparation_id=preparation_id,
            decision_id=decision.decision_id,
            integrity_id=integrity.integrity_id,
            proposal_id=decision.proposal_id,
            assessment_id=decision.assessment_id,
            evaluation_id=decision.evaluation_id,
            feedback_id=decision.feedback_id,
            outcome_id=decision.outcome_id,
            environment_id=decision.environment_id,
            expected_model_id=decision.expected_model_id,
            observed_model_id=decision.observed_model_id,
            requested_action=decision.requested_action,
            decision=decision.decision,
            assessment_status=decision.assessment_status,
            eligible=decision.eligible,
            retry_count=decision.retry_count,
            max_retries=decision.max_retries,
            evaluated_at=decision.evaluated_at,
            next_eligible_at=decision.next_eligible_at,
            reasons=reasons or {"status": "accepted retry authorization is prepared as inert handoff evidence"},
            lineage=lineage or {
                "decision_id": decision.decision_id,
                "integrity_id": integrity.integrity_id,
                "proposal_id": decision.proposal_id,
                "assessment_id": decision.assessment_id,
                "evaluation_id": decision.evaluation_id,
                "feedback_id": decision.feedback_id,
                "outcome_id": decision.outcome_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2",
    "EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2Error",
    "EnvironmentWorldModelRollbackRepairRetryExecutionPreparationV2Service",
]
