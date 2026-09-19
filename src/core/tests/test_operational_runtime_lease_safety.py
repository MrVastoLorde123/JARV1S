"""OPS-14 scheduler lease renewal and long-pulse fencing tests."""
from __future__ import annotations

import sqlite3
import tempfile
import time
import unittest
from dataclasses import dataclass
from pathlib import Path

from src.runtime.autonomous_runtime_schedule_persistence import (
    SQLiteAutonomousRuntimeScheduleStore,
)
from src.runtime.autonomous_runtime_scheduler import (
    AutonomousRuntimeSchedule,
    AutonomousRuntimeScheduler,
)


def db_factory(path: Path):
    return lambda: sqlite3.connect(path)


@dataclass(frozen=True)
class FakeRun:
    job: object


class HeartbeatStore:
    def __init__(self):
        self.schedules = {}
        self.renewals = 0
        self.completed = []

    def save(self, schedule):
        self.schedules[schedule.job_id] = schedule

    def load_due(self, now):
        return [
            schedule
            for schedule in self.schedules.values()
            if schedule.next_due <= now
        ]

    def list_all(self, *, limit=500):
        return tuple(self.schedules.values())[:limit]

    def delete(self, job_id):
        return self.schedules.pop(job_id, None) is not None

    def claim(self, schedule, now, lease_seconds):
        token = f"claim-{schedule.job_id}"
        self.schedules[schedule.job_id] = AutonomousRuntimeSchedule(
            job_id=schedule.job_id,
            next_due=schedule.next_due,
            interval=schedule.interval,
            claim_token=token,
            lease_until=now + lease_seconds,
        )
        return token

    def renew_claim(self, schedule, claim_token, now, lease_seconds):
        current = self.schedules[schedule.job_id]
        if current.claim_token != claim_token:
            return False
        self.renewals += 1
        self.schedules[schedule.job_id] = AutonomousRuntimeSchedule(
            job_id=current.job_id,
            next_due=current.next_due,
            interval=current.interval,
            claim_token=claim_token,
            lease_until=now + lease_seconds,
            failure_count=current.failure_count,
            last_failure=current.last_failure,
            last_failure_at=current.last_failure_at,
        )
        return True

    def complete_claim(self, schedule, claim_token, replacement):
        current = self.schedules.get(schedule.job_id)
        if current is None or current.claim_token != claim_token:
            return False
        self.completed.append((schedule.job_id, claim_token, replacement))
        if replacement is None:
            self.schedules.pop(schedule.job_id, None)
        else:
            self.schedules[schedule.job_id] = replacement
        return True


class SlowRunLoop:
    def __init__(self, duration=0.22):
        self.duration = duration
        self.calls = 0

    def run(self, job_id, *, max_pulses=1):
        self.calls += 1
        time.sleep(self.duration)
        return FakeRun(
            job=type(
                "Job",
                (),
                {
                    "terminal": True,
                    "resumable": False,
                },
            )()
        )


class FailingHeartbeatStore(HeartbeatStore):
    def renew_claim(self, schedule, claim_token, now, lease_seconds):
        self.renewals += 1
        return False


class OPS14LeaseTests(unittest.TestCase):
    def test_sqlite_renew_claim_extends_active_fence_and_rejects_bad_tokens(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lease.db"
            store = SQLiteAutonomousRuntimeScheduleStore(db_factory(path))
            now = time.time()
            schedule = AutonomousRuntimeSchedule(
                job_id="job-lease",
                next_due=now - 1,
                interval=10,
            )
            store.save(schedule)
            token = store.claim(schedule, now, 0.5)
            self.assertIsNotNone(token)

            renewed = store.renew_claim(
                schedule,
                token,
                now + 0.1,
                0.5,
            )
            self.assertTrue(renewed)

            wrong_token = store.renew_claim(
                schedule,
                "wrong-token",
                now + 0.2,
                0.5,
            )
            self.assertFalse(wrong_token)

            expired = store.renew_claim(
                schedule,
                token,
                now + 2.0,
                0.5,
            )
            self.assertFalse(expired)

    def test_long_running_pulse_receives_repeated_lease_renewals(self):
        store = HeartbeatStore()
        run_loop = SlowRunLoop()
        scheduler = AutonomousRuntimeScheduler(store, run_loop)
        scheduler.schedule("job-heartbeat", next_due=time.time() - 1, interval=10)

        results = scheduler.tick(
            time.time(),
            lease_seconds=0.09,
        )

        self.assertEqual(run_loop.calls, 1)
        self.assertGreaterEqual(store.renewals, 2)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].completed_claim)
        self.assertIsNone(results[0].failure)
        self.assertEqual(store.completed[0][2], None)

    def test_lease_loss_is_reported_and_never_silently_replaced(self):
        store = FailingHeartbeatStore()
        run_loop = SlowRunLoop(duration=0.15)
        scheduler = AutonomousRuntimeScheduler(store, run_loop)
        scheduler.schedule("job-lease-loss", next_due=time.time() - 1, interval=10)

        results = scheduler.tick(
            time.time(),
            lease_seconds=0.09,
        )

        self.assertEqual(len(results), 1)
        self.assertIsNotNone(results[0].failure)
        self.assertIn("lease", results[0].failure.lower())
        self.assertFalse(results[0].completed_claim)


if __name__ == "__main__":
    unittest.main(verbosity=2)
