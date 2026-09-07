"""Focused M23.155 tests for execution feedback."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_execution_outcome import (
    LearningStateExecutionOutcome,
    LearningStateExecutionOutcomeStatus,
)
from src.core.learning_state_execution_learning_state_execution_feedback import (
    LearningStateExecutionFeedback,
    LearningStateExecutionFeedbackService,
    LearningStateExecutionFeedbackStatus,
)


class M23_155ExecutionFeedbackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.outcome = LearningStateExecutionOutcome(
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
            authority_basis={"basis": "explicit-admission-boundary"},
            outcome_status=LearningStateExecutionOutcomeStatus.SUCCEEDED,
            outcome_observation={"result": "completed"},
            outcome_purpose="record observed execution result",
            outcome_rationale={"reason": "terminal executor observation"},
            payload={"attempt_id": "execution-attempt-153", "execution_target_id": "executor-1", "outcome_status": "SUCCEEDED"},
            status=LearningStateExecutionOutcomeStatus.SUCCEEDED,
            reasons=("observed execution outcome recorded for declared attempt",),
            lineage={
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

    def _record(self, outcome=None, **kwargs):
        params = {
            "feedback_id": "execution-feedback-155",
            "feedback_signal": {"quality": "positive", "lesson_candidate": False},
            "feedback_purpose": "record bounded feedback for later evaluation",
            "feedback_rationale": {"reason": "observed terminal outcome"},
        }
        params.update(kwargs)
        return LearningStateExecutionFeedbackService().record(outcome or self.outcome, **params)

    def test_exact_outcome_type_is_required(self):
        with self.assertRaises(TypeError):
            self._record(object())

    def test_succeeded_outcome_produces_recorded_feedback(self):
        result = self._record()
        self.assertIsInstance(result, LearningStateExecutionFeedback)
        self.assertEqual(result.status, LearningStateExecutionFeedbackStatus.RECORDED)
        self.assertTrue(result.is_recorded)

    def test_failed_outcome_produces_recorded_feedback(self):
        failed = self.outcome.__class__(**{**self.outcome.__dict__, "status": LearningStateExecutionOutcomeStatus.FAILED, "outcome_status": LearningStateExecutionOutcomeStatus.FAILED})
        result = self._record(failed)
        self.assertTrue(result.is_recorded)
        self.assertEqual(result.outcome_status, LearningStateExecutionOutcomeStatus.FAILED)

    def test_rejected_outcome_fails_closed(self):
        rejected = self.outcome.__class__(**{**self.outcome.__dict__, "status": LearningStateExecutionOutcomeStatus.REJECTED, "outcome_status": LearningStateExecutionOutcomeStatus.REJECTED})
        result = self._record(rejected)
        self.assertTrue(result.is_rejected)
        self.assertIn("execution outcome status must be SUCCEEDED or FAILED", result.reasons)

    def test_feedback_identity_must_be_distinct(self):
        result = self._record(feedback_id=self.outcome.outcome_id)
        self.assertTrue(result.is_rejected)
        self.assertIn("feedback identity must be distinct", result.reasons)

    def test_different_feedback_identities_remain_distinct(self):
        first = self._record(feedback_id="execution-feedback-155-a")
        second = self._record(feedback_id="execution-feedback-155-b")
        self.assertNotEqual(first.feedback_id, second.feedback_id)
        self.assertEqual(first.outcome_id, second.outcome_id)

    def test_feedback_signal_is_required(self):
        with self.assertRaises(ValueError):
            self._record(feedback_signal=None)

    def test_feedback_purpose_is_required(self):
        with self.assertRaises(ValueError):
            self._record(feedback_purpose="")

    def test_feedback_rationale_is_required(self):
        with self.assertRaises(ValueError):
            self._record(feedback_rationale=None)

    def test_outcome_lineage_is_checked(self):
        lineage = dict(self.outcome.lineage)
        lineage["outcome_id"] = "tampered-outcome"
        source = self.outcome.__class__(**{**self.outcome.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("outcome lineage mismatch", result.reasons)

    def test_attempt_lineage_is_checked(self):
        lineage = dict(self.outcome.lineage)
        lineage["attempt_id"] = "tampered-attempt"
        source = self.outcome.__class__(**{**self.outcome.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("attempt lineage mismatch", result.reasons)

    def test_admission_lineage_is_checked(self):
        lineage = dict(self.outcome.lineage)
        lineage["admission_id"] = "tampered-admission"
        source = self.outcome.__class__(**{**self.outcome.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("admission lineage mismatch", result.reasons)

    def test_eligibility_lineage_is_checked(self):
        lineage = dict(self.outcome.lineage)
        lineage["eligibility_id"] = "tampered-eligibility"
        source = self.outcome.__class__(**{**self.outcome.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("eligibility lineage mismatch", result.reasons)

    def test_handling_lineage_is_checked(self):
        lineage = dict(self.outcome.lineage)
        lineage["handling_id"] = "tampered-handling"
        source = self.outcome.__class__(**{**self.outcome.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("handling lineage mismatch", result.reasons)

    def test_consumption_lineage_is_checked(self):
        lineage = dict(self.outcome.lineage)
        lineage["consumption_id"] = "tampered-consumption"
        source = self.outcome.__class__(**{**self.outcome.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("consumption lineage mismatch", result.reasons)

    def test_receipt_lineage_is_checked(self):
        lineage = dict(self.outcome.lineage)
        lineage["receipt_id"] = "tampered-receipt"
        source = self.outcome.__class__(**{**self.outcome.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("receipt lineage mismatch", result.reasons)

    def test_handoff_lineage_is_checked(self):
        lineage = dict(self.outcome.lineage)
        lineage["handoff_id"] = "tampered-handoff"
        source = self.outcome.__class__(**{**self.outcome.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("handoff lineage mismatch", result.reasons)

    def test_integrity_lineage_is_checked(self):
        lineage = dict(self.outcome.lineage)
        lineage["integrity_id"] = "tampered-integrity"
        source = self.outcome.__class__(**{**self.outcome.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("integrity lineage mismatch", result.reasons)

    def test_validation_lineage_is_checked(self):
        lineage = dict(self.outcome.lineage)
        lineage["validation_id"] = "tampered-validation"
        source = self.outcome.__class__(**{**self.outcome.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("validation lineage mismatch", result.reasons)

    def test_semantic_use_lineage_is_checked(self):
        lineage = dict(self.outcome.lineage)
        lineage["semantic_use_id"] = "tampered-semantic-use"
        source = self.outcome.__class__(**{**self.outcome.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("semantic-use lineage mismatch", result.reasons)

    def test_source_request_lineage_is_checked(self):
        lineage = dict(self.outcome.lineage)
        lineage["request_id"] = "tampered-request"
        source = self.outcome.__class__(**{**self.outcome.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("source request lineage mismatch", result.reasons)

    def test_source_validation_lineage_is_checked(self):
        lineage = dict(self.outcome.lineage)
        lineage["source_validation_id"] = "tampered-source-validation"
        source = self.outcome.__class__(**{**self.outcome.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("source validation lineage mismatch", result.reasons)

    def test_interpretation_lineage_is_checked(self):
        lineage = dict(self.outcome.lineage)
        lineage["interpretation_id"] = "tampered-interpretation"
        source = self.outcome.__class__(**{**self.outcome.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("interpretation lineage mismatch", result.reasons)

    def test_inherited_provenance_is_checked(self):
        lineage = dict(self.outcome.lineage)
        lineage["source_request_id"] = "tampered-source-request"
        lineage["source_validation_provenance_id"] = "tampered-source-validation"
        lineage["read_id"] = "tampered-read"
        lineage["consumption_request_id"] = "tampered-consumption-request"
        source = self.outcome.__class__(**{**self.outcome.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("source request provenance mismatch", result.reasons)
        self.assertIn("source validation provenance mismatch", result.reasons)
        self.assertIn("read lineage mismatch", result.reasons)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_payload_is_bounded(self):
        result = self._record()
        self.assertEqual(dict(result.payload)["outcome_id"], self.outcome.outcome_id)
        self.assertEqual(dict(result.payload)["feedback_signal"], {"quality": "positive", "lesson_candidate": False})

    def test_payload_is_recursively_immutable(self):
        result = self._record()
        self.assertIsInstance(result.payload, MappingProxyType)
        self.assertIsInstance(result.payload["feedback_signal"], MappingProxyType)
        with self.assertRaises(TypeError):
            result.payload["outcome_id"] = "changed"

    def test_feedback_signal_is_recursively_immutable(self):
        result = self._record(feedback_signal={"nested": {"value": 1}})
        self.assertIsInstance(result.feedback_signal, MappingProxyType)
        self.assertIsInstance(result.feedback_signal["nested"], MappingProxyType)

    def test_authorization_scope_is_preserved_immutably(self):
        result = self._record()
        self.assertIsInstance(result.authorization_scope, MappingProxyType)
        self.assertIsInstance(result.authorization_scope["actions"], tuple)

    def test_source_outcome_is_not_mutated(self):
        before = dict(self.outcome.lineage)
        self._record()
        self.assertEqual(dict(self.outcome.lineage), before)

    def test_explicit_reasons_are_preserved(self):
        result = self._record(reasons=("executor feedback captured",))
        self.assertEqual(result.reasons, ("executor feedback captured",))

    def test_feedback_has_no_truth_learning_authority_or_execution_power(self):
        result = self._record()
        for name in (
            "invokes_executor", "invokes_learner", "schedules_work", "plans_work", "mutates_state",
            "persists_state", "reads_durable_state", "rereads_durable_state", "is_learning",
            "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "updates_model", "mutates_memory", "mutates_policy", "establishes_truth",
            "establishes_correctness", "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
