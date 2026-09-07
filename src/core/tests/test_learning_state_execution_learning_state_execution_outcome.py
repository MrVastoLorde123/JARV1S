"""Focused M23.154 tests for execution outcome."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_execution_attempt import (
    LearningStateExecutionAttempt,
    LearningStateExecutionAttemptStatus,
)
from src.core.learning_state_execution_learning_state_execution_outcome import (
    LearningStateExecutionOutcome,
    LearningStateExecutionOutcomeService,
    LearningStateExecutionOutcomeStatus,
)


class M23_154ExecutionOutcomeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.attempt = LearningStateExecutionAttempt(
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
            attempt_purpose="authorize one bounded execution attempt",
            attempt_rationale={"reason": "eligible evidence and declared target"},
            payload={"admission_id": "execution-admission-152", "execution_target_id": "executor-1"},
            status=LearningStateExecutionAttemptStatus.ATTEMPTED,
            reasons=("admitted execution boundary entered for declared attempt",),
            lineage={
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

    def _record(self, attempt=None, **kwargs):
        params = {
            "outcome_id": "execution-outcome-154",
            "execution_target_id": "executor-1",
            "outcome_status": LearningStateExecutionOutcomeStatus.SUCCEEDED,
            "outcome_observation": {"result": "completed"},
            "outcome_purpose": "record observed execution result",
            "outcome_rationale": {"reason": "terminal executor observation"},
        }
        params.update(kwargs)
        return LearningStateExecutionOutcomeService().record(
            attempt or self.attempt,
            **params,
        )

    def test_exact_attempt_type_is_required(self):
        with self.assertRaises(TypeError):
            self._record(object())

    def test_attempted_produces_outcome(self):
        result = self._record()
        self.assertIsInstance(result, LearningStateExecutionOutcome)
        self.assertEqual(result.status, LearningStateExecutionOutcomeStatus.SUCCEEDED)
        self.assertTrue(result.is_succeeded)

    def test_failed_outcome_is_recorded(self):
        result = self._record(outcome_status=LearningStateExecutionOutcomeStatus.FAILED)
        self.assertTrue(result.is_failed)
        self.assertEqual(result.outcome_status, LearningStateExecutionOutcomeStatus.FAILED)

    def test_rejected_attempt_fails_closed(self):
        rejected = self.attempt.__class__(
            **{**self.attempt.__dict__, "status": LearningStateExecutionAttemptStatus.REJECTED}
        )
        result = self._record(rejected)
        self.assertTrue(result.is_rejected)
        self.assertIn("execution attempt status must be ATTEMPTED", result.reasons)

    def test_outcome_identity_must_be_distinct(self):
        result = self._record(outcome_id=self.attempt.attempt_id)
        self.assertTrue(result.is_rejected)
        self.assertIn("outcome identity must be distinct", result.reasons)

    def test_different_outcome_identities_remain_distinct(self):
        first = self._record(outcome_id="execution-outcome-154-a")
        second = self._record(outcome_id="execution-outcome-154-b")
        self.assertNotEqual(first.outcome_id, second.outcome_id)
        self.assertEqual(first.attempt_id, second.attempt_id)

    def test_execution_target_is_required(self):
        with self.assertRaises(ValueError):
            self._record(execution_target_id=" ")

    def test_execution_target_must_match_attempt(self):
        result = self._record(execution_target_id="other-executor")
        self.assertTrue(result.is_rejected)
        self.assertIn("execution target must match attempt", result.reasons)

    def test_outcome_observation_is_required(self):
        with self.assertRaises(ValueError):
            self._record(outcome_observation=None)

    def test_outcome_purpose_is_required(self):
        with self.assertRaises(ValueError):
            self._record(outcome_purpose="")

    def test_outcome_rationale_is_required(self):
        with self.assertRaises(ValueError):
            self._record(outcome_rationale=None)

    def test_admission_lineage_is_checked(self):
        lineage = dict(self.attempt.lineage)
        lineage["admission_id"] = "tampered-admission"
        source = self.attempt.__class__(**{**self.attempt.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("admission lineage mismatch", result.reasons)

    def test_eligibility_lineage_is_checked(self):
        lineage = dict(self.attempt.lineage)
        lineage["eligibility_id"] = "tampered-eligibility"
        source = self.attempt.__class__(**{**self.attempt.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("eligibility lineage mismatch", result.reasons)

    def test_handling_lineage_is_checked(self):
        lineage = dict(self.attempt.lineage)
        lineage["handling_id"] = "tampered-handling"
        source = self.attempt.__class__(**{**self.attempt.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("handling lineage mismatch", result.reasons)

    def test_consumption_lineage_is_checked(self):
        lineage = dict(self.attempt.lineage)
        lineage["consumption_id"] = "tampered-consumption"
        source = self.attempt.__class__(**{**self.attempt.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("consumption lineage mismatch", result.reasons)

    def test_receipt_lineage_is_checked(self):
        lineage = dict(self.attempt.lineage)
        lineage["receipt_id"] = "tampered-receipt"
        source = self.attempt.__class__(**{**self.attempt.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("receipt lineage mismatch", result.reasons)

    def test_handoff_lineage_is_checked(self):
        lineage = dict(self.attempt.lineage)
        lineage["handoff_id"] = "tampered-handoff"
        source = self.attempt.__class__(**{**self.attempt.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("handoff lineage mismatch", result.reasons)

    def test_integrity_lineage_is_checked(self):
        lineage = dict(self.attempt.lineage)
        lineage["integrity_id"] = "tampered-integrity"
        source = self.attempt.__class__(**{**self.attempt.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("integrity lineage mismatch", result.reasons)

    def test_validation_lineage_is_checked(self):
        lineage = dict(self.attempt.lineage)
        lineage["validation_id"] = "tampered-validation"
        source = self.attempt.__class__(**{**self.attempt.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("validation lineage mismatch", result.reasons)

    def test_semantic_use_lineage_is_checked(self):
        lineage = dict(self.attempt.lineage)
        lineage["semantic_use_id"] = "tampered-semantic-use"
        source = self.attempt.__class__(**{**self.attempt.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("semantic-use lineage mismatch", result.reasons)

    def test_source_request_lineage_is_checked(self):
        lineage = dict(self.attempt.lineage)
        lineage["request_id"] = "tampered-request"
        source = self.attempt.__class__(**{**self.attempt.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("source request lineage mismatch", result.reasons)

    def test_source_validation_lineage_is_checked(self):
        lineage = dict(self.attempt.lineage)
        lineage["source_validation_id"] = "tampered-source-validation"
        source = self.attempt.__class__(**{**self.attempt.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("source validation lineage mismatch", result.reasons)

    def test_interpretation_lineage_is_checked(self):
        lineage = dict(self.attempt.lineage)
        lineage["interpretation_id"] = "tampered-interpretation"
        source = self.attempt.__class__(**{**self.attempt.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("interpretation lineage mismatch", result.reasons)

    def test_inherited_provenance_is_checked(self):
        lineage = dict(self.attempt.lineage)
        lineage["source_request_id"] = "tampered-source-request"
        lineage["source_validation_provenance_id"] = "tampered-source-validation"
        lineage["read_id"] = "tampered-read"
        lineage["consumption_request_id"] = "tampered-consumption-request"
        source = self.attempt.__class__(**{**self.attempt.__dict__, "lineage": lineage})
        result = self._record(source)
        self.assertIn("source request provenance mismatch", result.reasons)
        self.assertIn("source validation provenance mismatch", result.reasons)
        self.assertIn("read lineage mismatch", result.reasons)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_payload_is_bounded(self):
        result = self._record()
        self.assertEqual(
            dict(result.payload),
            {
                "attempt_id": self.attempt.attempt_id,
                "execution_target_id": "executor-1",
                "outcome_status": "SUCCEEDED",
            },
        )

    def test_payload_is_recursively_immutable(self):
        result = self._record()
        self.assertIsInstance(result.payload, MappingProxyType)
        with self.assertRaises(TypeError):
            result.payload["execution_target_id"] = "changed"

    def test_observation_is_recursively_immutable(self):
        result = self._record(outcome_observation={"result": {"code": 0}})
        self.assertIsInstance(result.outcome_observation, MappingProxyType)

    def test_authorization_scope_is_preserved_immutably(self):
        result = self._record()
        self.assertIsInstance(result.authorization_scope, MappingProxyType)
        self.assertIsInstance(result.authorization_scope["actions"], tuple)

    def test_source_attempt_is_not_mutated(self):
        before = dict(self.attempt.lineage)
        self._record()
        self.assertEqual(dict(self.attempt.lineage), before)

    def test_explicit_reasons_are_preserved(self):
        result = self._record(reasons=("executor reported terminal completion",))
        self.assertEqual(result.reasons, ("executor reported terminal completion",))

    def test_outcome_has_no_truth_learning_authority_or_execution_power(self):
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
