"""Focused M23.156 tests for the bounded execution-feedback evaluation boundary."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_execution_feedback import (
    LearningStateExecutionFeedback,
    LearningStateExecutionFeedbackService,
    LearningStateExecutionFeedbackStatus,
)
from src.core.learning_state_execution_learning_state_execution_outcome import (
    LearningStateExecutionOutcomeStatus,
)
from src.core.learning_state_execution_learning_state_execution_evaluation import (
    LearningStateExecutionEvaluation,
    LearningStateExecutionEvaluationService,
    LearningStateExecutionEvaluationStatus,
)


class M23_156ExecutionFeedbackEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.feedback = LearningStateExecutionFeedback(
            feedback_id="execution-feedback-155",
            outcome_id="execution-outcome-154",
            attempt_id="execution-attempt-153",
            admission_id="execution-admission-152",
            eligibility_id="execution-eligibility-151",
            handling_id="semantic-handling-150",
            consumption_id="semantic-consumption-149",
            receipt_id="semantic-receipt-148",
            handoff_id="semantic-handoff-147",
            integrity_id="semantic-use-integrity-146",
            validation_id="semantic-use-validation-145",
            semantic_use_id="semantic-use-144",
            source_request_id="consumption-request-136",
            source_request_lineage_id="semantic-use-request-143",
            source_validation_id="consumption-validation-138",
            source_validation_lineage_id="semantic-use-validation-145",
            interpretation_id="interpretation-140",
            read_id="durable-read-137",
            consumption_request_id="consumption-request-136",
            requester_id="user-1",
            consumer_id="semantic-consumer-1",
            handoff_target_id="downstream-consumer-1",
            recipient_id="semantic-recipient-1",
            handling_target_id="planning-context",
            execution_target_id="executor-1",
            authorization_scope={"actions": ["execute"], "target": "executor-1"},
            outcome_status=LearningStateExecutionOutcomeStatus.SUCCEEDED,
            outcome_observation={"result": "completed"},
            feedback_signal={"quality": "positive"},
            feedback_purpose="record bounded feedback for later evaluation",
            feedback_rationale={"reason": "observed terminal outcome"},
            payload={"outcome_id": "execution-outcome-154", "feedback_signal": {"quality": "positive"}},
            status=LearningStateExecutionFeedbackStatus.RECORDED,
            reasons=("execution feedback recorded from observed outcome",),
            lineage={
                "feedback_id": "execution-feedback-155",
                "outcome_id": "execution-outcome-154",
                "attempt_id": "execution-attempt-153",
                "admission_id": "execution-admission-152",
                "eligibility_id": "execution-eligibility-151",
                "handling_id": "semantic-handling-150",
                "consumption_id": "semantic-consumption-149",
                "receipt_id": "semantic-receipt-148",
                "handoff_id": "semantic-handoff-147",
                "integrity_id": "semantic-use-integrity-146",
                "validation_id": "semantic-use-validation-145",
                "semantic_use_id": "semantic-use-144",
                "request_id": "semantic-use-request-143",
                "source_validation_id": "semantic-use-validation-145",
                "interpretation_id": "interpretation-140",
                "source_request_id": "consumption-request-136",
                "source_validation_provenance_id": "consumption-validation-138",
                "read_id": "durable-read-137",
                "consumption_request_id": "consumption-request-136",
            },
        )

    def _evaluate(self, feedback=None, **kwargs):
        params = {
            "evaluation_id": "execution-evaluation-156",
            "objective": "assess whether the observed execution consequence met the declared objective",
            "evaluator_id": "evaluator-1",
            "evaluation_purpose": "bounded post-execution evaluation",
            "evaluation_judgment": {"assessment": "meets-objective", "score": 0.9},
            "evaluation_context": {"objective_class": "terminal-execution", "comparison": "declared-objective"},
        }
        params.update(kwargs)
        return LearningStateExecutionEvaluationService().evaluate(feedback or self.feedback, **params)

    def test_exact_feedback_type_is_required(self):
        with self.assertRaises(TypeError):
            self._evaluate(object())

    def test_recorded_feedback_produces_evaluated_result(self):
        result = self._evaluate()
        self.assertIsInstance(result, LearningStateExecutionEvaluation)
        self.assertEqual(result.status, LearningStateExecutionEvaluationStatus.EVALUATED)
        self.assertTrue(result.is_evaluated)

    def test_rejected_feedback_fails_closed(self):
        rejected = self.feedback.__class__(**{**self.feedback.__dict__, "status": LearningStateExecutionFeedbackStatus.REJECTED})
        result = self._evaluate(rejected)
        self.assertTrue(result.is_rejected)
        self.assertIn("execution feedback status must be RECORDED", result.reasons)

    def test_evaluation_identity_must_be_distinct(self):
        result = self._evaluate(evaluation_id=self.feedback.feedback_id)
        self.assertTrue(result.is_rejected)
        self.assertIn("evaluation identity must be distinct", result.reasons)

    def test_objective_is_required(self):
        with self.assertRaises(ValueError):
            self._evaluate(objective="")

    def test_evaluator_identity_is_required(self):
        with self.assertRaises(ValueError):
            self._evaluate(evaluator_id="")

    def test_evaluation_purpose_is_required(self):
        with self.assertRaises(ValueError):
            self._evaluate(evaluation_purpose="")

    def test_evaluation_judgment_is_required(self):
        with self.assertRaises(ValueError):
            self._evaluate(evaluation_judgment=None)

    def test_evaluation_context_is_required(self):
        with self.assertRaises(ValueError):
            self._evaluate(evaluation_context=None)

    def test_feedback_lineage_is_checked(self):
        lineage = dict(self.feedback.lineage)
        lineage["feedback_id"] = "tampered-feedback"
        source = self.feedback.__class__(**{**self.feedback.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertTrue(result.is_rejected)
        self.assertIn("feedback lineage mismatch", result.reasons)

    def test_outcome_lineage_is_checked(self):
        lineage = dict(self.feedback.lineage)
        lineage["outcome_id"] = "tampered-outcome"
        source = self.feedback.__class__(**{**self.feedback.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("outcome lineage mismatch", result.reasons)

    def test_attempt_lineage_is_checked(self):
        lineage = dict(self.feedback.lineage)
        lineage["attempt_id"] = "tampered-attempt"
        source = self.feedback.__class__(**{**self.feedback.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("attempt lineage mismatch", result.reasons)

    def test_source_request_lineage_is_checked(self):
        lineage = dict(self.feedback.lineage)
        lineage["request_id"] = "tampered-request"
        source = self.feedback.__class__(**{**self.feedback.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("source request lineage mismatch", result.reasons)

    def test_source_validation_provenance_is_checked(self):
        lineage = dict(self.feedback.lineage)
        lineage["source_validation_provenance_id"] = "tampered-source-validation"
        source = self.feedback.__class__(**{**self.feedback.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("source validation provenance mismatch", result.reasons)

    def test_consumption_request_lineage_is_checked(self):
        lineage = dict(self.feedback.lineage)
        lineage["consumption_request_id"] = "tampered-consumption-request"
        source = self.feedback.__class__(**{**self.feedback.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_execution_target_is_preserved(self):
        result = self._evaluate()
        self.assertEqual(result.execution_target_id, self.feedback.execution_target_id)
        self.assertEqual(dict(result.authorization_scope), dict(self.feedback.authorization_scope))

    def test_feedback_signal_and_observation_are_preserved(self):
        result = self._evaluate()
        self.assertEqual(dict(result.feedback_signal), dict(self.feedback.feedback_signal))
        self.assertEqual(dict(result.outcome_observation), dict(self.feedback.outcome_observation))
        self.assertEqual(result.feedback_purpose, self.feedback.feedback_purpose)

    def test_explicit_judgment_and_context_are_preserved(self):
        result = self._evaluate()
        self.assertEqual(dict(result.evaluation_judgment), {"assessment": "meets-objective", "score": 0.9})
        self.assertEqual(dict(result.evaluation_context)["comparison"], "declared-objective")

    def test_payload_is_bounded(self):
        result = self._evaluate()
        self.assertEqual(dict(result.payload)["feedback_id"], self.feedback.feedback_id)
        self.assertEqual(dict(result.payload)["objective"], result.objective)
        self.assertEqual(dict(result.payload)["evaluation_judgment"]["assessment"], "meets-objective")

    def test_payload_is_recursively_immutable(self):
        result = self._evaluate()
        self.assertIsInstance(result.payload, MappingProxyType)
        self.assertIsInstance(result.payload["evaluation_judgment"], MappingProxyType)
        with self.assertRaises(TypeError):
            result.payload["objective"] = "changed"

    def test_lineage_is_immutable(self):
        result = self._evaluate()
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["feedback_id"] = "changed"

    def test_source_feedback_is_not_mutated(self):
        before = dict(self.feedback.lineage)
        self._evaluate()
        self.assertEqual(dict(self.feedback.lineage), before)

    def test_explicit_reasons_are_preserved(self):
        result = self._evaluate(reasons=("evaluation captured",))
        self.assertEqual(result.reasons, ("evaluation captured",))

    def test_evaluation_has_no_authority_or_learning_power(self):
        result = self._evaluate()
        for name in (
            "mutates_state", "persists_state", "reads_durable_state", "rereads_durable_state",
            "is_learning", "applies_learning", "authorizes_learning", "authorizes_execution",
            "authorizes_retry", "invokes_learner", "invokes_executor", "schedules_work", "plans_work",
            "updates_model", "mutates_memory", "mutates_policy", "establishes_truth", "establishes_correctness",
            "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
