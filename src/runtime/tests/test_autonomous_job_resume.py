import unittest

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceService
from src.runtime.autonomous_job_resume import (
    AutonomousJobResumeBoundary,
    AutonomousJobResumeKind,
    AutonomousJobResumeRequest,
)


class MemoryStore:
    def __init__(self):
        self.jobs = {}
        self.revision = 0

    def save(self, job):
        self.revision += 1
        self.jobs[job.job_id] = job
        return f"r{self.revision}"

    def load(self, job_id):
        return self.jobs.get(job_id)


class M65Tests(unittest.TestCase):
    def boundary(self):
        store = MemoryStore()
        persistence = AutonomousJobPersistenceService(store)
        return AutonomousJobResumeBoundary(persistence), persistence, store

    def persist_waiting(self, status):
        job = AutonomousJob("j65", "inspect system").start()
        if status is AutonomousJobStatus.WAITING_AUTHORIZATION:
            job = job.wait_for_authorization("authorization required")
        elif status is AutonomousJobStatus.WAITING_TOOL:
            job = job.wait_for_tool("tool confirmation required")
        elif status is AutonomousJobStatus.WAITING_INPUT:
            job = job.wait_for_input("input required")
        elif status is AutonomousJobStatus.PAUSED:
            job = job.pause("paused")
        else:
            raise AssertionError("unsupported test status")
        return job

    def test_authorization_wait_requires_explicit_confirmation_and_resumes(self):
        boundary, persistence, store = self.boundary()
        job = self.persist_waiting(AutonomousJobStatus.WAITING_AUTHORIZATION)
        persistence.persist(job)

        with self.assertRaises(PermissionError):
            boundary.resume(AutonomousJobResumeRequest("j65", AutonomousJobResumeKind.AUTHORIZATION))

        out = boundary.resume(
            AutonomousJobResumeRequest("j65", AutonomousJobResumeKind.AUTHORIZATION, confirmed=True)
        )
        self.assertEqual(out.job.status, AutonomousJobStatus.RUNNING)
        self.assertEqual(store.jobs["j65"], out.job)
        self.assertEqual(out.persistence_receipt.revision, "r2")

    def test_tool_wait_requires_explicit_confirmation(self):
        boundary, persistence, _ = self.boundary()
        persistence.persist(self.persist_waiting(AutonomousJobStatus.WAITING_TOOL))

        with self.assertRaises(PermissionError):
            boundary.resume(AutonomousJobResumeRequest("j65", AutonomousJobResumeKind.TOOL))

        out = boundary.resume(
            AutonomousJobResumeRequest("j65", AutonomousJobResumeKind.TOOL, confirmed=True)
        )
        self.assertEqual(out.job.status, AutonomousJobStatus.RUNNING)

    def test_input_wait_requires_and_applies_explicit_context(self):
        boundary, persistence, _ = self.boundary()
        persistence.persist(self.persist_waiting(AutonomousJobStatus.WAITING_INPUT))

        with self.assertRaises(ValueError):
            boundary.resume(AutonomousJobResumeRequest("j65", AutonomousJobResumeKind.INPUT))

        out = boundary.resume(
            AutonomousJobResumeRequest(
                "j65", AutonomousJobResumeKind.INPUT, input_context={"answer": "ready"}
            )
        )
        self.assertEqual(out.job.status, AutonomousJobStatus.RUNNING)
        self.assertEqual(out.job.working_context["answer"], "ready")

    def test_paused_job_requires_explicit_pause_resume(self):
        boundary, persistence, _ = self.boundary()
        persistence.persist(self.persist_waiting(AutonomousJobStatus.PAUSED))

        out = boundary.resume(AutonomousJobResumeRequest("j65", AutonomousJobResumeKind.PAUSE))
        self.assertEqual(out.job.status, AutonomousJobStatus.RUNNING)

    def test_resume_kind_must_match_persisted_state(self):
        boundary, persistence, _ = self.boundary()
        persistence.persist(self.persist_waiting(AutonomousJobStatus.WAITING_TOOL))

        with self.assertRaises(ValueError):
            boundary.resume(
                AutonomousJobResumeRequest(
                    "j65", AutonomousJobResumeKind.INPUT, input_context={"answer": "ready"}
                )
            )


if __name__ == "__main__":
    unittest.main()
