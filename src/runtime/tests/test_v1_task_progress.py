from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_driver import AutonomousCycleDisposition, AutonomousCycleResult
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_task_progress import (
    AutonomousTaskProgressVerdict,
    DeterministicAutonomousTaskProgressEvaluator,
)
from src.runtime.autonomous_task_runtime import SQLiteAutonomousTaskRuntime


class V1TaskProgressTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evaluator = DeterministicAutonomousTaskProgressEvaluator()

    def _cycle(self, disposition=AutonomousCycleDisposition.CONTINUE) -> AutonomousCycleResult:
        return AutonomousCycleResult(
            disposition=disposition,
            phase="test",
            summary="cycle summary",
            observation="durable observation",
            reason="waiting" if disposition in {
                AutonomousCycleDisposition.WAIT_AUTHORIZATION,
                AutonomousCycleDisposition.WAIT_INPUT,
                AutonomousCycleDisposition.WAIT_TOOL,
                AutonomousCycleDisposition.PAUSE,
                AutonomousCycleDisposition.FAIL,
            } else None,
            result="done" if disposition is AutonomousCycleDisposition.COMPLETE else None,
        )

    def test_step_advance_is_progress(self) -> None:
        before = AutonomousJob.create("work", job_id="progress-1").start()
        after = before.record_step(phase="test", summary="did work")
        result = self.evaluator.evaluate(before, after, self._cycle())
        self.assertEqual(result.verdict, AutonomousTaskProgressVerdict.PROGRESSED)
        self.assertEqual(result.step_count_before, 0)
        self.assertEqual(result.step_count_after, 1)

    def test_waiting_state_is_blocked(self) -> None:
        before = AutonomousJob.create("work", job_id="progress-2").start()
        after = before.record_step(phase="test", summary="waiting").wait_for_input("input required")
        result = self.evaluator.evaluate(before, after, self._cycle(AutonomousCycleDisposition.WAIT_INPUT))
        self.assertEqual(result.verdict, AutonomousTaskProgressVerdict.BLOCKED)

    def test_completed_state_is_completed(self) -> None:
        before = AutonomousJob.create("work", job_id="progress-3").start()
        after = before.record_step(phase="test", summary="finished").complete("done")
        result = self.evaluator.evaluate(before, after, self._cycle(AutonomousCycleDisposition.COMPLETE))
        self.assertEqual(result.verdict, AutonomousTaskProgressVerdict.COMPLETED)

    def test_failed_state_is_failed(self) -> None:
        before = AutonomousJob.create("work", job_id="progress-4").start()
        after = before.record_step(phase="test", summary="failed").fail("broken")
        result = self.evaluator.evaluate(before, after, self._cycle(AutonomousCycleDisposition.FAIL))
        self.assertEqual(result.verdict, AutonomousTaskProgressVerdict.FAILED)

    def test_no_step_advance_is_no_progress(self) -> None:
        before = AutonomousJob.create("work", job_id="progress-5").start()
        result = self.evaluator.evaluate(before, before, self._cycle())
        self.assertEqual(result.verdict, AutonomousTaskProgressVerdict.NO_PROGRESS)

    def test_runtime_persists_progress_and_restores_after_restart(self) -> None:
        directory = tempfile.TemporaryDirectory()
        try:
            path = Path(directory.name) / "jarvis.db"
            calls = {"count": 0}

            def reason(job):
                calls["count"] += 1
                return AutonomousReasoningAction(
                    "complete",
                    AutonomousReasoningDisposition.COMPLETE,
                    "finished",
                    result="done",
                )

            runtime1 = SQLiteAutonomousTaskRuntime(
                reason,
                connection_factory=lambda: sqlite3.connect(path),
            )
            runtime1.submit("finish task", now=1, interval=5, job_id="progress-restart")
            result = runtime1.tick(1)[0]
            self.assertEqual(result.run.job.status, AutonomousJobStatus.COMPLETED)
            self.assertIsNotNone(result.run.pulses[0].progress)
            self.assertEqual(result.run.pulses[0].progress.verdict, AutonomousTaskProgressVerdict.COMPLETED)

            runtime2 = SQLiteAutonomousTaskRuntime(
                reason,
                connection_factory=lambda: sqlite3.connect(path),
            )
            restored = runtime2.inspect("progress-restart")
            self.assertIsNotNone(restored)
            self.assertEqual(restored.step_count, 1)
            self.assertEqual(restored.working_context["task_progress"]["verdict"], "COMPLETED")
            self.assertEqual(calls["count"], 1)
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()
