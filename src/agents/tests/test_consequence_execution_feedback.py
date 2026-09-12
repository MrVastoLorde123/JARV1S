import unittest

from src.agents.consequence_execution_feedback import (
    ConsequenceExecutionFeedback,
    ConsequenceExecutionFeedbackKind,
    ConsequenceExecutionFeedbackService,
)
from src.agents.consequence_execution_outcome import (
    ConsequenceExecutionOutcome,
    ConsequenceExecutionOutcomeStatus,
)
from src.tools.models import ToolError, ToolResult


class M36ConsequenceExecutionFeedbackTests(unittest.TestCase):
    def _outcome(self, status, *, execution_id="exec-1", reason=None, result=None):
        return ConsequenceExecutionOutcome(
            outcome_id=f"outcome-{status.value.lower()}",
            attempt_id="attempt-1",
            execution_id=execution_id,
            preparation_id="prep-1",
            authorization_id="auth-1",
            handoff_id="handoff-1",
            claim_id="claim-1",
            task_id="task-1",
            consequence_id="consequence-1",
            tool_name="demo_tool",
            invocation_id="invoke-1",
            status=status,
            authorization_granted=True,
            evidence_refs=("evidence-1",),
            verification_refs=("verification-1",),
            execution_result=result,
            reason=reason,
        )

    def test_success_maps_to_success_feedback(self):
        result = ToolResult(
            success=True,
            tool_name="demo_tool",
            content={"changed": True},
            metadata={"count": 1},
        )
        feedback = ConsequenceExecutionFeedbackService().evaluate(
            self._outcome(ConsequenceExecutionOutcomeStatus.COMPLETED_SUCCESS, result=result)
        )
        self.assertEqual(feedback.kind, ConsequenceExecutionFeedbackKind.SUCCESS)
        self.assertEqual(feedback.execution_id, "exec-1")
        self.assertEqual(feedback.payload["result"], {"changed": True})
        self.assertIsNone(feedback.reason)

    def test_failure_maps_to_failure_feedback(self):
        result = ToolResult(
            success=False,
            tool_name="demo_tool",
            error=ToolError(code="E_FAIL", message="tool failed"),
        )
        feedback = ConsequenceExecutionFeedbackService().evaluate(
            self._outcome(
                ConsequenceExecutionOutcomeStatus.COMPLETED_FAILURE,
                reason="tool failed",
                result=result,
            )
        )
        self.assertEqual(feedback.kind, ConsequenceExecutionFeedbackKind.FAILURE)
        self.assertEqual(feedback.reason, "tool failed")
        self.assertEqual(feedback.payload["execution_outcome_status"], "COMPLETED_FAILURE")

    def test_blocked_maps_to_not_executed(self):
        feedback = ConsequenceExecutionFeedbackService().evaluate(
            self._outcome(
                ConsequenceExecutionOutcomeStatus.NOT_EXECUTED,
                execution_id=None,
                reason="execution was blocked",
                result=None,
            )
        )
        self.assertEqual(feedback.kind, ConsequenceExecutionFeedbackKind.NOT_EXECUTED)
        self.assertIsNone(feedback.execution_id)
        self.assertEqual(feedback.reason, "execution was blocked")
        self.assertIsNone(feedback.payload["execution_result"])

    def test_full_provenance_is_preserved(self):
        feedback = ConsequenceExecutionFeedbackService().evaluate(
            self._outcome(
                ConsequenceExecutionOutcomeStatus.NOT_EXECUTED,
                execution_id=None,
                reason="blocked",
            )
        )
        self.assertEqual(feedback.outcome_id, "outcome-not_executed")
        self.assertEqual(feedback.attempt_id, "attempt-1")
        self.assertEqual(feedback.preparation_id, "prep-1")
        self.assertEqual(feedback.authorization_id, "auth-1")
        self.assertEqual(feedback.handoff_id, "handoff-1")
        self.assertEqual(feedback.claim_id, "claim-1")
        self.assertEqual(feedback.task_id, "task-1")
        self.assertEqual(feedback.consequence_id, "consequence-1")
        self.assertEqual(feedback.tool_name, "demo_tool")
        self.assertEqual(feedback.invocation_id, "invoke-1")
        self.assertEqual(feedback.evidence_refs, ("evidence-1",))
        self.assertEqual(feedback.verification_refs, ("verification-1",))
        self.assertTrue(feedback.authorization_granted)

    def test_feedback_id_is_deterministic(self):
        service = ConsequenceExecutionFeedbackService()
        outcome = self._outcome(
            ConsequenceExecutionOutcomeStatus.NOT_EXECUTED,
            execution_id=None,
            reason="blocked",
        )
        self.assertEqual(service.evaluate(outcome).feedback_id, service.evaluate(outcome).feedback_id)

    def test_identical_outcomes_produce_identical_feedback_id(self):
        service = ConsequenceExecutionFeedbackService()
        first = service.evaluate(
            self._outcome(ConsequenceExecutionOutcomeStatus.NOT_EXECUTED, execution_id=None, reason="blocked")
        )
        second = service.evaluate(
            self._outcome(ConsequenceExecutionOutcomeStatus.NOT_EXECUTED, execution_id=None, reason="blocked")
        )
        self.assertEqual(first.feedback_id, second.feedback_id)

    def test_different_reason_changes_feedback_id(self):
        service = ConsequenceExecutionFeedbackService()
        first = service.evaluate(
            self._outcome(ConsequenceExecutionOutcomeStatus.NOT_EXECUTED, execution_id=None, reason="blocked")
        )
        second = service.evaluate(
            self._outcome(ConsequenceExecutionOutcomeStatus.NOT_EXECUTED, execution_id=None, reason="policy")
        )
        self.assertNotEqual(first.feedback_id, second.feedback_id)

    def test_payload_is_immutable(self):
        feedback = ConsequenceExecutionFeedbackService().evaluate(
            self._outcome(
                ConsequenceExecutionOutcomeStatus.COMPLETED_SUCCESS,
                result=ToolResult(success=True, tool_name="demo_tool", content={"ok": True}),
            )
        )
        with self.assertRaises(TypeError):
            feedback.payload["new"] = True

    def test_success_feedback_requires_execution_identity(self):
        with self.assertRaises(ValueError):
            ConsequenceExecutionFeedback(
                feedback_id="feedback-1",
                outcome_id="outcome-1",
                attempt_id="attempt-1",
                execution_id=None,
                preparation_id="prep-1",
                authorization_id="auth-1",
                handoff_id="handoff-1",
                claim_id="claim-1",
                task_id="task-1",
                consequence_id="consequence-1",
                tool_name="demo_tool",
                invocation_id=None,
                kind=ConsequenceExecutionFeedbackKind.SUCCESS,
                payload={},
                authorization_granted=True,
                evidence_refs=(),
                verification_refs=(),
            )

    def test_not_executed_cannot_contain_execution_identity(self):
        with self.assertRaises(ValueError):
            ConsequenceExecutionFeedback(
                feedback_id="feedback-1",
                outcome_id="outcome-1",
                attempt_id="attempt-1",
                execution_id="exec-1",
                preparation_id="prep-1",
                authorization_id="auth-1",
                handoff_id="handoff-1",
                claim_id="claim-1",
                task_id="task-1",
                consequence_id="consequence-1",
                tool_name="demo_tool",
                invocation_id=None,
                kind=ConsequenceExecutionFeedbackKind.NOT_EXECUTED,
                payload={},
                authorization_granted=True,
                evidence_refs=(),
                verification_refs=(),
                reason="blocked",
            )

    def test_failure_requires_reason(self):
        with self.assertRaises(ValueError):
            ConsequenceExecutionFeedback(
                feedback_id="feedback-1",
                outcome_id="outcome-1",
                attempt_id="attempt-1",
                execution_id="exec-1",
                preparation_id="prep-1",
                authorization_id="auth-1",
                handoff_id="handoff-1",
                claim_id="claim-1",
                task_id="task-1",
                consequence_id="consequence-1",
                tool_name="demo_tool",
                invocation_id=None,
                kind=ConsequenceExecutionFeedbackKind.FAILURE,
                payload={},
                authorization_granted=True,
                evidence_refs=(),
                verification_refs=(),
            )

    def test_wrong_input_type_is_rejected(self):
        with self.assertRaises(TypeError):
            ConsequenceExecutionFeedbackService().evaluate(object())

    def test_context_preserves_authority_walls(self):
        feedback = ConsequenceExecutionFeedbackService().evaluate(
            self._outcome(
                ConsequenceExecutionOutcomeStatus.NOT_EXECUTED,
                execution_id=None,
                reason="blocked",
            )
        )
        context = feedback.to_context()
        self.assertTrue(context["feedback_observed"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])
        self.assertFalse(context["learning_write_requested"])
        self.assertFalse(context["memory_mutated"])

    def test_authorization_provenance_is_not_reissued_as_authority(self):
        feedback = ConsequenceExecutionFeedbackService().evaluate(
            self._outcome(
                ConsequenceExecutionOutcomeStatus.COMPLETED_SUCCESS,
                result=ToolResult(success=True, tool_name="demo_tool", content="ok"),
            )
        )
        self.assertTrue(feedback.authorization_granted)
        self.assertFalse(feedback.to_context()["authority_granted"])


if __name__ == "__main__":
    unittest.main()
