from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity import (
    LearningWriteAdaptationEvaluationExecutionFeedbackOutcome,
    LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus,
)
from src.tools.learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackError,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.outcome = LearningWriteAdaptationEvaluationExecutionFeedbackOutcome(
            execution_id="execution-1",
            preparation_id="preparation-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            evaluation_id="evaluation-1",
            decision_source_evaluation_id="historical-evaluation-1",
            feedback_id="feedback-1",
            source_feedback_id="source-feedback-1",
            candidate_id="candidate-1",
            source_candidate_id="source-candidate-1",
            execution_source_id="execution-source-1",
            source_execution_id="source-execution-1",
            source_admission_id="source-admission-1",
            proposal_source_id="source-proposal-1",
            domain="semantic",
            source_policy_id="source-policy-1",
            policy_id="policy-1",
            status=LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus.SUCCEEDED,
            execution_result={"changed": True},
            result_fingerprint="fingerprint-1",
        )
        self.service = LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackService()

    def test_successful_outcome_becomes_success_feedback(self) -> None:
        feedback = self.service.from_outcome(self.outcome)
        self.assertIsInstance(feedback, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback)
        self.assertEqual(
            feedback.kind,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_SUCCESS,
        )
        self.assertEqual(feedback.outcome_id, self.outcome.execution_id)
        self.assertEqual(feedback.payload["result_fingerprint"], "fingerprint-1")

    def test_failed_outcome_becomes_failure_feedback(self) -> None:
        outcome = LearningWriteAdaptationEvaluationExecutionFeedbackOutcome(
            execution_id="execution-1",
            preparation_id="preparation-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            evaluation_id="evaluation-1",
            decision_source_evaluation_id="historical-evaluation-1",
            feedback_id="feedback-1",
            source_feedback_id="source-feedback-1",
            candidate_id="candidate-1",
            source_candidate_id="source-candidate-1",
            execution_source_id="execution-source-1",
            source_execution_id="source-execution-1",
            source_admission_id="source-admission-1",
            proposal_source_id="source-proposal-1",
            domain="semantic",
            source_policy_id="source-policy-1",
            policy_id="policy-1",
            status=LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus.FAILED,
            reason="execution failed",
        )
        feedback = self.service.from_outcome(outcome)
        self.assertEqual(
            feedback.kind,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_FAILURE,
        )
        self.assertEqual(feedback.payload["reason"], "execution failed")

    def test_full_lineage_is_preserved(self) -> None:
        feedback = self.service.from_outcome(self.outcome)
        for field in (
            "outcome_id", "execution_id", "preparation_id", "admission_id", "proposal_id", "decision_id",
            "evaluation_id", "decision_source_evaluation_id", "source_feedback_id", "candidate_id",
            "source_candidate_id", "execution_source_id", "source_execution_id", "source_admission_id",
            "proposal_source_id", "domain", "source_policy_id", "policy_id",
        ):
            expected = self.outcome.execution_id if field == "outcome_id" else getattr(self.outcome, field)
            self.assertEqual(getattr(feedback, field), expected)

    def test_feedback_id_is_deterministic(self) -> None:
        first = self.service.from_outcome(self.outcome)
        second = self.service.from_outcome(self.outcome)
        self.assertEqual(first.feedback_id, second.feedback_id)
        self.assertNotEqual(first.feedback_id, self.outcome.execution_id)

    def test_payload_and_provenance_are_recursively_immutable(self) -> None:
        feedback = self.service.from_outcome(self.outcome)
        with self.assertRaises(TypeError):
            feedback.payload["nested"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            feedback.provenance["source"] = "other"  # type: ignore[index]

    def test_feedback_is_immutable(self) -> None:
        feedback = self.service.from_outcome(self.outcome)
        with self.assertRaises(FrozenInstanceError):
            feedback.domain = "other"  # type: ignore[misc]

    def test_to_context_preserves_authority_wall(self) -> None:
        feedback = self.service.from_outcome(self.outcome)
        context = feedback.to_context()
        self.assertTrue(context["result_integrity_feedback_observed"])
        self.assertFalse(context["adaptation_truth_proven"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])
        self.assertFalse(context["memory_mutation_allowed"])

    def test_invalid_outcome_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.from_outcome({"bad": True})  # type: ignore[arg-type]

    def test_success_payload_preserves_observed_result(self) -> None:
        feedback = self.service.from_outcome(self.outcome)
        self.assertEqual(feedback.payload["execution_result"]["changed"], True)
        self.assertEqual(feedback.payload["outcome_status"], "succeeded")

    def test_failure_feedback_does_not_invent_fingerprint(self) -> None:
        outcome = LearningWriteAdaptationEvaluationExecutionFeedbackOutcome(
            execution_id="execution-2",
            preparation_id="preparation-2",
            admission_id="admission-2",
            proposal_id="proposal-2",
            decision_id="decision-2",
            evaluation_id="evaluation-2",
            decision_source_evaluation_id="historical-evaluation-2",
            feedback_id="feedback-2",
            source_feedback_id="source-feedback-2",
            candidate_id="candidate-2",
            source_candidate_id="source-candidate-2",
            execution_source_id="execution-source-2",
            source_execution_id="source-execution-2",
            source_admission_id="source-admission-2",
            proposal_source_id="source-proposal-2",
            domain="semantic",
            source_policy_id="source-policy-2",
            policy_id="policy-2",
            status=LearningWriteAdaptationEvaluationExecutionFeedbackOutcomeStatus.FAILED,
            result_fingerprint=None,
            reason="failed",
        )
        feedback = self.service.from_outcome(outcome)
        self.assertNotIn("result_fingerprint", feedback.payload)

    def test_feedback_constructor_rejects_empty_reason(self) -> None:
        with self.assertRaises(LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackError):
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedback(
                feedback_id="feedback-1",
                outcome_id="execution-1",
                execution_id="execution-1",
                preparation_id="preparation-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                evaluation_id="evaluation-1",
                decision_source_evaluation_id="historical-evaluation-1",
                source_feedback_id="source-feedback-1",
                candidate_id="candidate-1",
                source_candidate_id="source-candidate-1",
                execution_source_id="execution-source-1",
                source_execution_id="source-execution-1",
                source_admission_id="source-admission-1",
                proposal_source_id="source-proposal-1",
                domain="semantic",
                source_policy_id="source-policy-1",
                policy_id="policy-1",
                kind=LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackKind.INTEGRITY_SUCCESS,
                payload={},
                provenance={"source": "test"},
                reason="",
            )


if __name__ == "__main__":
    unittest.main()
