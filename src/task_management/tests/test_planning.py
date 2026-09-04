from __future__ import annotations

import unittest

from src.task_management.dependencies import TaskDependencyGraph
from src.task_management.goals import Goal, Objective, Provenance
from src.task_management.planning import (
    LongHorizonPlanner,
    PlanStatus,
    PlanningError,
)
from src.task_management.progress import ObservedState, ProgressEvidence, TaskProgressEvaluator
from src.task_management.task import Task, TaskState


class LongHorizonPlanningTests(unittest.TestCase):
    def setUp(self) -> None:
        provenance = Provenance(source="test", reference_id="m20.5")
        self.goal = Goal(
            goal_id="goal-1",
            title="Build business",
            description="Build the home automation business",
            provenance=provenance,
        )
        self.objective = Objective(
            objective_id="objective-1",
            goal_id="goal-1",
            title="Launch first offer",
            description="Prepare the initial service offer",
            provenance=provenance,
        )
        self.tasks = (
            Task("task-a", "objective-1", "Research market", "Research target market", provenance, TaskState.COMPLETED),
            Task("task-b", "objective-1", "Define pricing", "Define service pricing", provenance, TaskState.IN_PROGRESS),
            Task("task-c", "objective-1", "Build website", "Create the first usable website", provenance, TaskState.PROPOSED),
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
            ProgressEvidence("ev-c", "task-c", ObservedState.UNKNOWN, "test", "ev-c", "2026-09-03T00:00:00+00:00")
        )
        self.planner = LongHorizonPlanner(self.goal, self.objective, self.tasks, self.graph, self.evaluator)

    def test_plan_uses_deterministic_graph_order(self) -> None:
        plan = self.planner.build(plan_id="plan-1")
        self.assertEqual(tuple(step.task_id for step in plan.steps), ("task-a", "task-b", "task-c"))
        self.assertEqual(tuple(step.ordinal for step in plan.steps), (1, 2, 3))

    def test_plan_preserves_progress_evaluation(self) -> None:
        plan = self.planner.build(plan_id="plan-1")
        self.assertEqual(plan.steps[0].progress_status.value, "ALIGNED")
        self.assertEqual(plan.steps[1].progress_status.value, "ALIGNED")
        self.assertEqual(plan.steps[2].progress_status.value, "UNVERIFIED")

    def test_conflicted_progress_marks_plan_for_review(self) -> None:
        evaluator = TaskProgressEvaluator(self.tasks)
        evaluator.add_evidence(
            ProgressEvidence("ev-a", "task-a", ObservedState.BLOCKED, "test", "ev-a", "2026-09-04T00:00:00+00:00")
        )
        evaluator.add_evidence(
            ProgressEvidence("ev-b", "task-b", ObservedState.IN_PROGRESS, "test", "ev-b", "2026-09-04T00:00:00+00:00")
        )
        evaluator.add_evidence(
            ProgressEvidence("ev-c", "task-c", ObservedState.PROPOSED, "test", "ev-c", "2026-09-04T00:00:00+00:00")
        )
        plan = LongHorizonPlanner(self.goal, self.objective, self.tasks, self.graph, evaluator).build(plan_id="plan-2")
        self.assertEqual(plan.status, PlanStatus.NEEDS_REVIEW)

    def test_plan_does_not_select_next_step(self) -> None:
        context = self.planner.build(plan_id="plan-1").to_context()
        self.assertFalse(context["next_step_selected"])
        self.assertFalse(context["schedule_created"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])

    def test_summary_reports_progress_without_action_selection(self) -> None:
        summary = self.planner.summarize()
        self.assertEqual(summary["task_count"], 3)
        self.assertEqual(summary["ordered_task_ids"], ("task-a", "task-b", "task-c"))
        self.assertEqual(summary["aligned_count"], 2)
        self.assertEqual(summary["unverified_count"], 1)
        self.assertEqual(summary["conflicted_count"], 0)
        self.assertFalse(summary["next_step_selected"])

    def test_mismatched_objective_is_rejected(self) -> None:
        other = Objective(
            objective_id="objective-2",
            goal_id="goal-1",
            title="Other objective",
            description="Other work",
            provenance=Provenance("test", "m20.5"),
        )
        with self.assertRaises(PlanningError):
            LongHorizonPlanner(self.goal, other, self.tasks, self.graph, self.evaluator)

    def test_mismatched_graph_is_rejected(self) -> None:
        graph = TaskDependencyGraph(("task-a", "task-b"))
        with self.assertRaises(PlanningError):
            LongHorizonPlanner(self.goal, self.objective, self.tasks, graph, self.evaluator)

    def test_plan_id_requires_explicit_identity(self) -> None:
        with self.assertRaises(ValueError):
            self.planner.build(plan_id=" ")

    def test_plan_is_immutable(self) -> None:
        plan = self.planner.build(plan_id="plan-1")
        with self.assertRaises(Exception):
            plan.plan_id = "changed"


if __name__ == "__main__":
    unittest.main()
