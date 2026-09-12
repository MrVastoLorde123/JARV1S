import unittest

from src.agents.coding_service import CodingAgentService
from src.agents.consequence_learning_decision import (
    ConsequenceLearningDecision,
    ConsequenceLearningDecisionStatus,
)
from src.agents.consequence_learning_write_request import (
    ConsequenceLearningWriteRequestService,
)


class M39CodingServiceConsequenceLearningWriteRequestTests(unittest.TestCase):
    def _decision(self, status=ConsequenceLearningDecisionStatus.LEARNING_ELIGIBLE, execution_id="exec-service-39"):
        return ConsequenceLearningDecision(
            decision_id="decision-service-39",
            evaluation_id="evaluation-service-39",
            feedback_id="feedback-service-39",
            outcome_id="outcome-service-39",
            attempt_id="attempt-service-39",
            execution_id=execution_id,
            preparation_id="prep-service-39",
            authorization_id="auth-service-39",
            handoff_id="handoff-service-39",
            claim_id="claim-service-39",
            task_id="task-service-39",
            consequence_id="coding:advance",
            tool_name="write_file",
            invocation_id="invoke-service-39",
            status=status,
            confidence=0.5,
            evidence={"signal": "SUCCESS_SIGNAL"},
            authorization_granted=True,
            reason="eligible",
        )

    def test_service_requires_explicit_binding(self):
        service = CodingAgentService(planner=object(), worker=object())
        with self.assertRaises(RuntimeError):
            service.create_consequence_learning_write_request(self._decision())

    def test_service_creates_request_through_bound_service(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_learning_write_request()
        request = service.create_consequence_learning_write_request(self._decision())
        self.assertEqual(request.execution_id, "exec-service-39")

    def test_service_accepts_injected_service(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_learning_write_request(ConsequenceLearningWriteRequestService())
        request = service.create_consequence_learning_write_request(self._decision())
        self.assertTrue(request.to_context()["learning_write_requested"])
        self.assertFalse(request.to_context()["learning_written"])

    def test_service_rejects_review_required(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_learning_write_request()
        with self.assertRaises(ValueError):
            service.create_consequence_learning_write_request(
                self._decision(ConsequenceLearningDecisionStatus.REVIEW_REQUIRED)
            )

    def test_service_rejects_not_eligible(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_learning_write_request()
        with self.assertRaises(ValueError):
            service.create_consequence_learning_write_request(
                self._decision(ConsequenceLearningDecisionStatus.NOT_ELIGIBLE, execution_id=None)
            )


if __name__ == "__main__":
    unittest.main()
