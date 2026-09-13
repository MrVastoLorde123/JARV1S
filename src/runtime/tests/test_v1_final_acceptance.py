import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_job import AutonomousJobStatus
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_task_plan import AutonomousTaskPlan
from src.runtime.autonomous_task_runtime import SQLiteAutonomousTaskRuntime
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest, ToolResult
from src.tools.registry import ToolRegistry


class _InventoryTool:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="inventory_probe",
            description="Deterministic V1 acceptance tool",
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
            content={"devices": 1},
            invocation_id=request.invocation_id,
        )


class V1FinalAcceptanceTests(unittest.TestCase):
    def test_one_task_survives_wait_resume_restart_and_finishes_under_runtime_authority(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            path = Path(directory.name) / "jarvis.db"
            registry = ToolRegistry()
            tool = _InventoryTool()
            registry.register(tool)
            calls = {"count": 0}

            def reason(job):
                calls["count"] += 1
                if calls["count"] == 1:
                    return AutonomousReasoningAction(
                        "inventory-tool",
                        AutonomousReasoningDisposition.TOOL_REQUEST,
                        "inspect devices",
                        tool_name="inventory_probe",
                        arguments={"site": "lab"},
                        metadata={
                            "task_ownership": {
                                "remaining_work": ["inspect devices", "publish inventory"],
                                "next_action": "inspect devices",
                            }
                        },
                    )
                if calls["count"] == 2:
                    return AutonomousReasoningAction(
                        "inventory-tool-again",
                        AutonomousReasoningDisposition.TOOL_REQUEST,
                        "inspect devices with the approved request",
                        tool_name="inventory_probe",
                        arguments={"site": "lab"},
                    )
                if calls["count"] == 3:
                    return AutonomousReasoningAction(
                        "publish",
                        AutonomousReasoningDisposition.CONTINUE,
                        "publish inventory",
                        metadata={
                            "task_ownership": {
                                "remaining_work": [],
                                "next_action": None,
                            }
                        },
                    )
                return AutonomousReasoningAction(
                    "complete",
                    AutonomousReasoningDisposition.COMPLETE,
                    "all planned work is complete",
                    result="inventory published",
                    metadata={
                        "task_ownership": {
                            "remaining_work": [],
                            "next_action": None,
                        }
                    },
                )

            def make_runtime():
                return SQLiteAutonomousTaskRuntime(
                    reason,
                    connection_factory=lambda: sqlite3.connect(path),
                    registry=registry,
                )

            runtime1 = make_runtime()
            runtime1.submit("inspect and publish lab inventory", now=1, interval=5, job_id="v1-final")
            runtime1.set_plan("v1-final", AutonomousTaskPlan.from_descriptions(["inspect devices", "publish inventory"]))

            first = runtime1.tick(1)[0]
            self.assertEqual(first.run.job.status, AutonomousJobStatus.WAITING_TOOL)
            self.assertEqual(tool.calls, [])

            resumed = runtime1.resume("v1-final", now=2, interval=5, confirmed=True)
            self.assertEqual(resumed.job.status, AutonomousJobStatus.RUNNING)

            runtime1.start_plan_step("v1-final", "step-1")
            second = runtime1.tick(2)[0]
            self.assertEqual(second.run.job.status, AutonomousJobStatus.RUNNING)
            self.assertEqual(tool.calls, [{"site": "lab"}])
            runtime1.complete_plan_step("v1-final", "step-1", reason="inventory probe completed")

            runtime2 = make_runtime()
            restored = runtime2.snapshot("v1-final")
            self.assertIsNotNone(restored)
            self.assertEqual(restored.job.step_count, 2)
            self.assertEqual(restored.ownership.remaining_work, ())
            self.assertEqual(restored.plan.current.step_id, "step-2")

            runtime2.start_plan_step("v1-final", "step-2")
            runtime2.complete_plan_step("v1-final", "step-2", reason="inventory published")
            third = runtime2.tick(7)[0]

            self.assertTrue(third.removed)
            self.assertEqual(third.run.job.status, AutonomousJobStatus.COMPLETED)
            self.assertEqual(third.run.job.result, "inventory published")
            self.assertTrue(runtime2.snapshot("v1-final").plan_complete)
            self.assertTrue(runtime2.snapshot("v1-final").ownership.complete)
            self.assertEqual(tool.calls, [{"site": "lab"}])
            self.assertEqual(calls["count"], 4)
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()
