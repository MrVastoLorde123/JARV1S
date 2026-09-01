from dataclasses import dataclass
from typing import Any

from src.core.execution_executor_models import PlanExecutionStatus
from src.core.execution_state import ExecutionOutput, ExecutionState


@dataclass(frozen=True)
class ExecutionAssessment:
    """Provider-neutral interpretation of one observed execution state."""

    goal: str
    situation: str
    completed: tuple[str, ...] = ()
    remaining: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    useful_outputs: tuple[ExecutionOutput, ...] = ()
    recommended_next_action: str | None = None
    confidence: float | None = None

    def __post_init__(self):
        if not isinstance(self.goal, str) or not self.goal.strip():
            raise ValueError("goal must be a non-empty string.")
        if not isinstance(self.situation, str) or not self.situation.strip():
            raise ValueError("situation must be a non-empty string.")
        for collection, name in (
            (self.completed, "completed"),
            (self.remaining, "remaining"),
            (self.blockers, "blockers"),
            (self.useful_outputs, "useful_outputs"),
        ):
            if not isinstance(collection, tuple):
                raise TypeError(f"{name} must be a tuple.")
        for value in (*self.completed, *self.remaining, *self.blockers):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("assessment entries must be non-empty strings.")
        for output in self.useful_outputs:
            if not isinstance(output, ExecutionOutput):
                raise TypeError("useful_outputs must contain ExecutionOutput values.")
        if self.recommended_next_action is not None:
            if not isinstance(self.recommended_next_action, str):
                raise TypeError("recommended_next_action must be a string or None.")
            if not self.recommended_next_action.strip():
                raise ValueError("recommended_next_action cannot be empty.")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0.")

    def to_context(self) -> dict[str, Any]:
        """Return a provider-neutral, model-friendly representation."""
        return {
            "goal": self.goal,
            "situation": self.situation,
            "completed": self.completed,
            "remaining": self.remaining,
            "blockers": self.blockers,
            "useful_outputs": tuple(
                {"step_id": output.step_id, "value": output.value}
                for output in self.useful_outputs
            ),
            "recommended_next_action": self.recommended_next_action,
            "confidence": self.confidence,
        }


class ExecutionAssessmentService:
    """Deterministically interpret verified execution state without model inference."""

    def assess(self, state: ExecutionState) -> ExecutionAssessment:
        if not isinstance(state, ExecutionState):
            raise TypeError("state must be an ExecutionState.")

        if state.status == PlanExecutionStatus.COMPLETED:
            return ExecutionAssessment(
                goal=state.goal,
                situation="objective_completed",
                completed=state.completed_steps,
                useful_outputs=state.available_outputs,
                recommended_next_action=None,
            )

        if state.status in (PlanExecutionStatus.FAILED, PlanExecutionStatus.BLOCKED):
            return ExecutionAssessment(
                goal=state.goal,
                situation="blocked",
                completed=state.completed_steps,
                remaining=state.unresolved_requirements,
                blockers=state.unresolved_requirements,
                useful_outputs=state.available_outputs,
                recommended_next_action=(
                    "CORRECT" if "CORRECT" in state.next_allowed_actions else None
                ),
            )

        return ExecutionAssessment(
            goal=state.goal,
            situation="no_progress",
            completed=state.completed_steps,
            remaining=state.unresolved_requirements,
            blockers=state.unresolved_requirements,
            useful_outputs=state.available_outputs,
            recommended_next_action=(
                state.next_allowed_actions[0] if state.next_allowed_actions else None
            ),
        )
