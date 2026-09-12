import unittest

from src.agents.consequence_learning_state_persistence import (
    ConsequenceLearningStatePersistenceReceipt,
)
from src.agents.consequence_learning_state_persistence_verification import (
    ConsequenceLearningStatePersistenceVerification,
    ConsequenceLearningStatePersistenceVerificationService,
)
from src.agents.consequence_learning_write_request import ConsequenceLearningWriteRequest


class Reader:
    def __init__(self, record=None):
        self.record = record
        self.calls = []

    def read(self, *, request_id, record_id):
        self.calls.append((request_id, record_id))
        return self.record


def request():
    return ConsequenceLearningWriteRequest(
        request_id="request-1", decision_id="decision-1", evaluation_id="evaluation-1",
        feedback_id="feedback-1", outcome_id="outcome-1", attempt_id="attempt-1",
        execution_id="execution-1", preparation_id="preparation-1", authorization_id="authorization-1",
        handoff_id="handoff-1", claim_id="claim-1", task_id="task-1", consequence_id="consequence-1",
        tool_name="tool", invocation_id="invocation-1", confidence=0.9,
        learning_payload={"decision_status": "LEARNING_ELIGIBLE", "signal_evidence": {"ok": True}, "decision_reason": "valid"},
        reason="eligible",
    )


def receipt(request_id="request-1", record_id="record-1"):
    return ConsequenceLearningStatePersistenceReceipt(
        receipt_id="receipt-1", request_id=request_id, record_id=record_id,
        persisted=True, writer_result=record_id,
    )


class M41PersistenceVerificationTests(unittest.TestCase):
    def test_requires_bound_reader(self):
        with self.assertRaisesRegex(RuntimeError, "reader is not bound"):
            ConsequenceLearningStatePersistenceVerificationService().verify(request(), receipt())

    def test_rejects_wrong_types(self):
        service = ConsequenceLearningStatePersistenceVerificationService(Reader({}))
        with self.assertRaises(TypeError):
            service.verify(object(), receipt())
        with self.assertRaises(TypeError):
            service.verify(request(), object())

    def test_rejects_receipt_for_different_request(self):
        service = ConsequenceLearningStatePersistenceVerificationService(Reader({}))
        with self.assertRaisesRegex(ValueError, "does not belong"):
            service.verify(request(), receipt("other"))

    def test_missing_record_is_unverified(self):
        reader = Reader(None)
        result = ConsequenceLearningStatePersistenceVerificationService(reader).verify(request(), receipt())
        self.assertIsInstance(result, ConsequenceLearningStatePersistenceVerification)
        self.assertFalse(result.observed)
        self.assertFalse(result.verified)
        self.assertEqual(reader.calls, [("request-1", "record-1")])

    def test_matching_record_is_verified(self):
        req = request()
        observed = {"request_id": req.request_id, "record_id": "record-1", "payload": dict(req.learning_payload)}
        result = ConsequenceLearningStatePersistenceVerificationService(Reader(observed)).verify(req, receipt())
        self.assertTrue(result.observed)
        self.assertTrue(result.verified)
        self.assertEqual(result.request_id, req.request_id)
        self.assertEqual(result.record_id, "record-1")

    def test_wrong_record_identity_is_not_verified(self):
        req = request()
        observed = {"request_id": req.request_id, "record_id": "other", "payload": dict(req.learning_payload)}
        result = ConsequenceLearningStatePersistenceVerificationService(Reader(observed)).verify(req, receipt())
        self.assertTrue(result.observed)
        self.assertFalse(result.verified)

    def test_wrong_request_identity_is_not_verified(self):
        req = request()
        observed = {"request_id": "other", "record_id": "record-1", "payload": dict(req.learning_payload)}
        result = ConsequenceLearningStatePersistenceVerificationService(Reader(observed)).verify(req, receipt())
        self.assertTrue(result.observed)
        self.assertFalse(result.verified)

    def test_wrong_payload_is_not_verified(self):
        req = request()
        observed = {"request_id": req.request_id, "record_id": "record-1", "payload": {"different": True}}
        result = ConsequenceLearningStatePersistenceVerificationService(Reader(observed)).verify(req, receipt())
        self.assertTrue(result.observed)
        self.assertFalse(result.verified)

    def test_verified_result_is_immutable(self):
        req = request()
        observed = {"request_id": req.request_id, "record_id": "record-1", "payload": dict(req.learning_payload)}
        result = ConsequenceLearningStatePersistenceVerificationService(Reader(observed)).verify(req, receipt())
        with self.assertRaises(Exception):
            result.verified = False

    def test_context_does_not_grant_authority(self):
        req = request()
        observed = {"request_id": req.request_id, "record_id": "record-1", "payload": dict(req.learning_payload)}
        context = ConsequenceLearningStatePersistenceVerificationService(Reader(observed)).verify(req, receipt()).to_context()
        self.assertTrue(context["learning_persistence_verified"])
        self.assertTrue(context["learning_persistence_observed"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["memory_mutated"])

    def test_verification_id_is_deterministic(self):
        req = request()
        observed = {"request_id": req.request_id, "record_id": "record-1", "payload": dict(req.learning_payload)}
        service = ConsequenceLearningStatePersistenceVerificationService(Reader(observed))
        first = service.verify(req, receipt())
        second = service.verify(req, receipt())
        self.assertEqual(first.verification_id, second.verification_id)


if __name__ == "__main__":
    unittest.main()
