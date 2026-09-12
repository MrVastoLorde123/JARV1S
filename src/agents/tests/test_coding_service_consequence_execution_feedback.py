import unittest

from src.agents.coding_service import CodingAgentService
from src.agents.consequence_execution_feedback import (
    ConsequenceExecutionFeedbackKind,
    ConsequenceExecutionFeedbackService,
)
from src.agents.consequence_execution_outcome import (
    ConsequenceExecutionOutcome,
    ConsequenceExecutionOutcomeStatus,
)
from src.tools.models import ToolResult


class M36CodingServiceConsequenceExecutionFeedbackTests(unittest.TestCase):
    def _outcome(self, status, *, execution_id="execution-service-36", reason=None, result=None):
        return ConsequenceExecutionOutcome(
            outcome_id="outcome-service-36",
            attempt_id="attempt-service-36",
            execution_id=execution_id,
            preparation_id="prep-service-36",
            authorization_id="auth-service-36",
            handoff_id="handoff-service-36",
            claim_id="claim-service-36",
            task_id="task-service-36",
            consequence_id="coding:advance",
            tool_name="write_file",
            invocation_id="invocation-service-36",
            status=status,
            authorization_granted=True,
            evidence_refs=("evidence-service-36",),
            verification_refs=("verification-service-36",),
            execution_result=result,
            reason=reason,
        )

    def test_service_requires_explicit_feedback_binding(self):
        service = CodingAgentService(planner=object(), worker=object())
        with self.assertRaises(RuntimeError):
            service.evaluate_execution_feedback(
                self._outcome(
                    ConsequenceExecutionOutcomeStatus.NOT_EXECUTED,
                    execution_id=None,
                    reason="blocked",
                )
            )

    def test_service_evaluates_outcome_through_bound_feedback_service(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_execution_feedback()
        feedback = service.evaluate_execution_feedback(
            self._outcome(
                ConsequenceExecutionOutcomeStatus.COMPLETED_SUCCESS,
                result=ToolResult(success=True, tool_name="write_file"),
            )
        )
        self.assertEqual(feedback.kind, ConsequenceExecutionFeedbackKind.SUCCESS)

    def test_service_accepts_injected_feedback_service(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_execution_feedback(ConsequenceExecutionFeedbackService())
        feedback = service.evaluate_execution_feedback(
            self._outcome(
                ConsequenceExecutionOutcomeStatus.COMPLETED_FAILURE,
                reason="executor unavailable",
            )
        )
        self.assertEqual(feedback.kind, ConsequenceExecutionFeedbackKind.FAILURE)
        self.assertEqual(feedback.reason, "executor unavailable")

    def test_feedback_does_not_retry_or_authorize(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_execution_feedback()
        feedback = service.evaluate_execution_feedback(
            self._outcome(
                ConsequenceExecutionOutcomeStatus.NOT_EXECUTED,
                execution_id=None,
                reason="blocked",
            )
        )
        context = feedback.to_context()
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])

    def test_feedback_preserves_authorization_provenance_without_authority(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_execution_feedback()
        feedback = service.evaluate_execution_feedback(
            self._outcome(
                ConsequenceExecutionOutcomeStatus.COMPLETED_SUCCESS,
                result=ToolResult(success=True, tool_name="write_file"),
            )
        )
        self.assertTrue(feedback.authorization_granted)
        self.assertFalse(feedback.to_context()["authority_granted"])


if __name__ == "__main__":
    unittest.main()
