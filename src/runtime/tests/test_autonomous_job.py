import unittest

from src.runtime.autonomous_job import (
    AutonomousJob,
    AutonomousJobEventKind,
    AutonomousJobStatus,
    AutonomousJobValidationError,
)


class AutonomousJobLifecycleTests(unittest.TestCase):
    def test_create_starts_queued_and_records_creation_event(self):
        job = AutonomousJob.create("Investigate the ATS Modbus issue", max_steps=5)
        self.assertEqual(job.status, AutonomousJobStatus.QUEUED)
        self.assertEqual(job.step_count, 0)
        self.assertEqual(job.capacity_remaining, 5)
        self.assertEqual(job.events[-1].kind, AutonomousJobEventKind.CREATED)
        self.assertFalse(job.to_dict()["authorization_granted"])
        self.assertFalse(job.to_dict()["execution_requested"])

    def test_start_then_record_step_preserves_working_context(self):
        job = AutonomousJob.create("Investigate", max_steps=3).start()
        next_job = job.record_step(
            phase="inspect",
            summary="Collected initial evidence",
            observation="Register 10 responds; register 9 does not.",
            context_delta={"register_9": "no_response", "register_10": "responds"},
        )
        self.assertEqual(next_job.status, AutonomousJobStatus.RUNNING)
        self.assertEqual(next_job.step_count, 1)
        self.assertEqual(next_job.steps[0].sequence, 1)
        self.assertEqual(next_job.working_context["register_10"], "responds")
        self.assertEqual(next_job.events[-1].kind, AutonomousJobEventKind.STEP_RECORDED)

    def test_wait_and_resume_preserves_identity_and_history(self):
        job = AutonomousJob.create("Investigate", max_steps=4).start()
        waiting = job.wait_for_tool("Diagnostic command is still running")
        self.assertEqual(waiting.status, AutonomousJobStatus.WAITING_TOOL)
        self.assertEqual(waiting.job_id, job.job_id)
        resumed = waiting.resume()
        self.assertEqual(resumed.status, AutonomousJobStatus.RUNNING)
        self.assertEqual(resumed.job_id, job.job_id)
        self.assertEqual(len(resumed.events), len(job.events) + 2)
        self.assertEqual(resumed.events[-1].kind, AutonomousJobEventKind.RESUMED)

    def test_authorization_wait_is_not_authorization(self):
        job = AutonomousJob.create("Do bounded work").start().wait_for_authorization(
            "A consequential write requires user authorization"
        )
        context = job.to_dict()
        self.assertEqual(job.status, AutonomousJobStatus.WAITING_AUTHORIZATION)
        self.assertTrue(context["waiting_reason"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["execution_requested"])

    def test_input_wait_is_resumable(self):
        job = AutonomousJob.create("Need missing information").start().wait_for_input("Need device IP")
        self.assertTrue(job.resumable)
        self.assertEqual(job.waiting_reason, "Need device IP")
        self.assertEqual(job.resume().status, AutonomousJobStatus.RUNNING)

    def test_complete_requires_result_and_is_terminal(self):
        job = AutonomousJob.create("Finish report").start().complete("Report prepared")
        self.assertEqual(job.status, AutonomousJobStatus.COMPLETED)
        self.assertTrue(job.terminal)
        self.assertEqual(job.result, "Report prepared")
        with self.assertRaises(AutonomousJobValidationError):
            job.start()

    def test_failure_requires_reason_and_is_terminal(self):
        job = AutonomousJob.create("Investigate").start().fail("Tool returned no usable response")
        self.assertEqual(job.status, AutonomousJobStatus.FAILED)
        self.assertTrue(job.terminal)
        self.assertEqual(job.failure_reason, "Tool returned no usable response")

    def test_cancel_is_terminal_and_preserves_reason(self):
        job = AutonomousJob.create("Long task").start().cancel("User cancelled the job")
        self.assertEqual(job.status, AutonomousJobStatus.CANCELLED)
        self.assertTrue(job.terminal)
        self.assertEqual(job.failure_reason, "User cancelled the job")

    def test_step_budget_is_bounded(self):
        job = AutonomousJob.create("Bounded", max_steps=1).start().record_step(
            phase="inspect",
            summary="One allowed cycle",
        )
        with self.assertRaises(AutonomousJobValidationError):
            job.record_step(phase="inspect", summary="Second cycle")

    def test_terminal_jobs_cannot_mutate_working_context(self):
        job = AutonomousJob.create("Done").start().complete("done")
        with self.assertRaises(AutonomousJobValidationError):
            job.with_working_context({"x": 1})

    def test_event_and_step_identity_is_deterministic(self):
        first = AutonomousJob.create("Deterministic", max_steps=7).start().record_step(
            phase="research",
            summary="Read the manual",
            observation="Found the register map",
        )
        second = AutonomousJob.create("Deterministic", max_steps=7).start().record_step(
            phase="research",
            summary="Read the manual",
            observation="Found the register map",
        )
        self.assertEqual(first.job_id, second.job_id)
        self.assertEqual(first.steps[0].step_id, second.steps[0].step_id)
        self.assertEqual(first.events[-1].event_id, second.events[-1].event_id)


if __name__ == "__main__":
    unittest.main()
