import unittest

from src.agents.coding_service import CodingAgentService
from src.agents.consequence_learning_state_persistence import ConsequenceLearningStatePersistenceService
from src.agents.consequence_learning_write_request import ConsequenceLearningWriteRequest


class RecordingWriter:
    def write(self, *, request_id, payload, provenance):
        self.last = (request_id, payload, provenance)
        return "record-service-40"


class M40CodingServiceConsequenceLearningStatePersistenceTests(unittest.TestCase):
    def _request(self):
        return ConsequenceLearningWriteRequest(
            request_id="write-service-40",
            decision_id="decision-service-40",
            evaluation_id="evaluation-service-40",
            feedback_id="feedback-service-40",
            outcome_id="outcome-service-40",
            attempt_id="attempt-service-40",
            execution_id="execution-service-40",
            preparation_id="prep-service-40",
            authorization_id="auth-service-40",
            handoff_id="handoff-service-40",
            claim_id="claim-service-40",
            task_id="task-service-40",
            consequence_id="coding:advance",
            tool_name="write_file",
            invocation_id="invoke-service-40",
            confidence=0.5,
            learning_payload={"signal": "SUCCESS_SIGNAL"},
            reason="eligible",
        )

    def test_service_requires_explicit_persistence_binding(self):
        service = CodingAgentService(planner=object(), worker=object())
        with self.assertRaises(RuntimeError):
            service.persist_consequence_learning_write_request(self._request())

    def test_service_binds_writer_and_persists_request(self):
        writer = RecordingWriter()
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_learning_state_persistence(writer)
        receipt = service.persist_consequence_learning_write_request(self._request())
        self.assertEqual(receipt.record_id, "record-service-40")
        self.assertTrue(receipt.persisted)

    def test_service_accepts_injected_persistence_service(self):
        writer = RecordingWriter()
        persistence = ConsequenceLearningStatePersistenceService(writer)
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_learning_state_persistence(persistence_service=persistence)
        receipt = service.persist_consequence_learning_write_request(self._request())
        self.assertTrue(receipt.persisted)

    def test_binding_writer_and_service_is_rejected(self):
        service = CodingAgentService(planner=object(), worker=object())
        with self.assertRaises(ValueError):
            service.bind_consequence_learning_state_persistence(
                RecordingWriter(),
                persistence_service=ConsequenceLearningStatePersistenceService(RecordingWriter()),
            )

    def test_persistence_receipt_does_not_authorize_execution(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_learning_state_persistence(RecordingWriter())
        receipt = service.persist_consequence_learning_write_request(self._request())
        context = receipt.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])


if __name__ == "__main__":
    unittest.main()
