import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceService
from src.runtime.autonomous_job_persistence_sqlite import SQLiteAutonomousJobStore
from src.runtime.autonomous_job_resume import AutonomousJobResumeKind, AutonomousJobResumeRequest
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_reasoning_feedback_pulse import AutonomousReasoningFeedbackPulse
from src.runtime.autonomous_reasoning_run_loop import AutonomousReasoningRunLoop
from src.runtime.autonomous_reasoning_tool_feedback_cycle import AutonomousReasoningToolFeedbackCycleCoordinator
from src.runtime.autonomous_reasoning_tool_gate import AutonomousReasoningToolGate
from src.runtime.autonomous_reasoning_worker import AutonomousReasoningWorker
from src.runtime.autonomous_resume_reasoning_handoff import AutonomousResumeReasoningHandoff
from src.runtime.autonomous_runtime_schedule_persistence import SQLiteAutonomousRuntimeScheduleStore
from src.runtime.autonomous_runtime_scheduler import AutonomousRuntimeScheduler
from src.tools.models import RiskLevel, ToolDefinition, ToolResult
from src.tools.protocol import ToolHandler
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService


class EchoTool(ToolHandler):
    def __init__(self, requires_confirmation=False):
        self.requires_confirmation = requires_confirmation
        self.executions = 0

    def definition(self):
        return ToolDefinition("echo", "Echo", "1.0", {}, {}, RiskLevel.LOW, self.requires_confirmation)

    def execute(self, request):
        self.executions += 1
        return ToolResult(True, request.tool_name, request.arguments, invocation_id=request.invocation_id)


class V1RuntimeRestartAcceptanceTests(unittest.TestCase):
    def make_runtime(self, directory, reason, *, requires_confirmation=False):
        path = Path(directory.name) / "jarvis.db"

        job_store = SQLiteAutonomousJobStore(lambda: sqlite3.connect(path))
        schedule_store = SQLiteAutonomousRuntimeScheduleStore(lambda: sqlite3.connect(path))
        persistence = AutonomousJobPersistenceService(job_store)
        registry = ToolRegistry()
        tool = EchoTool(requires_confirmation)
        registry.register(tool)
        gate = AutonomousReasoningToolGate(registry, ToolService(registry))
        worker = AutonomousReasoningWorker(reason)
        coordinator = AutonomousReasoningToolFeedbackCycleCoordinator(worker, gate)
        pulse = AutonomousReasoningFeedbackPulse(persistence, coordinator)
        run_loop = AutonomousReasoningRunLoop(pulse)
        scheduler = AutonomousRuntimeScheduler(schedule_store, run_loop)
        return persistence, scheduler, pulse, tool

    def test_runtime_continues_from_sqlite_state_after_restart(self):
        directory = tempfile.TemporaryDirectory()
        try:
            calls = {"count": 0}

            def reason(job):
                calls["count"] += 1
                if calls["count"] == 1:
                    return AutonomousReasoningAction(
                        "restart-tool",
                        AutonomousReasoningDisposition.TOOL_REQUEST,
                        "inspect with echo",
                        tool_name="echo",
                        arguments={"goal": job.goal},
                    )
                return AutonomousReasoningAction(
                    "restart-complete",
                    AutonomousReasoningDisposition.COMPLETE,
                    "resume completed",
                    result="restart-safe completion",
                )

            persistence1, scheduler1, _, tool1 = self.make_runtime(directory, reason)
            persistence1.persist(AutonomousJob.create("restart-safe goal", job_id="restart").start())
            scheduler1.schedule("restart", next_due=1, interval=5)
            first = scheduler1.tick(1)[0]
            self.assertEqual(first.run.job.status, AutonomousJobStatus.RUNNING)
            self.assertEqual(first.run.job.working_context["tool_result"]["tool_name"], "echo")
            self.assertEqual(tool1.executions, 1)

            persistence2, scheduler2, _, tool2 = self.make_runtime(directory, reason)
            restored = persistence2.restore("restart")
            self.assertEqual(restored.status, AutonomousJobStatus.RUNNING)
            self.assertEqual(restored.step_count, 1)
            second = scheduler2.tick(6)[0]

            self.assertTrue(second.removed)
            self.assertEqual(second.run.job.status, AutonomousJobStatus.COMPLETED)
            self.assertEqual(second.run.job.result, "restart-safe completion")
            self.assertEqual(second.run.job.step_count, 2)
            self.assertEqual(tool2.executions, 0)
            self.assertEqual(calls["count"], 2)
            self.assertIsNone(SQLiteAutonomousRuntimeScheduleStore(lambda: sqlite3.connect(Path(directory.name) / "jarvis.db")).load_due(100))
        finally:
            directory.cleanup()

    def test_waiting_authorization_survives_restart_without_implicit_execution(self):
        directory = tempfile.TemporaryDirectory()
        try:
            action = AutonomousReasoningAction(
                "protected",
                AutonomousReasoningDisposition.TOOL_REQUEST,
                "protected echo",
                tool_name="echo",
                arguments={"value": "protected"},
            )

            persistence1, scheduler1, _, tool1 = self.make_runtime(directory, lambda job: action, requires_confirmation=True)
            persistence1.persist(AutonomousJob.create("protected goal", job_id="protected").start())
            scheduler1.schedule("protected", next_due=1, interval=5)
            blocked = scheduler1.tick(1)[0]
            self.assertEqual(blocked.run.job.status, AutonomousJobStatus.WAITING_TOOL)
            self.assertEqual(tool1.executions, 0)

            persistence2, scheduler2, pulse2, tool2 = self.make_runtime(directory, lambda job: action, requires_confirmation=True)
            restored = persistence2.restore("protected")
            self.assertEqual(restored.status, AutonomousJobStatus.WAITING_TOOL)
            self.assertEqual(tool2.executions, 0)
            self.assertEqual(scheduler2.tick(6), ())
            self.assertEqual(tool2.executions, 0)

            handoff = AutonomousResumeReasoningHandoff(persistence2, pulse2)
            resumed = handoff.resume_and_pulse(
                AutonomousJobResumeRequest("protected", AutonomousJobResumeKind.TOOL, confirmed=True)
            )
            self.assertTrue(resumed.pulse.cycle.tool_executed)
            self.assertEqual(tool2.executions, 1)
            self.assertEqual(resumed.job.status, AutonomousJobStatus.RUNNING)
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
