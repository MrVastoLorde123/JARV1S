from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_feedback import (
    LearningWriteFeedbackEvent,
    LearningWriteFeedbackKind,
    LearningWriteFeedbackService,
)
from src.tools.learning_write_feedback_evaluation import (
    LearningWriteAdaptationCandidate,
    LearningWriteFeedbackEvaluationError,
    LearningWriteFeedbackEvaluationService,
    LearningWriteFeedbackSignalKind,
)
from src.tools.learning_write_outcome import LearningWriteOutcomeStatus


class LearningWriteFeedbackEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        outcome = self._outcome(LearningWriteOutcomeStatus.SUCCEEDED)
        self.feedback = LearningWriteFeedbackService().from_outcome(outcome)
        self.service = LearningWriteFeedbackEvaluationService()

    @staticmethod
    def _outcome(status: LearningWriteOutcomeStatus):
        from src.tools.learning_write_outcome import LearningWriteOutcome

        common = dict(
            execution_id="exec-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            candidate_id="candidate-1",
            domain="semantic",
            status=status,
        )
        if status is LearningWriteOutcomeStatus.SUCCEEDED:
            return LearningWriteOutcome(
                **common,
                write_result={"memory_id": 42},
                result_fingerprint="fp-1",
            )
        return LearningWriteOutcome(**common, reason="writer unavailable")

    def test_success_feedback_becomes_success_signal(self) -> None:
        candidate = self.service.evaluate(self.feedback)
        self.assertEqual(
            candidate.signal,
            LearningWriteFeedbackSignalKind.WRITE_SUCCESS_SIGNAL,
        )
        self.assertEqual(candidate.confidence, 0.5)

    def test_failure_feedback_becomes_failure_signal(self) -> None:
        feedback = LearningWriteFeedbackService().from_outcome(
            self._outcome(LearningWriteOutcomeStatus.FAILED)
        )
        candidate = self.service.evaluate(feedback)
        self.assertEqual(
            candidate.signal,
            LearningWriteFeedbackSignalKind.WRITE_FAILURE_SIGNAL,
        )

    def test_exact_write_lineage_is_preserved(self) -> None:
        candidate = self.service.evaluate(self.feedback)
        self.assertEqual(candidate.feedback_id, self.feedback.feedback_id)
        self.assertEqual(candidate.execution_id, self.feedback.execution_id)
        self.assertEqual(candidate.admission_id, self.feedback.admission_id)
        self.assertEqual(candidate.proposal_id, self.feedback.proposal_id)
        self.assertEqual(candidate.decision_id, self.feedback.decision_id)
        self.assertEqual(candidate.source_candidate_id, self.feedback.candidate_id)
        self.assertEqual(candidate.domain, self.feedback.domain)

    def test_candidate_id_is_deterministic(self) -> None:
        first = self.service.evaluate(self.feedback)
        second = self.service.evaluate(self.feedback)
        self.assertEqual(first.candidate_id, second.candidate_id)

    def test_evidence_is_immutable(self) -> None:
        candidate = self.service.evaluate(self.feedback)
        with self.assertRaises(TypeError):
            candidate.evidence["bad"] = True  # type: ignore[index]

    def test_nested_evidence_is_immutable(self) -> None:
        candidate = LearningWriteAdaptationCandidate(
            candidate_id="candidate-1",
            feedback_id="feedback-1",
            execution_id="exec-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            source_candidate_id="source-1",
            domain="semantic",
            signal=LearningWriteFeedbackSignalKind.WRITE_SUCCESS_SIGNAL,
            confidence=0.5,
            evidence={"nested": {"items": [{"x": 1}]}},
            provenance={"source": "test"},
            reason="observed",
        )
        with self.assertRaises(TypeError):
            candidate.evidence["nested"]["items"][0]["x"] = 2

    def test_candidate_is_immutable(self) -> None:
        candidate = self.service.evaluate(self.feedback)
        with self.assertRaises(FrozenInstanceError):
            candidate.signal = LearningWriteFeedbackSignalKind.WRITE_FAILURE_SIGNAL  # type: ignore[misc]

    def test_evaluation_is_non_authorizing_and_non_writing(self) -> None:
        candidate = self.service.evaluate(self.feedback)
        context = candidate.to_context()
        self.assertTrue(context["adaptation_candidate"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_invalid_feedback_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.evaluate({"bad": True})  # type: ignore[arg-type]

    def test_invalid_candidate_kind_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteFeedbackEvaluationError):
            LearningWriteAdaptationCandidate(
                candidate_id="candidate-1",
                feedback_id="feedback-1",
                execution_id="exec-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                source_candidate_id="source-1",
                domain="semantic",
                signal="bad",  # type: ignore[arg-type]
                confidence=0.5,
                evidence={},
                provenance={"source": "test"},
                reason="bad",
            )

    def test_feedback_payload_remains_observation(self) -> None:
        candidate = self.service.evaluate(self.feedback)
        self.assertEqual(candidate.evidence["feedback_kind"], "write_success")
        self.assertEqual(candidate.evidence["payload"]["result_fingerprint"], "fp-1")


if __name__ == "__main__":
    unittest.main()
