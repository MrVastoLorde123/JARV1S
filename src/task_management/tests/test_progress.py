from __future__ import annotations

import unittest

from src.task_management.goals import Provenance
from src.task_management.progress import (
    ObservedState,
    ProgressEvidence,
    ProgressEvaluationError,
    ProgressStatus,
    TaskProgressEvaluator,
)
from src.task_management.task import Task, TaskState


class TaskProgressEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        provenance = Provenance(source="test", reference_id="m20.4")
        self.task = Task(
            task_id="task-1",
            objective_id="objective-1",
            title="Build website",
            description="Create the first usable website",
            provenance=provenance,
            state=TaskState.IN_PROGRESS,
        )
        self.evaluator = TaskProgressEvaluator([self.task])

    def evidence(
        self,
        evidence_id: str,
        observed_state: ObservedState,
        *,
        observed_at: str = "2026-09-04T00:00:00+00:00",
    ) -> ProgressEvidence:
        return ProgressEvidence(
            evidence_id=evidence_id,
            task_id="task-1",
            observed_state=observed_state,
            source="test-observer",
            reference_id=evidence_id,
            observed_at=observed_at,
        )

    def test_no_evidence_is_unverified(self) -> None:
        evaluation = self.evaluator.evaluate("task-1")
        self.assertEqual(evaluation.status, ProgressStatus.UNVERIFIED)
        self.assertEqual(evaluation.observed_state, ObservedState.NOT_OBSERVED)

    def test_matching_observation_is_aligned(self) -> None:
        self.evaluator.add_evidence(self.evidence("ev-1", ObservedState.IN_PROGRESS))
        evaluation = self.evaluator.evaluate("task-1")
        self.assertEqual(evaluation.status, ProgressStatus.ALIGNED)
        self.assertFalse(evaluation.conflicts_with_recorded_state)

    def test_different_observation_is_conflicted(self) -> None:
        self.evaluator.add_evidence(self.evidence("ev-1", ObservedState.COMPLETED))
        evaluation = self.evaluator.evaluate("task-1")
        self.assertEqual(evaluation.status, ProgressStatus.CONFLICTED)
        self.assertTrue(evaluation.conflicts_with_recorded_state)

    def test_unknown_observation_is_unverified(self) -> None:
        self.evaluator.add_evidence(self.evidence("ev-1", ObservedState.UNKNOWN))
        evaluation = self.evaluator.evaluate("task-1")
        self.assertEqual(evaluation.status, ProgressStatus.UNVERIFIED)

    def test_latest_evidence_is_selected_deterministically(self) -> None:
        self.evaluator.add_evidence(
            self.evidence("ev-1", ObservedState.IN_PROGRESS, observed_at="2026-09-03T00:00:00+00:00")
        )
        self.evaluator.add_evidence(
            self.evidence("ev-2", ObservedState.COMPLETED, observed_at="2026-09-04T00:00:00+00:00")
        )
        evaluation = self.evaluator.evaluate("task-1")
        self.assertEqual(evaluation.observed_state, ObservedState.COMPLETED)
        self.assertEqual(evaluation.evidence_ids, ("ev-1", "ev-2"))

    def test_same_timestamp_uses_evidence_id_as_tie_break(self) -> None:
        self.evaluator.add_evidence(self.evidence("ev-b", ObservedState.IN_PROGRESS))
        self.evaluator.add_evidence(self.evidence("ev-a", ObservedState.COMPLETED))
        evaluation = self.evaluator.evaluate("task-1")
        self.assertEqual(evaluation.observed_state, ObservedState.IN_PROGRESS)
        self.assertEqual(evaluation.evidence_ids, ("ev-a", "ev-b"))

    def test_evidence_identity_is_conflict_aware(self) -> None:
        first = self.evidence("ev-1", ObservedState.IN_PROGRESS)
        self.evaluator.add_evidence(first)
        self.evaluator.add_evidence(first)
        with self.assertRaises(ProgressEvaluationError):
            self.evaluator.add_evidence(self.evidence("ev-1", ObservedState.COMPLETED))

    def test_unknown_task_is_rejected(self) -> None:
        with self.assertRaises(ProgressEvaluationError):
            self.evaluator.add_evidence(
                ProgressEvidence(
                    evidence_id="ev-1",
                    task_id="missing",
                    observed_state=ObservedState.COMPLETED,
                    source="test-observer",
                    reference_id="ev-1",
                )
            )

    def test_evaluation_does_not_mutate_task(self) -> None:
        self.evaluator.add_evidence(self.evidence("ev-1", ObservedState.COMPLETED))
        before = self.task
        self.evaluator.evaluate("task-1")
        self.assertEqual(self.evaluator._tasks["task-1"], before)
        self.assertEqual(before.state, TaskState.IN_PROGRESS)

    def test_context_is_non_authoritative(self) -> None:
        self.evaluator.add_evidence(self.evidence("ev-1", ObservedState.COMPLETED))
        context = self.evaluator.to_context("task-1")
        self.assertEqual(context["progress_status"], ProgressStatus.CONFLICTED.value)
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])

    def test_failed_and_unknown_observations_do_not_become_task_states(self) -> None:
        self.evaluator.add_evidence(self.evidence("ev-1", ObservedState.FAILED))
        evaluation = self.evaluator.evaluate("task-1")
        self.assertEqual(evaluation.observed_state, ObservedState.FAILED)
        self.assertEqual(self.task.state, TaskState.IN_PROGRESS)

    def test_evaluations_are_deterministically_ordered(self) -> None:
        provenance = Provenance(source="test", reference_id="m20.4")
        second = Task(
            task_id="task-2",
            objective_id="objective-1",
            title="Price services",
            description="Define pricing",
            provenance=provenance,
        )
        self.evaluator.register_task(second)
        ids = tuple(item.task_id for item in self.evaluator.evaluations())
        self.assertEqual(ids, ("task-1", "task-2"))


if __name__ == "__main__":
    unittest.main()
