from src.core.execution_plan_models import (
    ExecutionPlan,
    PlanStep,
)

from src.core.plan_validation_models import (
    PlanValidationIssue,
    PlanValidationResult,
)


class PlanValidator:
    """
    Validates ExecutionPlan structure before execution.

    The validator is read-only.

    It does not:
        - execute steps
        - modify plans
        - repair plans
        - invoke tools
        - invoke AI
    """

    def validate(
        self,
        plan: ExecutionPlan,
    ) -> PlanValidationResult:

        if not isinstance(
            plan,
            ExecutionPlan,
        ):
            raise TypeError(
                "plan must be an ExecutionPlan."
            )

        issues = []

        self._validate_steps(
            plan,
            issues,
        )

        self._validate_dependencies(
            plan,
            issues,
        )

        self._validate_order(
            plan,
            issues,
        )

        self._validate_confirmation_metadata(
            plan,
            issues,
        )

        return PlanValidationResult(
            valid=not issues,
            plan=plan,
            issues=tuple(issues),
            metadata={
                "validator": "deterministic",
                "issue_count": len(issues),
                "step_count": len(plan.steps),
            },
        )

    def _validate_steps(
        self,
        plan: ExecutionPlan,
        issues: list[PlanValidationIssue],
    ) -> None:

        for step in plan.steps:

            if not isinstance(
                step,
                PlanStep,
            ):
                issues.append(
                    PlanValidationIssue(
                        code="INVALID_STEP",
                        message=(
                            "Plan contains a non-PlanStep object."
                        ),
                    )
                )

                continue

            if not step.action.strip():

                issues.append(
                    PlanValidationIssue(
                        code="EMPTY_ACTION",
                        message=(
                            "Plan step must contain "
                            "an executable action."
                        ),
                        step_id=step.step_id,
                    )
                )

    def _validate_dependencies(
        self,
        plan: ExecutionPlan,
        issues: list[PlanValidationIssue],
    ) -> None:

        step_map = {
            step.step_id: step
            for step in plan.steps
        }

        for step in plan.steps:

            for dependency in step.depends_on:

                if dependency not in step_map:

                    issues.append(
                        PlanValidationIssue(
                            code="UNKNOWN_DEPENDENCY",
                            message=(
                                f"Step '{step.step_id}' "
                                f"depends on unknown step "
                                f"'{dependency}'."
                            ),
                            step_id=step.step_id,
                            metadata={
                                "dependency": dependency,
                            },
                        )
                    )

        self._validate_dependency_cycles(
            plan,
            issues,
        )

    def _validate_dependency_cycles(
        self,
        plan: ExecutionPlan,
        issues: list[PlanValidationIssue],
    ) -> None:

        step_map = {
            step.step_id: step
            for step in plan.steps
        }

        permanently_visited = set()
        currently_visiting = set()

        def visit(step_id: str) -> None:

            if step_id in permanently_visited:
                return

            if step_id in currently_visiting:

                issues.append(
                    PlanValidationIssue(
                        code="DEPENDENCY_CYCLE",
                        message=(
                            "Plan contains a dependency cycle."
                        ),
                        step_id=step_id,
                    )
                )

                return

            step = step_map.get(
                step_id
            )

            if step is None:
                return

            currently_visiting.add(
                step_id
            )

            for dependency in step.depends_on:
                visit(
                    dependency
                )

            currently_visiting.remove(
                step_id
            )

            permanently_visited.add(
                step_id
            )

        for step in plan.steps:
            visit(
                step.step_id
            )

    def _validate_order(
        self,
        plan: ExecutionPlan,
        issues: list[PlanValidationIssue],
    ) -> None:

        orders = [
            step.order
            for step in plan.steps
        ]

        if len(orders) != len(
            set(orders)
        ):

            issues.append(
                PlanValidationIssue(
                    code="DUPLICATE_ORDER",
                    message=(
                        "Plan steps must have unique order values."
                    ),
                )
            )

        if orders != sorted(orders):

            issues.append(
                PlanValidationIssue(
                    code="UNSORTED_ORDER",
                    message=(
                        "Plan steps must be ordered by "
                        "ascending order value."
                    ),
                )
            )

        expected_orders = list(
            range(len(orders))
        )

        if sorted(orders) != expected_orders:

            issues.append(
                PlanValidationIssue(
                    code="INVALID_ORDER_SEQUENCE",
                    message=(
                        "Plan step orders must form a "
                        "continuous sequence starting at 0."
                    ),
                )
            )

    def _validate_confirmation_metadata(
        self,
        plan: ExecutionPlan,
        issues: list[PlanValidationIssue],
    ) -> None:

        for step in plan.steps:

            value = step.requires_confirmation

            if not isinstance(
                value,
                bool,
            ):

                issues.append(
                    PlanValidationIssue(
                        code="INVALID_CONFIRMATION_FLAG",
                        message=(
                            "requires_confirmation must "
                            "be a boolean."
                        ),
                        step_id=step.step_id,
                    )
                )


def validate_plan(
    plan: ExecutionPlan,
) -> PlanValidationResult:
    """
    Convenience function using the deterministic
    default validator.
    """

    return PlanValidator().validate(
        plan
    )