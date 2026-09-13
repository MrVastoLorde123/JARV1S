import unittest

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceService
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_reasoning_feedback_pulse import AutonomousReasoningFeedbackPulse
from src.runtime.autonomous_reasoning_run_loop import AutonomousReasoningRunLoop
from src.runtime.autonomous_reasoning_tool_feedback_cycle import AutonomousReasoningToolFeedbackCycleCoordinator
from src.runtime.autonomous_reasoning_tool_gate import AutonomousReasoningToolGate
from src.runtime.autonomous_reasoning_worker import AutonomousReasoningWorker
from src.runtime.autonomous_resume_reasoning_handoff import AutonomousResumeReasoningHandoff
from src.runtime.autonomous_job_resume import AutonomousJobResumeKind, AutonomousJobResumeRequest
from src.runtime.autonomous_runtime_scheduler import AutonomousRuntimeSchedule, AutonomousRuntimeScheduler
from src.tools.models import RiskLevel, ToolDefinition, ToolResult
from src.tools.protocol import ToolHandler
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService


class MemoryRuntimeStore:
    def __init__(self):
        self.jobs = {}
        self.schedule = None
        self.claim_number = 0

    def save(self, value):
        if isinstance(value, AutonomousJob):
            self.jobs[value.job_id] = value
        else:
            self.schedule = value
        return f"r{len(self.jobs)}"

    def load(self, job_id):
        return self.jobs.get(job_id)

    def load_due(self, now):
        if self.schedule is None or self.schedule.next_due > now:
            return []
        return [self.schedule]

    def claim(self, schedule, now, lease_seconds):
        self.claim_number += 1
        token = f"claim-{self.claim_number}"
        self.schedule = AutonomousRuntimeSchedule(
            schedule.job_id,
            schedule.next_due,
            schedule.interval,
            claim_token=token,
            lease_until=now + lease_seconds,
            failure_count=schedule.failure_count,
            last_failure=schedule.last_failure,
            last_failure_at=schedule.last_failure_at,
        )
        return token

    def complete_claim(self, schedule, claim_token, replacement):
        if self.schedule is None or self.schedule.claim_token != claim_token:
            return False
        self.schedule = replacement
        return True


class EchoTool(ToolHandler):
    def __init__(self, requires_confirmation=False):
        self.requires_confirmation = requires_confirmation
        self.executions = 0

    def definition(self):
        return ToolDefinition("echo", "Echo", "1.0", {}, {}, RiskLevel.LOW, self.requires_confirmation)

    def execute(self, request):
        self.executions += 1
        return ToolResult(True, request.tool_name, request.arguments, invocation_id=request.invocation_id)


class V1RuntimeAcceptanceTests(unittest.TestCase):
    def build_runtime(self, reason, *, requires_confirmation=False):
        store = MemoryRuntimeStore()
        persistence = AutonomousJobPersistenceService(store)
        registry = ToolRegistry()
        tool = EchoTool(requires_confirmation)
        registry.register(tool)
        gate = AutonomousReasoningToolGate(registry, ToolService(registry))
        worker = AutonomousReasoningWorker(reason)
        coordinator = AutonomousReasoningToolFeedbackCycleCoordinator(worker, gate)
        pulse = AutonomousReasoningFeedbackPulse(persistence, coordinator)
        return store, persistence, tool, pulse, AutonomousReasoningRunLoop(pulse)

    def test_goal_persists_schedules_executes_tool_learns_from_feedback_and_completes(self):
        calls = {"count": 0}

        def reason(job):
            calls["count"] += 1
            if calls["count"] == 1:
                return AutonomousReasoningAction("a-v1-tool", AutonomousReasoningDisposition.TOOL_REQUEST, "inspect with echo", tool_name="echo", arguments={"goal": job.goal})
            return AutonomousReasoningAction("a-v1-complete", AutonomousReasoningDisposition.COMPLETE, "tool feedback was incorporated", result="V1 goal completed")

        store, persistence, tool, _, run_loop = self.build_runtime(reason)
        persistence.persist(AutonomousJob.create("inspect system", job_id="v1").start())
        scheduler = AutonomousRuntimeScheduler(store, run_loop)
        scheduler.schedule("v1", next_due=1, interval=5)

        first = scheduler.tick(1)[0]
        self.assertIsNotNone(first.run)
        self.assertEqual(first.run.job.status, AutonomousJobStatus.RUNNING)
        self.assertEqual(first.run.job.step_count, 1)
        self.assertEqual(first.run.job.working_context["tool_result"]["tool_name"], "echo")
        self.assertEqual(tool.executions, 1)
        self.assertIsNotNone(store.schedule)
        self.assertEqual(store.jobs["v1"].status, AutonomousJobStatus.RUNNING)

        second = scheduler.tick(6)[0]
        self.assertIsNotNone(second.run)
        self.assertTrue(second.removed)
        self.assertEqual(second.run.job.status, AutonomousJobStatus.COMPLETED)
        self.assertEqual(second.run.job.result, "V1 goal completed")
        self.assertEqual(second.run.job.step_count, 2)
        self.assertIsNone(store.schedule)
        self.assertEqual(calls["count"], 2)

    def test_confirmation_remains_an_explicit_authority_boundary(self):
        action = AutonomousReasoningAction("a-v1-confirm", AutonomousReasoningDisposition.TOOL_REQUEST, "run confirmed tool", tool_name="echo", arguments={"value": "protected"})
        _, persistence, tool, pulse, run_loop = self.build_runtime(lambda job: action, requires_confirmation=True)
        persistence.persist(AutonomousJob.create("protected action", job_id="confirm").start())

        blocked = run_loop.run("confirm", max_pulses=1)
        self.assertTrue(blocked.pulses[0].waiting)
        self.assertEqual(blocked.job.status, AutonomousJobStatus.WAITING_TOOL)
        self.assertEqual(tool.executions, 0)
        self.assertFalse(persistence.restore("confirm").to_dict()["authority_granted"])

        handoff = AutonomousResumeReasoningHandoff(persistence, pulse)
        resumed = handoff.resume_and_pulse(AutonomousJobResumeRequest("confirm", AutonomousJobResumeKind.TOOL, confirmed=True))
        self.assertTrue(resumed.pulse.cycle.tool_executed)
        self.assertEqual(resumed.job.status, AutonomousJobStatus.RUNNING)
        self.assertEqual(tool.executions, 1)

    def test_scheduler_failure_is_observable_and_becomes_retryable_state(self):
        class FailingRunLoop(AutonomousReasoningRunLoop):
            def __init__(self):
                pass
            def run(self, job_id, *, max_pulses=1):
                raise RuntimeError("simulated worker failure")

        store = MemoryRuntimeStore()
        persistence = AutonomousJobPersistenceService(store)
        persistence.persist(AutonomousJob.create("recoverable goal", job_id="failure").start())
        scheduler = AutonomousRuntimeScheduler(store, FailingRunLoop())
        scheduler.schedule("failure", next_due=10, interval=5)

        out = scheduler.tick(10)[0]
        self.assertIsNone(out.run)
        self.assertFalse(out.removed)
        self.assertEqual(out.failure, "RuntimeError: simulated worker failure")
        self.assertEqual(store.schedule.failure_count, 1)
        self.assertEqual(store.schedule.last_failure, "RuntimeError: simulated worker failure")
        self.assertEqual(store.schedule.next_due, 15)
        self.assertEqual(store.jobs["failure"].status, AutonomousJobStatus.RUNNING)


if __name__ == "__main__":
    unittest.main(verbosity=2)
