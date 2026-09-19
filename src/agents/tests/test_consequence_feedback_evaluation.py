import unittest

from src.agents.consequence_execution_feedback import (
    ConsequenceExecutionFeedback,
    ConsequenceExecutionFeedbackKind,
)
from src.agents.consequence_feedback_evaluation import (
    ConsequenceFeedbackEvaluation,
    ConsequenceFeedbackEvaluationService,
    ConsequenceFeedbackEvaluationSignal,
)


class M37ConsequenceFeedbackEvaluationTests(unittest.TestCase):
    def _feedback(self, kind, *, execution_id="exec-1", reason=None, externally_verified=False):
        return ConsequenceExecutionFeedback(
            feedback_id=f"feedback-{kind.value.lower()}",
            outcome_id=f"outcome-{kind.value.lower()}",
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
            kind=kind,
            payload={
                "observed": True,
                "externally_verified": externally_verified,
            },
            authorization_granted=True,
            evidence_refs=("evidence-1",),
            verification_refs=("verification-1",),
            reason=reason,
        )

    def test_unverified_success_maps_to_execution_success_signal(self):
        result = ConsequenceFeedbackEvaluationService().evaluate(
            self._feedback(ConsequenceExecutionFeedbackKind.SUCCESS)
        )
        self.assertEqual(
            result.signal,
            ConsequenceFeedbackEvaluationSignal.EXECUTION_SUCCESS_SIGNAL,
        )
        self.assertEqual(result.execution_id, "exec-1")

    def test_verified_success_maps_to_learning_success_signal(self):
        result = ConsequenceFeedbackEvaluationService().evaluate(
            self._feedback(
                ConsequenceExecutionFeedbackKind.SUCCESS,
                externally_verified=True,
            )
        )
        self.assertEqual(result.signal, ConsequenceFeedbackEvaluationSignal.SUCCESS_SIGNAL)
        self.assertEqual(result.execution_id, "exec-1")

    def test_failure_maps_to_failure_signal(self):
        result = ConsequenceFeedbackEvaluationService().evaluate(
            self._feedback(
                ConsequenceExecutionFeedbackKind.FAILURE,
                reason="executor unavailable",
            )
        )
        self.assertEqual(result.signal, ConsequenceFeedbackEvaluationSignal.FAILURE_SIGNAL)
        self.assertEqual(result.execution_id, "exec-1")

    def test_not_executed_maps_without_execution_identity(self):
        result = ConsequenceFeedbackEvaluationService().evaluate(
            self._feedback(
                ConsequenceExecutionFeedbackKind.NOT_EXECUTED,
                execution_id=None,
                reason="blocked",
            )
        )
        self.assertEqual(result.signal, ConsequenceFeedbackEvaluationSignal.NOT_EXECUTED_SIGNAL)
        self.assertIsNone(result.execution_id)

    def test_full_provenance_is_preserved(self):
        feedback = self._feedback(
            ConsequenceExecutionFeedbackKind.NOT_EXECUTED,
            execution_id=None,
            reason="blocked",
        )
        result = ConsequenceFeedbackEvaluationService().evaluate(feedback)
        self.assertEqual(result.feedback_id, feedback.feedback_id)
        self.assertEqual(result.outcome_id, feedback.outcome_id)
        self.assertEqual(result.attempt_id, feedback.attempt_id)
        self.assertEqual(result.preparation_id, feedback.preparation_id)
        self.assertEqual(result.authorization_id, feedback.authorization_id)
        self.assertEqual(result.handoff_id, feedback.handoff_id)
        self.assertEqual(result.claim_id, feedback.claim_id)
        self.assertEqual(result.task_id, feedback.task_id)
        self.assertEqual(result.consequence_id, feedback.consequence_id)
        self.assertEqual(result.tool_name, feedback.tool_name)
        self.assertEqual(result.invocation_id, feedback.invocation_id)
        self.assertTrue(result.authorization_granted)

    def test_confidence_is_bounded(self):
        result = ConsequenceFeedbackEvaluationService().evaluate(
            self._feedback(ConsequenceExecutionFeedbackKind.SUCCESS)
        )
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)

    def test_evaluation_id_is_deterministic(self):
        service = ConsequenceFeedbackEvaluationService()
        feedback = self._feedback(ConsequenceExecutionFeedbackKind.SUCCESS)
        self.assertEqual(service.evaluate(feedback).evaluation_id, service.evaluate(feedback).evaluation_id)

    def test_identical_feedback_produces_identical_evaluation_id(self):
        service = ConsequenceFeedbackEvaluationService()
        first = service.evaluate(self._feedback(ConsequenceExecutionFeedbackKind.SUCCESS))
        second = service.evaluate(self._feedback(ConsequenceExecutionFeedbackKind.SUCCESS))
        self.assertEqual(first.evaluation_id, second.evaluation_id)

    def test_different_feedback_kind_changes_evaluation_id(self):
        service = ConsequenceFeedbackEvaluationService()
        success = service.evaluate(self._feedback(ConsequenceExecutionFeedbackKind.SUCCESS))
        failure = service.evaluate(
            self._feedback(ConsequenceExecutionFeedbackKind.FAILURE, reason="failed")
        )
        self.assertNotEqual(success.evaluation_id, failure.evaluation_id)

    def test_evidence_is_immutable(self):
        result = ConsequenceFeedbackEvaluationService().evaluate(
            self._feedback(ConsequenceExecutionFeedbackKind.SUCCESS)
        )
        with self.assertRaises(TypeError):
            result.evidence["new"] = True

    def test_evaluation_does_not_write_learning_state(self):
        result = ConsequenceFeedbackEvaluationService().evaluate(
            self._feedback(ConsequenceExecutionFeedbackKind.SUCCESS)
        )
        context = result.to_context()
        self.assertTrue(context["evaluation_observed"])
        self.assertTrue(context["learning_decision_required"])
        self.assertFalse(context["learning_write_requested"])
        self.assertFalse(context["memory_mutated"])

    def test_evaluation_does_not_authorize_or_retry(self):
        result = ConsequenceFeedbackEvaluationService().evaluate(
            self._feedback(
                ConsequenceExecutionFeedbackKind.FAILURE,
                reason="failed",
            )
        )
        context = result.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_authorization_provenance_is_not_reissued_as_authorization(self):
        result = ConsequenceFeedbackEvaluationService().evaluate(
            self._feedback(ConsequenceExecutionFeedbackKind.SUCCESS)
        )
        self.assertTrue(result.authorization_granted)
        self.assertFalse(result.to_context()["authorization_granted"])

    def test_not_executed_rejects_execution_identity(self):
        with self.assertRaises(ValueError):
            ConsequenceFeedbackEvaluation(
                evaluation_id="evaluation-1",
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
                signal=ConsequenceFeedbackEvaluationSignal.NOT_EXECUTED_SIGNAL,
                confidence=0.5,
                evidence={},
                authorization_granted=True,
                reason="not executed",
            )

    def test_executed_signal_requires_execution_identity(self):
        with self.assertRaises(ValueError):
            ConsequenceFeedbackEvaluation(
                evaluation_id="evaluation-1",
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
                signal=ConsequenceFeedbackEvaluationSignal.SUCCESS_SIGNAL,
                confidence=0.5,
                evidence={},
                authorization_granted=True,
                reason="success",
            )

    def test_wrong_input_type_is_rejected(self):
        with self.assertRaises(TypeError):
            ConsequenceFeedbackEvaluationService().evaluate(object())


if __name__ == "__main__":
    unittest.main()
