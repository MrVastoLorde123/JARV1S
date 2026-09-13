import unittest

from src.runtime.autonomous_job import AutonomousJob
from src.runtime.autonomous_job_persistence import (
    AutonomousJobPersistenceService,
    AutonomousJobPersistenceValidationError,
)


class RecordingStore:
    def __init__(self, *, loaded=None):
        self.saved = []
        self.loaded = loaded

    def save(self, job):
        self.saved.append(job)
        return "revision-1"

    def load(self, job_id):
        return self.loaded


class M56AutonomousJobPersistenceTests(unittest.TestCase):
    def test_persistence_requires_explicit_store(self):
        service = AutonomousJobPersistenceService()
        job = AutonomousJob.create("Investigate").start()
        with self.assertRaises(RuntimeError):
            service.persist(job)

    def test_persist_forwards_exact_job_snapshot(self):
        store = RecordingStore()
        service = AutonomousJobPersistenceService(store)
        job = AutonomousJob.create("Investigate").start().record_step(
            phase="inspect",
            summary="Collected evidence",
            context_delta={"source": "manual"},
        )
        receipt = service.persist(job)
        self.assertIs(store.saved[0], job)
        self.assertEqual(receipt.job_id, job.job_id)
        self.assertEqual(receipt.revision, "revision-1")
        self.assertTrue(receipt.persisted)

    def test_receipt_is_deterministic(self):
        job = AutonomousJob.create("Deterministic")
        first_store = RecordingStore()
        second_store = RecordingStore()
        first = AutonomousJobPersistenceService(first_store).persist(job)
        second = AutonomousJobPersistenceService(second_store).persist(job)
        self.assertEqual(first.receipt_id, second.receipt_id)

    def test_persisted_context_preserves_authority_walls(self):
        job = AutonomousJob.create("Persist me").start()
        receipt = AutonomousJobPersistenceService(RecordingStore()).persist(job)
        context = receipt.to_context()
        self.assertTrue(context["autonomous_job_persisted"])
        self.assertTrue(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["truth_guaranteed"])

    def test_restore_returns_exact_job_identity(self):
        job = AutonomousJob.create("Restore me").start().record_step(
            phase="research",
            summary="Saved research context",
        )
        service = AutonomousJobPersistenceService(RecordingStore(loaded=job))
        restored = service.restore(job.job_id)
        self.assertIs(restored, job)

    def test_restore_missing_job_returns_none(self):
        service = AutonomousJobPersistenceService(RecordingStore(loaded=None))
        self.assertIsNone(service.restore("missing-job"))

    def test_restore_rejects_invalid_snapshot(self):
        service = AutonomousJobPersistenceService(RecordingStore(loaded=object()))
        with self.assertRaises(AutonomousJobPersistenceValidationError):
            service.restore("job-1")

    def test_restore_rejects_mismatched_identity(self):
        loaded = AutonomousJob.create("Different").start()
        service = AutonomousJobPersistenceService(RecordingStore(loaded=loaded))
        with self.assertRaises(AutonomousJobPersistenceValidationError):
            service.restore("expected-job")

    def test_store_must_return_revision_identifier(self):
        class BadStore(RecordingStore):
            def save(self, job):
                return ""

        service = AutonomousJobPersistenceService(BadStore())
        with self.assertRaises(AutonomousJobPersistenceValidationError):
            service.persist(AutonomousJob.create("Bad revision"))

    def test_binding_invalid_store_is_rejected(self):
        service = AutonomousJobPersistenceService()
        with self.assertRaises(TypeError):
            service.bind(object())


if __name__ == "__main__":
    unittest.main()
