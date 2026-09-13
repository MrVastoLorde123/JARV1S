import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.ai.models import AICapabilities, AIResponse
from src.ai.provider import AIProvider
from src.ai.service import AIService
from src.runtime.jarvis_task_runtime import JARVISTaskRuntime


class _ScriptedProvider(AIProvider):
    def __init__(self) -> None:
        self.calls = []
        self.responses = [
            {"action_id": "cycle-1", "disposition": "continue", "rationale": "keep working"},
            {"action_id": "cycle-2", "disposition": "complete", "rationale": "finished", "result": "done"},
        ]

    def provider_name(self) -> str:
        return "scripted-v1"

    def capabilities(self) -> AICapabilities:
        return AICapabilities(text_generation=True, structured_output=True)

    def generate(self, request):
        self.calls.append(request)
        return AIResponse(
            content=self.responses[len(self.calls) - 1],
            provider=self.provider_name(),
            model="scripted",
        )


class V1JARVISTaskRuntimeTests(unittest.TestCase):
    def test_runtime_composes_ai_reasoning_with_durable_task_runtime(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            service = object.__new__(AIService)
            path = Path(directory.name) / "jarvis.db"
            runtime = JARVISTaskRuntime(service, connection_factory=lambda: sqlite3.connect(path))
            submitted = runtime.submit("test durable JARVIS goal", now=1, interval=5, job_id="jarvis-runtime")
            self.assertEqual(submitted.job.goal, "test durable JARVIS goal")
            self.assertIsNotNone(runtime.inspect("jarvis-runtime"))
        finally:
            directory.cleanup()

    def test_real_ai_service_path_drives_durable_task_cycles(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            path = Path(directory.name) / "jarvis.db"
            provider = _ScriptedProvider()
            service = AIService()
            service.register_provider(provider)
            service.set_default_provider("scripted-v1")
            runtime = JARVISTaskRuntime(
                service,
                connection_factory=lambda: sqlite3.connect(path),
            )

            runtime.submit("complete through AIService", now=1, interval=5, job_id="jarvis-real")
            first = runtime.tick(1)[0]
            self.assertEqual(first.run.job.step_count, 1)
            self.assertEqual(first.run.job.status.value, "RUNNING")

            second = runtime.tick(6)[0]
            self.assertTrue(second.removed)
            self.assertEqual(second.run.job.status.value, "COMPLETED")
            self.assertEqual(second.run.job.result, "done")
            self.assertEqual(len(provider.calls), 2)
            self.assertEqual(provider.calls[0].context["job_id"], "jarvis-real")
            self.assertEqual(provider.calls[1].context["step_count"], 1)
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
