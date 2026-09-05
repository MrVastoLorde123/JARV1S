from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_feedback import (
    LearningWriteAdaptationFeedbackService,
)
from src.tools.learning_write_adaptation_feedback_evaluation import (
    LearningWriteAdaptationFeedbackEvaluationCandidate,
    LearningWriteAdaptationFeedbackEvaluationError,
    LearningWriteAdaptationFeedbackEvaluationService,
    LearningWriteAdaptationFeedbackSignalKind,
)
from src.tools.learning_write_adaptation_outcome import (
    LearningWriteAdaptationOutcome,
    LearningWriteAdaptationOutcomeStatus,
)


class LearningWriteAdaptationFeedbackEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        success_outcome = LearningWriteAdaptationOutcome(
            execution_id="adapt-exec-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            candidate_id="candidate-1",
            feedback_id="source-feedback-1",
            source_candidate_id="source-candidate-1",
            domain="semantic",
            status=LearningWriteAdaptationOutcomeStatus.SUCCEEDED,
            adaptation_result={"changed": True},
            result_fingerprint="fp-1",
        )
        self.success_feedback = LearningWriteAdaptationFeedbackService().from_outcome(
            success_outcome
        )

        failure_outcome = LearningWriteAdaptationOutcome(
            execution_id="adapt-exec-2",
            admission_id="admission-2",
            proposal_id="proposal-2",
            decision_id="decision-2",
            candidate_id="candidate-2",
            feedback_id="source-feedback-2",
            source_candidate_id="source-candidate-2",
            domain="procedural",
            status=LearningWriteAdaptationOutcomeStatus.FAILED,
            reason="applier unavailable",
        )
        self.failure_feedback = LearningWriteAdaptationFeedbackService().from_outcome(
            failure_outcome
        )
        self.service = LearningWriteAdaptationFeedbackEvaluationService()

    def test_success_feedback_becomes_success_evaluation_signal(self) -> None:
        evaluation = self.service.evaluate(self.success_feedback)
        self.assertEqual(
            evaluation.signal,
            LearningWriteAdaptationFeedbackSignalKind.ADAPTATION_SUCCESS_SIGNAL,
        )
        self.assertEqual(evaluation.confidence, 0.5)
        self.assertTrue(evaluation.evidence["payload"]["adaptation_result"]["changed"])

    def test_failure_feedback_becomes_failure_evaluation_signal(self) -> None:
        evaluation = self.service.evaluate(self.failure_feedback)
        self.assertEqual(
            evaluation.signal,
            LearningWriteAdaptationFeedbackSignalKind.ADAPTATION_FAILURE_SIGNAL,
        )
        self.assertEqual(evaluation.evidence["payload"]["reason"], "applier unavailable")

    def test_exact_lineage_is_preserved(self) -> None:
        evaluation = self.service.evaluate(self.success_feedback)
        self.assertEqual(evaluation.feedback_id, self.success_feedback.feedback_id)
        self.assertEqual(evaluation.source_feedback_id, self.success_feedback.source_feedback_id)
        self.assertEqual(evaluation.candidate_id, self.success_feedback.candidate_id)
        self.assertEqual(evaluation.execution_id, self.success_feedback.execution_id)
        self.assertEqual(evaluation.admission_id, self.success_feedback.admission_id)
        self.assertEqual(evaluation.proposal_id, self.success_feedback.proposal_id)
        self.assertEqual(evaluation.decision_id, self.success_feedback.decision_id)
        self.assertEqual(evaluation.source_candidate_id, self.success_feedback.source_candidate_id)
        self.assertEqual(evaluation.domain, self.success_feedback.domain)

    def test_evaluation_id_is_deterministic(self) -> None:
        first = self.service.evaluate(self.success_feedback)
        second = self.service.evaluate(self.success_feedback)
        self.assertEqual(first.evaluation_id, second.evaluation_id)

    def test_evaluation_is_immutable(self) -> None:
        evaluation = self.service.evaluate(self.success_feedback)
        with self.assertRaises(FrozenInstanceError):
            evaluation.confidence = 0.9  # type: ignore[misc]

    def test_evidence_is_recursively_immutable(self) -> None:
        feedback = self.success_feedback
        evaluation = self.service.evaluate(feedback)
        with self.assertRaises(TypeError):
            evaluation.evidence["new"] = "blocked"  # type: ignore[index]
        with self.assertRaises(TypeError):
            evaluation.evidence["payload"]["new"] = "blocked"  # type: ignore[index]

    def test_provenance_is_recursively_immutable(self) -> None:
        evaluation = self.service.evaluate(self.success_feedback)
        with self.assertRaises(TypeError):
            evaluation.provenance["new"] = "blocked"  # type: ignore[index]

    def test_context_is_non_authorizing_and_non_writing(self) -> None:
        evaluation = self.service.evaluate(self.success_feedback)
        context = evaluation.to_context()
        self.assertTrue(context["adaptation_evaluation"])
        self.assertFalse(context["learning_written"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_invalid_feedback_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.evaluate({"bad": True})  # type: ignore[arg-type]

    def test_invalid_signal_is_rejected(self) -> None:
        with self.assertRaises(LearningWriteAdaptationFeedbackEvaluationError):
            LearningWriteAdaptationFeedbackEvaluationCandidate(
                evaluation_id="eval-1",
                feedback_id="feedback-1",
                source_feedback_id="source-feedback-1",
                candidate_id="candidate-1",
                execution_id="execution-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                source_candidate_id="source-1",
                domain="semantic",
                signal="bad",  # type: ignore[arg-type]
                confidence=0.5,
                evidence={},
                provenance={"source": "test"},
                reason="test",
            )

    def test_confidence_must_be_bounded(self) -> None:
        with self.assertRaises(LearningWriteAdaptationFeedbackEvaluationError):
            LearningWriteAdaptationFeedbackEvaluationCandidate(
                evaluation_id="eval-1",
                feedback_id="feedback-1",
                source_feedback_id="source-feedback-1",
                candidate_id="candidate-1",
                execution_id="execution-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                source_candidate_id="source-1",
                domain="semantic",
                signal=LearningWriteAdaptationFeedbackSignalKind.ADAPTATION_SUCCESS_SIGNAL,
                confidence=1.1,
                evidence={},
                provenance={"source": "test"},
                reason="test",
            )


if __name__ == "__main__":
    unittest.main()
