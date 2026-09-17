"""M58: bind authorized execution verification to the existing M38 recovery boundary.

M57 binds an externally produced verification decision to the exact M56
execution outcome. M58 derives the existing bounded M38 recovery decision from
that verified lineage without authorizing, executing, verifying, or creating an
execution request.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .authorized_execution_verification import AuthorizedExecutionVerification
from .driveability import ContinuationCycle, Objective
from .verification_recovery import RecoveryDecision, derive_recovery_decision


@dataclass(frozen=True)
class AuthorizedExecutionRecovery:
    """Immutable recovery result bound to one exact authorized verification."""

    authorized_verification: AuthorizedExecutionVerification
    objective: Objective
    cycle: ContinuationCycle
    recovery: RecoveryDecision
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.authorized_verification, AuthorizedExecutionVerification):
            raise TypeError("authorized_verification must be an AuthorizedExecutionVerification")
        if not isinstance(self.objective, Objective):
            raise TypeError("objective must be an Objective")
        if not isinstance(self.cycle, ContinuationCycle):
            raise TypeError("cycle must be a ContinuationCycle")
        if not isinstance(self.recovery, RecoveryDecision):
            raise TypeError("recovery must be a RecoveryDecision")
        if self.cycle.objective_id != self.objective.objective_id:
            raise ValueError("recovery cycle must reference the supplied objective")
        if self.recovery.execution_id != self.authorized_verification.execution_id:
            raise ValueError("recovery execution identity must match the authorized verification")
        if self.recovery.continuation.objective.objective_id != self.objective.objective_id:
            raise ValueError("recovery continuation must reference the supplied objective")
        if self.recovery.continuation.cycle.cycle_id != self.cycle.cycle_id:
            raise ValueError("recovery continuation must reference the supplied cycle")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def execution_id(self) -> str:
        return self.authorized_verification.execution_id

    @property
    def authorization_id(self) -> str:
        return self.authorized_verification.authorization_id

    @property
    def disposition(self):
        return self.recovery.disposition

    @property
    def execution_requested(self) -> bool:
        return self.recovery.execution_requested

    def to_context(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "execution_id": self.execution_id,
            "verification_disposition": self.authorized_verification.disposition.value,
            "evidence_id": self.authorized_verification.evidence_id,
            "objective": self.objective.to_context(),
            "cycle": self.cycle.to_context(),
            "recovery": self.recovery.to_context(),
            "metadata": dict(self.metadata),
            "authorization_created": False,
            "execution_requested": False,
            "execution_performed": False,
            "verification_performed": False,
        }


def build_authorized_execution_recovery(
    authorized_verification: AuthorizedExecutionVerification,
    objective: Objective,
    cycle: ContinuationCycle,
    *,
    observation_ids: tuple[str, ...] = (),
    next_step: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> AuthorizedExecutionRecovery:
    """Derive one existing M38 recovery decision from exact M57 verification."""
    if not isinstance(authorized_verification, AuthorizedExecutionVerification):
        raise TypeError("authorized_verification must be an AuthorizedExecutionVerification")
    if not isinstance(objective, Objective):
        raise TypeError("objective must be an Objective")
    if not isinstance(cycle, ContinuationCycle):
        raise TypeError("cycle must be a ContinuationCycle")
    recovery = derive_recovery_decision(
        authorized_verification.verification,
        objective,
        cycle,
        observation_ids=observation_ids,
        next_step=next_step,
    )
    return AuthorizedExecutionRecovery(
        authorized_verification=authorized_verification,
        objective=objective,
        cycle=cycle,
        recovery=recovery,
        metadata=metadata or {},
    )


__all__ = ["AuthorizedExecutionRecovery", "build_authorized_execution_recovery"]
