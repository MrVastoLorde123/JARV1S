"""M33: bounded orchestration over a verified WorkPlan.

Task orchestration tracks plan progression and deterministically selects the
next bounded work step. It does not authorize, invoke, execute, or verify
consequential actions. Execution remains downstream of the existing authority
and controlled-agency boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from .work_planning import WorkPlan, WorkPlanStep, next_ready_steps


class OrchestrationStatus(str, Enum):
    READY = "READY"
    ACTIVE = "ACTIVE"
    WAITING = "WAITING"
    BLOCKED = "BLOCKED"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class StepExecutionState(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class CoordinationAction(str, Enum):
    START_STEP = "START_STEP"
    WAIT = "WAIT"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class OrchestratedStep:
    """Immutable status for one planned step."""

    step_id: str
    state: StepExecutionState = StepExecutionState.PENDING
    message: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.step_id, str) or not self.step_id.strip():
            raise ValueError("step_id must be a non-empty string")
        if not isinstance(self.state, StepExecutionState):
            raise TypeError("state must be a StepExecutionState")
        if not isinstance(self.message, str):
            raise TypeError("message must be a string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class CoordinationDecision:
    """Read-only decision describing what orchestration should do next."""

    action: CoordinationAction
    step: WorkPlanStep | None = None
    reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.action, CoordinationAction):
            raise TypeError("action must be a CoordinationAction")
        if self.step is not None and not isinstance(self.step, WorkPlanStep):
            raise TypeError("step must be a WorkPlanStep or None")
        if not isinstance(self.reason, str):
            raise TypeError("reason must be a string")
        if self.action is CoordinationAction.START_STEP and self.step is None:
            raise ValueError("START_STEP requires a step")
        if self.action is not CoordinationAction.START_STEP and self.step is not None:
            raise ValueError("only START_STEP may include a step")


@dataclass(frozen=True)
class TaskOrchestration:
    """Immutable progression state for one WorkPlan."""

    plan: WorkPlan
    status: OrchestrationStatus
    steps: tuple[OrchestratedStep, ...]
    current_step_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.plan, WorkPlan):
            raise TypeError("plan must be a WorkPlan")
        if not isinstance(self.status, OrchestrationStatus):
            raise TypeError("status must be an OrchestrationStatus")
        if not isinstance(self.steps, tuple) or any(not isinstance(item, OrchestratedStep) for item in self.steps):
            raise TypeError("steps must be a tuple of OrchestratedStep values")
        plan_ids = tuple(step.step_id for step in self.plan.steps)
        state_ids = tuple(step.step_id for step in self.steps)
        if state_ids != plan_ids:
            raise ValueError("orchestration step state must match plan order exactly")
        if self.current_step_id is not None and self.current_step_id not in set(plan_ids):
            raise ValueError("current_step_id must refer to a plan step")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def completed_step_ids(self) -> tuple[str, ...]:
        return tuple(item.step_id for item in self.steps if item.state is StepExecutionState.COMPLETE)

    @property
    def terminal(self) -> bool:
        return self.status in {OrchestrationStatus.COMPLETE, OrchestrationStatus.FAILED}


def begin_task_orchestration(plan: WorkPlan) -> TaskOrchestration:
    """Create orchestration state without authorizing or executing a plan."""
    if not isinstance(plan, WorkPlan):
        raise TypeError("plan must be a WorkPlan")
    return TaskOrchestration(
        plan=plan,
        status=OrchestrationStatus.READY,
        steps=tuple(OrchestratedStep(step.step_id) for step in plan.steps),
        metadata={"source": "M33", "work_id": plan.work_id},
    )


def choose_next_coordination(orchestration: TaskOrchestration) -> CoordinationDecision:
    """Select the next bounded coordination action deterministically."""
    if orchestration.terminal:
        return CoordinationDecision(
            action=CoordinationAction.COMPLETE,
            reason="orchestration is terminal",
        )

    blocked = next((item for item in orchestration.steps if item.state is StepExecutionState.BLOCKED), None)
    if blocked is not None:
        return CoordinationDecision(
            action=CoordinationAction.BLOCKED,
            reason=blocked.message or f"step {blocked.step_id} is blocked",
        )

    failed = next((item for item in orchestration.steps if item.state is StepExecutionState.FAILED), None)
    if failed is not None:
        return CoordinationDecision(
            action=CoordinationAction.BLOCKED,
            reason=failed.message or f"step {failed.step_id} failed",
        )

    active = next((item for item in orchestration.steps if item.state is StepExecutionState.ACTIVE), None)
    if active is not None:
        return CoordinationDecision(action=CoordinationAction.WAIT, reason=f"step {active.step_id} is active")

    ready = next_ready_steps(orchestration.plan, orchestration.completed_step_ids)
    ready = tuple(step for step in ready if orchestration.steps[orchestration.plan.steps.index(step)].state is StepExecutionState.PENDING)
    if ready:
        return CoordinationDecision(
            action=CoordinationAction.START_STEP,
            step=ready[0],
            reason="deterministically selected first ready pending step",
        )

    if all(item.state is StepExecutionState.COMPLETE for item in orchestration.steps):
        return CoordinationDecision(action=CoordinationAction.COMPLETE, reason="all plan steps are complete")

    return CoordinationDecision(action=CoordinationAction.WAIT, reason="no step is currently ready")


def update_orchestration(
    orchestration: TaskOrchestration,
    step_id: str,
    state: StepExecutionState,
    *,
    message: str = "",
    metadata: Mapping[str, Any] | None = None,
) -> TaskOrchestration:
    """Apply a bounded step-state observation and derive the next status."""
    if not isinstance(orchestration, TaskOrchestration):
        raise TypeError("orchestration must be a TaskOrchestration")
    if not isinstance(step_id, str) or not step_id.strip():
        raise ValueError("step_id must be a non-empty string")
    if not isinstance(state, StepExecutionState):
        raise TypeError("state must be a StepExecutionState")
    if step_id not in {step.step_id for step in orchestration.plan.steps}:
        raise ValueError("step_id is not present in the plan")

    updated = []
    for item in orchestration.steps:
        if item.step_id == step_id:
            updated.append(OrchestratedStep(step_id, state, message, metadata or {}))
        else:
            updated.append(item)

    updated_tuple = tuple(updated)
    if any(item.state is StepExecutionState.FAILED for item in updated_tuple):
        status = OrchestrationStatus.FAILED
    elif any(item.state is StepExecutionState.BLOCKED for item in updated_tuple):
        status = OrchestrationStatus.BLOCKED
    elif all(item.state is StepExecutionState.COMPLETE for item in updated_tuple):
        status = OrchestrationStatus.COMPLETE
    elif any(item.state is StepExecutionState.ACTIVE for item in updated_tuple):
        status = OrchestrationStatus.ACTIVE
    else:
        status = OrchestrationStatus.READY

    current = step_id if state is StepExecutionState.ACTIVE else None
    return TaskOrchestration(
        plan=orchestration.plan,
        status=status,
        steps=updated_tuple,
        current_step_id=current,
        metadata=orchestration.metadata,
    )


__all__ = [
    "CoordinationAction",
    "CoordinationDecision",
    "OrchestratedStep",
    "OrchestrationStatus",
    "StepExecutionState",
    "TaskOrchestration",
    "begin_task_orchestration",
    "choose_next_coordination",
    "update_orchestration",
]
