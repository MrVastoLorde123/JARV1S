import unittest

from src.agents.consequence_learning_state_application import ConsequenceLearningStateApplicationReceipt
from src.agents.consequence_learning_state_application_request import ConsequenceLearningStateApplicationRequest
from src.agents.consequence_learning_state_application_verification import (
    ConsequenceLearningStateApplicationVerification,
    ConsequenceLearningStateApplicationVerificationService,
)


class Reader:
    def __init__(self, record=None):
        self.record = record
        self.calls = []

    def read(self, *, applied_record_id):
        self.calls.append(applied_record_id)
        return self.record


def request():
    return ConsequenceLearningStateApplicationRequest(
        application_request_id="application-request-1",
        consumption_id="consumption-1",
        request_id="request-1",
        record_id="record-1",
        verification_id="verification-1",
        payload={"decision_status": "LEARNING_ELIGIBLE", "signal_evidence": {"ok": True}},
        reason="verified",
    )


def receipt(application_request_id="application-request-1", request_id="request-1", applied_record_id="applied-record-1"):
    return ConsequenceLearningStateApplicationReceipt(
        application_id="application-1",
        application_request_id=application_request_id,
        request_id=request_id,
        source_record_id="record-1",
        applied_record_id=applied_record_id,
        applied=True,
        applicator_result=applied_record_id,
    )


class M45ApplicationVerificationTests(unittest.TestCase):
    def test_requires_bound_reader(self):
        with self.assertRaisesRegex(RuntimeError, "reader is not bound"):
            ConsequenceLearningStateApplicationVerificationService().verify(request(), receipt())

    def test_rejects_wrong_types(self):
        service = ConsequenceLearningStateApplicationVerificationService(Reader({}))
        with self.assertRaises(TypeError):
            service.verify(object(), receipt())
        with self.assertRaises(TypeError):
            service.verify(request(), object())

    def test_rejects_mismatched_application_request(self):
        service = ConsequenceLearningStateApplicationVerificationService(Reader({}))
        with self.assertRaisesRegex(ValueError, "application request"):
            service.verify(request(), receipt("other"))

    def test_rejects_mismatched_source_request(self):
        service = ConsequenceLearningStateApplicationVerificationService(Reader({}))
        with self.assertRaisesRegex(ValueError, "source request"):
            service.verify(request(), receipt(request_id="other"))

    def test_missing_record_is_unverified(self):
        reader = Reader(None)
        result = ConsequenceLearningStateApplicationVerificationService(reader).verify(request(), receipt())
        self.assertIsInstance(result, ConsequenceLearningStateApplicationVerification)
        self.assertTrue(result.observed is False)
        self.assertFalse(result.verified)
        self.assertEqual(reader.calls, ["applied-record-1"])

    def test_matching_record_is_verified(self):
        req = request()
        observed = {
            "application_id": "application-1",
            "application_request_id": req.application_request_id,
            "request_id": req.request_id,
            "source_record_id": req.record_id,
            "applied_record_id": "applied-record-1",
            "payload": dict(req.payload),
        }
        result = ConsequenceLearningStateApplicationVerificationService(Reader(observed)).verify(req, receipt())
        self.assertTrue(result.observed)
        self.assertTrue(result.verified)

    def test_payload_mismatch_is_not_verified(self):
        req = request()
        observed = {
            "application_id": "application-1",
            "application_request_id": req.application_request_id,
            "request_id": req.request_id,
            "source_record_id": req.record_id,
            "applied_record_id": "applied-record-1",
            "payload": {"different": True},
        }
        result = ConsequenceLearningStateApplicationVerificationService(Reader(observed)).verify(req, receipt())
        self.assertTrue(result.observed)
        self.assertFalse(result.verified)

    def test_verification_result_is_immutable(self):
        req = request()
        observed = {
            "application_id": "application-1",
            "application_request_id": req.application_request_id,
            "request_id": req.request_id,
            "source_record_id": req.record_id,
            "applied_record_id": "applied-record-1",
            "payload": dict(req.payload),
        }
        result = ConsequenceLearningStateApplicationVerificationService(Reader(observed)).verify(req, receipt())
        with self.assertRaises(Exception):
            result.verified = False

    def test_context_does_not_grant_authority(self):
        req = request()
        observed = {
            "application_id": "application-1",
            "application_request_id": req.application_request_id,
            "request_id": req.request_id,
            "source_record_id": req.record_id,
            "applied_record_id": "applied-record-1",
            "payload": dict(req.payload),
        }
        context = ConsequenceLearningStateApplicationVerificationService(Reader(observed)).verify(req, receipt()).to_context()
        self.assertTrue(context["learning_state_application_verified"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])

    def test_verification_id_is_deterministic(self):
        req = request()
        observed = {
            "application_id": "application-1",
            "application_request_id": req.application_request_id,
            "request_id": req.request_id,
            "source_record_id": req.record_id,
            "applied_record_id": "applied-record-1",
            "payload": dict(req.payload),
        }
        service = ConsequenceLearningStateApplicationVerificationService(Reader(observed))
        first = service.verify(req, receipt())
        second = service.verify(req, receipt())
        self.assertEqual(first.verification_id, second.verification_id)


if __name__ == "__main__":
    unittest.main()
