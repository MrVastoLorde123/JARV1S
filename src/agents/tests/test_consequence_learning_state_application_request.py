import unittest

from src.agents.consequence_learning_state_application_request import (
    ConsequenceLearningStateApplicationRequest,
    ConsequenceLearningStateApplicationRequestService,
)
from src.agents.consequence_learning_state_consumption import ConsequenceLearningStateConsumption


def consumption():
    return ConsequenceLearningStateConsumption(
        consumption_id="consumption-1",
        request_id="request-1",
        record_id="record-1",
        source_verification_id="verification-1",
        payload={"decision_status": "LEARNING_ELIGIBLE", "signal_evidence": {"ok": True}},
        consumed=True,
        reason="verified",
    )


class M43ApplicationRequestTests(unittest.TestCase):
    def test_rejects_wrong_type(self):
        with self.assertRaises(TypeError):
            ConsequenceLearningStateApplicationRequestService().create(object())

    def test_creates_from_consumed_state(self):
        result = ConsequenceLearningStateApplicationRequestService().create(consumption())
        self.assertIsInstance(result, ConsequenceLearningStateApplicationRequest)
        self.assertEqual(result.consumption_id, "consumption-1")
        self.assertEqual(result.request_id, "request-1")
        self.assertEqual(result.record_id, "record-1")
        self.assertEqual(result.verification_id, "verification-1")

    def test_payload_is_preserved(self):
        source = consumption()
        result = ConsequenceLearningStateApplicationRequestService().create(source)
        self.assertEqual(result.payload, source.payload)
        self.assertIs(result.payload, source.payload)

    def test_result_is_immutable(self):
        result = ConsequenceLearningStateApplicationRequestService().create(consumption())
        with self.assertRaises(Exception):
            result.request_id = "other"

    def test_context_preserves_authority_walls(self):
        context = ConsequenceLearningStateApplicationRequestService().create(consumption()).to_context()
        self.assertTrue(context["learning_state_application_requested"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_application_request_id_is_deterministic(self):
        service = ConsequenceLearningStateApplicationRequestService()
        first = service.create(consumption())
        second = service.create(consumption())
        self.assertEqual(first.application_request_id, second.application_request_id)

    def test_lineage_is_retained_in_context(self):
        context = ConsequenceLearningStateApplicationRequestService().create(consumption()).to_context()
        self.assertEqual(context["consequence_learning_state_consumption_id"], "consumption-1")
        self.assertEqual(context["consequence_learning_persistence_verification_id"], "verification-1")
        self.assertEqual(context["consequence_learning_persistence_record_id"], "record-1")


if __name__ == "__main__":
    unittest.main()
