import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_job import AutonomousJobStatus
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_task_runtime import SQLiteAutonomousTaskRuntime
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest, ToolResult
from src.tools.registry import ToolRegistry


class _ConfirmedTool:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="confirmed_probe",
            description="Deterministic V1 continuation test tool",
            version="1.0.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            risk_level=RiskLevel.LOW,
            requires_confirmation=True,
        )

    def execute(self, request: ToolRequest) -> ToolResult:
        self.calls.append(dict(request.arguments))
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content={"ok": True, "arguments": dict(request.arguments)},
            invocation_id=request.invocation_id,
        )


class V1TaskToolResumeContinuationTests(unittest.TestCase):
    def test_confirmed_tool_resume_executes_once_then_continues_after_restart(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            path = Path(directory.name) / "jarvis.db"
            tool = _ConfirmedTool()
            registry = ToolRegistry()
            registry.register(tool)
            calls = {"count": 0}

            def reason(job):
                calls["count"] += 1
                if calls["count"] == 1:
                    return AutonomousReasoningAction(
                        "request-tool",
                        AutonomousReasoningDisposition.TOOL_REQUEST,
                        "inspect the confirmed probe",
                        tool_name="confirmed_probe",
                        arguments={"probe": "v1"},
                    )
                if calls["count"] == 2:
                    return AutonomousReasoningAction(
                        "execute-tool",
                        AutonomousReasoningDisposition.TOOL_REQUEST,
                        "reuse the confirmed probe after resume",
                        tool_name="confirmed_probe",
                        arguments={"probe": "v1"},
                    )
                return AutonomousReasoningAction(
                    "finish",
                    AutonomousReasoningDisposition.COMPLETE,
                    "tool feedback was consumed",
                    result="done",
                )

            def make_runtime():
                return SQLiteAutonomousTaskRuntime(
                    reason,
                    connection_factory=lambda: sqlite3.connect(path),
                    registry=registry,
                )

            runtime1 = make_runtime()
            runtime1.submit("complete confirmed tool task", now=1, interval=5, job_id="tool-task")

            first = runtime1.tick(1)[0]
            self.assertEqual(first.run.job.status, AutonomousJobStatus.WAITING_TOOL)
            self.assertEqual(tool.calls, [])

            resumed = runtime1.resume("tool-task", now=2, interval=5, confirmed=True)
            self.assertEqual(resumed.job.status, AutonomousJobStatus.RUNNING)
            self.assertEqual(resumed.job.working_context["_runtime_resume_authorization"], "TOOL")

            second = runtime1.tick(2)[0]
            self.assertEqual(second.run.job.status, AutonomousJobStatus.RUNNING)
            self.assertEqual(tool.calls, [{"probe": "v1"}])
            self.assertIsNone(second.run.job.working_context["_runtime_resume_authorization"])

            runtime2 = make_runtime()
            restored = runtime2.inspect("tool-task")
            self.assertIsNotNone(restored)
            self.assertEqual(restored.step_count, 2)

            third = runtime2.tick(7)[0]
            self.assertTrue(third.removed)
            self.assertEqual(third.run.job.status, AutonomousJobStatus.COMPLETED)
            self.assertEqual(third.run.job.result, "done")
            self.assertEqual(tool.calls, [{"probe": "v1"}])
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
