import unittest

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_driver import AutonomousCycleDisposition, AutonomousCycleResult, AutonomousJobDriver
from src.runtime.autonomous_job_execution_pulse import AutonomousJobExecutionPulse
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceService


class Store:
    def __init__(self, jobs=None):
        self.jobs = dict(jobs or {})
        self.saved = []

    def save(self, job):
        self.jobs[job.job_id] = job
        self.saved.append(job)
        return f"rev-{len(self.saved)}"

    def load(self, job_id):
        return self.jobs.get(job_id)


class Worker:
    def __init__(self):
        self.calls = 0

    def run_cycle(self, job):
        self.calls += 1
        return AutonomousCycleResult(
            disposition=AutonomousCycleDisposition.COMPLETE,
            phase="finish",
            summary="Completed the assigned investigation",
            result="Investigation complete",
        )


class AutonomousJobExecutionPulseTests(unittest.TestCase):
    def test_queued_job_is_started_advanced_and_persisted(self):
        job = AutonomousJob.create("Investigate ATS")
        store = Store({job.job_id: job})
        worker = Worker()
        pulse = AutonomousJobExecutionPulse(
            AutonomousJobPersistenceService(store),
            AutonomousJobDriver(worker),
        )

        result = pulse.pulse(job.job_id)

        self.assertEqual(result.job.status, AutonomousJobStatus.COMPLETED)
        self.assertTrue(result.progressed)
        self.assertIsNotNone(result.persistence_receipt)
        self.assertEqual(worker.calls, 1)
        self.assertEqual(len(store.saved), 1)

    def test_running_job_advances_once(self):
        job = AutonomousJob.create("Investigate").start()
        store = Store({job.job_id: job})
        worker = Worker()
        pulse = AutonomousJobExecutionPulse(
            AutonomousJobPersistenceService(store),
            AutonomousJobDriver(worker),
        )

        result = pulse.pulse(job.job_id)

        self.assertEqual(result.job.status, AutonomousJobStatus.COMPLETED)
        self.assertEqual(worker.calls, 1)

    def test_terminal_job_is_a_noop(self):
        job = AutonomousJob.create("Already done").start().complete("done")
        store = Store({job.job_id: job})
        worker = Worker()
        pulse = AutonomousJobExecutionPulse(
            AutonomousJobPersistenceService(store),
            AutonomousJobDriver(worker),
        )

        result = pulse.pulse(job.job_id)

        self.assertIs(result.job, job)
        self.assertFalse(result.progressed)
        self.assertIsNone(result.persistence_receipt)
        self.assertEqual(worker.calls, 0)
        self.assertFalse(store.saved)

    def test_waiting_job_is_a_noop(self):
        job = AutonomousJob.create("Need user").start().wait_for_input("Need device IP")
        store = Store({job.job_id: job})
        worker = Worker()
        pulse = AutonomousJobExecutionPulse(
            AutonomousJobPersistenceService(store),
            AutonomousJobDriver(worker),
        )

        result = pulse.pulse(job.job_id)

        self.assertEqual(result.job.status, AutonomousJobStatus.WAITING_INPUT)
        self.assertTrue(result.waiting)
        self.assertFalse(result.progressed)
        self.assertEqual(worker.calls, 0)

    def test_missing_job_is_rejected(self):
        store = Store()
        pulse = AutonomousJobExecutionPulse(
            AutonomousJobPersistenceService(store),
            AutonomousJobDriver(Worker()),
        )
        with self.assertRaises(LookupError):
            pulse.pulse("missing")


if __name__ == "__main__":
    unittest.main()
