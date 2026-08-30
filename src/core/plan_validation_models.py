from dataclasses import dataclass, field
from typing import Any

from src.core.execution_plan_models import (
    ExecutionPlan,
)


@dataclass(frozen=True)
class PlanValidationIssue:
    """
    One structural validation problem.
    """

    code: str
    message: str
    step_id: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class PlanValidationResult:
    """
    Result of validating an ExecutionPlan.
    """

    valid: bool
    plan: ExecutionPlan

    issues: tuple[PlanValidationIssue, ...] = ()

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self):

        if not isinstance(
            self.plan,
            ExecutionPlan,
        ):
            raise TypeError(
                "plan must be an ExecutionPlan."
            )

    @property
    def error_count(self) -> int:
        return len(self.issues)

    @property
    def error_count(self) -> int:
        return len(self.issues)