from __future__ import annotations

import unittest

from src.task_management.dependencies import TaskDependencyGraph
from src.task_management.goals import Goal, Objective, Provenance
from src.task_management.persistence import (
    PersistenceError,
    PersistenceSnapshot,
    PersistenceStore,
    build_snapshot,
    recover_snapshot,
)
from src.task_management.planning import LongHorizonPlanner
from src.task_management.progress import ObservedState, ProgressEvidence, TaskProgressEvaluator
from src.task_management.task import Task, TaskState


class PersistenceRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        provenance = Provenance("test", "m20.7")
        self.goal = Goal("goal-1", "Build business", "Build the home automation business", provenance)
        self.objective = Objective("objective-1", "goal-1", "Launch offer", "Prepare the first offer", provenance)
        self.tasks = (
            Task("task-a", "objective-1", "Research", "Research market", provenance, TaskState.COMPLETED, priority=2, created_at="2026-09-01T00:00:00+00:00", updated_at="2026-09-01T00:00:00+00:00"),
            Task("task-b", "objective-1", "Pricing", "Define pricing", provenance, TaskState.IN_PROGRESS, priority=1, created_at="2026-09-02T00:00:00+00:00", updated_at="2026-09-02T00:00:00+00:00"),
        )
        self.graph = TaskDependencyGraph(task.task_id for task in self.tasks)
        self.graph.add_dependency("task-a", "task-b")
        self.evaluator = TaskProgressEvaluator(self.tasks)
        self.evaluator.add_evidence(ProgressEvidence("ev-a", "task-a", ObservedState.COMPLETED, "test", "obs-a", "2026-09-03T00:00:00+00:00", "completed"))
        self.evaluator.add_evidence(ProgressEvidence("ev-b", "task-b", ObservedState.IN_PROGRESS, "test", "obs-b", "2026-09-04T00:00:00+00:00", "working"))
        self.plan = LongHorizonPlanner(
            self.goal, self.objective, self.tasks, self.graph, self.evaluator
        ).build(plan_id="plan-1", source_references=("ref-z", "ref-a"))

    def _snapshot(self) -> PersistenceSnapshot:
        return build_snapshot(
            "snapshot-1",
            self.plan,
            self.goal,
            self.objective,
            self.tasks,
            self.graph,
            self.evaluator,
        )

    def test_round_trip_preserves_full_snapshot(self) -> None:
        snapshot = self._snapshot()
        recovered = recover_snapshot(snapshot.to_json())
        self.assertEqual(recovered, snapshot)
        self.assertEqual(recovered.to_json(), snapshot.to_json())

    def test_recovery_reconstructs_progress_without_invention(self) -> None:
        snapshot = self._snapshot()
        recovered = recover_snapshot(snapshot.to_dict())
        self.assertEqual(tuple(item.evidence_id for item in recovered.evidence), ("ev-a", "ev-b"))
        self.assertEqual(tuple(item.observed_state for item in recovered.evidence), (ObservedState.COMPLETED, ObservedState.IN_PROGRESS))
        self.assertEqual(tuple(item.observed_state for item in recovered.evaluations), (ObservedState.COMPLETED, ObservedState.IN_PROGRESS))

    def test_store_is_idempotent_but_rejects_identity_conflict(self) -> None:
        store = PersistenceStore()
        snapshot = self._snapshot()
        store.put(snapshot)
        store.put(snapshot)
        self.assertEqual(store.get("snapshot-1"), snapshot)
        altered = PersistenceSnapshot(
            snapshot_id=snapshot.snapshot_id,
            plan_id=snapshot.plan_id,
            goal=Goal("goal-1", "Changed", snapshot.goal.description, snapshot.goal.provenance),
            objective=snapshot.objective,
            tasks=snapshot.tasks,
            dependencies=snapshot.dependencies,
            evidence=snapshot.evidence,
            evaluations=snapshot.evaluations,
            plan_status=snapshot.plan_status,
        )
        with self.assertRaises(PersistenceError):
            store.put(altered)

    def test_authority_cannot_be_recovered(self) -> None:
        payload = self._snapshot().to_dict()
        payload["authority"]["authorization_granted"] = True
        with self.assertRaises(PersistenceError):
            recover_snapshot(payload)

    def test_malformed_dependency_cannot_be_recovered(self) -> None:
        payload = self._snapshot().to_dict()
        payload["dependencies"] = [["task-a", "missing-task"]]
        with self.assertRaises(PersistenceError):
            recover_snapshot(payload)

    def test_evaluation_mismatch_cannot_be_recovered(self) -> None:
        payload = self._snapshot().to_dict()
        payload["evaluations"][0]["observed_state"] = ObservedState.BLOCKED.value
        with self.assertRaises(PersistenceError):
            recover_snapshot(payload)

    def test_schema_version_is_explicit(self) -> None:
        payload = self._snapshot().to_dict()
        payload["schema_version"] = 999
        with self.assertRaises(PersistenceError):
            recover_snapshot(payload)

    def test_snapshot_is_immutable(self) -> None:
        snapshot = self._snapshot()
        with self.assertRaises(Exception):
            snapshot.plan_id = "changed"

    def test_persistence_context_contains_no_authority(self) -> None:
        context = self._snapshot().to_dict()["authority"]
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])

    def test_task_graph_identity_is_required(self) -> None:
        with self.assertRaises(PersistenceError):
            build_snapshot(
                "snapshot-invalid",
                self.plan,
                self.goal,
                self.objective,
                self.tasks,
                TaskDependencyGraph(["task-a"]),
                self.evaluator,
            )


if __name__ == "__main__":
    unittest.main()
