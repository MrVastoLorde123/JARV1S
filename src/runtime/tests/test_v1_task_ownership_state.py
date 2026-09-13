from __future__ import annotations

import unittest

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceReceipt, AutonomousJobPersistenceService
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_reasoning_worker import AutonomousReasoningWorker
from src.runtime.autonomous_task_ownership import AutonomousTaskOwnershipState
from src.runtime.autonomous_task_ownership_controller import AutonomousTaskOwnershipController


class _MemoryPersistence(AutonomousJobPersistenceService):
    def __new__(cls):
        return object.__new__(cls)

    def __init__(self) -> None:
        self.jobs: dict[str, AutonomousJob] = {}

    def persist(self, job: AutonomousJob) -> AutonomousJobPersistenceReceipt:
        self.jobs[job.job_id] = job
        return AutonomousJobPersistenceReceipt(
            receipt_id=f"receipt-{job.job_id}-{job.step_count}",
            job_id=job.job_id,
            revision=f"revision-{job.step_count}",
            persisted=True,
        )

    def restore(self, job_id: str) -> AutonomousJob | None:
        return self.jobs.get(job_id)


class _RuntimeView:
    def __init__(self, persistence: _MemoryPersistence) -> None:
        self.persistence = persistence

    def inspect(self, job_id: str) -> AutonomousJob | None:
        return self.persistence.restore(job_id)


class V1TaskOwnershipStateTests(unittest.TestCase):
    def test_default_projection_is_working_without_false_progress(self) -> None:
        job = AutonomousJob.create("build the inventory", job_id="ownership-1").start()
        state = AutonomousTaskOwnershipState.from_job(job)

        self.assertEqual(state.goal, "build the inventory")
        self.assertEqual(state.status, AutonomousJobStatus.RUNNING)
        self.assertEqual(state.step_count, 0)
        self.assertEqual(state.remaining_work, ())
        self.assertIsNone(state.next_action)
        self.assertIsNone(state.blocker)
        self.assertTrue(state.working)
        self.assertFalse(state.complete)

    def test_reasoning_metadata_becomes_durable_ownership_state(self) -> None:
        action = AutonomousReasoningAction(
            "plan-1",
            AutonomousReasoningDisposition.CONTINUE,
            "inspect the switch inventory",
            metadata={
                "task_ownership": {
                    "remaining_work": ["collect switch list", "validate uplinks"],
                    "next_action": "collect switch list",
                }
            },
        )
        cycle = AutonomousReasoningWorker.action_to_cycle_result(action)

        self.assertEqual(
            cycle.context_delta["task_ownership"],
            {
                "remaining_work": ["collect switch list", "validate uplinks"],
                "next_action": "collect switch list",
                "blocker": None,
            },
        )

        job = AutonomousJob.create("inventory", job_id="ownership-2").start()
        job = job.record_step(
            phase=cycle.phase,
            summary=cycle.summary,
            context_delta=cycle.context_delta,
        )
        state = AutonomousTaskOwnershipState.from_job(job)

        self.assertEqual(state.remaining_work, ("collect switch list", "validate uplinks"))
        self.assertEqual(state.next_action, "collect switch list")
        self.assertIsNone(state.blocker)

    def test_waiting_cycle_records_blocker(self) -> None:
        action = AutonomousReasoningAction(
            "wait-1",
            AutonomousReasoningDisposition.WAIT_INPUT,
            "need operator input",
            wait_reason="device location is required",
        )
        cycle = AutonomousReasoningWorker.action_to_cycle_result(action)
        job = AutonomousJob.create("locate device", job_id="ownership-3").start()
        job = job.record_step(
            phase=cycle.phase,
            summary=cycle.summary,
            context_delta=cycle.context_delta,
        ).wait_for_input(cycle.reason)
        state = AutonomousTaskOwnershipState.from_job(job)

        self.assertTrue(state.blocked)
        self.assertEqual(state.blocker, "device location is required")
        self.assertEqual(state.waiting_reason, "device location is required")

    def test_controller_persists_remaining_work_and_next_action(self) -> None:
        persistence = _MemoryPersistence()
        job = AutonomousJob.create("finish inventory", job_id="ownership-4")
        persistence.persist(job)
        controller = AutonomousTaskOwnershipController(_RuntimeView(persistence), persistence)

        updated = controller.update(
            "ownership-4",
            remaining_work=["verify ports", "publish report"],
            next_action="verify ports",
            blocker=None,
        )

        self.assertEqual(updated.ownership.remaining_work, ("verify ports", "publish report"))
        self.assertEqual(updated.ownership.next_action, "verify ports")
        restored = persistence.restore("ownership-4")
        self.assertEqual(AutonomousTaskOwnershipState.from_job(restored).remaining_work, ("verify ports", "publish report"))

    def test_controller_rejects_terminal_state_mutation(self) -> None:
        persistence = _MemoryPersistence()
        job = AutonomousJob.create("finish", job_id="ownership-5").start().complete("done")
        persistence.persist(job)
        controller = AutonomousTaskOwnershipController(_RuntimeView(persistence), persistence)

        with self.assertRaises(ValueError):
            controller.update(
                "ownership-5",
                remaining_work=["should never remain"],
                next_action="invalid",
            )

    def test_ownership_validation_rejects_malformed_remaining_work(self) -> None:
        with self.assertRaises(ValueError):
            AutonomousTaskOwnershipState.normalize_context({"remaining_work": "not-a-list"})
        with self.assertRaises(ValueError):
            AutonomousTaskOwnershipState.normalize_context({"remaining_work": ["ok", ""]})


if __name__ == "__main__":
    unittest.main()
