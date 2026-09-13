import unittest

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceService
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_reasoning_feedback_pulse import AutonomousReasoningFeedbackPulse
from src.runtime.autonomous_reasoning_run_loop import AutonomousReasoningRunLoop
from src.runtime.autonomous_reasoning_tool_feedback_cycle import AutonomousReasoningToolFeedbackCycleCoordinator
from src.runtime.autonomous_reasoning_tool_gate import AutonomousReasoningToolGate
from src.runtime.autonomous_reasoning_worker import AutonomousReasoningWorker
from src.runtime.autonomous_runtime_scheduler import AutonomousRuntimeSchedule, AutonomousRuntimeScheduler
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService


class FencedStore:
    def __init__(self):
        self.schedule = None
        self.jobs = {}
        self.claim_counter = 0
        self.inject_replacement_on_complete = None

    def save(self, value):
        if isinstance(value, AutonomousJob):
            self.jobs[value.job_id] = value
        else:
            self.schedule = value
        return "revision"

    def load(self, job_id):
        return self.jobs.get(job_id)

    def load_due(self, now):
        if self.schedule is None or self.schedule.next_due > now:
            return []
        return [self.schedule]

    def claim(self, schedule, now, lease_seconds):
        if self.schedule is None:
            return None
        if self.schedule.claim_token is not None:
            return None
        self.claim_counter += 1
        token = f"lease-{self.claim_counter}"
        self.schedule = AutonomousRuntimeSchedule(
            schedule.job_id,
            schedule.next_due,
            schedule.interval,
            claim_token=token,
            lease_until=now + lease_seconds,
        )
        return token

    def complete_claim(self, schedule, claim_token, replacement):
        if self.inject_replacement_on_complete is not None:
            self.schedule = self.inject_replacement_on_complete
            self.inject_replacement_on_complete = None
        if self.schedule is None or self.schedule.claim_token != claim_token:
            return False
        self.schedule = replacement
        return True


class M71SchedulerLeaseFencingTests(unittest.TestCase):
    def build(self, store, action):
        persistence = AutonomousJobPersistenceService(store)
        persistence.persist(AutonomousJob("j71", "inspect").start())
        registry = ToolRegistry()
        gate = AutonomousReasoningToolGate(registry, ToolService(registry))
        worker = AutonomousReasoningWorker(lambda job: action)
        coordinator = AutonomousReasoningToolFeedbackCycleCoordinator(worker, gate)
        pulse = AutonomousReasoningFeedbackPulse(persistence, coordinator)
        return AutonomousRuntimeScheduler(store, AutonomousReasoningRunLoop(pulse))

    def test_matching_claim_can_complete_and_replace_schedule(self):
        store = FencedStore()
        scheduler = self.build(store, AutonomousReasoningAction("a", AutonomousReasoningDisposition.CONTINUE, "continue"))
        scheduler.schedule("j71", next_due=1, interval=5)
        out = scheduler.tick(1)[0]
        self.assertTrue(out.completed_claim)
        self.assertIsNotNone(store.schedule)
        self.assertIsNone(store.schedule.claim_token)
        self.assertEqual(store.schedule.next_due, 6)

    def test_terminal_matching_claim_can_remove_schedule(self):
        store = FencedStore()
        scheduler = self.build(store, AutonomousReasoningAction("a", AutonomousReasoningDisposition.COMPLETE, "done", result="ok"))
        scheduler.schedule("j71", next_due=1, interval=5)
        out = scheduler.tick(1)[0]
        self.assertEqual(out.run.job.status, AutonomousJobStatus.COMPLETED)
        self.assertTrue(out.completed_claim)
        self.assertIsNone(store.schedule)

    def test_stale_claim_cannot_overwrite_reclaimed_schedule(self):
        store = FencedStore()
        scheduler = self.build(store, AutonomousReasoningAction("a", AutonomousReasoningDisposition.CONTINUE, "continue"))
        scheduler.schedule("j71", next_due=1, interval=5)
        newer_owner = AutonomousRuntimeSchedule("j71", 1, 5, claim_token="new-owner", lease_until=40)
        store.inject_replacement_on_complete = newer_owner
        out = scheduler.tick(1)[0]
        self.assertFalse(out.completed_claim)
        self.assertEqual(store.schedule, newer_owner)

    def test_rejected_completion_has_no_fallback_mutation(self):
        store = FencedStore()
        scheduler = self.build(store, AutonomousReasoningAction("a", AutonomousReasoningDisposition.CONTINUE, "continue"))
        scheduler.schedule("j71", next_due=1, interval=5)
        original = store.schedule
        store.inject_replacement_on_complete = AutonomousRuntimeSchedule("j71", 1, 5, claim_token="new-owner", lease_until=50)
        out = scheduler.tick(1)[0]
        self.assertFalse(out.completed_claim)
        self.assertNotEqual(store.schedule, original)
        self.assertEqual(store.schedule.claim_token, "new-owner")
        self.assertEqual(store.schedule.lease_until, 50)

    def test_store_contract_requires_claim_completion_boundary(self):
        class LegacyStore:
            def save(self, schedule): return "revision"
            def load_due(self, now): return []
            def claim(self, schedule, now, lease_seconds): return None

        registry = ToolRegistry()
        gate = AutonomousReasoningToolGate(registry, ToolService(registry))
        worker = AutonomousReasoningWorker(lambda job: AutonomousReasoningAction("a", AutonomousReasoningDisposition.COMPLETE, "done"))
        coordinator = AutonomousReasoningToolFeedbackCycleCoordinator(worker, gate)
        pulse = AutonomousReasoningFeedbackPulse(AutonomousJobPersistenceService(LegacyStore()), coordinator)
        with self.assertRaises(TypeError):
            AutonomousRuntimeScheduler(LegacyStore(), AutonomousReasoningRunLoop(pulse))


if __name__ == "__main__": unittest.main()
