from __future__ import annotations

import unittest

from src.task_management.continuation import (
    ContinuationError,
    ContinuationStatus,
    NextStepEngine,
    NextStepProposal,
)
from src.task_management.dependencies import TaskDependencyGraph
from src.task_management.goals import Goal, Objective, Provenance
from src.task_management.planning import LongHorizonPlanner
from src.task_management.progress import (
    ObservedState,
    ProgressEvidence,
    TaskProgressEvaluator,
)
from src.task_management.task import Task, TaskState


class NextStepEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        provenance = Provenance(source="test", reference_id="m20.6")
        self.goal = Goal("goal-1", "Build business", "Build the home automation business", provenance)
        self.objective = Objective("objective-1", "goal-1", "Launch first offer", "Prepare initial service offer", provenance)
        self.tasks = (
            Task("task-a", "objective-1", "Research", "Research market", provenance, TaskState.COMPLETED),
            Task("task-b", "objective-1", "Pricing", "Define pricing", provenance, TaskState.IN_PROGRESS),
            Task("task-c", "objective-1", "Website", "Build website", provenance, TaskState.PROPOSED),
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

    def engine(self) -> NextStepEngine:
        return NextStepEngine(self.plan, self.graph, self.evaluator.evaluations())

    def test_selects_earliest_structurally_available_unfinished_task(self) -> None:
        decision = self.engine().decide()
        self.assertEqual(decision.status, ContinuationStatus.PROPOSED)
        self.assertIsNotNone(decision.proposal)
        self.assertEqual(decision.proposal.task_id, "task-b")
        self.assertEqual(decision.proposal.evidence_ids, ("ev-b",))

    def test_prerequisites_must_be_observed_completed(self) -> None:
        blocked_tasks = (
            Task("task-a", "objective-1", "Research", "Research market", Provenance("test", "m20.6")),
            Task("task-b", "objective-1", "Pricing", "Define pricing", Provenance("test", "m20.6")),
        )
        graph = TaskDependencyGraph(task.task_id for task in blocked_tasks)
        graph.add_dependency("task-a", "task-b")
        evaluator = TaskProgressEvaluator(blocked_tasks)
        evaluator.add_evidence(ProgressEvidence("ev-a", "task-a", ObservedState.IN_PROGRESS, "test", "ev-a"))
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
        self.assertIsNone(decision.proposal)

    def test_all_terminal_tasks_stop(self) -> None:
        terminal_tasks = (
            Task("task-a", "objective-1", "One", "One", Provenance("test", "m20.6"), TaskState.COMPLETED),
            Task("task-b", "objective-1", "Two", "Two", Provenance("test", "m20.6"), TaskState.CANCELLED),
        )
        graph = TaskDependencyGraph(task.task_id for task in terminal_tasks)
        graph.add_dependency("task-a", "task-b")
        evaluator = TaskProgressEvaluator(terminal_tasks)
        evaluator.add_evidence(ProgressEvidence("ev-a", "task-a", ObservedState.COMPLETED, "test", "ev-a"))
        evaluator.add_evidence(ProgressEvidence("ev-b", "task-b", ObservedState.CANCELLED, "test", "ev-b"))
        plan = LongHorizonPlanner(self.goal, self.objective, terminal_tasks, graph, evaluator).build(plan_id="plan-done")
        decision = NextStepEngine(plan, graph, evaluator.evaluations()).decide()
        self.assertEqual(decision.status, ContinuationStatus.NO_CONTINUATION)

    def test_proposal_is_immutable_and_non_authoritative(self) -> None:
        proposal = self.engine().select()
        self.assertIsInstance(proposal, NextStepProposal)
        with self.assertRaises(Exception):
            proposal.task_id = "changed"
        context = proposal.to_context()
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertTrue(context["bounded"])

    def test_decision_context_is_non_authoritative(self) -> None:
        context = self.engine().decide().to_context()
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])

    def test_plan_graph_evaluation_identities_must_match(self) -> None:
        extra = Task(
            "task-extra", "objective-1", "Extra", "Extra", Provenance("test", "m20.6")
        )
        evaluator = TaskProgressEvaluator((*self.tasks, extra))
        for evidence_id, task_id, state in (
            ("ev-a", "task-a", ObservedState.COMPLETED),
            ("ev-b", "task-b", ObservedState.IN_PROGRESS),
            ("ev-c", "task-c", ObservedState.UNKNOWN),
            ("ev-x", "task-extra", ObservedState.PROPOSED),
        ):
            evaluator.add_evidence(ProgressEvidence(evidence_id, task_id, state, "test", evidence_id))
        with self.assertRaises(ContinuationError):
            NextStepEngine(self.plan, self.graph, evaluator.evaluations())

    def test_no_next_step_selection_method_on_graph(self) -> None:
        self.assertFalse(hasattr(self.graph, "next_step"))
        self.assertFalse(hasattr(self.graph, "select_next"))
        self.assertFalse(hasattr(self.graph, "authorize"))
        self.assertFalse(hasattr(self.graph, "execute"))


if __name__ == "__main__":
    unittest.main()
