import unittest

from src.agents.consequence_learning_state_persistence import (
    ConsequenceLearningStatePersistenceReceipt,
    ConsequenceLearningStatePersistenceService,
)
from src.agents.consequence_learning_write_request import ConsequenceLearningWriteRequest


class RecordingWriter:
    def __init__(self, record_id="learning-record-40"):
        self.calls = []
        self.record_id = record_id

    def write(self, *, request_id, payload, provenance):
        self.calls.append((request_id, dict(payload), dict(provenance)))
        return self.record_id


class M40ConsequenceLearningStatePersistenceTests(unittest.TestCase):
    def _request(self):
        return ConsequenceLearningWriteRequest(
            request_id="write-request-40",
            decision_id="decision-40",
            evaluation_id="evaluation-40",
            feedback_id="feedback-40",
            outcome_id="outcome-40",
            attempt_id="attempt-40",
            execution_id="execution-40",
            preparation_id="prep-40",
            authorization_id="auth-40",
            handoff_id="handoff-40",
            claim_id="claim-40",
            task_id="task-40",
            consequence_id="coding:advance",
            tool_name="write_file",
            invocation_id="invoke-40",
            confidence=0.5,
            learning_payload={"signal": "SUCCESS_SIGNAL", "value": True},
            reason="eligible",
        )

    def test_unbound_writer_is_rejected(self):
        with self.assertRaises(RuntimeError):
            ConsequenceLearningStatePersistenceService().persist(self._request())

    def test_successful_write_returns_receipt(self):
        writer = RecordingWriter()
        receipt = ConsequenceLearningStatePersistenceService(writer).persist(self._request())
        self.assertIsInstance(receipt, ConsequenceLearningStatePersistenceReceipt)
        self.assertTrue(receipt.persisted)
        self.assertEqual(receipt.request_id, "write-request-40")
        self.assertEqual(receipt.record_id, "learning-record-40")
        self.assertTrue(receipt.to_context()["learning_write_persisted"])

    def test_exact_request_payload_and_provenance_are_forwarded(self):
        writer = RecordingWriter()
        request = self._request()
        ConsequenceLearningStatePersistenceService(writer).persist(request)
        request_id, payload, provenance = writer.calls[0]
        self.assertEqual(request_id, request.request_id)
        self.assertEqual(payload, dict(request.learning_payload))
        self.assertEqual(provenance["decision_id"], request.decision_id)
        self.assertEqual(provenance["execution_id"], request.execution_id)
        self.assertEqual(provenance["claim_id"], request.claim_id)

    def test_writer_result_must_be_non_empty_string(self):
        class BadWriter:
            def write(self, **kwargs):
                return ""
        with self.assertRaises(ValueError):
            ConsequenceLearningStatePersistenceService(BadWriter()).persist(self._request())

    def test_wrong_request_type_is_rejected(self):
        with self.assertRaises(TypeError):
            ConsequenceLearningStatePersistenceService(RecordingWriter()).persist(object())

    def test_receipt_id_is_deterministic(self):
        writer = RecordingWriter()
        service = ConsequenceLearningStatePersistenceService(writer)
        first = service.persist(self._request())
        second = service.persist(self._request())
        self.assertEqual(first.receipt_id, second.receipt_id)

    def test_context_does_not_grant_execution_authority(self):
        receipt = ConsequenceLearningStatePersistenceService(RecordingWriter()).persist(self._request())
        context = receipt.to_context()
        self.assertTrue(context["learning_written"])
        self.assertTrue(context["learning_write_persisted"])
        self.assertTrue(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])

    def test_bind_requires_writer_contract(self):
        with self.assertRaises(TypeError):
            ConsequenceLearningStatePersistenceService().bind(object())


if __name__ == "__main__":
    unittest.main()
