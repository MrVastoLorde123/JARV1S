"""M40: aggregate the existing agency lifecycle contracts without new authority.

This module provides an immutable read model over WorkState, WorkPlan,
TaskOrchestration, and optional recovery reconciliation. It joins identities
for inspection while leaving each underlying contract authoritative.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .recovery_state import RecoveryReconciliation
from .task_orchestration import TaskOrchestration
from .work_planning import WorkPlan
from .work_state import WorkState


@dataclass(frozen=True)
class AgencyLifecycleState:
    """Immutable aggregate read model for one bounded agency lifecycle."""

    work: WorkState
    plan: WorkPlan
    orchestration: TaskOrchestration
    recovery: RecoveryReconciliation | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.work, WorkState):
            raise TypeError("work must be a WorkState")
        if not isinstance(self.plan, WorkPlan):
            raise TypeError("plan must be a WorkPlan")
        if not isinstance(self.orchestration, TaskOrchestration):
            raise TypeError("orchestration must be a TaskOrchestration")
        if self.orchestration.plan != self.plan:
            raise ValueError("orchestration/plan identity mismatch")
        if self.plan.work_id != self.work.work_id:
            raise ValueError("plan/work identity mismatch")
        if self.recovery is not None:
            if not isinstance(self.recovery, RecoveryReconciliation):
                raise TypeError("recovery must be a RecoveryReconciliation or None")
            if self.recovery.work_id != self.work.work_id:
                raise ValueError("recovery/work identity mismatch")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def terminal(self) -> bool:
        return self.work.is_terminal and self.orchestration.terminal

    @property
    def blocked(self) -> bool:
        return self.work.is_blocked or self.orchestration.status.value == "BLOCKED"

    @property
    def current_step_id(self) -> str | None:
        return self.orchestration.current_step_id

    @property
    def authorization_granted(self) -> bool:
        return False

    @property
    def execution_requested(self) -> bool:
        return False

    def to_context(self) -> dict[str, Any]:
        return {
            "work_id": self.work.work_id,
            "objective": self.work.objective,
            "work_stage": self.work.stage.value,
            "work_status": self.work.status.value,
            "plan_work_id": self.plan.work_id,
            "orchestration_status": self.orchestration.status.value,
            "current_step_id": self.orchestration.current_step_id,
            "completed_step_ids": self.orchestration.completed_step_ids,
            "terminal": self.terminal,
            "blocked": self.blocked,
            "recovery": None if self.recovery is None else self.recovery.to_context(),
            "metadata": dict(self.metadata),
            "authorization_granted": False,
            "execution_requested": False,
        }


def build_agency_lifecycle_state(
    work: WorkState,
    plan: WorkPlan,
    orchestration: TaskOrchestration,
    *,
    recovery: RecoveryReconciliation | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> AgencyLifecycleState:
    """Join existing agency contracts into one immutable observational state."""
    return AgencyLifecycleState(
        work=work,
        plan=plan,
        orchestration=orchestration,
        recovery=recovery,
        metadata=metadata or {"source": "M40"},
    )


__all__ = ["AgencyLifecycleState", "build_agency_lifecycle_state"]
