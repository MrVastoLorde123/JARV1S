from src.core.execution_plan_models import (
    ExecutionPlan,
)

from src.core.execution_policy_models import (
    ExecutionPolicyResult,
    PolicyDecision,
    PolicyIssue,
)


class ExecutionPolicy:
    """
    Deterministic V1 execution policy.

    The policy decides whether a structurally valid plan
    may proceed to a future execution layer.

    It does not execute anything.

    V1 rules:

        PROVIDE_INFORMATION
            -> ALLOW

        USE_TOOL
            -> REQUIRE_CONFIRMATION

        PERFORM_ACTION
            -> REQUIRE_CONFIRMATION

        UNCLASSIFIED_TASK
            -> DENY

    Any explicitly confirmation-required step causes the
    plan to require confirmation.

    Empty plans are denied because there is nothing meaningful
    to execute.
    """

    _ACTION_DECISIONS = {
        "PROVIDE_INFORMATION":
            PolicyDecision.ALLOW,

        "USE_TOOL":
            PolicyDecision.REQUIRE_CONFIRMATION,

        "PERFORM_ACTION":
            PolicyDecision.REQUIRE_CONFIRMATION,

        "UNCLASSIFIED_TASK":
            PolicyDecision.DENY,
    }

    def evaluate(
        self,
        plan: ExecutionPlan,
    ) -> ExecutionPolicyResult:

        if not isinstance(
            plan,
            ExecutionPlan,
        ):
            raise TypeError(
                "plan must be an ExecutionPlan."
            )

        if not plan.steps:

            return ExecutionPolicyResult(
                decision=PolicyDecision.DENY,
                plan=plan,
                issues=(
                    PolicyIssue(
                        code="EMPTY_PLAN",
                        message=(
                            "Plans with no execution steps "
                            "cannot be executed."
                        ),
                    ),
                ),
                metadata={
                    "policy": "deterministic",
                    "step_count": 0,
                },
            )

        issues = []

        requires_confirmation = False

        for step in plan.steps:

            action = (
                step.action.strip()
                .upper()
            )

            decision = (
                self._ACTION_DECISIONS.get(
                    action
                )
            )

            if decision is None:

                issues.append(
                    PolicyIssue(
                        code="UNKNOWN_ACTION",
                        message=(
                            f"Unknown execution action "
                            f"'{step.action}'."
                        ),
                        step_id=step.step_id,
                        metadata={
                            "action": step.action,
                        },
                    )
                )

                continue

            if decision == PolicyDecision.DENY:

                issues.append(
                    PolicyIssue(
                        code="UNSAFE_ACTION",
                        message=(
                            f"Action '{step.action}' "
                            f"is not permitted by the "
                            f"V1 execution policy."
                        ),
                        step_id=step.step_id,
                        metadata={
                            "action": step.action,
                        },
                    )
                )

                continue

            if (
                decision
                == PolicyDecision.REQUIRE_CONFIRMATION
            ):
                requires_confirmation = True

            if step.requires_confirmation:
                requires_confirmation = True

        if issues:

            return ExecutionPolicyResult(
                decision=PolicyDecision.DENY,
                plan=plan,
                issues=tuple(issues),
                metadata={
                    "policy": "deterministic",
                    "step_count": len(
                        plan.steps
                    ),
                },
            )

        if requires_confirmation:

            return ExecutionPolicyResult(
                decision=(
                    PolicyDecision.REQUIRE_CONFIRMATION
                ),
                plan=plan,
                metadata={
                    "policy": "deterministic",
                    "step_count": len(
                        plan.steps
                    ),
                },
            )

        return ExecutionPolicyResult(
            decision=PolicyDecision.ALLOW,
            plan=plan,
            metadata={
                "policy": "deterministic",
                "step_count": len(
                    plan.steps
                ),
            },
        )


def evaluate_plan(
    plan: ExecutionPlan,
) -> ExecutionPolicyResult:
    """
    Convenience wrapper around the deterministic
    default execution policy.
    """

    return ExecutionPolicy().evaluate(
        plan
    )