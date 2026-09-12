import unittest

from src.agents.consequence_learning_state_application_feedback import ConsequenceLearningStateApplicationFeedback
from src.agents.consequence_learning_state_application_feedback_evaluation import (
    ConsequenceLearningStateApplicationFeedbackEvaluation,
    ConsequenceLearningStateApplicationFeedbackEvaluationService,
    ConsequenceLearningStateApplicationFeedbackEvaluationSignal,
)


def feedback():
    return ConsequenceLearningStateApplicationFeedback(
        feedback_id="feedback-1",
        evaluation_id="evaluation-1",
        observation_id="observation-1",
        verification_id="verification-1",
        application_id="application-1",
        applied_record_id="applied-record-1",
        status="OBSERVED_APPLIED",
        feedback="observed applied state",
        reason="verified",
    )


class M49ApplicationFeedbackEvaluationTests(unittest.TestCase):
    def test_rejects_wrong_type(self):
        with self.assertRaises(TypeError):
            ConsequenceLearningStateApplicationFeedbackEvaluationService().evaluate(object())

    def test_evaluates_application_feedback(self):
        result = ConsequenceLearningStateApplicationFeedbackEvaluationService().evaluate(feedback())
        self.assertIsInstance(result, ConsequenceLearningStateApplicationFeedbackEvaluation)
        self.assertEqual(result.signal, ConsequenceLearningStateApplicationFeedbackEvaluationSignal.APPLICATION_CONFIRMED_SIGNAL)
        self.assertEqual(result.feedback_id, "feedback-1")
        self.assertEqual(result.observation_evaluation_id, "evaluation-1")

    def test_confidence_is_bounded(self):
        result = ConsequenceLearningStateApplicationFeedbackEvaluationService().evaluate(feedback())
        self.assertEqual(result.confidence, 0.5)

    def test_result_is_immutable(self):
        result = ConsequenceLearningStateApplicationFeedbackEvaluationService().evaluate(feedback())
        with self.assertRaises(Exception):
            result.signal = ConsequenceLearningStateApplicationFeedbackEvaluationSignal.APPLICATION_CONFIRMED_SIGNAL

    def test_evaluation_id_is_deterministic(self):
        service = ConsequenceLearningStateApplicationFeedbackEvaluationService()
        first = service.evaluate(feedback())
        second = service.evaluate(feedback())
        self.assertEqual(first.evaluation_id, second.evaluation_id)

    def test_lineage_is_preserved(self):
        result = ConsequenceLearningStateApplicationFeedbackEvaluationService().evaluate(feedback())
        self.assertEqual(result.observation_id, "observation-1")
        self.assertEqual(result.verification_id, "verification-1")
        self.assertEqual(result.application_id, "application-1")
        self.assertEqual(result.applied_record_id, "applied-record-1")

    def test_context_requires_later_learning_decision(self):
        context = ConsequenceLearningStateApplicationFeedbackEvaluationService().evaluate(feedback()).to_context()
        self.assertTrue(context["learning_decision_required"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_signal_does_not_grant_authority(self):
        result = ConsequenceLearningStateApplicationFeedbackEvaluationService().evaluate(feedback())
        self.assertEqual(result.signal.value, "APPLICATION_CONFIRMED_SIGNAL")


if __name__ == "__main__":
    unittest.main()
