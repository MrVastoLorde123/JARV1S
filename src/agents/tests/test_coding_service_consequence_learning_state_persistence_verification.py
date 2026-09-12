import unittest

from src.agents.coding_service import CodingAgentService
from src.agents.consequence_learning_state_persistence import ConsequenceLearningStatePersistenceReceipt
from src.agents.consequence_learning_state_persistence_verification import ConsequenceLearningStatePersistenceVerificationService
from src.agents.consequence_learning_write_request import ConsequenceLearningWriteRequest


class DummyWorker: pass
class Reader:
    def __init__(self, record): self.record = record
    def read(self, *, request_id, record_id): return self.record


def request():
    return ConsequenceLearningWriteRequest(
        request_id="request-1", decision_id="decision-1", evaluation_id="evaluation-1", feedback_id="feedback-1",
        outcome_id="outcome-1", attempt_id="attempt-1", execution_id="execution-1", preparation_id="preparation-1",
        authorization_id="authorization-1", handoff_id="handoff-1", claim_id="claim-1", task_id="task-1",
        consequence_id="consequence-1", tool_name="tool", invocation_id="invocation-1", confidence=0.9,
        learning_payload={"decision_status":"LEARNING_ELIGIBLE"}, reason="eligible")


def receipt():
    return ConsequenceLearningStatePersistenceReceipt(receipt_id="receipt-1", request_id="request-1", record_id="record-1", persisted=True, writer_result="record-1")


class M41CodingServiceTests(unittest.TestCase):
    def service(self, verification=None):
        return CodingAgentService(object(), DummyWorker(), consequence_learning_state_persistence_verification_service=verification)

    def test_requires_explicit_verification_binding(self):
        with self.assertRaisesRegex(RuntimeError, "not bound"):
            self.service().verify_consequence_learning_state_persistence(request(), receipt())

    def test_accepts_injected_verification_service(self):
        req = request()
        reader = Reader({"request_id":"request-1", "record_id":"record-1", "payload":dict(req.learning_payload)})
        verification = ConsequenceLearningStatePersistenceVerificationService(reader)
        result = self.service(verification).verify_consequence_learning_state_persistence(req, receipt())
        self.assertTrue(result.verified)

    def test_bind_accepts_reader(self):
        req = request()
        reader = Reader({"request_id":"request-1", "record_id":"record-1", "payload":dict(req.learning_payload)})
        service = self.service()
        service.bind_consequence_learning_state_persistence_verification(reader)
        self.assertTrue(service.verify_consequence_learning_state_persistence(req, receipt()).verified)

    def test_bind_rejects_reader_and_service_together(self):
        service = self.service()
        verification = ConsequenceLearningStatePersistenceVerificationService(Reader(None))
        with self.assertRaisesRegex(ValueError, "either reader or verification_service"):
            service.bind_consequence_learning_state_persistence_verification(Reader(None), verification_service=verification)

    def test_bind_requires_one_argument(self):
        service = self.service()
        with self.assertRaisesRegex(ValueError, "reader or verification_service is required"):
            service.bind_consequence_learning_state_persistence_verification()

    def test_verification_does_not_grant_authority(self):
        req = request()
        verification = ConsequenceLearningStatePersistenceVerificationService(Reader({"request_id":"request-1", "record_id":"record-1", "payload":dict(req.learning_payload)}))
        result = self.service(verification).verify_consequence_learning_state_persistence(req, receipt())
        context = result.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])


if __name__ == "__main__":
    unittest.main()
