from dataclasses import dataclass
from typing import Any

from src.core.execution_state import ExecutionOutput, ExecutionState


@dataclass(frozen=True)
class ExecutionProgress:
    """Immutable progress across multiple execution attempts for one goal."""

    goal: str
    states: tuple[ExecutionState, ...] = ()

    def __post_init__(self):
        if not isinstance(self.goal, str) or not self.goal.strip():
            raise ValueError("goal must be a non-empty string.")
        if not isinstance(self.states, tuple):
            raise TypeError("states must be a tuple.")
        for state in self.states:
            if not isinstance(state, ExecutionState):
                raise TypeError("states must contain ExecutionState values.")
            if state.goal != self.goal:
                raise ValueError("all execution states must belong to the same goal.")

    @classmethod
    def from_state(cls, state: ExecutionState) -> "ExecutionProgress":
        if not isinstance(state, ExecutionState):
            raise TypeError("state must be an ExecutionState.")
        return cls(goal=state.goal, states=(state,))

    @property
    def attempt_count(self) -> int:
        return len(self.states)

    @property
    def current(self) -> ExecutionState:
        if not self.states:
            raise ValueError("execution progress has no attempts.")
        return self.states[-1]

    def record(self, state: ExecutionState) -> "ExecutionProgress":
        if not isinstance(state, ExecutionState):
            raise TypeError("state must be an ExecutionState.")
        if state.goal != self.goal:
            raise ValueError("execution state goal does not match progress goal.")
        return ExecutionProgress(goal=self.goal, states=self.states + (state,))

    @property
    def completed_steps(self) -> tuple[str, ...]:
        """Return attempt-qualified completed step identifiers."""
        values: list[str] = []
        for state in self.states:
            values.extend(f"{state.plan_id}:{step_id}" for step_id in state.completed_steps)
        return tuple(dict.fromkeys(values))

    @property
    def available_outputs(self) -> tuple[ExecutionOutput, ...]:
        values: list[ExecutionOutput] = []
        for state in self.states:
            values.extend(state.available_outputs)
        return tuple(values)

    def to_context(self) -> dict[str, Any]:
        """Return a provider-neutral model context spanning all attempts."""
        return {
            "goal": self.goal,
            "attempt_count": self.attempt_count,
            "current": self.current.to_context(),
            "completed_steps_across_attempts": self.completed_steps,
            "available_outputs_across_attempts": tuple(
                {"step_id": item.step_id, "value": item.value}
                for item in self.available_outputs
            ),
            "unresolved_requirements": self.current.unresolved_requirements,
            "next_allowed_actions": self.current.next_allowed_actions,
            "attempts": tuple(state.to_context() for state in self.states),
        }
