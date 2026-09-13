import unittest
from unittest.mock import MagicMock

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceService
from src.runtime.autonomous_reasoning_run_loop import AutonomousReasoningRunLoop
from src.runtime.autonomous_runtime_scheduler import AutonomousRuntimeSchedule, AutonomousRuntimeScheduler


class Store:
    def __init__(self):
        self.jobs = {}
        self.schedule = None
        self.claim_counter = 0

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
        self.claim_counter += 1
        token = f"lease-{self.claim_counter}"
        self.schedule = AutonomousRuntimeSchedule(
            schedule.job_id,
            schedule.next_due,
            schedule.interval,
            claim_token=token,
            lease_until=now + lease_seconds,
            failure_count=schedule.failure_count,
        )
        return token

    def complete_claim(self, schedule, claim_token, replacement):
        if self.schedule is None or self.schedule.claim_token != claim_token:
            return False
        self.schedule = replacement
        return True


class FailingRunLoop(AutonomousReasoningRunLoop):
    def __init__(self):
        pass

    def run(self, job_id, *, max_pulses=1):
        raise RuntimeError("worker crashed")


class SuccessfulRunLoop(AutonomousReasoningRunLoop):
    def __init__(self):
        pass

    def run(self, job_id, *, max_pulses=1):
        result = MagicMock()
        result.job = MagicMock()
        result.job.status = AutonomousJobStatus.RUNNING
        result.job.resumable = False
        return result


class M73SchedulerFailureBackoffTests(unittest.TestCase):
    def build(self, run_loop):
        store = Store()
        AutonomousJobPersistenceService(store).persist(AutonomousJob("j73", "inspect").start())
        return AutonomousRuntimeScheduler(store, run_loop), store

    def test_first_failure_doubles_interval(self):
        scheduler, store = self.build(FailingRunLoop())
        scheduler.schedule("j73", next_due=1, interval=5)
        out = scheduler.tick(1)[0]
        self.assertEqual(out.failure, "RuntimeError: worker crashed")
        self.assertEqual(store.schedule.next_due, 11)
        self.assertEqual(store.schedule.failure_count, 1)

    def test_failure_backoff_grows_and_caps(self):
        scheduler, store = self.build(FailingRunLoop())
        store.save(AutonomousRuntimeSchedule("j73", 1, 5, failure_count=2))
        out = scheduler.tick(1, max_backoff_multiplier=8)[0]
        self.assertTrue(out.completed_claim)
        self.assertEqual(store.schedule.next_due, 21)
        self.assertEqual(store.schedule.failure_count, 3)

    def test_backoff_cap_prevents_unbounded_delay(self):
        scheduler, store = self.build(FailingRunLoop())
        store.save(AutonomousRuntimeSchedule("j73", 1, 5, failure_count=8))
        scheduler.tick(1, max_backoff_multiplier=8)
        self.assertEqual(store.schedule.next_due, 41)
        self.assertEqual(store.schedule.failure_count, 9)

    def test_success_resets_failure_streak(self):
        scheduler, store = self.build(SuccessfulRunLoop())
        store.save(AutonomousRuntimeSchedule("j73", 1, 5, failure_count=4))
        out = scheduler.tick(1)[0]
        self.assertTrue(out.completed_claim)
        self.assertEqual(store.schedule.failure_count, 0)
        self.assertEqual(store.schedule.next_due, 6)

    def test_failure_count_is_validated(self):
        with self.assertRaises(ValueError):
            AutonomousRuntimeSchedule("j73", 1, 5, failure_count=-1)
        with self.assertRaises(ValueError):
            AutonomousRuntimeSchedule("j73", 1, 5, failure_count=True)


if __name__ == "__main__":
    unittest.main()
