from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StepExecutionStatus(str, Enum):
    """
    Result state of an executed plan step.
    """

    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PlanExecutionStatus(str, Enum):
    """
    Result state of an execution attempt.
    """

    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class StepExecutionResult:
    """
    Result produced after attempting one PlanStep.
    """

    step_id: str

    action: str

    status: StepExecutionStatus

    output: Any = None

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self):

        if not isinstance(
            self.step_id,
            str,
        ):
            raise TypeError(
                "step_id must be a string."
            )

        if not self.step_id.strip():
            raise ValueError(
                "step_id cannot be empty."
            )

        if not isinstance(
            self.action,
            str,
        ):
            raise TypeError(
                "action must be a string."
            )

        if not self.action.strip():
            raise ValueError(
                "action cannot be empty."
            )

        if not isinstance(
            self.status,
            StepExecutionStatus,
        ):
            raise TypeError(
                "status must be a StepExecutionStatus."
            )

        if (
            self.status
            == StepExecutionStatus.FAILED
            and not self.error
        ):
            raise ValueError(
                "Failed step results require an error."
            )

        if (
            self.status
            == StepExecutionStatus.COMPLETED
            and self.error is not None
        ):
            raise ValueError(
                "Completed step results cannot contain an error."
            )


@dataclass(frozen=True)
class PlanExecutionResult:
    """
    Result produced after attempting an ExecutionPlan.
    """

    plan_id: str

    status: PlanExecutionStatus

    steps: tuple[StepExecutionResult, ...]

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def success(self) -> bool:
        return (
            self.status
            == PlanExecutionStatus.COMPLETED
        )

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def failed_steps(self) -> tuple[StepExecutionResult, ...]:
        return tuple(
            step
            for step in self.steps
            if step.status
            == StepExecutionStatus.FAILED
        )