import unittest

from src.agents.consequence_learning_state_application_feedback_evaluation import (
    ConsequenceLearningStateApplicationFeedbackEvaluation,
    ConsequenceLearningStateApplicationFeedbackEvaluationSignal,
)
from src.agents.consequence_learning_state_application_feedback_learning_decision import (
    ConsequenceLearningStateApplicationFeedbackLearningDecision,
    ConsequenceLearningStateApplicationFeedbackLearningDecisionService,
    ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus,
)


def evaluation():
    return ConsequenceLearningStateApplicationFeedbackEvaluation(
        evaluation_id="evaluation-49",
        feedback_id="feedback-1",
        observation_evaluation_id="observation-evaluation-1",
        observation_id="observation-1",
        verification_id="verification-1",
        application_id="application-1",
        applied_record_id="applied-record-1",
        signal=ConsequenceLearningStateApplicationFeedbackEvaluationSignal.APPLICATION_CONFIRMED_SIGNAL,
        confidence=0.5,
        reason="confirmed",
    )


class M50ApplicationFeedbackLearningDecisionTests(unittest.TestCase):
    def test_rejects_wrong_type(self):
        with self.assertRaises(TypeError):
            ConsequenceLearningStateApplicationFeedbackLearningDecisionService().decide(object())

    def test_decides_confirmed_application_as_learning_eligible(self):
        result = ConsequenceLearningStateApplicationFeedbackLearningDecisionService().decide(evaluation())
        self.assertIsInstance(result, ConsequenceLearningStateApplicationFeedbackLearningDecision)
        self.assertEqual(result.status, ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus.LEARNING_ELIGIBLE)
        self.assertTrue(result.eligible)
        self.assertFalse(result.requires_review)

    def test_signal_is_preserved(self):
        result = ConsequenceLearningStateApplicationFeedbackLearningDecisionService().decide(evaluation())
        self.assertEqual(result.signal, ConsequenceLearningStateApplicationFeedbackEvaluationSignal.APPLICATION_CONFIRMED_SIGNAL)
        self.assertEqual(result.confidence, 0.5)

    def test_decision_id_is_deterministic(self):
        service = ConsequenceLearningStateApplicationFeedbackLearningDecisionService()
        first = service.decide(evaluation())
        second = service.decide(evaluation())
        self.assertEqual(first.decision_id, second.decision_id)

    def test_result_is_immutable(self):
        result = ConsequenceLearningStateApplicationFeedbackLearningDecisionService().decide(evaluation())
        with self.assertRaises(Exception):
            result.status = ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus.REVIEW_REQUIRED

    def test_lineage_is_preserved(self):
        result = ConsequenceLearningStateApplicationFeedbackLearningDecisionService().decide(evaluation())
        self.assertEqual(result.evaluation_id, "evaluation-49")
        self.assertEqual(result.feedback_id, "feedback-1")
        self.assertEqual(result.observation_evaluation_id, "observation-evaluation-1")
        self.assertEqual(result.observation_id, "observation-1")
        self.assertEqual(result.verification_id, "verification-1")
        self.assertEqual(result.application_id, "application-1")
        self.assertEqual(result.applied_record_id, "applied-record-1")

    def test_context_requires_later_application_learning_write(self):
        context = ConsequenceLearningStateApplicationFeedbackLearningDecisionService().decide(evaluation()).to_context()
        self.assertTrue(context["learning_decision_made"])
        self.assertTrue(context["learning_eligible"])
        self.assertFalse(context["application_learning_write_requested"])
        self.assertFalse(context["application_learning_written"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_decision_does_not_grant_authority(self):
        result = ConsequenceLearningStateApplicationFeedbackLearningDecisionService().decide(evaluation())
        self.assertEqual(result.status.value, "LEARNING_ELIGIBLE")


if __name__ == "__main__":
    unittest.main()
