import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence_sqlite import SQLiteAutonomousJobStore


class V1DurableJobPersistenceTests(unittest.TestCase):
    def make_store(self):
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / "jobs.db"

        def connection_factory():
            return sqlite3.connect(path)

        return directory, path, SQLiteAutonomousJobStore(connection_factory)

    def test_save_then_new_store_restores_complete_snapshot(self):
        directory, path, store = self.make_store()
        try:
            job = AutonomousJob.create(
                "inspect system",
                job_id="job-1",
                working_context={"source": "operator", "count": 1},
            ).start()
            job = job.record_step(
                phase="observe",
                summary="inspected",
                observation="healthy",
                context_delta={"result": "healthy"},
            )
            revision = store.save(job)

            reopened = SQLiteAutonomousJobStore(lambda: sqlite3.connect(path))
            restored = reopened.load("job-1")
            self.assertEqual(restored, job)
            self.assertEqual(reopened.save(job), revision)
        finally:
            directory.cleanup()

    def test_new_snapshot_replaces_previous_revision(self):
        directory, path, store = self.make_store()
        try:
            first = AutonomousJob.create("inspect", job_id="job-1")
            second = first.start()
            first_revision = store.save(first)
            second_revision = store.save(second)
            self.assertNotEqual(first_revision, second_revision)
            self.assertEqual(store.load("job-1"), second)
        finally:
            directory.cleanup()

    def test_waiting_state_and_context_survive_restart(self):
        directory, path, store = self.make_store()
        try:
            job = (
                AutonomousJob.create("use protected tool", job_id="job-1")
                .start()
                .record_step(phase="reason", summary="tool required")
                .wait_for_authorization("explicit confirmation required")
            )
            store.save(job)
            reopened = SQLiteAutonomousJobStore(lambda: sqlite3.connect(path))
            restored = reopened.load("job-1")
            self.assertEqual(restored.status, AutonomousJobStatus.WAITING_AUTHORIZATION)
            self.assertEqual(restored.waiting_reason, "explicit confirmation required")
            self.assertEqual(restored.step_count, 1)
        finally:
            directory.cleanup()

    def test_terminal_state_survives_restart(self):
        directory, path, store = self.make_store()
        try:
            job = AutonomousJob.create("finish", job_id="job-1").start().complete("done")
            store.save(job)
            reopened = SQLiteAutonomousJobStore(lambda: sqlite3.connect(path))
            restored = reopened.load("job-1")
            self.assertEqual(restored, job)
            self.assertTrue(restored.terminal)
        finally:
            directory.cleanup()

    def test_missing_job_returns_none(self):
        directory, _, store = self.make_store()
        try:
            self.assertIsNone(store.load("missing"))
        finally:
            directory.cleanup()

    def test_invalid_job_identity_is_rejected(self):
        directory, _, store = self.make_store()
        try:
            with self.assertRaises(TypeError):
                store.save(object())
            with self.assertRaises(ValueError):
                store.load("")
        finally:
            directory.cleanup()

    def test_corrupted_snapshot_revision_is_rejected(self):
        directory, path, store = self.make_store()
        try:
            job = AutonomousJob.create("inspect", job_id="job-1")
            store.save(job)
            connection = sqlite3.connect(path)
            try:
                connection.execute(
                    "UPDATE autonomous_jobs SET snapshot_json = ? WHERE job_id = ?",
                    ("{\"corrupted\":true}", "job-1"),
                )
                connection.commit()
            finally:
                connection.close()
            with self.assertRaises(ValueError):
                store.load("job-1")
        finally:
            directory.cleanup()

    def test_schema_is_idempotent(self):
        directory, path, _ = self.make_store()
        try:
            SQLiteAutonomousJobStore(lambda: sqlite3.connect(path))
            SQLiteAutonomousJobStore(lambda: sqlite3.connect(path))
            connection = sqlite3.connect(path)
            try:
                tables = connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='autonomous_jobs'"
                ).fetchall()
            finally:
                connection.close()
            self.assertEqual(tables, [("autonomous_jobs",)])
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()
