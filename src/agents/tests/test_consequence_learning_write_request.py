import unittest

from src.agents.consequence_learning_decision import (
    ConsequenceLearningDecision,
    ConsequenceLearningDecisionStatus,
)
from src.agents.consequence_learning_write_request import (
    ConsequenceLearningWriteRequest,
    ConsequenceLearningWriteRequestService,
)


class M39ConsequenceLearningWriteRequestTests(unittest.TestCase):
    def _decision(self, status=ConsequenceLearningDecisionStatus.LEARNING_ELIGIBLE, execution_id="exec-39"):
        return ConsequenceLearningDecision(
            decision_id="decision-39",
            evaluation_id="evaluation-39",
            feedback_id="feedback-39",
            outcome_id="outcome-39",
            attempt_id="attempt-39",
            execution_id=execution_id,
            preparation_id="prep-39",
            authorization_id="auth-39",
            handoff_id="handoff-39",
            claim_id="claim-39",
            task_id="task-39",
            consequence_id="coding:advance",
            tool_name="write_file",
            invocation_id="invoke-39",
            status=status,
            confidence=0.5,
            evidence={"signal": "SUCCESS_SIGNAL"},
            authorization_granted=True,
            reason="eligible",
        )

    def test_only_eligible_decision_creates_request(self):
        request = ConsequenceLearningWriteRequestService().create(self._decision())
        self.assertIsInstance(request, ConsequenceLearningWriteRequest)
        self.assertEqual(request.execution_id, "exec-39")

    def test_review_required_is_rejected(self):
        with self.assertRaises(ValueError):
            ConsequenceLearningWriteRequestService().create(
                self._decision(ConsequenceLearningDecisionStatus.REVIEW_REQUIRED)
            )

    def test_not_eligible_is_rejected(self):
        with self.assertRaises(ValueError):
            ConsequenceLearningWriteRequestService().create(
                self._decision(ConsequenceLearningDecisionStatus.NOT_ELIGIBLE, execution_id=None)
            )

    def test_request_id_is_deterministic(self):
        service = ConsequenceLearningWriteRequestService()
        first = service.create(self._decision())
        second = service.create(self._decision())
        self.assertEqual(first.request_id, second.request_id)

    def test_payload_is_immutable(self):
        request = ConsequenceLearningWriteRequestService().create(self._decision())
        with self.assertRaises(TypeError):
            request.learning_payload["x"] = True

    def test_context_does_not_claim_persistence(self):
        context = ConsequenceLearningWriteRequestService().create(self._decision()).to_context()
        self.assertTrue(context["learning_write_requested"])
        self.assertFalse(context["learning_written"])
        self.assertFalse(context["learning_write_persisted"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])

    def test_wrong_input_type_is_rejected(self):
        with self.assertRaises(TypeError):
            ConsequenceLearningWriteRequestService().create(object())


if __name__ == "__main__":
    unittest.main()
