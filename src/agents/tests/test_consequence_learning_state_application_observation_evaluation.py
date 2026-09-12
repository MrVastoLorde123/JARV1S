import unittest

from src.agents.consequence_learning_state_application_observation import (
    ConsequenceLearningStateApplicationObservation,
)
from src.agents.consequence_learning_state_application_observation_evaluation import (
    ConsequenceLearningStateApplicationObservationEvaluation,
    ConsequenceLearningStateApplicationObservationEvaluationService,
    ConsequenceLearningStateApplicationObservationEvaluationStatus,
)


def observation(observed=True):
    return ConsequenceLearningStateApplicationObservation(
        observation_id="observation-1",
        verification_id="verification-1",
        application_id="application-1",
        application_request_id="application-request-1",
        request_id="request-1",
        applied_record_id="applied-record-1",
        observed=observed,
        reason="verified",
    )


class M47ApplicationObservationEvaluationTests(unittest.TestCase):
    def test_rejects_wrong_type(self):
        with self.assertRaises(TypeError):
            ConsequenceLearningStateApplicationObservationEvaluationService().evaluate(object())

    def test_rejects_unobserved_state(self):
        with self.assertRaisesRegex(ValueError, "requires an observed application"):
            ConsequenceLearningStateApplicationObservationEvaluationService().evaluate(observation(False))

    def test_evaluates_observed_application(self):
        result = ConsequenceLearningStateApplicationObservationEvaluationService().evaluate(observation())
        self.assertIsInstance(result, ConsequenceLearningStateApplicationObservationEvaluation)
        self.assertEqual(result.status, ConsequenceLearningStateApplicationObservationEvaluationStatus.OBSERVED_APPLIED)
        self.assertEqual(result.observation_id, "observation-1")
        self.assertEqual(result.verification_id, "verification-1")

    def test_result_is_immutable(self):
        result = ConsequenceLearningStateApplicationObservationEvaluationService().evaluate(observation())
        with self.assertRaises(Exception):
            result.status = "OTHER"

    def test_context_preserves_authority_walls(self):
        context = ConsequenceLearningStateApplicationObservationEvaluationService().evaluate(observation()).to_context()
        self.assertEqual(context["consequence_learning_state_application_observation_evaluation_status"], "OBSERVED_APPLIED")
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_evaluation_id_is_deterministic(self):
        service = ConsequenceLearningStateApplicationObservationEvaluationService()
        first = service.evaluate(observation())
        second = service.evaluate(observation())
        self.assertEqual(first.evaluation_id, second.evaluation_id)

    def test_lineage_is_retained(self):
        context = ConsequenceLearningStateApplicationObservationEvaluationService().evaluate(observation()).to_context()
        self.assertEqual(context["consequence_learning_state_application_observation_id"], "observation-1")
        self.assertEqual(context["consequence_learning_state_application_verification_id"], "verification-1")
        self.assertEqual(context["consequence_learning_state_application_id"], "application-1")
        self.assertEqual(context["consequence_learning_state_applied_record_id"], "applied-record-1")


if __name__ == "__main__":
    unittest.main()
