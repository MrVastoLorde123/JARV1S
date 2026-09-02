import unittest
from unittest.mock import Mock

from src.context.models import ContextItem, ContextPackage, OBSERVATION, PRIVATE
from src.context.working_context import WorkingContext
from src.context.working_context_composer import WorkingContextComposer
from src.core.conversation_models import StateSnapshot, Turn
from src.core.execution_executor_models import PlanExecutionStatus
from src.core.execution_state import ExecutionState
from src.core.execution_progress import ExecutionProgress
from src.core.task_models import TaskRequest, TaskType


class WorkingContextTests(unittest.TestCase):
    def _package(self):
        return ContextPackage(
            request="find the config",
            items=(ContextItem(source_type="MEMORY", content="JARVIS config lives in src/core"),),
            instructions=("Do not invent information.",),
            metadata={"memory_count": 1},
        )

    def _state(self):
        return StateSnapshot(
            conversation_id="conversation-1",
            created_at="2026-09-01T00:00:00Z",
            updated_at="2026-09-01T00:01:00Z",
            turns=(Turn("user", "find the config", "2026-09-01T00:01:00Z"),),
            active_topic="JARVIS",
            active_task="inspect configuration",
        )

    def _execution_state(self):
        return ExecutionState(
            goal="find the config",
            plan_id="plan-1",
            status=PlanExecutionStatus.COMPLETED,
            completed_steps=("inspect",),
            next_allowed_actions=("COMPLETE",),
        )

    def test_composer_preserves_existing_context_package_and_adds_working_sources(self):
        builder = Mock(return_value=self._package())
        composer = WorkingContextComposer(builder)
        state = self._state()
        task = TaskRequest("find the config", TaskType.INFORMATION)
        execution = self._execution_state()
        progress = ExecutionProgress.from_state(execution)

        working = composer.compose(
            "find the config",
            conversation_state=state,
            task=task,
            execution_state=execution,
            execution_progress=progress,
            observations=("config file observed",),
        )

        self.assertIsInstance(working, WorkingContext)
        self.assertIs(working.context_package, builder.return_value)
        self.assertIs(working.conversation_state, state)
        self.assertIs(working.task, task)
        self.assertIs(working.execution_state, execution)
        self.assertIs(working.execution_progress, progress)
        self.assertEqual(len(working.observations), 1)
        self.assertEqual(working.observations[0].source_type, OBSERVATION)
        self.assertEqual(working.observations[0].privacy_level, PRIVATE)
        builder.assert_called_once()

    def test_to_context_is_provider_neutral_and_contains_all_sources(self):
        composer = WorkingContextComposer(lambda *args, **kwargs: self._package())
        task = TaskRequest("find the config", TaskType.INFORMATION, {"source": "user"})
        execution = self._execution_state()
        progress = ExecutionProgress.from_state(execution)

        working = composer.compose(
            "find the config",
            conversation_state=self._state(),
            task=task,
            execution_state=execution,
            execution_progress=progress,
            observations=(ContextItem(OBSERVATION, "file exists"),),
        )
        context = working.to_context()

        self.assertEqual(context["request"], "find the config")
        self.assertEqual(context["context"]["items"][0]["source_type"], "MEMORY")
        self.assertEqual(context["conversation_state"]["active_task"], "inspect configuration")
        self.assertEqual(context["task"]["task_type"], "INFORMATION")
        self.assertEqual(context["execution_state"]["status"], "COMPLETED")
        self.assertEqual(context["execution_progress"]["attempt_count"], 1)
        self.assertEqual(context["observations"][0]["content"], "file exists")

    def test_composer_rejects_empty_request(self):
        composer = WorkingContextComposer(lambda *args, **kwargs: self._package())
        with self.assertRaises(ValueError):
            composer.compose("   ")

    def test_working_context_rejects_mismatched_execution_goal(self):
        execution = ExecutionState(
            goal="different goal",
            plan_id="plan-2",
            status=PlanExecutionStatus.COMPLETED,
            completed_steps=("inspect",),
            next_allowed_actions=("COMPLETE",),
        )
        progress = ExecutionProgress.from_state(execution)
        with self.assertRaises(ValueError):
            WorkingContext(
                request="find the config",
                context_package=self._package(),
                execution_state=self._execution_state(),
                execution_progress=progress,
            )


if __name__ == "__main__":
    unittest.main()
