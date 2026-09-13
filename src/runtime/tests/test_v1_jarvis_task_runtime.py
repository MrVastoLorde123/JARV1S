import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.ai.service import AIService
from src.runtime.jarvis_task_runtime import JARVISTaskRuntime


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


if __name__ == "__main__":
    unittest.main()
