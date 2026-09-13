import unittest

from src.agents.consequence_learning_state_application_feedback_evaluation import (
    ConsequenceLearningStateApplicationFeedbackEvaluationSignal,
)
from src.agents.consequence_learning_state_application_feedback_learning_decision import (
    ConsequenceLearningStateApplicationFeedbackLearningDecision,
    ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus,
)
from src.agents.consequence_learning_state_application_learning_write_request import (
    ConsequenceLearningStateApplicationLearningWriteRequest,
    ConsequenceLearningStateApplicationLearningWriteRequestService,
)


def decision(status=ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus.LEARNING_ELIGIBLE):
    return ConsequenceLearningStateApplicationFeedbackLearningDecision(
        decision_id="decision-50",
        evaluation_id="evaluation-49",
        feedback_id="feedback-1",
        observation_evaluation_id="observation-evaluation-1",
        observation_id="observation-1",
        verification_id="verification-1",
        application_id="application-1",
        applied_record_id="applied-record-1",
        status=status,
        signal=ConsequenceLearningStateApplicationFeedbackEvaluationSignal.APPLICATION_CONFIRMED_SIGNAL,
        confidence=0.5,
        reason="eligible",
    )


class M51ApplicationLearningWriteRequestTests(unittest.TestCase):
    def test_rejects_wrong_type(self):
        with self.assertRaises(TypeError):
            ConsequenceLearningStateApplicationLearningWriteRequestService().create(object())

    def test_creates_only_from_learning_eligible_decision(self):
        result = ConsequenceLearningStateApplicationLearningWriteRequestService().create(decision())
        self.assertIsInstance(result, ConsequenceLearningStateApplicationLearningWriteRequest)
        self.assertEqual(result.decision_id, "decision-50")
        self.assertEqual(result.signal, "APPLICATION_CONFIRMED_SIGNAL")

    def test_rejects_non_eligible_decision(self):
        with self.assertRaisesRegex(ValueError, "LEARNING_ELIGIBLE"):
            ConsequenceLearningStateApplicationLearningWriteRequestService().create(
                decision(ConsequenceLearningStateApplicationFeedbackLearningDecisionStatus.REVIEW_REQUIRED)
            )

    def test_request_id_is_deterministic(self):
        service = ConsequenceLearningStateApplicationLearningWriteRequestService()
        first = service.create(decision())
        second = service.create(decision())
        self.assertEqual(first.request_id, second.request_id)

    def test_payload_is_immutable(self):
        result = ConsequenceLearningStateApplicationLearningWriteRequestService().create(decision())
        with self.assertRaises(Exception):
            result.learning_payload["x"] = "changed"

    def test_lineage_is_preserved(self):
        result = ConsequenceLearningStateApplicationLearningWriteRequestService().create(decision())
        self.assertEqual(result.evaluation_id, "evaluation-49")
        self.assertEqual(result.feedback_id, "feedback-1")
        self.assertEqual(result.observation_evaluation_id, "observation-evaluation-1")
        self.assertEqual(result.observation_id, "observation-1")
        self.assertEqual(result.verification_id, "verification-1")
        self.assertEqual(result.application_id, "application-1")
        self.assertEqual(result.applied_record_id, "applied-record-1")

    def test_context_marks_request_without_mutation(self):
        context = ConsequenceLearningStateApplicationLearningWriteRequestService().create(decision()).to_context()
        self.assertTrue(context["application_learning_write_requested"])
        self.assertFalse(context["application_learning_written"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_result_is_immutable(self):
        result = ConsequenceLearningStateApplicationLearningWriteRequestService().create(decision())
        with self.assertRaises(Exception):
            result.reason = "changed"


if __name__ == "__main__":
    unittest.main()
