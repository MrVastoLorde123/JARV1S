"""M59: bind the exact M58 recovery result to the existing M39 reconciliation boundary.

M58 derives bounded recovery from externally verified execution. M59 applies
that exact recovery decision through the existing M39 reconciliation contract.
It does not create authority, request or perform execution, verify outcomes,
or redefine recovery policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .authorized_execution_recovery import AuthorizedExecutionRecovery
from .recovery_state import RecoveryReconciliation, reconcile_recovery
from .work_state import WorkState


@dataclass(frozen=True)
class AuthorizedExecutionReconciliation:
    """Immutable reconciliation result bound to one exact authorized recovery."""

    authorized_recovery: AuthorizedExecutionRecovery
    work_state: WorkState
    reconciliation: RecoveryReconciliation
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.authorized_recovery, AuthorizedExecutionRecovery):
            raise TypeError("authorized_recovery must be an AuthorizedExecutionRecovery")
        if not isinstance(self.work_state, WorkState):
            raise TypeError("work_state must be a WorkState")
        if not isinstance(self.reconciliation, RecoveryReconciliation):
            raise TypeError("reconciliation must be a RecoveryReconciliation")
        recovery = self.authorized_recovery.recovery
        if self.reconciliation.decision != recovery:
            raise ValueError("reconciliation must reference the exact M38 recovery decision")
        if self.reconciliation.execution_id != self.authorized_recovery.execution_id:
            raise ValueError("reconciliation execution identity must match the authorized recovery")
        if self.reconciliation.work_id != self.work_state.work_id:
            raise ValueError("reconciliation work identity must match the supplied work state")
        if self.reconciliation.before != self.work_state:
            raise ValueError("reconciliation before-state must match the supplied work state")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def execution_id(self) -> str:
        return self.authorized_recovery.execution_id

    @property
    def authorization_id(self) -> str:
        return self.authorized_recovery.authorization_id

    @property
    def work_id(self) -> str:
        return self.work_state.work_id

    @property
    def disposition(self):
        return self.reconciliation.disposition

    def to_context(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "execution_id": self.execution_id,
            "work_id": self.work_id,
            "recovery": self.authorized_recovery.to_context(),
            "reconciliation": self.reconciliation.to_context(),
            "metadata": dict(self.metadata),
            "authorization_created": False,
            "execution_requested": False,
            "execution_performed": False,
            "verification_performed": False,
        }


def build_authorized_execution_reconciliation(
    authorized_recovery: AuthorizedExecutionRecovery,
    work_state: WorkState,
    *,
    metadata: Mapping[str, Any] | None = None,
) -> AuthorizedExecutionReconciliation:
    """Apply one exact M58 recovery result through the existing M39 reconciler."""
    if not isinstance(authorized_recovery, AuthorizedExecutionRecovery):
        raise TypeError("authorized_recovery must be an AuthorizedExecutionRecovery")
    if not isinstance(work_state, WorkState):
        raise TypeError("work_state must be a WorkState")
    reconciliation = reconcile_recovery(work_state, authorized_recovery.recovery)
    return AuthorizedExecutionReconciliation(
        authorized_recovery=authorized_recovery,
        work_state=work_state,
        reconciliation=reconciliation,
        metadata=metadata or {},
    )


__all__ = ["AuthorizedExecutionReconciliation", "build_authorized_execution_reconciliation"]
