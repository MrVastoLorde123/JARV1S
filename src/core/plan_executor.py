from collections.abc import Callable

from src.core.execution_executor_models import (
    PlanExecutionResult,
    PlanExecutionStatus,
    StepExecutionResult,
    StepExecutionStatus,
)

from src.core.execution_plan_models import (
    ExecutionPlan,
    PlanStep,
)

from src.core.execution_policy_models import (
    ExecutionPolicyResult,
    PolicyDecision,
)


ExecutionHandler = Callable[
    [PlanStep],
    object,
]


class PlanExecutor:
    """
    Executes validated and authorized ExecutionPlans.

    The executor knows nothing about concrete tools.

    Actions are mapped to explicitly registered handlers.

    The executor does not:
        - plan
        - validate
        - authorize
        - invoke AI
        - discover tools
        - mutate the ExecutionPlan
    """

    def __init__(
        self,
        handlers: dict[str, ExecutionHandler] | None = None,
    ):
        self._handlers: dict[
            str,
            ExecutionHandler,
        ] = {}

        if handlers is not None:

            for action, handler in handlers.items():
                self.register_handler(
                    action,
                    handler,
                )

    def register_handler(
        self,
        action: str,
        handler: ExecutionHandler,
    ) -> None:
        """
        Register an execution handler for an action.
        """

        if not isinstance(
            action,
            str,
        ):
            raise TypeError(
                "action must be a string."
            )

        action = action.strip().upper()

        if not action:
            raise ValueError(
                "action cannot be empty."
            )

        if not callable(handler):
            raise TypeError(
                "handler must be callable."
            )

        self._handlers[action] = handler

    def has_handler(
        self,
        action: str,
    ) -> bool:

        if not isinstance(
            action,
            str,
        ):
            raise TypeError(
                "action must be a string."
            )

        return (
            action.strip().upper()
            in self._handlers
        )

    def execute(
        self,
        plan: ExecutionPlan,
        policy_result: ExecutionPolicyResult,
    ) -> PlanExecutionResult:
        """
        Execute an authorized plan.
        """

        self._validate_inputs(
            plan,
            policy_result,
        )

        if (
            policy_result.decision
            != PolicyDecision.ALLOW
        ):

            return PlanExecutionResult(
                plan_id=plan.plan_id,
                status=PlanExecutionStatus.BLOCKED,
                steps=(),
                error=(
                    "Execution is not authorized by policy."
                ),
                metadata={
                    "executor": "deterministic",
                    "policy_decision": (
                        policy_result.decision.value
                    ),
                },
            )

        if not plan.steps:

            return PlanExecutionResult(
                plan_id=plan.plan_id,
                status=PlanExecutionStatus.FAILED,
                steps=(),
                error=(
                    "Cannot execute an empty plan."
                ),
                metadata={
                    "executor": "deterministic",
                },
            )

        results: list[StepExecutionResult] = []

        completed_step_ids: set[str] = set()

        for step in sorted(
            plan.steps,
            key=lambda item: item.order,
        ):

            missing_dependencies = [
                dependency
                for dependency in step.depends_on
                if dependency
                not in completed_step_ids
            ]

            if missing_dependencies:

                result = StepExecutionResult(
                    step_id=step.step_id,
                    action=step.action,
                    status=StepExecutionStatus.FAILED,
                    error=(
                        "Step dependencies were not completed: "
                        + ", ".join(
                            missing_dependencies
                        )
                    ),
                )

                results.append(
                    result
                )

                break

            handler = self._handlers.get(
                step.action.strip().upper()
            )

            if handler is None:

                result = StepExecutionResult(
                    step_id=step.step_id,
                    action=step.action,
                    status=StepExecutionStatus.FAILED,
                    error=(
                        f"No handler is registered for "
                        f"action '{step.action}'."
                    ),
                )

                results.append(
                    result
                )

                break

            try:

                output = handler(
                    step
                )

                result = StepExecutionResult(
                    step_id=step.step_id,
                    action=step.action,
                    status=StepExecutionStatus.COMPLETED,
                    output=output,
                )

                results.append(
                    result
                )

                completed_step_ids.add(
                    step.step_id
                )

            except Exception as exc:

                result = StepExecutionResult(
                    step_id=step.step_id,
                    action=step.action,
                    status=StepExecutionStatus.FAILED,
                    error=str(exc),
                )

                results.append(
                    result
                )

                break

        success = all(
            step.status
            == StepExecutionStatus.COMPLETED
            for step in results
        ) and len(results) == len(
            plan.steps
        )

        if success:

            return PlanExecutionResult(
                plan_id=plan.plan_id,
                status=PlanExecutionStatus.COMPLETED,
                steps=tuple(results),
                metadata={
                    "executor": "deterministic",
                    "step_count": len(results),
                },
            )

        failed_step = next(
            (
                step
                for step in results
                if step.status
                == StepExecutionStatus.FAILED
            ),
            None,
        )

        return PlanExecutionResult(
            plan_id=plan.plan_id,
            status=PlanExecutionStatus.FAILED,
            steps=tuple(results),
            error=(
                failed_step.error
                if failed_step is not None
                else "Plan execution failed."
            ),
            metadata={
                "executor": "deterministic",
                "step_count": len(results),
            },
        )

    @staticmethod
    def _validate_inputs(
        plan: ExecutionPlan,
        policy_result: ExecutionPolicyResult,
    ) -> None:

        if not isinstance(
            plan,
            ExecutionPlan,
        ):
            raise TypeError(
                "plan must be an ExecutionPlan."
            )

        if not isinstance(
            policy_result,
            ExecutionPolicyResult,
        ):
            raise TypeError(
                "policy_result must be an "
                "ExecutionPolicyResult."
            )

        if policy_result.plan.plan_id != plan.plan_id:

            raise ValueError(
                "policy_result does not belong to the supplied plan."
            )