from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.core.execution_plan_models import (
    ExecutionPlan,
)


class PolicyDecision(str, Enum):
    """
    Result of evaluating an execution plan.
    """

    ALLOW = "ALLOW"
    REQUIRE_CONFIRMATION = "REQUIRE_CONFIRMATION"
    DENY = "DENY"


@dataclass(frozen=True)
class PolicyIssue:
    """
    One policy finding.
    """

    code: str

    message: str

    step_id: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class ExecutionPolicyResult:
    """
    Result of evaluating an ExecutionPlan against
    execution policy.

    This object contains a decision only.
    It does not execute or mutate the plan.
    """

    decision: PolicyDecision

    plan: ExecutionPlan

    issues: tuple[PolicyIssue, ...] = ()

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
    def allowed(self) -> bool:
        return (
            self.decision
            == PolicyDecision.ALLOW
        )

    @property
    def requires_confirmation(self) -> bool:
        return (
            self.decision
            == PolicyDecision.REQUIRE_CONFIRMATION
        )

    @property
    def denied(self) -> bool:
        return (
            self.decision
            == PolicyDecision.DENY
        )

    @property
    def issue_count(self) -> int:
        return len(
            self.issues
        )