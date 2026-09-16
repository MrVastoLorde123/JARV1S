"""M32: bounded planning contract over Work State.

Planning proposes an ordered set of bounded work steps. It does not authorize,
execute, verify, or mutate the environment. Each consequential execution must
still re-enter the existing deterministic authority boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from .work_state import WorkRole, WorkStage, WorkState


class PlanStepKind(str, Enum):
    RESEARCH = "RESEARCH"
    ANALYZE = "ANALYZE"
    IMPLEMENT = "IMPLEMENT"
    VERIFY = "VERIFY"
    REVIEW = "REVIEW"
    COORDINATE = "COORDINATE"


@dataclass(frozen=True)
class WorkPlanStep:
    step_id: str
    title: str
    kind: PlanStepKind
    role: WorkRole
    requires_capabilities: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("step_id", "title"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.kind, PlanStepKind):
            raise TypeError("kind must be a PlanStepKind")
        if not isinstance(self.role, WorkRole):
            raise TypeError("role must be a WorkRole")
        for name, values in (("requires_capabilities", self.requires_capabilities), ("depends_on", self.depends_on)):
            if not isinstance(values, tuple) or any(not isinstance(item, str) or not item.strip() for item in values):
                raise TypeError(f"{name} must be a tuple of non-empty strings")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must be unique")
        if self.step_id in self.depends_on:
            raise ValueError("step cannot depend on itself")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class WorkPlan:
    work_id: str
    objective: str
    stage: WorkStage
    role: WorkRole
    steps: tuple[WorkPlanStep, ...]
    rationale: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.work_id, str) or not self.work_id.strip():
            raise ValueError("work_id must be a non-empty string")
        if not isinstance(self.objective, str) or not self.objective.strip():
            raise ValueError("objective must be a non-empty string")
        if not isinstance(self.stage, WorkStage):
            raise TypeError("stage must be a WorkStage")
        if not isinstance(self.role, WorkRole):
            raise TypeError("role must be a WorkRole")
        if not isinstance(self.steps, tuple) or any(not isinstance(item, WorkPlanStep) for item in self.steps):
            raise TypeError("steps must be a tuple of WorkPlanStep values")
        if len(self.steps) > 64:
            raise ValueError("work plan cannot exceed 64 steps")
        ids = tuple(step.step_id for step in self.steps)
        if len(set(ids)) != len(ids):
            raise ValueError("work plan step IDs must be unique")
        step_ids = set(ids)
        for step in self.steps:
            unknown = set(step.depends_on) - step_ids
            if unknown:
                raise ValueError(f"step {step.step_id} depends on unknown steps: {sorted(unknown)}")
        if not isinstance(self.rationale, str):
            raise TypeError("rationale must be a string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def is_empty(self) -> bool:
        return not self.steps


def build_work_plan(work: WorkState, steps: tuple[WorkPlanStep, ...], *, rationale: str = "") -> WorkPlan:
    """Create a plan anchored to the supplied immutable Work State."""
    if type(work) is not WorkState:
        raise TypeError("work must be a WorkState")
    role = work.role
    if role is WorkRole.GENERAL and steps:
        role = steps[0].role
    return WorkPlan(
        work_id=work.work_id,
        objective=work.objective,
        stage=work.stage,
        role=role,
        steps=tuple(steps),
        rationale=rationale,
        metadata={
            "source": work.source,
            "evidence_cursor": work.evidence_cursor,
            "required_capabilities": work.required_capabilities,
        },
    )


def next_ready_steps(plan: WorkPlan, completed_step_ids: tuple[str, ...] = ()) -> tuple[WorkPlanStep, ...]:
    """Return deterministic ready steps without executing anything."""
    completed = set(completed_step_ids)
    if any(step_id not in {step.step_id for step in plan.steps} for step_id in completed):
        raise ValueError("completed_step_ids contains an unknown step")
    return tuple(
        step for step in plan.steps
        if step.step_id not in completed and set(step.depends_on).issubset(completed)
    )


__all__ = ["PlanStepKind", "WorkPlanStep", "WorkPlan", "build_work_plan", "next_ready_steps"]
