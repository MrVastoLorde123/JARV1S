"""OPS-08 acceptance tests for the live durable continuous runtime."""
from __future__ import annotations

import sqlite3
import tempfile
import time
import unittest
from pathlib import Path

from src.core.jarvis_runtime import JARVISRuntime
from src.runtime.autonomous_job import AutonomousJobStatus
from src.runtime.operational_continuous_runtime import OperationalContinuousRuntime


class FakeResponse:
    def __init__(self, content, metadata):
        self.content = content
        self.metadata = metadata


class ScriptedProcessor:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def ask(self, query):
        self.calls.append(query)
        if not self._responses:
            raise AssertionError("scripted processor has no response left")
        value = self._responses.pop(0)
        if isinstance(value, BaseException):
            raise value
        return value


def db_factory(path: Path):
    return lambda: sqlite3.connect(path)


class OPS08ContinuousRuntimeTests(unittest.TestCase):
    def test_completed_job_runs_through_live_processor_and_is_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "jarvis.db"
            processor = ScriptedProcessor(
                [
                    FakeResponse(
                        "read completed",
                        {
                            "route": "TASK",
                            "stage": "EXECUTION",
                            "execution_status": "COMPLETED",
                        },
                    )
                ]
            )
            runtime = OperationalContinuousRuntime(
                processor,
                connection_factory=db_factory(path),
            )

            job = runtime.submit("Read the switch status.", now=100, interval=10)
            results = runtime.tick(100)

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].run.job.status, AutonomousJobStatus.COMPLETED)
            self.assertEqual(runtime.scheduler._store.load_due(1000), [])
            restored = runtime.inspect(job.job_id)
            self.assertEqual(restored.status, AutonomousJobStatus.COMPLETED)
            self.assertEqual(len(processor.calls), 1)

    def test_failed_execution_gets_bounded_recovery_then_completes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "jarvis.db"
            processor = ScriptedProcessor(
                [
                    FakeResponse(
                        "first attempt failed",
                        {
                            "route": "TASK",
                            "stage": "EXECUTION",
                            "execution_status": "FAILED",
                        },
                    ),
                    FakeResponse(
                        "corrective attempt completed",
                        {
                            "route": "TASK",
                            "stage": "EXECUTION",
                            "execution_status": "COMPLETED",
                        },
                    ),
                ]
            )
            runtime = OperationalContinuousRuntime(
                processor,
                max_recovery_attempts=1,
                connection_factory=db_factory(path),
            )

            job = runtime.submit("Inspect the device.", now=100, interval=10)
            first = runtime.tick(100)[0]
            self.assertEqual(first.run.job.status, AutonomousJobStatus.RUNNING)
            self.assertEqual(first.run.job.working_context["recovery_attempts"], 1)

            second = runtime.tick(110)[0]
            self.assertEqual(second.run.job.status, AutonomousJobStatus.COMPLETED)
            self.assertEqual(len(processor.calls), 2)
            self.assertIn("Previous cycle evidence", processor.calls[1])
            self.assertEqual(runtime.inspect(job.job_id).status, AutonomousJobStatus.COMPLETED)

    def test_waiting_authorization_survives_runtime_restart_without_implicit_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "jarvis.db"

            first_processor = ScriptedProcessor(
                [
                    FakeResponse(
                        "confirmation required",
                        {
                            "route": "TASK",
                            "stage": "CONFIRMATION",
                            "operation_id": "operation-123",
                            "plan_id": "plan-123",
                            "plan_fingerprint": "fingerprint-123",
                        },
                    )
                ]
            )
            first = OperationalContinuousRuntime(
                first_processor,
                connection_factory=db_factory(path),
            )
            job = first.submit("Change the protected device.", now=100, interval=10)
            first_result = first.tick(100)[0]
            self.assertEqual(first_result.run.job.status, AutonomousJobStatus.WAITING_AUTHORIZATION)
            self.assertEqual(first_result.run.job.working_context["pending_operation_id"], "operation-123")
            first.stop()

            second_processor = ScriptedProcessor(
                [
                    FakeResponse(
                        "confirmed and completed",
                        {
                            "route": "TASK",
                            "stage": "EXECUTION",
                            "execution_status": "COMPLETED",
                        },
                    )
                ]
            )
            second = OperationalContinuousRuntime(
                second_processor,
                connection_factory=db_factory(path),
            )

            restored = second.inspect(job.job_id)
            self.assertEqual(restored.status, AutonomousJobStatus.WAITING_AUTHORIZATION)
            self.assertEqual(len(second_processor.calls), 0)

            resumed = second.resume(
                job.job_id,
                confirmed=True,
                now=200,
                interval=10,
            )
            self.assertEqual(resumed.status, AutonomousJobStatus.RUNNING)
            completed = second.tick(200)[0]
            self.assertEqual(completed.run.job.status, AutonomousJobStatus.COMPLETED)
            self.assertEqual(len(second_processor.calls), 1)

    def test_background_runtime_starts_and_stops_cleanly(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "jarvis.db"
            processor = ScriptedProcessor(
                [
                    FakeResponse(
                        "background complete",
                        {
                            "route": "TASK",
                            "stage": "EXECUTION",
                            "execution_status": "COMPLETED",
                        },
                    )
                ]
            )
            runtime = OperationalContinuousRuntime(
                processor,
                connection_factory=db_factory(path),
                poll_interval=0.01,
            )
            runtime.submit("Read the current status.", interval=0.01)

            runtime.start()
            deadline = time.time() + 1.0
            while time.time() < deadline:
                if processor.calls:
                    break
                time.sleep(0.01)
            runtime.stop()

            self.assertFalse(runtime.running)
            self.assertGreaterEqual(len(processor.calls), 1)


class OPS08RuntimeFacadeTests(unittest.TestCase):
    def test_facade_exposes_the_single_attached_operational_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "jarvis.db"
            processor = ScriptedProcessor([])
            runtime = OperationalContinuousRuntime(
                processor,
                connection_factory=db_factory(path),
            )
            facade = JARVISRuntime.from_processor(
                processor,
                operational_runtime=runtime,
            )

            self.assertIs(facade.operational_runtime, runtime)
            submitted = facade.submit_autonomous(
                "Read status.",
                now=100,
                interval=10,
            )
            self.assertEqual(
                facade.inspect_autonomous(submitted.job_id).status,
                AutonomousJobStatus.QUEUED,
            )

