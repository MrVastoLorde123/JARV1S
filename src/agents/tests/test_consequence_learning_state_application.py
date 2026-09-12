import unittest

from src.agents.consequence_learning_state_application import (
    ConsequenceLearningStateApplicationReceipt,
    ConsequenceLearningStateApplicationService,
)
from src.agents.consequence_learning_state_application_request import ConsequenceLearningStateApplicationRequest


class Applicator:
    def __init__(self, result="applied-record-1"):
        self.result = result
        self.calls = []

    def apply(self, *, application_request_id, request_id, record_id, payload):
        self.calls.append((application_request_id, request_id, record_id, payload))
        return self.result


def request():
    return ConsequenceLearningStateApplicationRequest(
        application_request_id="application-request-1",
        consumption_id="consumption-1",
        request_id="request-1",
        record_id="record-1",
        verification_id="verification-1",
        payload={"decision_status": "LEARNING_ELIGIBLE"},
        reason="verified",
    )


class M44LearningStateApplicationTests(unittest.TestCase):
    def test_requires_bound_applicator(self):
        with self.assertRaisesRegex(RuntimeError, "applicator is not bound"):
            ConsequenceLearningStateApplicationService().apply(request())

    def test_rejects_wrong_type(self):
        with self.assertRaises(TypeError):
            ConsequenceLearningStateApplicationService(Applicator()).apply(object())

    def test_applies_matching_request(self):
        applicator = Applicator()
        result = ConsequenceLearningStateApplicationService(applicator).apply(request())
        self.assertIsInstance(result, ConsequenceLearningStateApplicationReceipt)
        self.assertTrue(result.applied)
        self.assertEqual(result.applied_record_id, "applied-record-1")
        self.assertEqual(applicator.calls[0][0], "application-request-1")
        self.assertEqual(applicator.calls[0][1], "request-1")

    def test_rejects_empty_applicator_result(self):
        with self.assertRaisesRegex(ValueError, "non-empty record identity"):
            ConsequenceLearningStateApplicationService(Applicator(" ")).apply(request())

    def test_receipt_is_immutable(self):
        result = ConsequenceLearningStateApplicationService(Applicator()).apply(request())
        with self.assertRaises(Exception):
            result.applied = False

    def test_application_id_is_deterministic(self):
        first = ConsequenceLearningStateApplicationService(Applicator()).apply(request())
        second = ConsequenceLearningStateApplicationService(Applicator()).apply(request())
        self.assertEqual(first.application_id, second.application_id)

    def test_context_marks_mutation_without_authority(self):
        context = ConsequenceLearningStateApplicationService(Applicator()).apply(request()).to_context()
        self.assertTrue(context["learning_state_application_applied"])
        self.assertTrue(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_bind_rejects_invalid_applicator(self):
        with self.assertRaises(TypeError):
            ConsequenceLearningStateApplicationService().bind(object())


if __name__ == "__main__":
    unittest.main()
