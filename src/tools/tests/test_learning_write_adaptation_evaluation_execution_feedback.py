from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_evaluation_execution_feedback import (
    LearningWriteAdaptationEvaluationExecutionFeedback,
    LearningWriteAdaptationEvaluationExecutionFeedbackError,
    LearningWriteAdaptationEvaluationExecutionFeedbackKind,
    LearningWriteAdaptationEvaluationExecutionFeedbackService,
)
from src.tools.learning_write_adaptation_evaluation_execution_result import (
    LearningWriteAdaptationEvaluationExecutionOutcome,
    LearningWriteAdaptationEvaluationExecutionOutcomeStatus,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackTests(unittest.TestCase):
    def _success(self, result=None):
        return LearningWriteAdaptationEvaluationExecutionOutcome(
            execution_id="execution-1", preparation_id="preparation-1", admission_id="admission-1",
            proposal_id="proposal-1", decision_id="decision-1", evaluation_id="evaluation-1",
            feedback_id="feedback-1", source_feedback_id="source-feedback-1", candidate_id="candidate-1",
            source_candidate_id="source-candidate-1", source_execution_id="source-execution-1",
            domain="semantic", policy_id="policy-1",
            status=LearningWriteAdaptationEvaluationExecutionOutcomeStatus.SUCCEEDED,
            execution_result={"changed": True} if result is None else result, result_fingerprint="fp-1",
        )

    def _failure(self):
        return LearningWriteAdaptationEvaluationExecutionOutcome(
            execution_id="execution-1", preparation_id="preparation-1", admission_id="admission-1",
            proposal_id="proposal-1", decision_id="decision-1", evaluation_id="evaluation-1",
            feedback_id="feedback-1", source_feedback_id="source-feedback-1", candidate_id="candidate-1",
            source_candidate_id="source-candidate-1", source_execution_id="source-execution-1",
            domain="semantic", policy_id="policy-1",
            status=LearningWriteAdaptationEvaluationExecutionOutcomeStatus.FAILED, reason="boom",
        )

    def test_success_is_normalized(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackService().from_outcome(self._success())
        self.assertEqual(feedback.kind, LearningWriteAdaptationEvaluationExecutionFeedbackKind.EXECUTION_SUCCESS)
        self.assertEqual(feedback.payload["outcome_status"], "succeeded")
        self.assertEqual(feedback.payload["execution_result"], {"changed": True})

    def test_failure_is_normalized(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackService().from_outcome(self._failure())
        self.assertEqual(feedback.kind, LearningWriteAdaptationEvaluationExecutionFeedbackKind.EXECUTION_FAILURE)
        self.assertEqual(feedback.payload["outcome_status"], "failed")
        self.assertEqual(feedback.payload["reason"], "boom")

    def test_exact_lineage_is_preserved(self):
        outcome = self._success()
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackService().from_outcome(outcome)
        for field in ("execution_id", "preparation_id", "admission_id", "proposal_id", "decision_id", "evaluation_id", "source_feedback_id", "candidate_id", "source_candidate_id", "source_execution_id", "domain", "policy_id"):
            self.assertEqual(getattr(feedback, field), getattr(outcome, field))

    def test_feedback_id_is_deterministic(self):
        service = LearningWriteAdaptationEvaluationExecutionFeedbackService()
        self.assertEqual(service.from_outcome(self._success()).feedback_id, service.from_outcome(self._success()).feedback_id)

    def test_feedback_id_changes_when_observed_result_changes(self):
        service = LearningWriteAdaptationEvaluationExecutionFeedbackService()
        self.assertNotEqual(service.from_outcome(self._success({"changed": True})).feedback_id, service.from_outcome(self._success({"changed": False})).feedback_id)

    def test_payload_is_immutable(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackService().from_outcome(self._success())
        with self.assertRaises(TypeError):
            feedback.payload["new"] = "value"  # type: ignore[index]

    def test_provenance_is_immutable(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackService().from_outcome(self._success())
        with self.assertRaises(TypeError):
            feedback.provenance["new"] = "value"  # type: ignore[index]

    def test_event_is_immutable(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackService().from_outcome(self._success())
        with self.assertRaises(FrozenInstanceError):
            feedback.domain = "other"  # type: ignore[misc]

    def test_result_fingerprint_is_preserved_as_observation(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackService().from_outcome(self._success())
        self.assertEqual(feedback.payload["result_fingerprint"], "fp-1")

    def test_feedback_does_not_grant_authority(self):
        context = LearningWriteAdaptationEvaluationExecutionFeedbackService().from_outcome(self._success()).to_context()
        for field in ("authority_granted", "authorization_granted", "execution_requested", "retry_requested", "revocation_requested", "memory_mutation_allowed"):
            self.assertFalse(context[field])

    def test_context_preserves_full_lineage(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackService().from_outcome(self._success())
        context = feedback.to_context()
        self.assertEqual(context["learning_write_adaptation_evaluation_execution_id"], feedback.execution_id)
        self.assertEqual(context["learning_write_adaptation_evaluation_execution_preparation_id"], feedback.preparation_id)
        self.assertEqual(context["learning_write_adaptation_evaluation_decision_id"], feedback.decision_id)
        self.assertEqual(context["learning_write_adaptation_source_feedback_id"], feedback.source_feedback_id)
        self.assertEqual(context["learning_write_adaptation_evaluation_execution_policy_id"], feedback.policy_id)

    def test_provenance_contains_source_identity(self):
        feedback = LearningWriteAdaptationEvaluationExecutionFeedbackService().from_outcome(self._success())
        self.assertEqual(feedback.provenance["source"], "learning_write_adaptation_evaluation_execution_result")
        self.assertEqual(feedback.provenance["outcome_id"], feedback.execution_id)

    def test_constructor_rejects_invalid_feedback_kind(self):
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackError):
            LearningWriteAdaptationEvaluationExecutionFeedback(
                feedback_id="feedback", execution_id="execution", preparation_id="preparation", admission_id="admission",
                proposal_id="proposal", decision_id="decision", evaluation_id="evaluation", source_feedback_id="source-feedback",
                candidate_id="candidate", source_candidate_id="source-candidate", source_execution_id="source-execution",
                domain="semantic", policy_id="policy", kind="bad", payload={}, provenance={"source": "test"}, reason="reason",  # type: ignore[arg-type]
            )

    def test_service_rejects_invalid_outcome_type(self):
        with self.assertRaises(TypeError):
            LearningWriteAdaptationEvaluationExecutionFeedbackService().from_outcome(object())  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
