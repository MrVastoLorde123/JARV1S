import unittest

from src.agents.consequence_learning_state_consumption import (
    ConsequenceLearningStateConsumption,
    ConsequenceLearningStateConsumptionService,
)
from src.agents.consequence_learning_state_persistence_verification import (
    ConsequenceLearningStatePersistenceVerification,
)
from src.agents.consequence_learning_write_request import ConsequenceLearningWriteRequest


def request():
    return ConsequenceLearningWriteRequest(
        request_id="request-1", decision_id="decision-1", evaluation_id="evaluation-1",
        feedback_id="feedback-1", outcome_id="outcome-1", attempt_id="attempt-1",
        execution_id="execution-1", preparation_id="preparation-1", authorization_id="authorization-1",
        handoff_id="handoff-1", claim_id="claim-1", task_id="task-1", consequence_id="consequence-1",
        tool_name="tool", invocation_id="invocation-1", confidence=0.9,
        learning_payload={"decision_status": "LEARNING_ELIGIBLE", "signal_evidence": {"ok": True}},
        reason="eligible",
    )


def verification(*, verified=True, request_id="request-1", record_id="record-1"):
    return ConsequenceLearningStatePersistenceVerification(
        verification_id="verification-1", request_id=request_id, record_id=record_id,
        verified=verified, observed=verified, reason="verified",
    )


class M42LearningStateConsumptionTests(unittest.TestCase):
    def test_rejects_wrong_types(self):
        service = ConsequenceLearningStateConsumptionService()
        with self.assertRaises(TypeError):
            service.consume(object(), verification())
        with self.assertRaises(TypeError):
            service.consume(request(), object())

    def test_requires_verified_persistence(self):
        with self.assertRaisesRegex(ValueError, "requires verified persistence"):
            ConsequenceLearningStateConsumptionService().consume(request(), verification(verified=False))

    def test_rejects_verification_for_different_request(self):
        with self.assertRaisesRegex(ValueError, "does not belong"):
            ConsequenceLearningStateConsumptionService().consume(request(), verification(request_id="other"))

    def test_consumes_matching_verified_state(self):
        result = ConsequenceLearningStateConsumptionService().consume(request(), verification())
        self.assertIsInstance(result, ConsequenceLearningStateConsumption)
        self.assertTrue(result.consumed)
        self.assertEqual(result.request_id, "request-1")
        self.assertEqual(result.record_id, "record-1")
        self.assertEqual(result.payload["decision_status"], "LEARNING_ELIGIBLE")

    def test_consumed_payload_matches_request(self):
        req = request()
        result = ConsequenceLearningStateConsumptionService().consume(req, verification())
        self.assertEqual(result.payload, dict(req.learning_payload))

    def test_result_is_immutable(self):
        result = ConsequenceLearningStateConsumptionService().consume(request(), verification())
        with self.assertRaises(Exception):
            result.consumed = False

    def test_context_marks_consumption_without_authority(self):
        context = ConsequenceLearningStateConsumptionService().consume(request(), verification()).to_context()
        self.assertTrue(context["learning_state_consumed"])
        self.assertTrue(context["learning_write_persisted"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_consumption_id_is_deterministic(self):
        service = ConsequenceLearningStateConsumptionService()
        first = service.consume(request(), verification())
        second = service.consume(request(), verification())
        self.assertEqual(first.consumption_id, second.consumption_id)

    def test_lineage_retains_verification_identity(self):
        result = ConsequenceLearningStateConsumptionService().consume(request(), verification())
        self.assertEqual(result.source_verification_id, "verification-1")
        self.assertEqual(result.to_context()["consequence_learning_persistence_verification_id"], "verification-1")


if __name__ == "__main__":
    unittest.main()
