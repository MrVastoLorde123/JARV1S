from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_feedback import (
    LearningWriteFeedbackEvent,
    LearningWriteFeedbackError,
    LearningWriteFeedbackKind,
    LearningWriteFeedbackService,
)
from src.tools.learning_write_outcome import (
    LearningWriteOutcome,
    LearningWriteOutcomeStatus,
)


class LearningWriteFeedbackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = LearningWriteFeedbackService()

    @staticmethod
    def _build_outcome(status: LearningWriteOutcomeStatus) -> LearningWriteOutcome:
        if status is LearningWriteOutcomeStatus.SUCCEEDED:
            return LearningWriteOutcome(
                execution_id="exec-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                candidate_id="candidate-1",
                domain="semantic",
                status=status,
                write_result={"memory_id": 42},
                result_fingerprint="fp-1",
            )
        return LearningWriteOutcome(
            execution_id="exec-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            candidate_id="candidate-1",
            domain="semantic",
            status=status,
            reason="writer unavailable",
        )

    def test_success_outcome_becomes_success_feedback(self) -> None:
        feedback = self.service.from_outcome(self._build_outcome(LearningWriteOutcomeStatus.SUCCEEDED))
        self.assertEqual(feedback.kind, LearningWriteFeedbackKind.WRITE_SUCCESS)
        self.assertEqual(feedback.payload["result_fingerprint"], "fp-1")

    def test_failed_outcome_becomes_failure_feedback(self) -> None:
        feedback = self.service.from_outcome(self._build_outcome(LearningWriteOutcomeStatus.FAILED))
        self.assertEqual(feedback.kind, LearningWriteFeedbackKind.WRITE_FAILURE)
        self.assertEqual(feedback.payload["reason"], "writer unavailable")

    def test_feedback_preserves_exact_identity(self) -> None:
        outcome = self._build_outcome(LearningWriteOutcomeStatus.SUCCEEDED)
        feedback = self.service.from_outcome(outcome)
        self.assertEqual(feedback.execution_id, outcome.execution_id)
        self.assertEqual(feedback.admission_id, outcome.admission_id)
        self.assertEqual(feedback.proposal_id, outcome.proposal_id)
        self.assertEqual(feedback.decision_id, outcome.decision_id)
        self.assertEqual(feedback.candidate_id, outcome.candidate_id)
        self.assertEqual(feedback.domain, outcome.domain)

    def test_feedback_id_is_deterministic(self) -> None:
        outcome = self._build_outcome(LearningWriteOutcomeStatus.SUCCEEDED)
        first = self.service.from_outcome(outcome)
        second = self.service.from_outcome(outcome)
        self.assertEqual(first.feedback_id, second.feedback_id)

    def test_payload_is_immutable(self) -> None:
        feedback = self.service.from_outcome(self._build_outcome(LearningWriteOutcomeStatus.SUCCEEDED))
        with self.assertRaises(TypeError):
            feedback.payload["nested"] = {"bad": True}  # type: ignore[index]

    def test_nested_payload_is_immutable(self) -> None:
        feedback = LearningWriteFeedbackEvent(
            feedback_id="feedback-1",
            execution_id="exec-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            candidate_id="candidate-1",
            domain="semantic",
            kind=LearningWriteFeedbackKind.WRITE_SUCCESS,
            payload={"nested": {"items": [{"x": 1}]}},
            provenance={"source": "learning_write_outcome"},
            reason="observed",
        )
        with self.assertRaises(TypeError):
            feedback.payload["nested"]["items"][0]["x"] = 2

    def test_feedback_is_immutable(self) -> None:
        feedback = self.service.from_outcome(self._build_outcome(LearningWriteOutcomeStatus.SUCCEEDED))
        with self.assertRaises(FrozenInstanceError):
            feedback.kind = LearningWriteFeedbackKind.WRITE_FAILURE  # type: ignore[misc]

    def test_feedback_is_non_authorizing_and_non_writing(self) -> None:
        feedback = self.service.from_outcome(self._build_outcome(LearningWriteOutcomeStatus.SUCCEEDED))
        context = feedback.to_context()
        self.assertTrue(context["learning_written"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_invalid_outcome_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.from_outcome({"bad": True})  # type: ignore[arg-type]

    def test_invalid_kind_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteFeedbackError):
            LearningWriteFeedbackEvent(
                feedback_id="feedback-1",
                execution_id="exec-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                candidate_id="candidate-1",
                domain="semantic",
                kind="bad",  # type: ignore[arg-type]
                payload={},
                provenance={"source": "x"},
                reason="bad",
            )


if __name__ == "__main__":
    unittest.main()
