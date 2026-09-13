import unittest

from src.runtime.autonomous_runtime_scheduler import (
    AutonomousRuntimeSchedule,
    scheduler_claim_token,
    scheduler_lease_expired,
)


class LeaseStore:
    def __init__(self, schedule):
        self.schedule = schedule

    def claim(self, now, lease_seconds):
        schedule = self.schedule
        if schedule.claim_token is not None and not scheduler_lease_expired(schedule.lease_until, now):
            return None
        token = scheduler_claim_token(schedule.job_id, now, lease_seconds)
        self.schedule = AutonomousRuntimeSchedule(
            schedule.job_id,
            schedule.next_due,
            schedule.interval,
            claim_token=token,
            lease_until=now + lease_seconds,
        )
        return token


class M70SchedulerLeaseRecoveryTests(unittest.TestCase):
    def test_active_lease_is_not_expired(self):
        self.assertFalse(scheduler_lease_expired(10.0, 9.99))

    def test_expiry_is_inclusive(self):
        self.assertTrue(scheduler_lease_expired(10.0, 10.0))

    def test_expired_lease_can_be_reclaimed_with_new_token(self):
        original = AutonomousRuntimeSchedule("j70", 1.0, 5.0, claim_token="old", lease_until=10.0)
        store = LeaseStore(original)
        token = store.claim(10.0, 30.0)
        self.assertIsNotNone(token)
        self.assertNotEqual(token, "old")
        self.assertEqual(store.schedule.claim_token, token)
        self.assertEqual(store.schedule.lease_until, 40.0)

    def test_active_lease_blocks_reclaim(self):
        original = AutonomousRuntimeSchedule("j70", 1.0, 5.0, claim_token="old", lease_until=10.0)
        store = LeaseStore(original)
        self.assertIsNone(store.claim(9.0, 30.0))
        self.assertEqual(store.schedule.claim_token, "old")
        self.assertEqual(store.schedule.lease_until, 10.0)

    def test_unclaimed_schedule_can_be_claimed(self):
        original = AutonomousRuntimeSchedule("j70", 1.0, 5.0)
        store = LeaseStore(original)
        token = store.claim(2.0, 30.0)
        self.assertIsNotNone(token)
        self.assertEqual(store.schedule.lease_until, 32.0)

    def test_invalid_lease_values_are_rejected(self):
        with self.assertRaises(TypeError):
            scheduler_lease_expired(True, 1.0)
        with self.assertRaises(TypeError):
            scheduler_lease_expired(1.0, False)


if __name__ == "__main__":
    unittest.main()
