import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_runtime_schedule_persistence import SQLiteAutonomousRuntimeScheduleStore
from src.runtime.autonomous_runtime_scheduler import AutonomousRuntimeSchedule


class V1DurableSchedulerPersistenceTests(unittest.TestCase):
    def make_store(self):
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / "scheduler.db"

        def connection_factory():
            return sqlite3.connect(path)

        store = SQLiteAutonomousRuntimeScheduleStore(connection_factory)
        return directory, store

    def test_save_then_new_store_loads_persisted_schedule(self):
        directory, store = self.make_store()
        try:
            schedule = AutonomousRuntimeSchedule(
                "job-1",
                10.0,
                5.0,
                failure_count=2,
                last_failure="RuntimeError: failed",
                last_failure_at=9.0,
            )
            store.save(schedule)

            reopened = SQLiteAutonomousRuntimeScheduleStore(store._connection_factory)
            self.assertEqual(reopened.load_due(10.0), [schedule])
        finally:
            directory.cleanup()

    def test_save_replaces_existing_job_without_duplicate_rows(self):
        directory, store = self.make_store()
        try:
            first = AutonomousRuntimeSchedule("job-1", 10.0, 5.0)
            second = AutonomousRuntimeSchedule("job-1", 20.0, 7.0)
            store.save(first)
            store.save(second)
            self.assertEqual(store.load_due(100.0), [second])
        finally:
            directory.cleanup()

    def test_claim_persists_lease_across_store_instances(self):
        directory, store = self.make_store()
        try:
            schedule = AutonomousRuntimeSchedule("job-1", 10.0, 5.0)
            store.save(schedule)
            claim = store.claim(schedule, now=10.0, lease_seconds=30.0)
            self.assertIsNotNone(claim)

            reopened = SQLiteAutonomousRuntimeScheduleStore(store._connection_factory)
            persisted = reopened.load_due(10.0)[0]
            self.assertEqual(persisted.claim_token, claim)
            self.assertEqual(persisted.lease_until, 40.0)
        finally:
            directory.cleanup()

    def test_active_lease_blocks_second_claim(self):
        directory, store = self.make_store()
        try:
            schedule = AutonomousRuntimeSchedule("job-1", 10.0, 5.0)
            store.save(schedule)
            first = store.claim(schedule, now=10.0, lease_seconds=30.0)
            second = store.claim(schedule, now=20.0, lease_seconds=30.0)
            self.assertIsNotNone(first)
            self.assertIsNone(second)
        finally:
            directory.cleanup()

    def test_expired_lease_can_be_reclaimed(self):
        directory, store = self.make_store()
        try:
            schedule = AutonomousRuntimeSchedule("job-1", 10.0, 5.0)
            store.save(schedule)
            first = store.claim(schedule, now=10.0, lease_seconds=30.0)
            second = store.claim(schedule, now=40.0, lease_seconds=30.0)
            self.assertIsNotNone(first)
            self.assertIsNotNone(second)
            self.assertNotEqual(first, second)
        finally:
            directory.cleanup()

    def test_matching_claim_can_complete_and_remove_schedule(self):
        directory, store = self.make_store()
        try:
            schedule = AutonomousRuntimeSchedule("job-1", 10.0, 5.0)
            store.save(schedule)
            claim = store.claim(schedule, now=10.0, lease_seconds=30.0)
            self.assertTrue(store.complete_claim(schedule, claim, None))
            self.assertEqual(store.load_due(100.0), [])
        finally:
            directory.cleanup()

    def test_matching_claim_can_complete_and_replace_schedule(self):
        directory, store = self.make_store()
        try:
            schedule = AutonomousRuntimeSchedule("job-1", 10.0, 5.0)
            store.save(schedule)
            claim = store.claim(schedule, now=10.0, lease_seconds=30.0)
            replacement = AutonomousRuntimeSchedule(
                "job-1",
                20.0,
                5.0,
                failure_count=1,
                last_failure="RuntimeError: failed",
                last_failure_at=10.0,
            )
            self.assertTrue(store.complete_claim(schedule, claim, replacement))
            self.assertEqual(store.load_due(20.0), [replacement])
        finally:
            directory.cleanup()

    def test_stale_claim_cannot_overwrite_reclaimed_schedule(self):
        directory, store = self.make_store()
        try:
            schedule = AutonomousRuntimeSchedule("job-1", 10.0, 5.0)
            store.save(schedule)
            stale = store.claim(schedule, now=10.0, lease_seconds=30.0)
            newer = store.claim(schedule, now=40.0, lease_seconds=30.0)
            replacement = AutonomousRuntimeSchedule("job-1", 50.0, 5.0)

            self.assertFalse(store.complete_claim(schedule, stale, replacement))
            persisted = store.load_due(50.0)[0]
            self.assertEqual(persisted.claim_token, newer)
            self.assertEqual(persisted.lease_until, 70.0)
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()
