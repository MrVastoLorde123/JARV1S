import unittest

from src.agents.coding_service import CodingAgentService
from src.agents.consequence_execution_feedback import (
    ConsequenceExecutionFeedback,
    ConsequenceExecutionFeedbackKind,
)
from src.agents.consequence_feedback_evaluation import (
    ConsequenceFeedbackEvaluationService,
    ConsequenceFeedbackEvaluationSignal,
)


class M37CodingServiceConsequenceFeedbackEvaluationTests(unittest.TestCase):
    def _make_feedback(self, kind, *, execution_id="execution-service-37", reason=None):
        return ConsequenceExecutionFeedback(
            feedback_id="feedback-service-37",
            outcome_id="outcome-service-37",
            attempt_id="attempt-service-37",
            execution_id=execution_id,
            preparation_id="prep-service-37",
            authorization_id="auth-service-37",
            handoff_id="handoff-service-37",
            claim_id="claim-service-37",
            task_id="task-service-37",
            consequence_id="coding:advance",
            tool_name="write_file",
            invocation_id="invocation-service-37",
            kind=kind,
            payload={"observed": True},
            authorization_granted=True,
            evidence_refs=("evidence-service-37",),
            verification_refs=("verification-service-37",),
            reason=reason,
        )

    def test_service_requires_explicit_evaluation_binding(self):
        service = CodingAgentService(planner=object(), worker=object())
        with self.assertRaises(RuntimeError):
            service.evaluate_consequence_feedback(
                self._make_feedback(
                    ConsequenceExecutionFeedbackKind.NOT_EXECUTED,
                    execution_id=None,
                    reason="blocked",
                )
            )

    def test_service_evaluates_bound_feedback_service(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_feedback_evaluation()
        result = service.evaluate_consequence_feedback(
            self._make_feedback(ConsequenceExecutionFeedbackKind.SUCCESS)
        )
        self.assertEqual(result.signal, ConsequenceFeedbackEvaluationSignal.SUCCESS_SIGNAL)

    def test_service_accepts_injected_evaluation_service(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_feedback_evaluation(ConsequenceFeedbackEvaluationService())
        result = service.evaluate_consequence_feedback(
            self._make_feedback(
                ConsequenceExecutionFeedbackKind.FAILURE,
                reason="executor unavailable",
            )
        )
        self.assertEqual(result.signal, ConsequenceFeedbackEvaluationSignal.FAILURE_SIGNAL)
        self.assertEqual(result.execution_id, "execution-service-37")

    def test_service_handles_not_executed_without_execution_identity(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_feedback_evaluation()
        result = service.evaluate_consequence_feedback(
            self._make_feedback(
                ConsequenceExecutionFeedbackKind.NOT_EXECUTED,
                execution_id=None,
                reason="blocked",
            )
        )
        self.assertEqual(result.signal, ConsequenceFeedbackEvaluationSignal.NOT_EXECUTED_SIGNAL)
        self.assertIsNone(result.execution_id)

    def test_service_evaluation_does_not_retry_or_write_learning(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_feedback_evaluation()
        result = service.evaluate_consequence_feedback(
            self._make_feedback(
                ConsequenceExecutionFeedbackKind.FAILURE,
                reason="executor unavailable",
            )
        )
        context = result.to_context()
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["learning_write_requested"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])


if __name__ == "__main__":
    unittest.main()
