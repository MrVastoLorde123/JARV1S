import unittest
from unittest.mock import MagicMock

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceService
from src.runtime.autonomous_reasoning_run_loop import AutonomousReasoningRunLoop
from src.runtime.autonomous_runtime_scheduler import AutonomousRuntimeSchedule, AutonomousRuntimeScheduler


class Store:
    def __init__(self):
        self.jobs = {}; self.schedule = None; self.claim_counter = 0
    def save(self, value):
        if isinstance(value, AutonomousJob): self.jobs[value.job_id] = value
        else: self.schedule = value
        return "revision"
    def load(self, job_id): return self.jobs.get(job_id)
    def load_due(self, now): return [] if self.schedule is None or self.schedule.next_due > now else [self.schedule]
    def claim(self, schedule, now, lease_seconds):
        self.claim_counter += 1; token = f"lease-{self.claim_counter}"
        self.schedule = AutonomousRuntimeSchedule(schedule.job_id, schedule.next_due, schedule.interval, token, now + lease_seconds, schedule.failure_count, schedule.last_failure, schedule.last_failure_at)
        return token
    def complete_claim(self, schedule, claim_token, replacement):
        if self.schedule is None or self.schedule.claim_token != claim_token: return False
        self.schedule = replacement; return True


class FailingRunLoop(AutonomousReasoningRunLoop):
    def __init__(self): pass
    def run(self, job_id, *, max_pulses=1): raise RuntimeError("worker crashed")


class SuccessfulRunLoop(AutonomousReasoningRunLoop):
    def __init__(self): pass
    def run(self, job_id, *, max_pulses=1):
        result = MagicMock(); result.job = MagicMock(); result.job.status = AutonomousJobStatus.RUNNING; result.job.resumable = False; return result


class M74SchedulerFailureMetadataTests(unittest.TestCase):
    def build(self, run_loop):
        store = Store(); AutonomousJobPersistenceService(store).persist(AutonomousJob("j74", "inspect").start()); return AutonomousRuntimeScheduler(store, run_loop), store

    def test_failure_persists_reason_timestamp_and_streak(self):
        scheduler, store = self.build(FailingRunLoop()); scheduler.schedule("j74", next_due=1, interval=5)
        out = scheduler.tick(7)[0]
        self.assertEqual(out.failure, "RuntimeError: worker crashed")
        self.assertEqual(store.schedule.failure_count, 1)
        self.assertEqual(store.schedule.last_failure, "RuntimeError: worker crashed")
        self.assertEqual(store.schedule.last_failure_at, 7)
        self.assertEqual(store.schedule.next_due, 12)

    def test_failure_metadata_updates_on_later_failure(self):
        scheduler, store = self.build(FailingRunLoop())
        store.save(AutonomousRuntimeSchedule("j74", 1, 5, failure_count=1, last_failure="old", last_failure_at=2))
        scheduler.tick(10)
        self.assertEqual(store.schedule.failure_count, 2)
        self.assertEqual(store.schedule.last_failure, "RuntimeError: worker crashed")
        self.assertEqual(store.schedule.last_failure_at, 10)
        self.assertEqual(store.schedule.next_due, 20)

    def test_success_clears_failure_metadata(self):
        scheduler, store = self.build(SuccessfulRunLoop())
        store.save(AutonomousRuntimeSchedule("j74", 1, 5, failure_count=3, last_failure="RuntimeError: worker crashed", last_failure_at=10))
        scheduler.tick(11)
        self.assertEqual(store.schedule.failure_count, 0)
        self.assertIsNone(store.schedule.last_failure)
        self.assertIsNone(store.schedule.last_failure_at)
        self.assertEqual(store.schedule.next_due, 16)

    def test_failure_metadata_pair_is_validated(self):
        with self.assertRaises(ValueError): AutonomousRuntimeSchedule("j74", 1, 5, last_failure="boom")
        with self.assertRaises(TypeError): AutonomousRuntimeSchedule("j74", 1, 5, last_failure_at=True)
        with self.assertRaises(ValueError): AutonomousRuntimeSchedule("j74", 1, 5, last_failure_at=2)


if __name__ == "__main__": unittest.main()
