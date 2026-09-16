"""M34: bounded dispatch from planned work steps to worker assignments.

Dispatch translates one already-selected WorkPlanStep into a concrete,
bounded WorkerAssignment accepted by the existing workforce registry. It does
not authorize, invoke, execute, or verify consequential work.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .work_planning import WorkPlan, WorkPlanStep
from .workforce import WorkerAssignment, WorkerRegistry


@dataclass(frozen=True)
class DispatchRequest:
    """Immutable request to bind one planned step to one worker definition."""

    plan: WorkPlan
    step_id: str
    worker_id: str
    input_scope: tuple[str, ...] = ()
    output_scope: tuple[str, ...] = ()
    max_steps: int = 1
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.plan, WorkPlan):
            raise TypeError("plan must be a WorkPlan")
        if not isinstance(self.step_id, str) or not self.step_id.strip():
            raise ValueError("step_id must be a non-empty string")
        if self.step_id not in {step.step_id for step in self.plan.steps}:
            raise ValueError("step_id is not present in the plan")
        if not isinstance(self.worker_id, str) or not self.worker_id.strip():
            raise ValueError("worker_id must be a non-empty string")
        for name, values in (("input_scope", self.input_scope), ("output_scope", self.output_scope)):
            if not isinstance(values, tuple) or any(not isinstance(item, str) or not item.strip() for item in values):
                raise TypeError(f"{name} must be a tuple of non-empty strings")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must be unique")
        if not isinstance(self.max_steps, int) or isinstance(self.max_steps, bool) or self.max_steps <= 0:
            raise ValueError("max_steps must be a positive integer")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class DispatchResult:
    """Immutable binding result; assignment remains non-authorizing."""

    plan_id: str
    step: WorkPlanStep
    assignment: WorkerAssignment
    worker_id: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.plan_id, str) or not self.plan_id.strip():
            raise ValueError("plan_id must be a non-empty string")
        if not isinstance(self.step, WorkPlanStep):
            raise TypeError("step must be a WorkPlanStep")
        if not isinstance(self.assignment, WorkerAssignment):
            raise TypeError("assignment must be a WorkerAssignment")
        if self.assignment.worker_id != self.worker_id:
            raise ValueError("worker_id must match assignment worker_id")
        if self.assignment.objective != self.step.title:
            raise ValueError("assignment objective must match step title")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "step_id": self.step.step_id,
            "worker_id": self.worker_id,
            "assignment": self.assignment.to_context(),
            "metadata": dict(self.metadata),
            "authorization_granted": False,
            "execution_requested": False,
        }


class WorkDispatcher:
    """Bind planned steps to bounded workers through the existing registry."""

    def __init__(self, registry: WorkerRegistry) -> None:
        if not isinstance(registry, WorkerRegistry):
            raise TypeError("registry must be a WorkerRegistry")
        self._registry = registry

    def dispatch(self, request: DispatchRequest) -> DispatchResult:
        if not isinstance(request, DispatchRequest):
            raise TypeError("request must be a DispatchRequest")
        step = next(item for item in request.plan.steps if item.step_id == request.step_id)
        missing = tuple(capability for capability in step.requires_capabilities if capability not in self._registry.get(request.worker_id).capabilities)
        if missing:
            raise ValueError(f"worker {request.worker_id} lacks required capabilities: {missing}")
        assignment = WorkerAssignment(
            assignment_id=f"{request.plan.work_id}:{request.step_id}",
            worker_id=request.worker_id,
            objective=step.title,
            allowed_capabilities=step.requires_capabilities,
            input_scope=request.input_scope,
            output_scope=request.output_scope,
            max_steps=request.max_steps,
            metadata={"plan_id": request.plan.work_id, "step_id": step.step_id, **dict(request.metadata)},
        )
        self._registry.validate_assignment(assignment)
        return DispatchResult(
            plan_id=request.plan.work_id,
            step=step,
            assignment=assignment,
            worker_id=request.worker_id,
            metadata={"source": "M34"},
        )


__all__ = ["DispatchRequest", "DispatchResult", "WorkDispatcher"]
