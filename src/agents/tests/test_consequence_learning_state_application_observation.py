import unittest

from src.agents.consequence_learning_state_application_observation import (
    ConsequenceLearningStateApplicationObservation,
    ConsequenceLearningStateApplicationObservationService,
)
from src.agents.consequence_learning_state_application_verification import (
    ConsequenceLearningStateApplicationVerification,
)


def verification(*, verified=True):
    return ConsequenceLearningStateApplicationVerification(
        verification_id="verification-1",
        application_id="application-1",
        application_request_id="application-request-1",
        request_id="request-1",
        applied_record_id="applied-record-1",
        verified=verified,
        observed=verified,
        reason="verified",
    )


class M46ApplicationObservationTests(unittest.TestCase):
    def test_rejects_wrong_type(self):
        with self.assertRaises(TypeError):
            ConsequenceLearningStateApplicationObservationService().observe(object())

    def test_requires_verified_application(self):
        with self.assertRaisesRegex(ValueError, "requires verified application state"):
            ConsequenceLearningStateApplicationObservationService().observe(verification(verified=False))

    def test_observes_verified_application(self):
        result = ConsequenceLearningStateApplicationObservationService().observe(verification())
        self.assertIsInstance(result, ConsequenceLearningStateApplicationObservation)
        self.assertTrue(result.observed)
        self.assertEqual(result.verification_id, "verification-1")
        self.assertEqual(result.application_id, "application-1")
        self.assertEqual(result.application_request_id, "application-request-1")
        self.assertEqual(result.request_id, "request-1")
        self.assertEqual(result.applied_record_id, "applied-record-1")

    def test_result_is_immutable(self):
        result = ConsequenceLearningStateApplicationObservationService().observe(verification())
        with self.assertRaises(Exception):
            result.observed = False

    def test_context_preserves_authority_walls(self):
        context = ConsequenceLearningStateApplicationObservationService().observe(verification()).to_context()
        self.assertTrue(context["learning_state_application_verified"])
        self.assertTrue(context["learning_state_application_observed"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_observation_id_is_deterministic(self):
        service = ConsequenceLearningStateApplicationObservationService()
        first = service.observe(verification())
        second = service.observe(verification())
        self.assertEqual(first.observation_id, second.observation_id)

    def test_lineage_is_preserved(self):
        result = ConsequenceLearningStateApplicationObservationService().observe(verification())
        self.assertEqual(result.to_context()["consequence_learning_state_application_verification_id"], "verification-1")
        self.assertEqual(result.to_context()["consequence_learning_state_application_id"], "application-1")
        self.assertEqual(result.to_context()["consequence_learning_state_applied_record_id"], "applied-record-1")


if __name__ == "__main__":
    unittest.main()
