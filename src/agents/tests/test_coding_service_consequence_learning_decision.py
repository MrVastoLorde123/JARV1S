import unittest

from src.agents.coding_service import CodingAgentService
from src.agents.consequence_feedback_evaluation import (
    ConsequenceFeedbackEvaluation,
    ConsequenceFeedbackEvaluationService,
    ConsequenceFeedbackEvaluationSignal,
)
from src.agents.consequence_learning_decision import (
    ConsequenceLearningDecisionService,
    ConsequenceLearningDecisionStatus,
)


class M38CodingServiceConsequenceLearningDecisionTests(unittest.TestCase):
    def _make_evaluation(self, signal, execution_id="execution-service-38"):
        return ConsequenceFeedbackEvaluation(
            evaluation_id="evaluation-service-38",
            feedback_id="feedback-service-38",
            outcome_id="outcome-service-38",
            attempt_id="attempt-service-38",
            execution_id=execution_id,
            preparation_id="prep-service-38",
            authorization_id="auth-service-38",
            handoff_id="handoff-service-38",
            claim_id="claim-service-38",
            task_id="task-service-38",
            consequence_id="coding:advance",
            tool_name="write_file",
            invocation_id="invocation-service-38",
            signal=signal,
            confidence=0.5,
            evidence={"observed": True},
            authorization_granted=True,
            reason="evaluation reason",
        )

    def test_service_requires_explicit_learning_decision_binding(self):
        service = CodingAgentService(planner=object(), worker=object())
        with self.assertRaises(RuntimeError):
            service.decide_consequence_learning(
                self._make_evaluation(ConsequenceFeedbackEvaluationSignal.SUCCESS_SIGNAL)
            )

    def test_service_decides_through_bound_service(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_learning_decision()
        decision = service.decide_consequence_learning(
            self._make_evaluation(ConsequenceFeedbackEvaluationSignal.SUCCESS_SIGNAL)
        )
        self.assertEqual(decision.status, ConsequenceLearningDecisionStatus.LEARNING_ELIGIBLE)

    def test_service_accepts_injected_learning_decision_service(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_learning_decision(ConsequenceLearningDecisionService())
        decision = service.decide_consequence_learning(
            self._make_evaluation(ConsequenceFeedbackEvaluationSignal.FAILURE_SIGNAL)
        )
        self.assertEqual(decision.status, ConsequenceLearningDecisionStatus.REVIEW_REQUIRED)

    def test_service_does_not_write_learning(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_learning_decision()
        decision = service.decide_consequence_learning(
            self._make_evaluation(ConsequenceFeedbackEvaluationSignal.SUCCESS_SIGNAL)
        )
        context = decision.to_context()
        self.assertFalse(context["learning_write_requested"])
        self.assertFalse(context["learning_written"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["authority_granted"])


if __name__ == "__main__":
    unittest.main()
