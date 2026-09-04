from __future__ import annotations

import unittest

from src.task_management.dependencies import TaskDependencyGraph
from src.task_management.goals import Goal, Objective, Provenance
from src.task_management.planning import LongHorizonPlanner
from src.task_management.progress import (
    ObservedState,
    ProgressEvidence,
    ProgressStatus,
    TaskProgressEvaluator,
)
from src.task_management.continuation import (
    ContinuationError,
    ContinuationStatus,
    NextStepEngine,
    NextStepProposal,
)
from src.task_management.task import Task, TaskState


class NextStepEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        provenance = Provenance(source="test", reference_id="m20.6")
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
        self.plan = LongHorizonPlanner(
            self.goal, self.objective, self.tasks, self.graph, self.evaluator
        ).build(plan_id="plan-1")

    def test_selects_earliest_structurally_available_unfinished_task(self) -> None:
        decision = NextStepEngine(self.plan, self.graph, self.evaluator.evaluations()).decide()
        self.assertEqual(decision.status, ContinuationStatus.PROPOSED)
        self.assertIsNotNone(decision.proposal)
        self.assertEqual(decision.proposal.task_id, "task-c")
        self.assertEqual(decision.proposal.evidence_ids, ("ev-c",))

    def test_prerequisites_must_be_observed_completed(self) -> None:
        blocked_tasks = (
            Task("task-a", "objective-1", "Research", "Research market", Provenance("test", "m20.6")),
            Task("task-b", "objective-1", "Pricing", "Define pricing", Provenance("test", "m20.6")),
        )
        graph = TaskDependencyGraph(task.task_id for task in blocked_tasks)
        graph.add_dependency("task-a", "task-b")
        evaluator = TaskProgressEvaluator(blocked_tasks)
        evaluator.add_evidence(ProgressEvidence("ev-a", "task-a", ObservedState.PROPOSED, "test", "ev-a"))
        evaluator.add_evidence(ProgressEvidence("ev-b", "task-b", ObservedState.PROPOSED, "test", "ev-b"))
        plan = LongHorizonPlanner(
            self.goal, self.objective, blocked_tasks, graph, evaluator
        ).build(plan_id="plan-blocked")
        decision = NextStepEngine(plan, graph, evaluator.evaluations()).decide()
        self.assertEqual(decision.status, ContinuationStatus.NO_CONTINUATION)

    def test_conflicted_progress_requires_review(self) -> None:
        conflicted = TaskProgressEvaluator(self.tasks)
        conflicted.add_evidence(
            ProgressEvidence("ev-a", "task-a", ObservedState.BLOCKED, "test", "ev-a", "2026-09-04T00:00:00+00:00")
        )
        conflicted.add_evidence(
            ProgressEvidence("ev-b", "task-b", ObservedState.IN_PROGRESS, "test", "ev-b", "2026-09-04T00:00:00+00:00")
        )
        conflicted.add_evidence(
            ProgressEvidence("ev-c", "task-c", ObservedState.PROPOSED, "test", "ev-c", "2026-09-04T00:00:00+00:00")
        )
        plan = LongHorizonPlanner(
            self.goal, self.objective, self.tasks, self.graph, conflicted
        ).build(plan_id="plan-review")
        decision = NextStepEngine(plan, self.graph, conflicted.evaluations()).decide()
        self.assertEqual(decision.status, ContinuationStatus.NEEDS_REVIEW)

    def test_all_terminal_tasks_stop(self) -> None:
        terminal_tasks = tuple(
            Task(task.task_id, task.objective_id, task.title, task.description, task.provenance, TaskState.COMPLETED)
            for task in self.tasks
        )
        evaluator = TaskProgressEvaluator(terminal_tasks)
        for task in terminal_tasks:
            evaluator.add_evidence(
                ProgressEvidence(
                    f"{task.task_id}-ev",
                    task.task_id,
                    ObservedState.COMPLETED,
                    "test",
                    f"{task.task_id}-ev",
                )
            )
        plan = LongHorizonPlanner(
            self.goal, self.objective, terminal_tasks, self.graph, evaluator
        ).build(plan_id="plan-terminal")
        decision = NextStepEngine(plan, self.graph, evaluator.evaluations()).decide()
        self.assertEqual(decision.status, ContinuationStatus.NO_CONTINUATION)

    def test_decision_context_is_non_authoritative(self) -> None:
        decision = NextStepEngine(self.plan, self.graph, self.evaluator.evaluations()).decide()
        context = decision.to_context()
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])

    def test_no_next_step_selection_method_on_graph(self) -> None:
        self.assertFalse(hasattr(self.graph, "next_step"))
        self.assertFalse(hasattr(self.graph, "select_next_step"))

    def test_plan_graph_evaluation_identities_must_match(self) -> None:
        with self.assertRaises(ContinuationError):
            NextStepEngine(self.plan, TaskDependencyGraph(["task-a", "task-b"]), self.evaluator.evaluations())

        with self.assertRaises(ContinuationError):
            missing = self.evaluator.evaluations()[:-1]
            NextStepEngine(self.plan, self.graph, missing)

    def test_proposal_is_immutable_and_non_authoritative(self) -> None:
        decision = NextStepEngine(self.plan, self.graph, self.evaluator.evaluations()).decide()
        proposal = decision.proposal
        self.assertIsInstance(proposal, NextStepProposal)
        with self.assertRaises(Exception):
            proposal.task_id = "changed"
        self.assertFalse(proposal.authorization_granted)
        self.assertFalse(proposal.execution_requested)
        self.assertTrue(proposal.bounded)


if __name__ == "__main__":
    unittest.main()
