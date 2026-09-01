from dataclasses import dataclass, field
from typing import Callable

from src.core.execution_confirmation import ExecutionConfirmationService
from src.core.execution_executor_models import PlanExecutionResult
from src.core.execution_plan_models import ExecutionPlan
from src.core.execution_policy import ExecutionPolicy
from src.core.execution_policy_models import ExecutionPolicyResult, PolicyDecision
from src.core.execution_state import ExecutionState
from src.core.plan_executor import PlanExecutor
from src.core.plan_validator import PlanValidator
from src.core.task_models import TaskRequest


@dataclass(frozen=True)
class ExecutionObservation:
    """Provider-neutral observation of one plan execution attempt."""

    plan: ExecutionPlan
    execution: PlanExecutionResult
    state: ExecutionState | None = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.plan, ExecutionPlan):
            raise TypeError("plan must be an ExecutionPlan.")
        if not isinstance(self.execution, PlanExecutionResult):
            raise TypeError("execution must be a PlanExecutionResult.")
        if self.state is None:
            object.__setattr__(
                self,
                "state",
                ExecutionState.from_execution(
                    self.plan.task_description,
                    self.execution,
                ),
            )
        elif not isinstance(self.state, ExecutionState):
            raise TypeError("state must be an ExecutionState or None.")

    @property
    def success(self) -> bool:
        return self.execution.success


@dataclass(frozen=True)
class ContinuationDecision:
    """Provider-neutral decision derived from execution state."""

    action: str
    reason: str

    @property
    def should_continue(self) -> bool:
        return self.action == "CONTINUE"


@dataclass(frozen=True)
class ExecutionLoopResult:
    """Terminal state of a guarded execution run."""

    status: str
    iterations: int
    observations: tuple[ExecutionObservation, ...]
    pending_operation_id: str | None = None
    last_policy: ExecutionPolicyResult | None = None
    next_task: TaskRequest | None = None


ContinuationPlanner = Callable[[TaskRequest, ExecutionObservation], TaskRequest | None]


class ExecutionContinuationService:
    """
    Derive a conservative continuation decision from provider-neutral state.

    The state explicitly declares which control-level actions remain legal.
    This service never invents an action outside that declaration.
    """

    def decide(
        self,
        state: ExecutionState | ExecutionObservation,
    ) -> ContinuationDecision:
        if isinstance(state, ExecutionObservation):
            state = state.state
        if not isinstance(state, ExecutionState):
            raise TypeError("state must be an ExecutionState or ExecutionObservation.")

        allowed = state.next_allowed_actions
        if "COMPLETE" in allowed:
            return ContinuationDecision(
                "COMPLETE",
                "Execution state marks the objective complete.",
            )

        if "CORRECT" in allowed:
            return ContinuationDecision(
                "CONTINUE",
                "Execution state permits a corrective continuation.",
            )

        return ContinuationDecision(
            "STOP",
            "Execution state does not permit continuation.",
        )


class GuardedExecutionLoop:
    """
    Compose planning, validation, policy, confirmation, execution and observation.

    Every plan, including a corrective plan, returns through the exact same
    validator -> policy -> confirmation -> executor pipeline. This class never
    invokes AI and never executes a plan outside PlanExecutor.
    """

    def __init__(
        self,
        planner,
        validator: PlanValidator,
        policy: ExecutionPolicy,
        executor: PlanExecutor,
        confirmation: ExecutionConfirmationService,
        continuation: ExecutionContinuationService | None = None,
        max_iterations: int = 3,
    ):
        if not hasattr(planner, "plan") or not callable(planner.plan):
            raise TypeError("planner must expose plan(task).")
        if not isinstance(validator, PlanValidator):
            raise TypeError("validator must be a PlanValidator.")
        if not isinstance(policy, ExecutionPolicy):
            raise TypeError("policy must be an ExecutionPolicy.")
        if not isinstance(executor, PlanExecutor):
            raise TypeError("executor must be a PlanExecutor.")
        if not isinstance(confirmation, ExecutionConfirmationService):
            raise TypeError("confirmation must be an ExecutionConfirmationService.")
        if continuation is not None and not isinstance(continuation, ExecutionContinuationService):
            raise TypeError("continuation must be an ExecutionContinuationService.")
        if not isinstance(max_iterations, int) or max_iterations < 1:
            raise ValueError("max_iterations must be a positive integer.")

        self.planner = planner
        self.validator = validator
        self.policy = policy
        self.executor = executor
        self.confirmation = confirmation
        self.continuation = continuation or ExecutionContinuationService()
        self.max_iterations = max_iterations

    def run(
        self,
        task: TaskRequest,
        corrective_planner: ContinuationPlanner | None = None,
    ) -> ExecutionLoopResult:
        if not isinstance(task, TaskRequest):
            raise TypeError("task must be a TaskRequest.")
        if corrective_planner is not None and not callable(corrective_planner):
            raise TypeError("corrective_planner must be callable or None.")

        observations: list[ExecutionObservation] = []
        current_task = task

        for iteration in range(1, self.max_iterations + 1):
            plan = self.planner.plan(current_task)
            validation = self.validator.validate(plan)
            if not validation.valid:
                return ExecutionLoopResult(
                    status="VALIDATION_FAILED",
                    iterations=iteration,
                    observations=tuple(observations),
                    last_policy=None,
                    next_task=current_task,
                )

            policy = self.policy.evaluate(plan)
            if policy.decision == PolicyDecision.DENY:
                return ExecutionLoopResult(
                    status="POLICY_DENIED",
                    iterations=iteration,
                    observations=tuple(observations),
                    last_policy=policy,
                    next_task=current_task,
                )

            if policy.decision == PolicyDecision.REQUIRE_CONFIRMATION:
                pending = self.confirmation.stage(plan)
                return ExecutionLoopResult(
                    status="AWAITING_CONFIRMATION",
                    iterations=iteration,
                    observations=tuple(observations),
                    pending_operation_id=pending.operation_id,
                    last_policy=policy,
                    next_task=current_task,
                )

            execution = self.executor.execute(plan, policy)
            observation = ExecutionObservation(
                plan=plan,
                execution=execution,
                state=ExecutionState.from_execution(task.content, execution),
                metadata={"iteration": iteration},
            )
            observations.append(observation)

            decision = self.continuation.decide(observation.state)
            if not decision.should_continue:
                return ExecutionLoopResult(
                    status="COMPLETED" if decision.action == "COMPLETE" else "CORRECTION_REQUIRED",
                    iterations=iteration,
                    observations=tuple(observations),
                    last_policy=policy,
                )

            if corrective_planner is None:
                return ExecutionLoopResult(
                    status="CORRECTION_REQUIRED",
                    iterations=iteration,
                    observations=tuple(observations),
                    last_policy=policy,
                )

            if iteration == self.max_iterations:
                return ExecutionLoopResult(
                    status="MAX_ITERATIONS_REACHED",
                    iterations=iteration,
                    observations=tuple(observations),
                    last_policy=policy,
                )

            current_task = corrective_planner(current_task, observation)
            if current_task is None:
                return ExecutionLoopResult(
                    status="CORRECTION_UNAVAILABLE",
                    iterations=iteration,
                    observations=tuple(observations),
                    last_policy=policy,
                )
            if not isinstance(current_task, TaskRequest):
                raise TypeError("corrective_planner must return TaskRequest or None.")

        return ExecutionLoopResult(
            status="MAX_ITERATIONS_REACHED",
            iterations=self.max_iterations,
            observations=tuple(observations),
        )
