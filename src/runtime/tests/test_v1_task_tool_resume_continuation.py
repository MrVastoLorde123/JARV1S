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
    def __init__(self, name: str = "confirmed_probe") -> None:
        self.calls: list[dict[str, object]] = []
        self.name = name

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name=self.name,
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
    def make_runtime(self, path, registry, reason):
        return SQLiteAutonomousTaskRuntime(
            reason,
            connection_factory=lambda: sqlite3.connect(path),
            registry=registry,
        )

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

            runtime1 = self.make_runtime(path, registry, reason)
            runtime1.submit("complete confirmed tool task", now=1, interval=5, job_id="tool-task")

            first = runtime1.tick(1)[0]
            self.assertEqual(first.run.job.status, AutonomousJobStatus.WAITING_TOOL)
            self.assertEqual(tool.calls, [])

            resumed = runtime1.resume("tool-task", now=2, interval=5, confirmed=True)
            self.assertEqual(resumed.job.status, AutonomousJobStatus.RUNNING)
            authorization = resumed.job.working_context["_runtime_resume_authorization"]
            self.assertEqual(authorization["kind"], "TOOL")
            self.assertTrue(authorization["request_fingerprint"])

            second = runtime1.tick(2)[0]
            self.assertEqual(second.run.job.status, AutonomousJobStatus.RUNNING)
            self.assertEqual(tool.calls, [{"probe": "v1"}])
            self.assertIsNone(second.run.job.working_context["_runtime_resume_authorization"])

            runtime2 = self.make_runtime(path, registry, reason)
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

    def test_confirmed_resume_cannot_authorize_a_changed_tool_request(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            path = Path(directory.name) / "jarvis.db"
            confirmed_tool = _ConfirmedTool("confirmed_probe")
            other_tool = _ConfirmedTool("other_probe")
            registry = ToolRegistry()
            registry.register(confirmed_tool)
            registry.register(other_tool)
            calls = {"count": 0}

            def reason(job):
                calls["count"] += 1
                if calls["count"] == 1:
                    return AutonomousReasoningAction(
                        "request-tool",
                        AutonomousReasoningDisposition.TOOL_REQUEST,
                        "inspect the confirmed probe",
                        tool_name="confirmed_probe",
                        arguments={"probe": "approved"},
                    )
                return AutonomousReasoningAction(
                    "changed-tool",
                    AutonomousReasoningDisposition.TOOL_REQUEST,
                    "switch to another tool after resume",
                    tool_name="other_probe",
                    arguments={"probe": "changed"},
                )

            runtime = self.make_runtime(path, registry, reason)
            runtime.submit("reject changed tool authorization", now=1, interval=5, job_id="changed-tool")
            self.assertEqual(runtime.tick(1)[0].run.job.status, AutonomousJobStatus.WAITING_TOOL)

            runtime.resume("changed-tool", now=2, interval=5, confirmed=True)
            result = runtime.tick(2)[0]

            self.assertEqual(result.run.job.status, AutonomousJobStatus.WAITING_TOOL)
            self.assertEqual(confirmed_tool.calls, [])
            self.assertEqual(other_tool.calls, [])
            self.assertEqual(result.run.job.working_context.get("pending_tool_request", {}).get("tool_name"), "other_probe")
        finally:
            directory.cleanup()

    def test_resume_authorization_is_consumed_before_provider_failure(self) -> None:
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
                raise RuntimeError("provider unavailable")

            runtime = self.make_runtime(path, registry, reason)
            runtime.submit("consume authorization before failure", now=1, interval=5, job_id="failure-consume")
            self.assertEqual(runtime.tick(1)[0].run.job.status, AutonomousJobStatus.WAITING_TOOL)

            runtime.resume("failure-consume", now=2, interval=5, confirmed=True)
            failed = runtime.tick(2)[0]
            self.assertIsNone(failed.run)

            restored = runtime.inspect("failure-consume")
            self.assertIsNone(restored.working_context.get("_runtime_resume_authorization"))
            self.assertEqual(tool.calls, [])
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
