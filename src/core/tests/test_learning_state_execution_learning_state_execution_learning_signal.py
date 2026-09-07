"""Focused M23.157 tests for the bounded evaluation-to-learning-signal boundary."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_execution_evaluation import (
    LearningStateExecutionEvaluation,
    LearningStateExecutionEvaluationStatus,
)
from src.core.learning_state_execution_learning_state_execution_learning_signal import (
    LearningStateExecutionLearningSignal,
    LearningStateExecutionLearningSignalKind,
    LearningStateExecutionLearningSignalService,
    LearningStateExecutionLearningSignalStatus,
)


class M23_157EvaluationLearningSignalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evaluation = LearningStateExecutionEvaluation(
            evaluation_id="execution-evaluation-156",
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
            outcome_status="SUCCEEDED",
            outcome_observation={"result": "completed"},
            feedback_signal={"quality": "positive"},
            feedback_purpose="record bounded feedback for later evaluation",
            feedback_rationale={"reason": "observed terminal outcome"},
            objective="assess whether the observed execution consequence met the declared objective",
            evaluator_id="evaluator-1",
            evaluation_purpose="bounded post-execution evaluation",
            evaluation_judgment={"assessment": "meets-objective", "score": 0.9},
            evaluation_context={"objective_class": "terminal-execution", "comparison": "declared-objective"},
            payload={"feedback_id": "execution-feedback-155", "objective": "assess", "evaluation_judgment": {"assessment": "meets-objective"}},
            status=LearningStateExecutionEvaluationStatus.EVALUATED,
            reasons=("execution feedback evaluated against explicit objective",),
            lineage={
                "evaluation_id": "execution-evaluation-156",
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
                "source_request_provenance_id": "consumption-request-136",
                "source_validation_provenance_id": "consumption-validation-138",
                "read_id": "durable-read-137",
                "consumption_request_id": "consumption-request-136",
            },
        )

    def _create(self, evaluation=None, **kwargs):
        params = {
            "signal_id": "learning-signal-157",
            "signal_kind": LearningStateExecutionLearningSignalKind.POSITIVE,
            "signal_purpose": "represent evaluated execution evidence for a later learning mechanism",
            "signal_context": {"source": "execution-evaluation", "scope": "bounded"},
        }
        params.update(kwargs)
        return LearningStateExecutionLearningSignalService().create(evaluation or self.evaluation, **params)

    def test_exact_evaluation_type_is_required(self):
        with self.assertRaises(TypeError):
            self._create(object())

    def test_evaluated_result_produces_recorded_signal(self):
        result = self._create()
        self.assertIsInstance(result, LearningStateExecutionLearningSignal)
        self.assertEqual(result.status, LearningStateExecutionLearningSignalStatus.RECORDED)
        self.assertTrue(result.is_recorded)

    def test_rejected_evaluation_fails_closed(self):
        rejected = self.evaluation.__class__(**{**self.evaluation.__dict__, "status": LearningStateExecutionEvaluationStatus.REJECTED})
        result = self._create(rejected)
        self.assertTrue(result.is_rejected)
        self.assertIn("execution evaluation status must be EVALUATED", result.reasons)

    def test_signal_identity_must_be_distinct(self):
        result = self._create(signal_id=self.evaluation.evaluation_id)
        self.assertTrue(result.is_rejected)
        self.assertIn("signal identity must be distinct", result.reasons)

    def test_signal_kind_must_be_explicit_enum(self):
        with self.assertRaises(TypeError):
            self._create(signal_kind="POSITIVE")

    def test_signal_purpose_is_required(self):
        with self.assertRaises(ValueError):
            self._create(signal_purpose="")

    def test_signal_context_is_required(self):
        with self.assertRaises(ValueError):
            self._create(signal_context=None)

    def test_negative_signal_kind_is_preserved(self):
        result = self._create(signal_kind=LearningStateExecutionLearningSignalKind.NEGATIVE)
        self.assertEqual(result.signal_kind, LearningStateExecutionLearningSignalKind.NEGATIVE)

    def test_unknown_signal_kind_is_allowed_as_explicit_classification(self):
        result = self._create(signal_kind=LearningStateExecutionLearningSignalKind.UNKNOWN)
        self.assertEqual(result.signal_kind, LearningStateExecutionLearningSignalKind.UNKNOWN)

    def test_evaluation_lineage_is_checked(self):
        lineage = dict(self.evaluation.lineage)
        lineage["evaluation_id"] = "tampered-evaluation"
        source = self.evaluation.__class__(**{**self.evaluation.__dict__, "lineage": lineage})
        result = self._create(source)
        self.assertIn("evaluation lineage mismatch", result.reasons)

    def test_feedback_lineage_is_checked(self):
        lineage = dict(self.evaluation.lineage)
        lineage["feedback_id"] = "tampered-feedback"
        source = self.evaluation.__class__(**{**self.evaluation.__dict__, "lineage": lineage})
        result = self._create(source)
        self.assertIn("feedback lineage mismatch", result.reasons)

    def test_attempt_lineage_is_checked(self):
        lineage = dict(self.evaluation.lineage)
        lineage["attempt_id"] = "tampered-attempt"
        source = self.evaluation.__class__(**{**self.evaluation.__dict__, "lineage": lineage})
        result = self._create(source)
        self.assertIn("attempt lineage mismatch", result.reasons)

    def test_source_request_lineage_is_checked(self):
        lineage = dict(self.evaluation.lineage)
        lineage["request_id"] = "tampered-request"
        source = self.evaluation.__class__(**{**self.evaluation.__dict__, "lineage": lineage})
        result = self._create(source)
        self.assertIn("source request lineage mismatch", result.reasons)

    def test_source_validation_provenance_is_checked(self):
        lineage = dict(self.evaluation.lineage)
        lineage["source_validation_provenance_id"] = "tampered-source-validation"
        source = self.evaluation.__class__(**{**self.evaluation.__dict__, "lineage": lineage})
        result = self._create(source)
        self.assertIn("source validation provenance mismatch", result.reasons)

    def test_consumption_request_lineage_is_checked(self):
        lineage = dict(self.evaluation.lineage)
        lineage["consumption_request_id"] = "tampered-consumption-request"
        source = self.evaluation.__class__(**{**self.evaluation.__dict__, "lineage": lineage})
        result = self._create(source)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_evaluation_evidence_is_preserved(self):
        result = self._create()
        self.assertEqual(result.evaluation_id, self.evaluation.evaluation_id)
        self.assertEqual(result.objective, self.evaluation.objective)
        self.assertEqual(dict(result.evaluation_judgment)["assessment"], "meets-objective")
        self.assertEqual(dict(result.evaluation_context)["comparison"], "declared-objective")

    def test_upstream_execution_evidence_is_preserved(self):
        result = self._create()
        self.assertEqual(result.outcome_id, self.evaluation.outcome_id)
        self.assertEqual(result.attempt_id, self.evaluation.attempt_id)
        self.assertEqual(result.execution_target_id, self.evaluation.execution_target_id)
        self.assertEqual(dict(result.authorization_scope)["target"], "executor-1")

    def test_signal_context_and_payload_are_recursively_immutable(self):
        result = self._create(signal_context={"nested": {"items": ["x"]}})
        self.assertIsInstance(result.signal_context, MappingProxyType)
        self.assertIsInstance(result.signal_context["nested"], MappingProxyType)
        self.assertIsInstance(result.signal_context["nested"]["items"], tuple)
        self.assertIsInstance(result.payload, MappingProxyType)
        with self.assertRaises(TypeError):
            result.payload["evaluation_id"] = "changed"

    def test_lineage_is_immutable(self):
        result = self._create()
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["evaluation_id"] = "changed"

    def test_source_evaluation_is_not_mutated(self):
        before = dict(self.evaluation.lineage)
        self._create()
        self.assertEqual(dict(self.evaluation.lineage), before)

    def test_signal_has_no_learning_or_authority_power(self):
        result = self._create()
        for name in (
            "is_learning", "applies_learning", "proposes_adaptation", "authorizes_learning",
            "authorizes_execution", "authorizes_retry", "invokes_learner", "invokes_executor",
            "schedules_work", "plans_work", "updates_model", "mutates_memory", "mutates_policy",
            "mutates_state", "persists_state", "reads_durable_state", "rereads_durable_state",
            "interprets_state", "establishes_truth", "establishes_correctness", "establishes_certainty",
            "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_explicit_reasons_are_preserved(self):
        result = self._create(reasons=("signal classification captured",))
        self.assertEqual(result.reasons, ("signal classification captured",))

    def test_distinct_signal_identities_remain_distinct(self):
        first = self._create(signal_id="learning-signal-157-a")
        second = self._create(signal_id="learning-signal-157-b")
        self.assertNotEqual(first.signal_id, second.signal_id)
        self.assertEqual(first.evaluation_id, second.evaluation_id)


if __name__ == "__main__":
    unittest.main()
