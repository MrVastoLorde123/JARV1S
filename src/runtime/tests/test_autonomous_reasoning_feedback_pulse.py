import unittest

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceService
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_reasoning_feedback_pulse import AutonomousReasoningFeedbackPulse
from src.runtime.autonomous_reasoning_tool_feedback_cycle import AutonomousReasoningToolFeedbackCycleCoordinator
from src.runtime.autonomous_reasoning_tool_gate import AutonomousReasoningToolGate
from src.runtime.autonomous_reasoning_worker import AutonomousReasoningWorker
from src.tools.models import RiskLevel, ToolDefinition, ToolResult
from src.tools.protocol import ToolHandler
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService


class MemoryStore:
    def __init__(self):
        self.jobs = {}
        self.revision = 0

    def save(self, job):
        self.revision += 1
        self.jobs[job.job_id] = job
        return f"r{self.revision}"

    def load(self, job_id):
        return self.jobs.get(job_id)


class EchoTool(ToolHandler):
    def __init__(self, confirm=False):
        self.confirm = confirm

    def definition(self):
        return ToolDefinition("echo", "Echo", "1.0", {}, {}, RiskLevel.LOW, self.confirm)

    def execute(self, request):
        return ToolResult(True, request.tool_name, request.arguments, invocation_id=request.invocation_id)


class M64Tests(unittest.TestCase):
    def pulse(self, *, confirm=False, action=None):
        registry = ToolRegistry()
        registry.register(EchoTool(confirm))
        gate = AutonomousReasoningToolGate(registry, ToolService(registry))
        action = action or AutonomousReasoningAction(
            "a64",
            AutonomousReasoningDisposition.TOOL_REQUEST,
            "inspect",
            tool_name="echo",
            arguments={"x": 1},
        )
        coordinator = AutonomousReasoningToolFeedbackCycleCoordinator(
            AutonomousReasoningWorker(lambda job: action), gate
        )
        store = MemoryStore()
        persistence = AutonomousJobPersistenceService(store)
        return AutonomousReasoningFeedbackPulse(persistence, coordinator), persistence, store

    def test_queued_job_starts_runs_feedback_and_persists_running_state(self):
        pulse, persistence, store = self.pulse()
        job = AutonomousJob("j64", "inspect system")
        persistence.persist(job)

        out = pulse.pulse("j64")

        self.assertEqual(out.job.status, AutonomousJobStatus.RUNNING)
        self.assertTrue(out.progressed)
        self.assertIsNotNone(out.persistence_receipt)
        self.assertEqual(store.jobs["j64"], out.job)
        self.assertEqual(out.job.steps[-1].context_delta["tool_result"]["content"]["x"], 1)

    def test_confirmation_required_persists_waiting_for_tool(self):
        pulse, persistence, store = self.pulse(confirm=True)
        persistence.persist(AutonomousJob("j64", "inspect system"))

        out = pulse.pulse("j64")

        self.assertEqual(out.job.status, AutonomousJobStatus.WAITING_TOOL)
        self.assertTrue(out.waiting)
        self.assertEqual(store.jobs["j64"], out.job)
        self.assertIsNotNone(out.persistence_receipt)

    def test_terminal_job_is_not_reexecuted(self):
        pulse, persistence, store = self.pulse()
        job = AutonomousJob("j64", "inspect system").start().complete("already done")
        receipt = persistence.persist(job)

        out = pulse.pulse("j64")

        self.assertEqual(out.job, job)
        self.assertFalse(out.progressed)
        self.assertIsNone(out.cycle)
        self.assertIsNone(out.persistence_receipt)
        self.assertEqual(store.jobs["j64"], job)
        self.assertEqual(receipt.revision, "r1")

    def test_missing_job_is_rejected(self):
        pulse, _, _ = self.pulse()
        with self.assertRaises(LookupError):
            pulse.pulse("missing")


if __name__ == "__main__":
    unittest.main()
