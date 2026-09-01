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
    may proceed to execution.

    It does not execute anything.

    V1 rules:

        PROVIDE_INFORMATION
            -> ALLOW

        USE_TOOL
            -> ALLOW

        PERFORM_ACTION
            -> REQUIRE_CONFIRMATION

        UNCLASSIFIED_TASK
            -> DENY

    Tool-specific confirmation is owned by the tool-layer
    PolicyGate, which evaluates the concrete ToolDefinition.
    Any explicitly confirmation-required step still causes
    the plan to require confirmation at this layer.

    Empty plans are denied because there is nothing meaningful
    to execute.
    """

    _ACTION_DECISIONS = {
        "PROVIDE_INFORMATION":
            PolicyDecision.ALLOW,

        "USE_TOOL":
            PolicyDecision.ALLOW,

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
                step.action.strip().upper()
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

    def authorize_confirmed(
        self,
        plan: ExecutionPlan,
    ) -> ExecutionPolicyResult:
        """
        Re-evaluate an exact plan after explicit user
        confirmation.

        Confirmation does not bypass policy.

        ALLOW
            remains ALLOW.

        REQUIRE_CONFIRMATION
            becomes ALLOW because the required confirmation
            has now been supplied.

        DENY
            remains DENY.

        The plan itself is never modified.
        """

        result = self.evaluate(plan)

        if result.decision == PolicyDecision.DENY:
            return result

        if (
            result.decision
            == PolicyDecision.REQUIRE_CONFIRMATION
        ):
            return ExecutionPolicyResult(
                decision=PolicyDecision.ALLOW,
                plan=result.plan,
                issues=result.issues,
                metadata={
                    **result.metadata,
                    "confirmation_authorized": True,
                    "authorization_mode": (
                        "explicit_confirmation"
                    ),
                },
            )

        return result


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
