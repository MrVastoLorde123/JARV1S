import unittest

from src.agents.consequence_learning_state_application_learning_persistence import (
    ConsequenceLearningStateApplicationLearningPersistenceReceipt,
    ConsequenceLearningStateApplicationLearningPersistenceService,
)
from src.agents.consequence_learning_state_application_learning_write_request import (
    ConsequenceLearningStateApplicationLearningWriteRequest,
)


class RecordingWriter:
    def __init__(self, result="application-learning-record-52"):
        self.result = result
        self.last = None

    def write(self, *, request_id, payload, provenance):
        self.last = (request_id, dict(payload), dict(provenance))
        return self.result


def request():
    return ConsequenceLearningStateApplicationLearningWriteRequest(
        request_id="application-learning-write-request-52",
        decision_id="decision-50",
        evaluation_id="evaluation-49",
        feedback_id="feedback-48",
        observation_evaluation_id="observation-evaluation-47",
        observation_id="observation-46",
        verification_id="verification-45",
        application_id="application-44",
        applied_record_id="applied-record-44",
        signal="APPLICATION_CONFIRMED_SIGNAL",
        confidence=0.5,
        learning_payload={"signal": "APPLICATION_CONFIRMED_SIGNAL", "confidence": 0.5},
        reason="eligible",
    )


class M52ApplicationLearningPersistenceTests(unittest.TestCase):
    def test_rejects_wrong_type(self):
        with self.assertRaises(TypeError):
            ConsequenceLearningStateApplicationLearningPersistenceService(RecordingWriter()).persist(object())

    def test_requires_explicit_writer(self):
        with self.assertRaises(RuntimeError):
            ConsequenceLearningStateApplicationLearningPersistenceService().persist(request())

    def test_persists_through_injected_writer(self):
        writer = RecordingWriter()
        receipt = ConsequenceLearningStateApplicationLearningPersistenceService(writer).persist(request())
        self.assertIsInstance(receipt, ConsequenceLearningStateApplicationLearningPersistenceReceipt)
        self.assertTrue(receipt.persisted)
        self.assertEqual(receipt.record_id, "application-learning-record-52")

    def test_exact_payload_and_provenance_are_forwarded(self):
        writer = RecordingWriter()
        req = request()
        ConsequenceLearningStateApplicationLearningPersistenceService(writer).persist(req)
        request_id, payload, provenance = writer.last
        self.assertEqual(request_id, req.request_id)
        self.assertEqual(payload, dict(req.learning_payload))
        self.assertEqual(provenance["decision_id"], req.decision_id)
        self.assertEqual(provenance["evaluation_id"], req.evaluation_id)
        self.assertEqual(provenance["feedback_id"], req.feedback_id)
        self.assertEqual(provenance["observation_evaluation_id"], req.observation_evaluation_id)
        self.assertEqual(provenance["observation_id"], req.observation_id)
        self.assertEqual(provenance["verification_id"], req.verification_id)
        self.assertEqual(provenance["application_id"], req.application_id)
        self.assertEqual(provenance["applied_record_id"], req.applied_record_id)

    def test_receipt_id_is_deterministic(self):
        writer = RecordingWriter()
        service = ConsequenceLearningStateApplicationLearningPersistenceService(writer)
        first = service.persist(request())
        second = service.persist(request())
        self.assertEqual(first.receipt_id, second.receipt_id)

    def test_empty_writer_result_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-empty record identifier"):
            ConsequenceLearningStateApplicationLearningPersistenceService(RecordingWriter(" ")).persist(request())

    def test_receipt_is_immutable(self):
        receipt = ConsequenceLearningStateApplicationLearningPersistenceService(RecordingWriter()).persist(request())
        with self.assertRaises(Exception):
            receipt.record_id = "other"

    def test_context_preserves_authority_walls(self):
        context = ConsequenceLearningStateApplicationLearningPersistenceService(RecordingWriter()).persist(request()).to_context()
        self.assertTrue(context["application_learning_write_requested"])
        self.assertTrue(context["application_learning_written"])
        self.assertTrue(context["application_learning_persisted"])
        self.assertTrue(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])


if __name__ == "__main__":
    unittest.main()
