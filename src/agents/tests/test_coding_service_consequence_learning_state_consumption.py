import unittest

from src.agents.coding_service import CodingAgentService
from src.agents.consequence_learning_state_consumption import ConsequenceLearningStateConsumptionService
from src.agents.consequence_learning_state_persistence_verification import ConsequenceLearningStatePersistenceVerification
from src.agents.consequence_learning_write_request import ConsequenceLearningWriteRequest


class DummyWorker:
    pass


def request():
    return ConsequenceLearningWriteRequest(
        request_id="request-1", decision_id="decision-1", evaluation_id="evaluation-1",
        feedback_id="feedback-1", outcome_id="outcome-1", attempt_id="attempt-1",
        execution_id="execution-1", preparation_id="preparation-1", authorization_id="authorization-1",
        handoff_id="handoff-1", claim_id="claim-1", task_id="task-1", consequence_id="consequence-1",
        tool_name="tool", invocation_id="invocation-1", confidence=0.9,
        learning_payload={"decision_status": "LEARNING_ELIGIBLE"}, reason="eligible",
    )


def verification():
    return ConsequenceLearningStatePersistenceVerification(
        verification_id="verification-1", request_id="request-1", record_id="record-1",
        verified=True, observed=True, reason="verified",
    )


class M42CodingServiceTests(unittest.TestCase):
    def service(self, service=None):
        return CodingAgentService(
            object(),
            DummyWorker(),
            consequence_learning_state_consumption_service=service,
        )

    def test_requires_explicit_consumption_binding(self):
        with self.assertRaisesRegex(RuntimeError, "not bound"):
            self.service().consume_consequence_learning_state(request(), verification())

    def test_accepts_injected_consumption_service(self):
        result = self.service(ConsequenceLearningStateConsumptionService()).consume_consequence_learning_state(
            request(), verification()
        )
        self.assertTrue(result.consumed)

    def test_bind_accepts_service(self):
        service = self.service()
        service.bind_consequence_learning_state_consumption(ConsequenceLearningStateConsumptionService())
        self.assertTrue(service.consume_consequence_learning_state(request(), verification()).consumed)

    def test_bind_requires_service(self):
        service = self.service()
        with self.assertRaisesRegex(ValueError, "consumption_service is required"):
            service.bind_consequence_learning_state_consumption()

    def test_consumption_preserves_authority_walls(self):
        result = self.service(ConsequenceLearningStateConsumptionService()).consume_consequence_learning_state(
            request(), verification()
        )
        context = result.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])

    def test_consumption_returns_m42_result(self):
        result = self.service(ConsequenceLearningStateConsumptionService()).consume_consequence_learning_state(
            request(), verification()
        )
        self.assertEqual(result.source_verification_id, "verification-1")
        self.assertEqual(result.record_id, "record-1")


if __name__ == "__main__":
    unittest.main()
