import unittest

from src.agents.consequence_feedback_evaluation import (
    ConsequenceFeedbackEvaluation,
    ConsequenceFeedbackEvaluationSignal,
)
from src.agents.consequence_learning_decision import (
    ConsequenceLearningDecision,
    ConsequenceLearningDecisionService,
    ConsequenceLearningDecisionStatus,
)


class M38ConsequenceLearningDecisionTests(unittest.TestCase):
    def _make_evaluation(self, signal, execution_id="exec-38"):
        return ConsequenceFeedbackEvaluation(
            evaluation_id="evaluation-38",
            feedback_id="feedback-38",
            outcome_id="outcome-38",
            attempt_id="attempt-38",
            execution_id=execution_id,
            preparation_id="prep-38",
            authorization_id="auth-38",
            handoff_id="handoff-38",
            claim_id="claim-38",
            task_id="task-38",
            consequence_id="coding:advance",
            tool_name="write_file",
            invocation_id="invoke-38",
            signal=signal,
            confidence=0.5,
            evidence={"observed": True},
            authorization_granted=True,
            reason="evaluation reason",
        )

    def test_success_is_learning_eligible(self):
        decision = ConsequenceLearningDecisionService().decide(
            self._make_evaluation(ConsequenceFeedbackEvaluationSignal.SUCCESS_SIGNAL)
        )
        self.assertEqual(decision.status, ConsequenceLearningDecisionStatus.LEARNING_ELIGIBLE)
        self.assertTrue(decision.eligible)
        self.assertFalse(decision.requires_review)

    def test_failure_requires_review(self):
        decision = ConsequenceLearningDecisionService().decide(
            self._make_evaluation(ConsequenceFeedbackEvaluationSignal.FAILURE_SIGNAL)
        )
        self.assertEqual(decision.status, ConsequenceLearningDecisionStatus.REVIEW_REQUIRED)
        self.assertFalse(decision.eligible)
        self.assertTrue(decision.requires_review)

    def test_not_executed_is_not_eligible(self):
        evaluation = self._make_evaluation(
            ConsequenceFeedbackEvaluationSignal.NOT_EXECUTED_SIGNAL,
            execution_id=None,
        )
        decision = ConsequenceLearningDecisionService().decide(evaluation)
        self.assertEqual(decision.status, ConsequenceLearningDecisionStatus.NOT_ELIGIBLE)
        self.assertIsNone(decision.execution_id)

    def test_provenance_is_preserved(self):
        decision = ConsequenceLearningDecisionService().decide(
            self._make_evaluation(ConsequenceFeedbackEvaluationSignal.SUCCESS_SIGNAL)
        )
        self.assertEqual(decision.evaluation_id, "evaluation-38")
        self.assertEqual(decision.feedback_id, "feedback-38")
        self.assertEqual(decision.outcome_id, "outcome-38")
        self.assertEqual(decision.attempt_id, "attempt-38")
        self.assertEqual(decision.preparation_id, "prep-38")
        self.assertEqual(decision.authorization_id, "auth-38")
        self.assertEqual(decision.handoff_id, "handoff-38")
        self.assertEqual(decision.claim_id, "claim-38")
        self.assertEqual(decision.task_id, "task-38")
        self.assertEqual(decision.consequence_id, "coding:advance")
        self.assertTrue(decision.authorization_granted)

    def test_confidence_is_preserved_not_upgraded(self):
        evaluation = self._make_evaluation(ConsequenceFeedbackEvaluationSignal.SUCCESS_SIGNAL)
        decision = ConsequenceLearningDecisionService().decide(evaluation)
        self.assertEqual(decision.confidence, evaluation.confidence)

    def test_decision_id_is_deterministic(self):
        service = ConsequenceLearningDecisionService()
        evaluation = self._make_evaluation(ConsequenceFeedbackEvaluationSignal.FAILURE_SIGNAL)
        self.assertEqual(service.decide(evaluation).decision_id, service.decide(evaluation).decision_id)

    def test_context_does_not_write_learning(self):
        decision = ConsequenceLearningDecisionService().decide(
            self._make_evaluation(ConsequenceFeedbackEvaluationSignal.SUCCESS_SIGNAL)
        )
        context = decision.to_context()
        self.assertTrue(context["learning_decision_made"])
        self.assertTrue(context["learning_eligible"])
        self.assertFalse(context["learning_write_requested"])
        self.assertFalse(context["learning_written"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])

    def test_payload_is_immutable(self):
        decision = ConsequenceLearningDecisionService().decide(
            self._make_evaluation(ConsequenceFeedbackEvaluationSignal.SUCCESS_SIGNAL)
        )
        with self.assertRaises(TypeError):
            decision.evidence["new"] = True

    def test_wrong_input_type_is_rejected(self):
        with self.assertRaises(TypeError):
            ConsequenceLearningDecisionService().decide(object())

    def test_not_eligible_cannot_invent_execution_identity(self):
        with self.assertRaises(ValueError):
            ConsequenceLearningDecision(
                decision_id="decision-1",
                evaluation_id="evaluation-1",
                feedback_id="feedback-1",
                outcome_id="outcome-1",
                attempt_id="attempt-1",
                execution_id="invented-exec",
                preparation_id="prep-1",
                authorization_id="auth-1",
                handoff_id="handoff-1",
                claim_id="claim-1",
                task_id="task-1",
                consequence_id="consequence-1",
                tool_name="demo_tool",
                invocation_id=None,
                status=ConsequenceLearningDecisionStatus.NOT_ELIGIBLE,
                confidence=0.5,
                evidence={},
                authorization_granted=True,
                reason="not eligible",
            )


if __name__ == "__main__":
    unittest.main()
