import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from src.context.models import ContextItem, ContextPackage, OBSERVATION
from src.context.working_context import WorkingContext
from src.context.working_context_composer import WorkingContextComposer
from src.context.jarvis_working_context import JARVISWorkingContextRuntime
from src.core.conversation_models import StateSnapshot
from src.core.task_models import TaskRequest, TaskType


class FakeConversation:
    def __init__(self):
        self.snapshot_value = StateSnapshot(
            conversation_id="conversation-1",
            created_at="2026-09-01T00:00:00Z",
            updated_at="2026-09-01T00:01:00Z",
            turns=(),
            active_topic="JARVIS",
            active_task="inspect configuration",
        )

    def snapshot(self):
        return self.snapshot_value


class JARVISWorkingContextRuntimeTests(unittest.TestCase):
    def _package(self):
        return ContextPackage(
            request="inspect configuration",
            items=(ContextItem("MEMORY", "JARVIS configuration is under src/core"),),
            instructions=("Do not invent information.",),
            metadata={"memory_count": 1},
        )

    def _runtime(self, jarvis):
        builder = Mock(return_value=self._package())
        composer = WorkingContextComposer(builder)
        return JARVISWorkingContextRuntime(jarvis, composer=composer)

    def test_runtime_uses_jarvis_owned_conversation_and_options(self):
        jarvis = SimpleNamespace(
            context_options=SimpleNamespace(name="options"),
            conversation=FakeConversation(),
        )
        runtime = self._runtime(jarvis)

        task = TaskRequest("inspect configuration", TaskType.INFORMATION)
        result = runtime.compose(
            "inspect configuration",
            task=task,
            observations=("configuration file observed",),
        )

        self.assertIsInstance(result, WorkingContext)
        self.assertIs(result.conversation_state, jarvis.conversation.snapshot_value)
        self.assertIs(result.task, task)
        self.assertEqual(result.observations[0].content, "configuration file observed")

    def test_runtime_preserves_composer_output(self):
        package = self._package()
        working = WorkingContext(
            request="inspect configuration",
            context_package=package,
            observations=(ContextItem(OBSERVATION, "file observed"),),
        )
        builder = Mock(return_value=package)
        composer = WorkingContextComposer(builder)
        jarvis = SimpleNamespace(
            context_options=SimpleNamespace(),
            conversation=FakeConversation(),
        )
        runtime = JARVISWorkingContextRuntime(jarvis, composer=composer)

        result = runtime.compose("inspect configuration")
        self.assertIsInstance(result, WorkingContext)
        self.assertEqual(result.request, working.request)
        self.assertIs(result.context_package, package)

    def test_runtime_rejects_missing_conversation(self):
        jarvis = SimpleNamespace(context_options=SimpleNamespace())
        runtime = JARVISWorkingContextRuntime(jarvis)

        with self.assertRaises(AttributeError):
            runtime.compose("inspect configuration")


if __name__ == "__main__":
    unittest.main()
