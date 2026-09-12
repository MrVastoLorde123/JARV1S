import unittest

from src.agents.consequence_learning_state_application_feedback import (
    ConsequenceLearningStateApplicationFeedback,
    ConsequenceLearningStateApplicationFeedbackService,
)
from src.agents.consequence_learning_state_application_observation_evaluation import (
    ConsequenceLearningStateApplicationObservationEvaluation,
    ConsequenceLearningStateApplicationObservationEvaluationStatus,
)


def evaluation(status=ConsequenceLearningStateApplicationObservationEvaluationStatus.OBSERVED_APPLIED):
    return ConsequenceLearningStateApplicationObservationEvaluation(
        evaluation_id="evaluation-1",
        observation_id="observation-1",
        verification_id="verification-1",
        application_id="application-1",
        applied_record_id="applied-record-1",
        status=status,
        reason="observed",
    )


class M48LearningStateApplicationFeedbackTests(unittest.TestCase):
    def test_rejects_wrong_type(self):
        with self.assertRaises(TypeError):
            ConsequenceLearningStateApplicationFeedbackService().create(object())

    def test_creates_from_m47_evaluation(self):
        result = ConsequenceLearningStateApplicationFeedbackService().create(evaluation())
        self.assertIsInstance(result, ConsequenceLearningStateApplicationFeedback)
        self.assertEqual(result.evaluation_id, "evaluation-1")
        self.assertEqual(result.observation_id, "observation-1")
        self.assertEqual(result.verification_id, "verification-1")

    def test_upstream_m47_rejects_unsupported_status(self):
        with self.assertRaisesRegex(ValueError, "unsupported application-observation evaluation status"):
            evaluation("OTHER")

    def test_feedback_id_is_deterministic(self):
        service = ConsequenceLearningStateApplicationFeedbackService()
        first = service.create(evaluation())
        second = service.create(evaluation())
        self.assertEqual(first.feedback_id, second.feedback_id)

    def test_result_is_immutable(self):
        result = ConsequenceLearningStateApplicationFeedbackService().create(evaluation())
        with self.assertRaises(Exception):
            result.status = "OTHER"

    def test_context_preserves_authority_walls(self):
        context = ConsequenceLearningStateApplicationFeedbackService().create(evaluation()).to_context()
        self.assertEqual(context["consequence_learning_state_application_feedback_status"], "OBSERVED_APPLIED")
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_lineage_is_preserved(self):
        result = ConsequenceLearningStateApplicationFeedbackService().create(evaluation())
        self.assertEqual(result.evaluation_id, "evaluation-1")
        self.assertEqual(result.observation_id, "observation-1")
        self.assertEqual(result.application_id, "application-1")
        self.assertEqual(result.applied_record_id, "applied-record-1")

    def test_feedback_is_nonempty(self):
        result = ConsequenceLearningStateApplicationFeedbackService().create(evaluation())
        self.assertTrue(result.feedback.strip())


if __name__ == "__main__":
    unittest.main()
