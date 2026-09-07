"""Focused M23.153 tests for execution attempts."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_execution_admission_authorization import (
    LearningStateExecutionAdmissionAuthorization,
    LearningStateExecutionAdmissionAuthorizationStatus,
)
from src.core.learning_state_execution_learning_state_execution_attempt import (
    LearningStateExecutionAttempt,
    LearningStateExecutionAttemptService,
    LearningStateExecutionAttemptStatus,
)


class M23_153ExecutionAttemptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.admission = LearningStateExecutionAdmissionAuthorization(
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
            admission_purpose="authorize one bounded execution attempt",
            admission_rationale={"reason": "eligible evidence and declared target"},
            payload={
                "eligibility_id": "execution-eligibility-151",
                "execution_target_id": "executor-1",
                "authorization_scope": {"actions": ["execute"], "target": "executor-1"},
            },
            status=LearningStateExecutionAdmissionAuthorizationStatus.ADMITTED,
            reasons=("eligible execution target admitted within the declared authorization scope",),
            lineage={
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
                "execution_target_id": "executor-1",
            },
        )

    def _attempt(self, admission=None, **kwargs):
        params = {
            "attempt_id": "execution-attempt-153",
            "execution_target_id": "executor-1",
            "attempt_purpose": "enter one bounded execution attempt",
            "attempt_rationale": {"reason": "explicitly admitted target"},
        }
        params.update(kwargs)
        return LearningStateExecutionAttemptService().attempt(
            admission or self.admission,
            **params,
        )

    def test_exact_admission_type_is_required(self):
        with self.assertRaises(TypeError):
            self._attempt(object())

    def test_admitted_produces_attempted(self):
        result = self._attempt()
        self.assertIsInstance(result, LearningStateExecutionAttempt)
        self.assertEqual(result.status, LearningStateExecutionAttemptStatus.ATTEMPTED)
        self.assertTrue(result.is_attempted)
        self.assertFalse(result.authorizes_execution)

    def test_rejected_admission_fails_closed(self):
        rejected = self.admission.__class__(
            **{**self.admission.__dict__, "status": LearningStateExecutionAdmissionAuthorizationStatus.REJECTED}
        )
        result = self._attempt(rejected)
        self.assertTrue(result.is_rejected)
        self.assertIn("execution admission status must be ADMITTED", result.reasons)

    def test_attempt_identity_must_be_distinct(self):
        result = self._attempt(attempt_id=self.admission.admission_id)
        self.assertTrue(result.is_rejected)
        self.assertIn("attempt identity must be distinct", result.reasons)

    def test_different_attempt_identities_remain_distinct(self):
        first = self._attempt(attempt_id="execution-attempt-153-a")
        second = self._attempt(attempt_id="execution-attempt-153-b")
        self.assertNotEqual(first.attempt_id, second.attempt_id)
        self.assertEqual(first.admission_id, second.admission_id)

    def test_execution_target_is_required(self):
        with self.assertRaises(ValueError):
            self._attempt(execution_target_id=" ")

    def test_execution_target_must_match_admission(self):
        result = self._attempt(execution_target_id="other-executor")
        self.assertTrue(result.is_rejected)
        self.assertIn("execution target must match admission", result.reasons)

    def test_attempt_purpose_is_required(self):
        with self.assertRaises(ValueError):
            self._attempt(attempt_purpose="")

    def test_attempt_rationale_is_required(self):
        with self.assertRaises(ValueError):
            self._attempt(attempt_rationale=None)

    def test_admission_lineage_is_checked(self):
        lineage = dict(self.admission.lineage)
        lineage["admission_id"] = "tampered-admission"
        source = self.admission.__class__(**{**self.admission.__dict__, "lineage": lineage})
        result = self._attempt(source)
        self.assertIn("admission lineage mismatch", result.reasons)

    def test_eligibility_lineage_is_checked(self):
        lineage = dict(self.admission.lineage)
        lineage["eligibility_id"] = "tampered-eligibility"
        source = self.admission.__class__(**{**self.admission.__dict__, "lineage": lineage})
        result = self._attempt(source)
        self.assertIn("eligibility lineage mismatch", result.reasons)

    def test_handling_lineage_is_checked(self):
        lineage = dict(self.admission.lineage)
        lineage["handling_id"] = "tampered-handling"
        source = self.admission.__class__(**{**self.admission.__dict__, "lineage": lineage})
        result = self._attempt(source)
        self.assertIn("handling lineage mismatch", result.reasons)

    def test_consumption_lineage_is_checked(self):
        lineage = dict(self.admission.lineage)
        lineage["consumption_id"] = "tampered-consumption"
        source = self.admission.__class__(**{**self.admission.__dict__, "lineage": lineage})
        result = self._attempt(source)
        self.assertIn("consumption lineage mismatch", result.reasons)

    def test_receipt_lineage_is_checked(self):
        lineage = dict(self.admission.lineage)
        lineage["receipt_id"] = "tampered-receipt"
        source = self.admission.__class__(**{**self.admission.__dict__, "lineage": lineage})
        result = self._attempt(source)
        self.assertIn("receipt lineage mismatch", result.reasons)

    def test_handoff_lineage_is_checked(self):
        lineage = dict(self.admission.lineage)
        lineage["handoff_id"] = "tampered-handoff"
        source = self.admission.__class__(**{**self.admission.__dict__, "lineage": lineage})
        result = self._attempt(source)
        self.assertIn("handoff lineage mismatch", result.reasons)

    def test_integrity_lineage_is_checked(self):
        lineage = dict(self.admission.lineage)
        lineage["integrity_id"] = "tampered-integrity"
        source = self.admission.__class__(**{**self.admission.__dict__, "lineage": lineage})
        result = self._attempt(source)
        self.assertIn("integrity lineage mismatch", result.reasons)

    def test_validation_lineage_is_checked(self):
        lineage = dict(self.admission.lineage)
        lineage["validation_id"] = "tampered-validation"
        source = self.admission.__class__(**{**self.admission.__dict__, "lineage": lineage})
        result = self._attempt(source)
        self.assertIn("validation lineage mismatch", result.reasons)

    def test_semantic_use_lineage_is_checked(self):
        lineage = dict(self.admission.lineage)
        lineage["semantic_use_id"] = "tampered-semantic-use"
        source = self.admission.__class__(**{**self.admission.__dict__, "lineage": lineage})
        result = self._attempt(source)
        self.assertIn("semantic-use lineage mismatch", result.reasons)

    def test_source_request_lineage_is_checked(self):
        lineage = dict(self.admission.lineage)
        lineage["request_id"] = "tampered-request"
        source = self.admission.__class__(**{**self.admission.__dict__, "lineage": lineage})
        result = self._attempt(source)
        self.assertIn("source request lineage mismatch", result.reasons)

    def test_source_validation_lineage_is_checked(self):
        lineage = dict(self.admission.lineage)
        lineage["source_validation_id"] = "tampered-source-validation"
        source = self.admission.__class__(**{**self.admission.__dict__, "lineage": lineage})
        result = self._attempt(source)
        self.assertIn("source validation lineage mismatch", result.reasons)

    def test_inherited_provenance_is_checked(self):
        lineage = dict(self.admission.lineage)
        lineage["source_request_id"] = "tampered-source-request"
        lineage["source_validation_provenance_id"] = "tampered-source-validation"
        lineage["read_id"] = "tampered-read"
        lineage["consumption_request_id"] = "tampered-consumption-request"
        source = self.admission.__class__(**{**self.admission.__dict__, "lineage": lineage})
        result = self._attempt(source)
        self.assertIn("source request provenance mismatch", result.reasons)
        self.assertIn("source validation provenance mismatch", result.reasons)
        self.assertIn("read lineage mismatch", result.reasons)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_payload_is_bounded(self):
        result = self._attempt()
        self.assertEqual(
            dict(result.payload),
            {"admission_id": self.admission.admission_id, "execution_target_id": "executor-1"},
        )

    def test_payload_is_recursively_immutable(self):
        result = self._attempt()
        self.assertIsInstance(result.payload, MappingProxyType)
        with self.assertRaises(TypeError):
            result.payload["execution_target_id"] = "changed"

    def test_authorization_scope_is_preserved_immutably(self):
        result = self._attempt()
        self.assertEqual(dict(result.authorization_scope), {"actions": ("execute",), "target": "executor-1"})
        self.assertIsInstance(result.authorization_scope, MappingProxyType)
        self.assertIsInstance(result.authorization_scope["actions"], tuple)

    def test_source_admission_is_not_mutated(self):
        before = dict(self.admission.lineage)
        self._attempt()
        self.assertEqual(dict(self.admission.lineage), before)

    def test_explicit_reasons_are_preserved(self):
        result = self._attempt(reasons=("bounded execution attempt recorded",))
        self.assertEqual(result.reasons, ("bounded execution attempt recorded",))

    def test_attempt_does_not_execute_or_authorize(self):
        result = self._attempt()
        for name in (
            "invokes_executor", "invokes_learner", "schedules_work", "plans_work", "mutates_state",
            "persists_state", "reads_durable_state", "rereads_durable_state", "is_learning",
            "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "updates_model", "mutates_memory", "mutates_policy", "establishes_truth",
            "establishes_correctness", "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_attempt_preserves_declared_authorization_scope(self):
        result = self._attempt()
        self.assertEqual(result.execution_target_id, self.admission.execution_target_id)
        self.assertEqual(dict(result.authorization_scope), dict(self.admission.authorization_scope))
        self.assertEqual(result.authority_basis, self.admission.authority_basis)


if __name__ == "__main__":
    unittest.main()
