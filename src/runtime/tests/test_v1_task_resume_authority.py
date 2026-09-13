import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_job import AutonomousJobStatus
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_task_runtime import SQLiteAutonomousTaskRuntime


class V1TaskResumeAuthorityTests(unittest.TestCase):
    def _runtime(self, directory):
        path = Path(directory.name) / "jarvis.db"
        return SQLiteAutonomousTaskRuntime(
            lambda job: AutonomousReasoningAction("continue", AutonomousReasoningDisposition.CONTINUE, "continue"),
            connection_factory=lambda: sqlite3.connect(path),
        )

    def test_authorization_resume_requires_confirmation(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            runtime = self._runtime(directory)
            runtime.submit("authorized task", now=1, interval=5, job_id="resume-auth")
            waiting = runtime.inspect("resume-auth").start().wait_for_authorization("approval required")
            runtime.job_store.save(waiting)
            with self.assertRaises(PermissionError):
                runtime.resume("resume-auth", now=2, interval=5)
            resumed = runtime.resume("resume-auth", now=2, interval=5, confirmed=True)
            self.assertEqual(resumed.job.status, AutonomousJobStatus.RUNNING)
        finally:
            directory.cleanup()

    def test_tool_resume_requires_confirmation(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            runtime = self._runtime(directory)
            runtime.submit("tool task", now=1, interval=5, job_id="resume-tool")
            waiting = runtime.inspect("resume-tool").start().wait_for_tool("tool completion required")
            runtime.job_store.save(waiting)
            with self.assertRaises(PermissionError):
                runtime.resume("resume-tool", now=2, interval=5)
            resumed = runtime.resume("resume-tool", now=2, interval=5, confirmed=True)
            self.assertEqual(resumed.job.status, AutonomousJobStatus.RUNNING)
        finally:
            directory.cleanup()

    def test_input_resume_requires_non_empty_context(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            runtime = self._runtime(directory)
            runtime.submit("input task", now=1, interval=5, job_id="resume-input")
            waiting = runtime.inspect("resume-input").start().wait_for_input("input required")
            runtime.job_store.save(waiting)
            with self.assertRaises(ValueError):
                runtime.resume("resume-input", now=2, interval=5)
            with self.assertRaises(ValueError):
                runtime.resume("resume-input", now=2, interval=5, input_context={})
            resumed = runtime.resume("resume-input", now=2, interval=5, input_context={"answer": "ready"})
            self.assertEqual(resumed.job.status, AutonomousJobStatus.RUNNING)
            self.assertEqual(resumed.job.working_context["answer"], "ready")
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()
