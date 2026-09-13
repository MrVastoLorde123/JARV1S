import unittest

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceService
from src.runtime.autonomous_job_resume import (
    AutonomousJobResumeBoundary,
    AutonomousJobResumeKind,
    AutonomousJobResumeRequest,
)
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_reasoning_feedback_pulse import AutonomousReasoningFeedbackPulse
from src.runtime.autonomous_reasoning_tool_feedback_cycle import AutonomousReasoningToolFeedbackCycleCoordinator
from src.runtime.autonomous_reasoning_tool_gate import AutonomousReasoningToolGate
from src.runtime.autonomous_reasoning_worker import AutonomousReasoningWorker
from src.runtime.autonomous_resume_reasoning_handoff import AutonomousResumeReasoningHandoff
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


class M65Tests(unittest.TestCase):
    def boundary(self):
        store = MemoryStore()
        persistence = AutonomousJobPersistenceService(store)
        return AutonomousJobResumeBoundary(persistence), persistence, store

    def persist_waiting(self, status):
        job = AutonomousJob("j65", "inspect system").start()
        if status is AutonomousJobStatus.WAITING_AUTHORIZATION:
            job = job.wait_for_authorization("authorization required")
        elif status is AutonomousJobStatus.WAITING_TOOL:
            job = job.wait_for_tool("tool confirmation required")
        elif status is AutonomousJobStatus.WAITING_INPUT:
            job = job.wait_for_input("input required")
        elif status is AutonomousJobStatus.PAUSED:
            job = job.pause("paused")
        else:
            raise AssertionError("unsupported test status")
        return job

    def test_authorization_wait_requires_explicit_confirmation_and_resumes(self):
        boundary, persistence, store = self.boundary()
        persistence.persist(self.persist_waiting(AutonomousJobStatus.WAITING_AUTHORIZATION))
        with self.assertRaises(PermissionError):
            boundary.resume(AutonomousJobResumeRequest("j65", AutonomousJobResumeKind.AUTHORIZATION))
        out = boundary.resume(AutonomousJobResumeRequest("j65", AutonomousJobResumeKind.AUTHORIZATION, confirmed=True))
        self.assertEqual(out.job.status, AutonomousJobStatus.RUNNING)
        self.assertEqual(store.jobs["j65"], out.job)
        self.assertEqual(out.persistence_receipt.revision, "r2")

    def test_tool_wait_requires_explicit_confirmation(self):
        boundary, persistence, _ = self.boundary()
        persistence.persist(self.persist_waiting(AutonomousJobStatus.WAITING_TOOL))
        with self.assertRaises(PermissionError):
            boundary.resume(AutonomousJobResumeRequest("j65", AutonomousJobResumeKind.TOOL))
        out = boundary.resume(AutonomousJobResumeRequest("j65", AutonomousJobResumeKind.TOOL, confirmed=True))
        self.assertEqual(out.job.status, AutonomousJobStatus.RUNNING)

    def test_input_wait_requires_and_applies_explicit_context(self):
        boundary, persistence, _ = self.boundary()
        persistence.persist(self.persist_waiting(AutonomousJobStatus.WAITING_INPUT))
        with self.assertRaises(ValueError):
            boundary.resume(AutonomousJobResumeRequest("j65", AutonomousJobResumeKind.INPUT))
        out = boundary.resume(AutonomousJobResumeRequest("j65", AutonomousJobResumeKind.INPUT, input_context={"answer": "ready"}))
        self.assertEqual(out.job.status, AutonomousJobStatus.RUNNING)
        self.assertEqual(out.job.working_context["answer"], "ready")

    def test_paused_job_requires_explicit_pause_resume(self):
        boundary, persistence, _ = self.boundary()
        persistence.persist(self.persist_waiting(AutonomousJobStatus.PAUSED))
        out = boundary.resume(AutonomousJobResumeRequest("j65", AutonomousJobResumeKind.PAUSE))
        self.assertEqual(out.job.status, AutonomousJobStatus.RUNNING)

    def test_resume_kind_must_match_persisted_state(self):
        boundary, persistence, _ = self.boundary()
        persistence.persist(self.persist_waiting(AutonomousJobStatus.WAITING_TOOL))
        with self.assertRaises(ValueError):
            boundary.resume(AutonomousJobResumeRequest("j65", AutonomousJobResumeKind.INPUT, input_context={"answer": "ready"}))


class M66Tests(unittest.TestCase):
    def handoff(self, confirm=True):
        store = MemoryStore()
        persistence = AutonomousJobPersistenceService(store)
        registry = ToolRegistry()
        registry.register(EchoTool(confirm))
        gate = AutonomousReasoningToolGate(registry, ToolService(registry))
        action = AutonomousReasoningAction("a66", AutonomousReasoningDisposition.TOOL_REQUEST, "inspect", tool_name="echo", arguments={"x": 1})
        coordinator = AutonomousReasoningToolFeedbackCycleCoordinator(AutonomousReasoningWorker(lambda job: action), gate)
        pulse = AutonomousReasoningFeedbackPulse(persistence, coordinator)
        return AutonomousResumeReasoningHandoff(persistence, pulse), persistence

    def test_confirmed_tool_resume_reenters_one_pulse(self):
        handoff, persistence = self.handoff(confirm=True)
        persistence.persist(AutonomousJob("j66", "inspect").start().wait_for_tool("confirmation"))
        out = handoff.resume_and_pulse(AutonomousJobResumeRequest("j66", AutonomousJobResumeKind.TOOL, confirmed=True))
        self.assertTrue(out.pulse.cycle.tool_executed)
        self.assertEqual(out.job.status, AutonomousJobStatus.RUNNING)

    def test_input_resume_reenters_one_pulse(self):
        handoff, persistence = self.handoff(confirm=False)
        persistence.persist(AutonomousJob("j66", "inspect").start().wait_for_input("detail"))
        out = handoff.resume_and_pulse(AutonomousJobResumeRequest("j66", AutonomousJobResumeKind.INPUT, input_context={"answer": "ready"}))
        self.assertIsNotNone(out.pulse.cycle)
        self.assertEqual(out.job.status, AutonomousJobStatus.RUNNING)
        self.assertEqual(out.job.working_context["answer"], "ready")


if __name__ == "__main__":
    unittest.main()
