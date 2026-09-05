"""M23.42: inert execution preparation / handoff for rollback-repair retry.

This boundary consumes exact, integrity-verified retry authorization evidence and
produces a provider-neutral immutable preparation artifact. It does not execute,
schedule, re-authorize, mutate persistence, or select a worker.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_authorization_decision import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision,
)
from src.core.environment_world_model_rollback_repair_retry_authorization_integrity import (
    EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrity,
)


class EnvironmentWorldModelRollbackRepairRetryExecutionPreparationError(RuntimeError):
    """Raised when retry execution preparation evidence is structurally invalid."""


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
class EnvironmentWorldModelRollbackRepairRetryExecutionPreparation:
    """Immutable, non-executing retry preparation / handoff evidence."""

    preparation_id: str
    environment_id: str
    authorization_decision_id: str
    authorization_integrity_id: str
    proposal_id: str
    eligibility_id: str
    action_decision_id: str
    expected_model_id: str
    observed_model_id: str
    requested_action: str
    decision: str
    eligible: bool
    evaluated_at: datetime
    next_eligible_at: datetime | None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "preparation_id",
            "environment_id",
            "authorization_decision_id",
            "authorization_integrity_id",
            "proposal_id",
            "eligibility_id",
            "action_decision_id",
            "expected_model_id",
            "observed_model_id",
            "requested_action",
            "decision",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.requested_action != "RETRY_REPAIR":
            raise ValueError("requested_action must be RETRY_REPAIR")
        if self.decision != "ACCEPT":
            raise ValueError("decision must be ACCEPT")
        if not isinstance(self.eligible, bool):
            raise TypeError("eligible must be a boolean")
        if not self.eligible:
            raise ValueError("eligible must be True for retry execution preparation")
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
    def authorizes_retry(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryExecutionPreparationService:
    """Prepare an inert retry handoff from exact authorization evidence."""

    def prepare(
        self,
        decision: EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision,
        integrity: EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrity,
        *,
        preparation_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryExecutionPreparation:
        if type(decision) is not EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision:
            raise TypeError(
                "decision must be EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision"
            )
        if type(integrity) is not EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrity:
            raise TypeError(
                "integrity must be EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrity"
            )
        if not isinstance(preparation_id, str) or not preparation_id.strip():
            raise ValueError("preparation_id must be a non-empty string")
        if integrity.integrity_status != "VALID":
            raise EnvironmentWorldModelRollbackRepairRetryExecutionPreparationError(
                "authorization integrity must be VALID before retry execution preparation"
            )
        if decision.decision != "ACCEPT":
            raise EnvironmentWorldModelRollbackRepairRetryExecutionPreparationError(
                "retry execution preparation requires an ACCEPT decision"
            )
        if decision.requested_action != "RETRY_REPAIR":
            raise EnvironmentWorldModelRollbackRepairRetryExecutionPreparationError(
                "retry execution preparation requires RETRY_REPAIR"
            )
        if not decision.eligible:
            raise EnvironmentWorldModelRollbackRepairRetryExecutionPreparationError(
                "retry execution preparation requires eligible retry evidence"
            )

        identities_match = (
            integrity.authorization_decision_id == decision.decision_id
            and integrity.environment_id == decision.environment_id
            and integrity.proposal_id == decision.proposal_id
            and integrity.eligibility_id == decision.eligibility_id
            and integrity.action_decision_id == decision.action_decision_id
            and integrity.requested_action == decision.requested_action
            and integrity.decision == decision.decision
            and integrity.proposal_eligible == decision.eligible
        )
        if not identities_match:
            raise EnvironmentWorldModelRollbackRepairRetryExecutionPreparationError(
                "authorization integrity does not bind to the exact accepted retry decision"
            )

        return EnvironmentWorldModelRollbackRepairRetryExecutionPreparation(
            preparation_id=preparation_id,
            environment_id=decision.environment_id,
            authorization_decision_id=decision.decision_id,
            authorization_integrity_id=integrity.integrity_id,
            proposal_id=decision.proposal_id,
            eligibility_id=decision.eligibility_id,
            action_decision_id=decision.action_decision_id,
            expected_model_id=decision.expected_model_id,
            observed_model_id=decision.observed_model_id,
            requested_action=decision.requested_action,
            decision=decision.decision,
            eligible=decision.eligible,
            evaluated_at=decision.evaluated_at,
            next_eligible_at=decision.next_eligible_at,
            reasons=reasons or {
                "status": "accepted retry authorization is prepared as inert handoff evidence"
            },
            lineage=lineage
            or {
                "authorization_decision_id": decision.decision_id,
                "authorization_integrity_id": integrity.integrity_id,
                "proposal_id": decision.proposal_id,
                "eligibility_id": decision.eligibility_id,
                "action_decision_id": decision.action_decision_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryExecutionPreparation",
    "EnvironmentWorldModelRollbackRepairRetryExecutionPreparationError",
    "EnvironmentWorldModelRollbackRepairRetryExecutionPreparationService",
]
