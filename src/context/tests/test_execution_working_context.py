import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from src.context.execution_working_context import ExecutionWorkingContextBridge
from src.context.jarvis_working_context import JARVISWorkingContextRuntime
from src.context.models import ContextItem, ContextPackage, OBSERVATION, ContextOptions
from src.context.working_context import WorkingContext
from src.context.working_context_composer import WorkingContextComposer
from src.core.execution_confirmation import ExecutionConfirmationService
from src.core.execution_executor_models import PlanExecutionResult, PlanExecutionStatus
from src.core.execution_loop import ExecutionObservation, GuardedExecutionLoop
from src.core.execution_plan_models import ExecutionPlan
from src.core.execution_planner import ExecutionPlanner
from src.core.execution_policy import ExecutionPolicy
from src.core.execution_progress import ExecutionProgress
from src.core.execution_state import ExecutionState
from src.core.plan_executor import PlanExecutor
from src.core.plan_validator import PlanValidator
from src.core.task_models import TaskRequest, TaskType


class ExecutionWorkingContextBridgeTests(unittest.TestCase):
    def _package(self):
        return ContextPackage(
            request="inspect config",
            items=(ContextItem("MEMORY", "config is under src/core"),),
            instructions=("Do not invent information.",),
            metadata={},
        )

    def _runtime(self, composer=None):
        jarvis = SimpleNamespace(
            context_options=ContextOptions(
                include_memories=False,
                include_evidence=False,
                include_state=False,
            ),
            conversation=SimpleNamespace(
                snapshot=lambda: SimpleNamespace(
                    conversation_id="conversation-1",
                    created_at="2026-09-01T00:00:00Z",
                    updated_at="2026-09-01T00:01:00Z",
                    turns=(),
                    active_topic=None,
                    active_task=None,
                    metadata={},
                )
            ),
        )
        if composer is None:
            composer = WorkingContextComposer(Mock(return_value=self._package()))
        return JARVISWorkingContextRuntime(jarvis, composer=composer)

    def _observation(self):
        state = ExecutionState(
            goal="inspect config",
            plan_id="plan-1",
            status=PlanExecutionStatus.COMPLETED,
            completed_steps=("inspect",),
            next_allowed_actions=("COMPLETE",),
        )
        progress = ExecutionProgress.from_state(state)
        plan = ExecutionPlan(
            plan_id="plan-1",
            task_description="inspect config",
            steps=(),
        )
        execution = PlanExecutionResult(
            plan_id="plan-1",
            status=PlanExecutionStatus.COMPLETED,
            steps=(),
            metadata={},
        )
        return ExecutionObservation(
            plan=plan,
            execution=execution,
            state=state,
            progress=progress,
            metadata={"iteration": 1},
        )

    def test_bridge_composes_from_verified_observation(self):
        runtime = self._runtime()
        bridge = ExecutionWorkingContextBridge(runtime)

        task = TaskRequest("inspect config", TaskType.INFORMATION)
        result = bridge.observe(task, self._observation(), observations=("file observed",))

        self.assertIsInstance(result, WorkingContext)
        self.assertIs(bridge.latest, result)
        self.assertEqual(result.execution_state.status, PlanExecutionStatus.COMPLETED)
        self.assertEqual(result.execution_progress.attempt_count, 1)
        self.assertEqual(result.observations[0].content, "file observed")

    def test_bridge_requires_verified_state_and_progress(self):
        runtime = self._runtime()
        bridge = ExecutionWorkingContextBridge(runtime)
        task = TaskRequest("inspect config", TaskType.INFORMATION)
        observation = self._observation()
        observation_without_progress = ExecutionObservation(
            plan=observation.plan,
            execution=observation.execution,
            state=observation.state,
            progress=None,
            metadata=observation.metadata,
        )

        with self.assertRaises(ValueError):
            bridge.observe(task, observation_without_progress)

    def test_bridge_does_not_execute_or_change_observation(self):
        runtime = self._runtime()
        bridge = ExecutionWorkingContextBridge(runtime)
        task = TaskRequest("inspect config", TaskType.INFORMATION)
        observation = self._observation()

        bridge.observe(task, observation)

        self.assertEqual(observation.state.next_allowed_actions, ("COMPLETE",))

    def test_guarded_loop_publishes_verified_observation_to_bridge(self):
        runtime = self._runtime()
        bridge = ExecutionWorkingContextBridge(runtime)
        planner = Mock(spec=ExecutionPlanner)
        planner.plan.return_value = ExecutionPlan(
            plan_id="plan-1",
            task_description="inspect config",
            steps=(),
        )
        loop = GuardedExecutionLoop(
            planner=planner,
            validator=PlanValidator(),
            policy=ExecutionPolicy(),
            executor=PlanExecutor(),
            confirmation=ExecutionConfirmationService(),
            observation_observer=bridge,
        )

        task = TaskRequest("inspect config", TaskType.INFORMATION)
        result = loop.run(task)

        self.assertEqual(result.status, "COMPLETED")
        self.assertIsNotNone(bridge.latest)
        self.assertIs(bridge.latest.execution_state, result.observations[0].state)
        self.assertIs(bridge.latest.execution_progress, result.observations[0].progress)


if __name__ == "__main__":
    unittest.main()
