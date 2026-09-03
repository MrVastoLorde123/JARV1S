import unittest

from src.learning.reasoning_quality import (
    FeedbackSignal,
    QualityDimension,
    QualitySignal,
    ReasoningFeedback,
    ReasoningFeedbackConflictError,
    ReasoningFeedbackController,
    ReasoningQualityAssessment,
    ReasoningQualityEvaluator,
    ReasoningQualityStore,
)


class ReasoningQualityTests(unittest.TestCase):
    def signals(self, scores=(0.9, 0.8)):
        return (
            QualitySignal("q1", QualityDimension.OUTCOME_ALIGNMENT, scores[0], "outcome alignment observed"),
            QualitySignal("q2", QualityDimension.EVIDENCE_USE, scores[1], "evidence was used explicitly"),
        )

    def assessment(self, *, score=None, confidence=0.8):
        if score is None:
            signals = self.signals()
        else:
            signals = (
                QualitySignal("q1", QualityDimension.OUTCOME_ALIGNMENT, score, "explicit quality signal"),
            )
        return ReasoningQualityEvaluator().assess(
            reasoning_id="reason-1",
            signals=signals,
            confidence=confidence,
        )

    def test_quality_signal_is_bounded_and_immutable(self):
        signal = self.signals()[0]
        self.assertEqual(signal.dimension, QualityDimension.OUTCOME_ALIGNMENT)
        with self.assertRaises(Exception):
            signal.score = 0.1
        with self.assertRaises(ValueError):
            QualitySignal("q3", QualityDimension.CLARITY, 1.1, "bad")

    def test_assessment_requires_at_least_one_signal(self):
        with self.assertRaises(ValueError):
            ReasoningQualityEvaluator().assess(reasoning_id="reason-1", signals=())

    def test_assessment_rejects_duplicate_dimensions(self):
        signals = (
            QualitySignal("q1", QualityDimension.CLARITY, 0.8, "first"),
            QualitySignal("q2", QualityDimension.CLARITY, 0.9, "duplicate dimension"),
        )
        with self.assertRaises(ValueError):
            ReasoningQualityEvaluator().assess(reasoning_id="reason-1", signals=signals)

    def test_assessment_score_is_deterministic_average(self):
        assessment = self.assessment()
        self.assertAlmostEqual(assessment.overall_score, 0.85, places=12)
        self.assertEqual(assessment.assessment_id, "reason-1:quality")

    def test_assessment_preserves_evaluation_provenance(self):
        assessment = ReasoningQualityEvaluator().assess(
            reasoning_id="reason-1",
            signals=self.signals(),
            evaluation_id="exp-1:evaluation",
            provenance={"source": "m10.5", "evaluation_id": "exp-1:evaluation"},
        )
        self.assertEqual(assessment.evaluation_id, "exp-1:evaluation")
        self.assertEqual(assessment.provenance["evaluation_id"], "exp-1:evaluation")

    def test_feedback_signal_thresholds_are_deterministic(self):
        controller = ReasoningFeedbackController()
        self.assertEqual(controller.generate(self.assessment(score=0.9), target="planning").signal, FeedbackSignal.RETAIN)
        self.assertEqual(controller.generate(self.assessment(score=0.7), target="planning").signal, FeedbackSignal.IMPROVE)
        self.assertEqual(controller.generate(self.assessment(score=0.5), target="planning").signal, FeedbackSignal.CAUTION)
        self.assertEqual(controller.generate(self.assessment(score=0.2), target="planning").signal, FeedbackSignal.INSUFFICIENT)

    def test_feedback_requires_assessment_and_target(self):
        controller = ReasoningFeedbackController()
        with self.assertRaises(TypeError):
            controller.generate("not-an-assessment", target="planning")
        with self.assertRaises(ValueError):
            controller.generate(self.assessment(), target="")

    def test_feedback_preserves_assessment_lineage(self):
        assessment = self.assessment()
        feedback = ReasoningFeedbackController().generate(
            assessment,
            target="response.structure",
            feedback_id="feedback-1",
        )
        self.assertEqual(feedback.assessment_id, assessment.assessment_id)
        self.assertEqual(feedback.feedback_id, "feedback-1")

    def test_feedback_serialization_never_grants_authority(self):
        assessment = self.assessment()
        feedback = ReasoningFeedbackController().generate(assessment, target="planning")
        payload = feedback.to_dict()
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_mutation"])

    def test_store_is_immutable_and_conflict_aware(self):
        assessment = self.assessment()
        feedback = ReasoningFeedbackController().generate(assessment, target="planning")
        store = ReasoningQualityStore()
        updated = store.append_assessment(assessment)
        updated = updated.append_feedback(feedback)
        self.assertEqual(store.assessments, ())
        self.assertEqual(store.feedback, ())
        with self.assertRaises(ReasoningFeedbackConflictError):
            updated.append_assessment(assessment)
        with self.assertRaises(ReasoningFeedbackConflictError):
            updated.append_feedback(feedback)

    def test_feedback_must_reference_stored_assessment(self):
        assessment = self.assessment()
        feedback = ReasoningFeedbackController().generate(assessment, target="planning")
        with self.assertRaises(ValueError):
            ReasoningQualityStore().append_feedback(feedback)

    def test_serialization_is_deterministic_and_non_authoritative(self):
        assessment = self.assessment()
        feedback = ReasoningFeedbackController().generate(assessment, target="planning")
        store = ReasoningQualityStore().append_assessment(assessment).append_feedback(feedback)
        first = store.to_json()
        second = store.to_json()
        self.assertEqual(first, second)
        self.assertIn('"policy_mutation": false', first)
        self.assertIn('"authority_granted": false', first)


if __name__ == "__main__":
    unittest.main()
