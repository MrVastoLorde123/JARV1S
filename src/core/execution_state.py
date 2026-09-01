from dataclasses import dataclass, field
from typing import Any

from src.core.execution_executor_models import (
    PlanExecutionResult,
    PlanExecutionStatus,
    StepExecutionStatus,
)


@dataclass(frozen=True)
class ExecutionOutput:
    """Provider-neutral output captured from one completed execution step."""

    step_id: str
    value: Any


@dataclass(frozen=True)
class ExecutionState:
    """Immutable state derived from one execution observation."""

    goal: str
    plan_id: str
    status: PlanExecutionStatus
    completed_steps: tuple[str, ...] = ()
    failed_steps: tuple[str, ...] = ()
    available_outputs: tuple[ExecutionOutput, ...] = ()
    unresolved_requirements: tuple[str, ...] = ()
    next_allowed_actions: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.goal, str) or not self.goal.strip():
            raise ValueError("goal must be a non-empty string.")
        if not isinstance(self.plan_id, str) or not self.plan_id.strip():
            raise ValueError("plan_id must be a non-empty string.")
        if not isinstance(self.status, PlanExecutionStatus):
            raise TypeError("status must be a PlanExecutionStatus.")
        if not isinstance(self.completed_steps, tuple):
            raise TypeError("completed_steps must be a tuple.")
        if not isinstance(self.failed_steps, tuple):
            raise TypeError("failed_steps must be a tuple.")
        if not isinstance(self.available_outputs, tuple):
            raise TypeError("available_outputs must be a tuple.")
        if not isinstance(self.unresolved_requirements, tuple):
            raise TypeError("unresolved_requirements must be a tuple.")
        if not isinstance(self.next_allowed_actions, tuple):
            raise TypeError("next_allowed_actions must be a tuple.")

        for step_id in (*self.completed_steps, *self.failed_steps):
            if not isinstance(step_id, str) or not step_id.strip():
                raise ValueError("step ids must be non-empty strings.")
        for output in self.available_outputs:
            if not isinstance(output, ExecutionOutput):
                raise TypeError("available_outputs must contain ExecutionOutput values.")
        for value in (*self.unresolved_requirements, *self.next_allowed_actions):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("state entries must be non-empty strings.")

    @classmethod
    def from_execution(
        cls,
        goal: str,
        execution: PlanExecutionResult,
    ) -> "ExecutionState":
        if not isinstance(execution, PlanExecutionResult):
            raise TypeError("execution must be a PlanExecutionResult.")

        completed_steps = tuple(
            step.step_id
            for step in execution.steps
            if step.status == StepExecutionStatus.COMPLETED
        )
        failed_steps = tuple(
            step.step_id
            for step in execution.steps
            if step.status == StepExecutionStatus.FAILED
        )
        available_outputs = tuple(
            ExecutionOutput(step.step_id, step.output)
            for step in execution.steps
            if step.status == StepExecutionStatus.COMPLETED
            and step.output is not None
        )

        unresolved: tuple[str, ...]
        if execution.success:
            unresolved = ()
        else:
            requirements = []
            for step in execution.failed_steps:
                requirements.append(
                    f"Resolve failed step '{step.step_id}': {step.error}"
                )
            unresolved = tuple(requirements)

        if execution.status == PlanExecutionStatus.COMPLETED:
            next_actions = ("COMPLETE",)
        elif execution.status == PlanExecutionStatus.FAILED:
            next_actions = ("CORRECT", "STOP")
        else:
            next_actions = ("STOP",)

        return cls(
            goal=goal,
            plan_id=execution.plan_id,
            status=execution.status,
            completed_steps=completed_steps,
            failed_steps=failed_steps,
            available_outputs=available_outputs,
            unresolved_requirements=unresolved,
            next_allowed_actions=next_actions,
            metadata=dict(execution.metadata),
        )

    def to_context(self) -> dict[str, Any]:
        """Return a provider-neutral, model-friendly representation of the state."""
        return {
            "goal": self.goal,
            "plan_id": self.plan_id,
            "status": self.status.value,
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps,
            "available_outputs": tuple(
                {"step_id": item.step_id, "value": item.value}
                for item in self.available_outputs
            ),
            "unresolved_requirements": self.unresolved_requirements,
            "next_allowed_actions": self.next_allowed_actions,
        }
