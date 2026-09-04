from __future__ import annotations

import unittest

from src.task_management.continuation import ContinuationStatus
from src.task_management.dependencies import TaskDependencyGraph
from src.task_management.goals import Goal, Objective, Provenance
from src.task_management.persistence import PersistenceSnapshot
from src.task_management.progress import ObservedState, ProgressEvidence, TaskProgressEvaluator
from src.task_management.runtime import LongHorizonRuntime, LongHorizonRuntimeError
from src.task_management.task import Task, TaskState


class LongHorizonRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        provenance = Provenance("test", "m20.8")
        self.goal = Goal("goal-1", "Build business", "Build the business", provenance)
        self.objective = Objective(
            "objective-1", "goal-1", "Launch offer", "Prepare launch", provenance, state="ACTIVE"
        )
        self.tasks = (
            Task("task-a", "objective-1", "Research", "Research market", provenance, TaskState.COMPLETED),
            Task("task-b", "objective-1", "Price", "Define pricing", provenance, TaskState.IN_PROGRESS),
            Task("task-c", "objective-1", "Site", "Build site", provenance, TaskState.PROPOSED),
        )
        self.graph = TaskDependencyGraph(task.task_id for task in self.tasks)
        self.graph.add_dependency("task-a", "task-b")
        self.graph.add_dependency("task-b", "task-c")
        self.evaluator = TaskProgressEvaluator(self.tasks)
        self.evaluator.add_evidence(
            ProgressEvidence("ev-a", "task-a", ObservedState.COMPLETED, "test", "ev-a", "2026-09-01T00:00:00+00:00")
        )
        self.evaluator.add_evidence(
            ProgressEvidence("ev-b", "task-b", ObservedState.IN_PROGRESS, "test", "ev-b", "2026-09-02T00:00:00+00:00")
        )
        self.evaluator.add_evidence(
            ProgressEvidence("ev-c", "task-c", ObservedState.PROPOSED, "test", "ev-c", "2026-09-03T00:00:00+00:00")
        )
        self.runtime = LongHorizonRuntime(
            self.goal, self.objective, self.tasks, self.graph, self.evaluator
        )

    def test_build_integrates_all_m20_layers(self) -> None:
        state = self.runtime.build(plan_id="plan-1", snapshot_id="snapshot-1")
        self.assertEqual(state.plan.plan_id, "plan-1")
        self.assertEqual(state.snapshot.snapshot_id, "snapshot-1")
        self.assertEqual(state.decision.status, ContinuationStatus.PROPOSED)
        self.assertEqual(state.decision.proposal.task_id, "task-b")

    def test_recovery_reconstructs_same_runtime_state(self) -> None:
        state = self.runtime.build(plan_id="plan-1", snapshot_id="snapshot-1")
        recovered = LongHorizonRuntime.recover(state.snapshot.to_json())
        rebuilt = self.runtime.rebuild_from_recovery(recovered)
        self.assertIsInstance(recovered, PersistenceSnapshot)
        self.assertEqual(rebuilt.plan, state.plan)
        self.assertEqual(rebuilt.evaluations, state.evaluations)
        self.assertEqual(rebuilt.snapshot.to_json(), state.snapshot.to_json())
        self.assertEqual(rebuilt.decision, state.decision)

    def test_recovery_does_not_grant_authority(self) -> None:
        state = self.runtime.build(plan_id="plan-1", snapshot_id="snapshot-1")
        recovered = LongHorizonRuntime.recover(state.snapshot.to_json())
        rebuilt = self.runtime.rebuild_from_recovery(recovered)
        context = rebuilt.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["decision"]["authorization_granted"])
        self.assertFalse(context["decision"]["execution_requested"])

    def test_recovery_rejects_cross_objective_task_state(self) -> None:
        payload = self.runtime.build(plan_id="plan-1", snapshot_id="snapshot-1").snapshot.to_dict()
        payload["tasks"][0]["objective_id"] = "other-objective"
        with self.assertRaises(LongHorizonRuntimeError):
            LongHorizonRuntime.recover(payload)

    def test_recovery_never_executes(self) -> None:
        state = self.runtime.build(plan_id="plan-1", snapshot_id="snapshot-1")
        payload = state.snapshot.to_dict()
        self.assertFalse(payload["authority"]["authority_granted"])
        self.assertFalse(payload["authority"]["authorization_granted"])
        self.assertFalse(payload["authority"]["execution_requested"])
        self.assertFalse(hasattr(self.runtime, "execute"))
        self.assertFalse(hasattr(self.runtime, "authorize"))


if __name__ == "__main__":
    unittest.main()
