"""M41: integrate the existing V6 agency lifecycle contracts for inspection.

This module joins already-authoritative contracts from planning through
execution observation, verification, recovery, and work-state reconciliation.
It creates no new authority, execution, verification, persistence, or provider
selection surface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .execution_bridge import AgencyExecutionBridgeResult
from .execution_handoff import ExecutionHandoff
from .execution_outcome import AgencyExecutionOutcome, VerificationDecision
from .lifecycle_state import AgencyLifecycleState
from .recovery_state import RecoveryReconciliation
from .verification_recovery import RecoveryDecision


@dataclass(frozen=True)
class AgencyLifecycleIntegration:
    """Immutable end-to-end read model for one V6 agency lifecycle."""

    lifecycle: AgencyLifecycleState
    handoff: ExecutionHandoff | None = None
    execution: AgencyExecutionBridgeResult | None = None
    outcome: AgencyExecutionOutcome | None = None
    verification: VerificationDecision | None = None
    recovery_decision: RecoveryDecision | None = None
    recovery: RecoveryReconciliation | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.lifecycle, AgencyLifecycleState):
            raise TypeError("lifecycle must be an AgencyLifecycleState")
        values = {
            "handoff": (ExecutionHandoff, self.handoff),
            "execution": (AgencyExecutionBridgeResult, self.execution),
            "outcome": (AgencyExecutionOutcome, self.outcome),
            "verification": (VerificationDecision, self.verification),
            "recovery_decision": (RecoveryDecision, self.recovery_decision),
            "recovery": (RecoveryReconciliation, self.recovery),
        }
        for name, (expected, value) in values.items():
            if value is not None and not isinstance(value, expected):
                raise TypeError(f"{name} has an invalid type")

        work_id = self.lifecycle.work.work_id
        if self.recovery is not None and self.recovery.work_id != work_id:
            raise ValueError("recovery/work identity mismatch")
        if self.recovery_decision is not None:
            if self.recovery_decision.execution_id != self.execution_id:
                raise ValueError("recovery decision/execution identity mismatch")
        if self.verification is not None and self.verification.execution_id != self.execution_id:
            raise ValueError("verification/execution identity mismatch")
        if self.outcome is not None and self.outcome.execution_id != self.execution_id:
            raise ValueError("outcome/execution identity mismatch")
        if self.execution is not None and self.execution.execution_id != self.execution_id:
            raise ValueError("execution bridge identity mismatch")
        if self.handoff is not None and self.execution_id != self.handoff.execution_id:
            raise ValueError("handoff/execution identity mismatch")
        if self.recovery is not None and self.recovery.execution_id != self.execution_id:
            raise ValueError("reconciliation/execution identity mismatch")
        if self.recovery_decision is not None and self.recovery is not None:
            if self.recovery.decision != self.recovery_decision:
                raise ValueError("reconciliation/recovery decision mismatch")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def execution_id(self) -> str | None:
        for value in (self.handoff, self.execution, self.outcome, self.verification, self.recovery_decision, self.recovery):
            if value is None:
                continue
            if hasattr(value, "execution_id"):
                return value.execution_id
        return None

    @property
    def terminal(self) -> bool:
        return self.lifecycle.terminal or bool(self.recovery and self.recovery.after.is_terminal)

    @property
    def blocked(self) -> bool:
        return self.lifecycle.blocked or bool(self.recovery and self.recovery.after.is_blocked)

    @property
    def authorization_granted(self) -> bool:
        return False

    @property
    def execution_requested(self) -> bool:
        return False

    def to_context(self) -> dict[str, Any]:
        return {
            "work_id": self.lifecycle.work.work_id,
            "execution_id": self.execution_id,
            "work_stage": self.lifecycle.work.stage.value,
            "work_status": self.lifecycle.work.status.value,
            "plan_work_id": self.lifecycle.plan.work_id,
            "orchestration_status": self.lifecycle.orchestration.status.value,
            "handoff_present": self.handoff is not None,
            "execution_present": self.execution is not None,
            "outcome_present": self.outcome is not None,
            "verification_present": self.verification is not None,
            "recovery_decision_present": self.recovery_decision is not None,
            "recovery_reconciliation_present": self.recovery is not None,
            "terminal": self.terminal,
            "blocked": self.blocked,
            "metadata": dict(self.metadata),
            "authorization_granted": False,
            "execution_requested": False,
        }


def build_agency_lifecycle_integration(
    lifecycle: AgencyLifecycleState,
    *,
    handoff: ExecutionHandoff | None = None,
    execution: AgencyExecutionBridgeResult | None = None,
    outcome: AgencyExecutionOutcome | None = None,
    verification: VerificationDecision | None = None,
    recovery_decision: RecoveryDecision | None = None,
    recovery: RecoveryReconciliation | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> AgencyLifecycleIntegration:
    """Join existing lifecycle contracts into one observational integration record."""
    return AgencyLifecycleIntegration(
        lifecycle=lifecycle,
        handoff=handoff,
        execution=execution,
        outcome=outcome,
        verification=verification,
        recovery_decision=recovery_decision,
        recovery=recovery,
        metadata=metadata or {"source": "M41"},
    )


__all__ = ["AgencyLifecycleIntegration", "build_agency_lifecycle_integration"]
