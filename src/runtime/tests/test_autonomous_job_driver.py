import unittest

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_driver import (
    AutonomousCycleDisposition,
    AutonomousCycleResult,
    AutonomousJobDriver,
)


class ScriptedWorker:
    def __init__(self, results):
        self.results = list(results)
        self.calls = 0

    def run_cycle(self, job):
        self.calls += 1
        return self.results.pop(0)


class FailingWorker:
    def run_cycle(self, job):
        raise RuntimeError("diagnostic backend exploded")


class AutonomousJobDriverTests(unittest.TestCase):
    def test_tick_records_one_cycle_and_continues(self):
        worker = ScriptedWorker(
            [
                AutonomousCycleResult(
                    disposition=AutonomousCycleDisposition.CONTINUE,
                    phase="inspect",
                    summary="Inspected the first evidence source",
                    observation="Found a likely register mismatch",
                    context_delta={"hypothesis": "register_map_mismatch"},
                )
            ]
        )
        job = AutonomousJob.create("Investigate ATS").start()
        result = AutonomousJobDriver(worker).tick(job)
        self.assertEqual(result.status, AutonomousJobStatus.RUNNING)
        self.assertEqual(result.step_count, 1)
        self.assertEqual(result.working_context["hypothesis"], "register_map_mismatch")
        self.assertEqual(worker.calls, 1)

    def test_run_drives_multiple_cycles_to_completion(self):
        worker = ScriptedWorker(
            [
                AutonomousCycleResult(
                    disposition=AutonomousCycleDisposition.CONTINUE,
                    phase="inspect",
                    summary="Collected evidence",
                ),
                AutonomousCycleResult(
                    disposition=AutonomousCycleDisposition.CONTINUE,
                    phase="test",
                    summary="Ran a diagnostic",
                ),
                AutonomousCycleResult(
                    disposition=AutonomousCycleDisposition.COMPLETE,
                    phase="evaluate",
                    summary="Confirmed the cause",
                    result="Register 9 is not part of the working response map.",
                ),
            ]
        )
        job = AutonomousJob.create("Investigate ATS", max_steps=5).start()
        result = AutonomousJobDriver(worker).run(job)
        self.assertEqual(result.status, AutonomousJobStatus.COMPLETED)
        self.assertEqual(result.step_count, 3)
        self.assertEqual(result.result, "Register 9 is not part of the working response map.")
        self.assertEqual(worker.calls, 3)

    def test_authorization_wait_stops_the_loop(self):
        worker = ScriptedWorker(
            [
                AutonomousCycleResult(
                    disposition=AutonomousCycleDisposition.WAIT_AUTHORIZATION,
                    phase="authorize",
                    summary="A consequential operation is ready",
                    reason="Writing the controller requires explicit authorization",
                )
            ]
        )
        job = AutonomousJob.create("Repair ATS").start()
        result = AutonomousJobDriver(worker).run(job)
        self.assertEqual(result.status, AutonomousJobStatus.WAITING_AUTHORIZATION)
        self.assertEqual(result.waiting_reason, "Writing the controller requires explicit authorization")
        self.assertFalse(result.to_dict()["authorization_granted"])
        self.assertEqual(worker.calls, 1)

    def test_input_wait_stops_the_loop(self):
        worker = ScriptedWorker(
            [
                AutonomousCycleResult(
                    disposition=AutonomousCycleDisposition.WAIT_INPUT,
                    phase="diagnose",
                    summary="Need one missing network detail",
                    reason="Need the ATS unit IP address",
                )
            ]
        )
        job = AutonomousJob.create("Diagnose network issue").start()
        result = AutonomousJobDriver(worker).run(job)
        self.assertEqual(result.status, AutonomousJobStatus.WAITING_INPUT)
        self.assertEqual(worker.calls, 1)

    def test_tool_wait_stops_the_loop(self):
        worker = ScriptedWorker(
            [
                AutonomousCycleResult(
                    disposition=AutonomousCycleDisposition.WAIT_TOOL,
                    phase="execute",
                    summary="Diagnostic command submitted",
                    reason="Waiting for diagnostic process",
                )
            ]
        )
        job = AutonomousJob.create("Run diagnostic").start()
        result = AutonomousJobDriver(worker).run(job)
        self.assertEqual(result.status, AutonomousJobStatus.WAITING_TOOL)
        self.assertEqual(worker.calls, 1)

    def test_cycle_limit_pauses_without_failing(self):
        worker = ScriptedWorker(
            [
                AutonomousCycleResult(
                    disposition=AutonomousCycleDisposition.CONTINUE,
                    phase="research",
                    summary="First research pass",
                ),
                AutonomousCycleResult(
                    disposition=AutonomousCycleDisposition.CONTINUE,
                    phase="research",
                    summary="Second research pass",
                ),
            ]
        )
        job = AutonomousJob.create("Research", max_steps=10).start()
        result = AutonomousJobDriver(worker).run(job, max_cycles=1)
        self.assertEqual(result.status, AutonomousJobStatus.PAUSED)
        self.assertEqual(result.waiting_reason, "driver cycle limit reached")
        self.assertEqual(result.step_count, 1)
        self.assertEqual(worker.calls, 1)

    def test_worker_exception_is_contained_as_failure(self):
        job = AutonomousJob.create("Investigate").start()
        result = AutonomousJobDriver(FailingWorker()).tick(job)
        self.assertEqual(result.status, AutonomousJobStatus.FAILED)
        self.assertIn("RuntimeError", result.failure_reason)
        self.assertIn("diagnostic backend exploded", result.failure_reason)

    def test_invalid_worker_result_fails_the_job(self):
        class BadWorker:
            def run_cycle(self, job):
                return {"not": "a cycle result"}

        job = AutonomousJob.create("Investigate").start()
        result = AutonomousJobDriver(BadWorker()).tick(job)
        self.assertEqual(result.status, AutonomousJobStatus.FAILED)
        self.assertIn("invalid cycle result", result.failure_reason)

    def test_terminal_job_does_not_call_worker(self):
        worker = ScriptedWorker([])
        job = AutonomousJob.create("Done").start().complete("finished")
        result = AutonomousJobDriver(worker).run(job)
        self.assertIs(result, job)
        self.assertEqual(worker.calls, 0)


if __name__ == "__main__":
    unittest.main()
