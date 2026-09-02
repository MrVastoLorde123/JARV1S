import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from src.context.execution_working_context import ExecutionWorkingContextBridge
from src.context.jarvis_working_context import JARVISWorkingContextRuntime
from src.context.models import ContextItem, ContextPackage, OBSERVATION
from src.context.working_context import WorkingContext
from src.core.execution_executor_models import PlanExecutionResult, PlanExecutionStatus
from src.core.execution_loop import ExecutionObservation
from src.core.execution_progress import ExecutionProgress
from src.core.execution_state import ExecutionState
from src.core.execution_plan_models import ExecutionPlan
from src.core.task_models import TaskRequest, TaskType


class ExecutionWorkingContextBridgeTests(unittest.TestCase):
    def _package(self):
        return ContextPackage(
            request="inspect config",
            items=(ContextItem("MEMORY", "config is under src/core"),),
            instructions=("Do not invent information.",),
            metadata={},
        )

    def _observation(self):
        state = ExecutionState(
            goal="inspect config",
            plan_id="plan-1",
            status=PlanExecutionStatus.COMPLETED,
            completed_steps=("inspect",),
            next_allowed_actions=("COMPLETE",),
        )
        progress = ExecutionProgress.from_state(state)
        plan = SimpleNamespace(plan_id="plan-1", task_description="inspect config")
        execution = PlanExecutionResult(
            plan_id="plan-1",
            status=PlanExecutionStatus.COMPLETED,
            success=True,
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
        composer = Mock(spec=WorkingContext)
        runtime = Mock(spec=JARVISWorkingContextRuntime)
        working = WorkingContext(request="inspect config", context_package=self._package())
        runtime.compose.return_value = working
        bridge = ExecutionWorkingContextBridge(runtime)

        task = TaskRequest("inspect config", TaskType.INFORMATION)
        result = bridge.observe(task, self._observation(), observations=("file observed",))

        self.assertIs(result, working)
        self.assertIs(bridge.latest, working)
        kwargs = runtime.compose.call_args.kwargs
        self.assertEqual(kwargs["execution_state"].status, PlanExecutionStatus.COMPLETED)
        self.assertEqual(kwargs["execution_progress"].attempt_count, 1)
        self.assertEqual(kwargs["observations"], ("file observed",))

    def test_bridge_requires_verified_state_and_progress(self):
        runtime = Mock(spec=JARVISWorkingContextRuntime)
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
        runtime = Mock(spec=JARVISWorkingContextRuntime)
        runtime.compose.return_value = WorkingContext(request="inspect config", context_package=self._package())
        bridge = ExecutionWorkingContextBridge(runtime)
        task = TaskRequest("inspect config", TaskType.INFORMATION)
        observation = self._observation()

        bridge.observe(task, observation)

        self.assertEqual(observation.state.next_allowed_actions, ("COMPLETE",))
        runtime.compose.assert_called_once()


if __name__ == "__main__":
    unittest.main()
