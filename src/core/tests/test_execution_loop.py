import unittest
from unittest.mock import Mock

from src.core.execution_confirmation import ExecutionConfirmationService
from src.core.execution_executor_models import (
    PlanExecutionResult,
    PlanExecutionStatus,
    StepExecutionResult,
    StepExecutionStatus,
)
from src.core.execution_loop import (
    ExecutionContinuationService,
    ExecutionObservation,
    GuardedExecutionLoop,
)
from src.core.execution_plan_models import ExecutionPlan, PlanStatus, PlanStep, StepStatus
from src.core.execution_policy import ExecutionPolicy
from src.core.execution_policy_models import PolicyDecision
from src.core.multi_step_planner import MultiStepExecutionPlanner
from src.core.plan_executor import PlanExecutor
from src.core.plan_validator import PlanValidator
from src.core.task_models import TaskRequest, TaskType


class FakePlanner:
    def __init__(self, plans):
        self.plans = list(plans)
        self.calls = []

    def plan(self, task):
        self.calls.append(task)
        return self.plans.pop(0)


def plan(plan_id="p1", action="PROVIDE_INFORMATION"):
    return ExecutionPlan(
        plan_id=plan_id,
        task_description="do it",
        status=PlanStatus.READY,
        steps=(
            PlanStep(
                step_id="step-1",
                description="do it",
                action=action,
                order=0,
                status=StepStatus.READY,
            ),
        ),
    )


class GuardedExecutionLoopTests(unittest.TestCase):
    def setUp(self):
        self.validator = PlanValidator()
        self.policy = ExecutionPolicy()
        self.confirmation = ExecutionConfirmationService()

    def test_successful_plan_completes_after_observation(self):
        planner = FakePlanner([plan()])
        executor = PlanExecutor({"PROVIDE_INFORMATION": lambda step: "done"})
        loop = GuardedExecutionLoop(
            planner,
            self.validator,
            self.policy,
            executor,
            self.confirmation,
        )
        result = loop.run(TaskRequest("do it", TaskType.INFORMATION))
        self.assertEqual(result.status, "COMPLETED")
        self.assertEqual(len(result.observations), 1)
        self.assertTrue(result.observations[0].success)
        self.assertEqual(result.observations[0].state.completed_steps, ("step-1",))
        self.assertEqual(result.observations[0].state.next_allowed_actions, ("COMPLETE",))

    def test_multi_step_plan_executes_in_order(self):
        planner = MultiStepExecutionPlanner()
        seen = []
        executor = PlanExecutor({"PROVIDE_INFORMATION": lambda step: seen.append(step.description) or step.description})
        loop = GuardedExecutionLoop(
            planner,
            self.validator,
            self.policy,
            executor,
            self.confirmation,
        )
        result = loop.run(
            TaskRequest(
                "inspect the project then summarize the result",
                TaskType.INFORMATION,
            )
        )
        self.assertEqual(result.status, "COMPLETED")
        self.assertEqual(seen, ["inspect the project", "summarize the result"])
        self.assertEqual(result.observations[0].execution.step_count, 2)

    def test_failed_plan_stops_without_implicit_replanning(self):
        planner = FakePlanner([plan()])
        executor = PlanExecutor({"PROVIDE_INFORMATION": lambda step: (_ for _ in ()).throw(RuntimeError("boom"))})
        loop = GuardedExecutionLoop(
            planner,
            self.validator,
            self.policy,
            executor,
            self.confirmation,
        )
        result = loop.run(TaskRequest("do it", TaskType.INFORMATION))
        self.assertEqual(result.status, "CORRECTION_REQUIRED")
        self.assertEqual(len(planner.calls), 1)

    def test_corrective_plan_reenters_full_safety_pipeline(self):
        first = plan("p1")
        second = plan("p2")
        planner = FakePlanner([first, second])
        executor = PlanExecutor({"PROVIDE_INFORMATION": lambda step: "done"})
        loop = GuardedExecutionLoop(
            planner,
            self.validator,
            self.policy,
            executor,
            self.confirmation,
            max_iterations=2,
        )

        calls = []
        original_execute = executor.execute

        def execute(plan_arg, policy_arg):
            calls.append((plan_arg.plan_id, policy_arg.decision))
            if len(calls) == 1:
                return PlanExecutionResult(
                    plan_id=plan_arg.plan_id,
                    status=PlanExecutionStatus.FAILED,
                    steps=(
                        StepExecutionResult(
                            step_id="step-1",
                            action="PROVIDE_INFORMATION",
                            status=StepExecutionStatus.FAILED,
                            error="boom",
                        ),
                    ),
                    error="boom",
                )
            return original_execute(plan_arg, policy_arg)

        executor.execute = execute
        next_task = TaskRequest("correct it", TaskType.INFORMATION)
        result = loop.run(
            TaskRequest("do it", TaskType.INFORMATION),
            corrective_planner=lambda task, observation: next_task,
        )
        self.assertEqual(result.status, "COMPLETED")
        self.assertEqual([item[0] for item in calls], ["p1", "p2"])
        self.assertTrue(all(decision == PolicyDecision.ALLOW for _, decision in calls))
        self.assertEqual(len(result.observations), 2)
        self.assertEqual(result.observations[0].state.failed_steps, ("step-1",))
        self.assertEqual(result.observations[1].state.completed_steps, ("step-1",))

    def test_confirmation_stops_before_executor(self):
        planner = FakePlanner([plan(action="PERFORM_ACTION")])
        executor = Mock(spec=PlanExecutor)
        loop = GuardedExecutionLoop(
            planner,
            self.validator,
            self.policy,
            executor,
            self.confirmation,
        )
        result = loop.run(TaskRequest("do it", TaskType.ACTION))
        self.assertEqual(result.status, "AWAITING_CONFIRMATION")
        self.assertIsNotNone(result.pending_operation_id)
        executor.execute.assert_not_called()

    def test_max_iterations_prevents_unbounded_loop(self):
        planner = FakePlanner([plan("p1"), plan("p2"), plan("p3")])
        executor = PlanExecutor({"PROVIDE_INFORMATION": lambda step: (_ for _ in ()).throw(RuntimeError("boom"))})
        loop = GuardedExecutionLoop(
            planner,
            self.validator,
            self.policy,
            executor,
            self.confirmation,
            max_iterations=2,
        )
        result = loop.run(
            TaskRequest("do it", TaskType.INFORMATION),
            corrective_planner=lambda task, observation: TaskRequest("retry", TaskType.INFORMATION),
        )
        self.assertEqual(result.status, "MAX_ITERATIONS_REACHED")
        self.assertEqual(result.iterations, 2)

    def test_observation_is_provider_neutral(self):
        execution = PlanExecutionResult(
            plan_id="p1",
            status=PlanExecutionStatus.COMPLETED,
            steps=(),
        )
        observation = ExecutionObservation(plan("p1"), execution)
        decision = ExecutionContinuationService().decide(observation.state)
        self.assertEqual(decision.action, "COMPLETE")
        self.assertFalse(decision.should_continue)
        self.assertEqual(observation.state.status, PlanExecutionStatus.COMPLETED)


if __name__ == "__main__":
    unittest.main()
