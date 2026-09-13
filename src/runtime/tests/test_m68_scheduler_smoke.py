import unittest
from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceService
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_reasoning_feedback_pulse import AutonomousReasoningFeedbackPulse
from src.runtime.autonomous_reasoning_run_loop import AutonomousReasoningRunLoop
from src.runtime.autonomous_reasoning_tool_feedback_cycle import AutonomousReasoningToolFeedbackCycleCoordinator
from src.runtime.autonomous_reasoning_tool_gate import AutonomousReasoningToolGate
from src.runtime.autonomous_reasoning_worker import AutonomousReasoningWorker
from src.runtime.autonomous_runtime_scheduler import AutonomousRuntimeScheduler, AutonomousRuntimeSchedule
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService


class Store:
    def __init__(self):
        self.jobs = {}
        self.schedule = None
        self.claimed = False
        self.completed_claim_tokens = set()

    def save(self, x):
        if isinstance(x, AutonomousJob):
            self.jobs[x.job_id] = x
        else:
            self.schedule = x
        return "r"

    def load(self, j):
        return self.jobs.get(j)

    def load_due(self, n):
        return [] if self.schedule is None or self.schedule.next_due > n else [self.schedule, self.schedule]

    def claim(self, schedule, now, lease_seconds):
        if self.claimed:
            return None
        self.claimed = True
        token = "lease"
        self.schedule = AutonomousRuntimeSchedule(
            schedule.job_id,
            schedule.next_due,
            schedule.interval,
            claim_token=token,
            lease_until=now + lease_seconds,
        )
        return token

    def complete_claim(self, schedule, claim_token, replacement):
        if claim_token in self.completed_claim_tokens:
            return False
        if self.schedule is None or self.schedule.claim_token != claim_token:
            return False
        self.schedule = replacement
        self.completed_claim_tokens.add(claim_token)
        return True


class M68SchedulerSmoke(unittest.TestCase):
    def build(self, action):
        store = Store()
        persistence = AutonomousJobPersistenceService(store)
        persistence.persist(AutonomousJob("j68", "inspect").start())
        gate = AutonomousReasoningToolGate(ToolRegistry(), ToolService(ToolRegistry()))
        worker = AutonomousReasoningWorker(lambda job: action)
        coordinator = AutonomousReasoningToolFeedbackCycleCoordinator(worker, gate)
        pulse = AutonomousReasoningFeedbackPulse(persistence, coordinator)
        return AutonomousRuntimeScheduler(store, AutonomousReasoningRunLoop(pulse)), store

    def test_due_terminal_removed(self):
        s, store = self.build(AutonomousReasoningAction("a", AutonomousReasoningDisposition.COMPLETE, "done", result="ok"))
        s.schedule("j68", next_due=1, interval=5)
        out = s.tick(1)[0]
        self.assertEqual(out.run.job.status, AutonomousJobStatus.COMPLETED)
        self.assertTrue(out.removed)
        self.assertTrue(out.completed_claim)
        self.assertIsNone(store.schedule)

    def test_not_due_untouched(self):
        s, store = self.build(AutonomousReasoningAction("a", AutonomousReasoningDisposition.COMPLETE, "done", result="ok"))
        s.schedule("j68", next_due=2, interval=5)
        self.assertEqual(s.tick(1), ())
        self.assertIsNotNone(store.schedule)

    def test_claim_pair_is_validated(self):
        with self.assertRaises(ValueError):
            AutonomousRuntimeSchedule("j69", 1, 5, claim_token="lease")

    def test_duplicate_due_observation_executes_only_once(self):
        s, _ = self.build(AutonomousReasoningAction("a", AutonomousReasoningDisposition.COMPLETE, "done", result="ok"))
        s.schedule("j68", next_due=1, interval=5)
        out = s.tick(1, max_jobs=2)
        self.assertIsNotNone(out[0].run)
        self.assertTrue(out[0].completed_claim)
        self.assertIsNone(out[1].run)


if __name__ == "__main__": unittest.main()
