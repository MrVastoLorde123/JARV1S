"""Focused M23.152 tests for execution admission / authorization."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_execution_eligibility import (
    LearningStateExecutionEligibility,
    LearningStateExecutionEligibilityStatus,
)
from src.core.learning_state_execution_learning_state_execution_admission_authorization import (
    LearningStateExecutionAdmissionAuthorization,
    LearningStateExecutionAdmissionAuthorizationService,
    LearningStateExecutionAdmissionAuthorizationStatus,
)


class M23_152ExecutionAdmissionAuthorizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.eligibility = LearningStateExecutionEligibility(
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
            eligibility_purpose="consider handled semantic result for execution",
            eligibility_rationale={"reason": "declared target consideration"},
            payload={"handling_id": "semantic-handling-150", "execution_target_id": "executor-1"},
            status=LearningStateExecutionEligibilityStatus.ELIGIBLE,
            reasons=("handled semantic use satisfies bounded execution preconditions",),
            lineage={
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

    def _admit(self, eligibility=None, **kwargs):
        params = {
            "admission_id": "execution-admission-152",
            "execution_target_id": "executor-1",
            "authorization_scope": {"actions": ["execute"], "target": "executor-1"},
            "authority_basis": {"basis": "explicit-admission-boundary"},
            "admission_purpose": "authorize one bounded execution attempt",
            "admission_rationale": {"reason": "eligible evidence and declared target"},
        }
        params.update(kwargs)
        return LearningStateExecutionAdmissionAuthorizationService().admit(
            eligibility or self.eligibility,
            **params,
        )

    def test_exact_eligibility_type_is_required(self):
        with self.assertRaises(TypeError):
            self._admit(object())

    def test_eligible_produces_admitted(self):
        result = self._admit()
        self.assertIsInstance(result, LearningStateExecutionAdmissionAuthorization)
        self.assertEqual(result.status, LearningStateExecutionAdmissionAuthorizationStatus.ADMITTED)
        self.assertTrue(result.is_admitted)
        self.assertTrue(result.authorizes_execution)

    def test_ineligible_fails_closed(self):
        ineligible = self.eligibility.__class__(
            **{**self.eligibility.__dict__, "status": LearningStateExecutionEligibilityStatus.INELIGIBLE}
        )
        result = self._admit(ineligible)
        self.assertTrue(result.is_rejected)
        self.assertIn("execution eligibility status must be ELIGIBLE", result.reasons)
        self.assertFalse(result.authorizes_execution)

    def test_admission_identity_must_be_distinct(self):
        result = self._admit(admission_id=self.eligibility.eligibility_id)
        self.assertTrue(result.is_rejected)
        self.assertIn("admission identity must be distinct", result.reasons)

    def test_different_admission_identities_remain_distinct(self):
        first = self._admit(admission_id="execution-admission-152-a")
        second = self._admit(admission_id="execution-admission-152-b")
        self.assertNotEqual(first.admission_id, second.admission_id)
        self.assertEqual(first.eligibility_id, second.eligibility_id)

    def test_execution_target_is_required(self):
        with self.assertRaises(ValueError):
            self._admit(execution_target_id=" ")

    def test_execution_target_must_match_eligibility(self):
        result = self._admit(execution_target_id="other-executor")
        self.assertTrue(result.is_rejected)
        self.assertIn("execution target must match eligibility", result.reasons)

    def test_authorization_scope_is_required(self):
        with self.assertRaises(ValueError):
            self._admit(authorization_scope=None)

    def test_authority_basis_is_required(self):
        with self.assertRaises(ValueError):
            self._admit(authority_basis=None)

    def test_admission_purpose_is_required(self):
        with self.assertRaises(ValueError):
            self._admit(admission_purpose="")

    def test_admission_rationale_is_required(self):
        with self.assertRaises(ValueError):
            self._admit(admission_rationale=None)

    def test_eligibility_lineage_is_checked(self):
        lineage = dict(self.eligibility.lineage)
        lineage["eligibility_id"] = "tampered-eligibility"
        source = self.eligibility.__class__(**{**self.eligibility.__dict__, "lineage": lineage})
        result = self._admit(source)
        self.assertIn("eligibility lineage mismatch", result.reasons)

    def test_handling_lineage_is_checked(self):
        lineage = dict(self.eligibility.lineage)
        lineage["handling_id"] = "tampered-handling"
        source = self.eligibility.__class__(**{**self.eligibility.__dict__, "lineage": lineage})
        result = self._admit(source)
        self.assertIn("handling lineage mismatch", result.reasons)

    def test_consumption_lineage_is_checked(self):
        lineage = dict(self.eligibility.lineage)
        lineage["consumption_id"] = "tampered-consumption"
        source = self.eligibility.__class__(**{**self.eligibility.__dict__, "lineage": lineage})
        result = self._admit(source)
        self.assertIn("consumption lineage mismatch", result.reasons)

    def test_receipt_lineage_is_checked(self):
        lineage = dict(self.eligibility.lineage)
        lineage["receipt_id"] = "tampered-receipt"
        source = self.eligibility.__class__(**{**self.eligibility.__dict__, "lineage": lineage})
        result = self._admit(source)
        self.assertIn("receipt lineage mismatch", result.reasons)

    def test_handoff_lineage_is_checked(self):
        lineage = dict(self.eligibility.lineage)
        lineage["handoff_id"] = "tampered-handoff"
        source = self.eligibility.__class__(**{**self.eligibility.__dict__, "lineage": lineage})
        result = self._admit(source)
        self.assertIn("handoff lineage mismatch", result.reasons)

    def test_integrity_lineage_is_checked(self):
        lineage = dict(self.eligibility.lineage)
        lineage["integrity_id"] = "tampered-integrity"
        source = self.eligibility.__class__(**{**self.eligibility.__dict__, "lineage": lineage})
        result = self._admit(source)
        self.assertIn("integrity lineage mismatch", result.reasons)

    def test_validation_lineage_is_checked(self):
        lineage = dict(self.eligibility.lineage)
        lineage["validation_id"] = "tampered-validation"
        source = self.eligibility.__class__(**{**self.eligibility.__dict__, "lineage": lineage})
        result = self._admit(source)
        self.assertIn("validation lineage mismatch", result.reasons)

    def test_semantic_use_lineage_is_checked(self):
        lineage = dict(self.eligibility.lineage)
        lineage["semantic_use_id"] = "tampered-semantic-use"
        source = self.eligibility.__class__(**{**self.eligibility.__dict__, "lineage": lineage})
        result = self._admit(source)
        self.assertIn("semantic-use lineage mismatch", result.reasons)

    def test_source_request_lineage_is_checked(self):
        lineage = dict(self.eligibility.lineage)
        lineage["request_id"] = "tampered-request"
        source = self.eligibility.__class__(**{**self.eligibility.__dict__, "lineage": lineage})
        result = self._admit(source)
        self.assertIn("source request lineage mismatch", result.reasons)

    def test_source_validation_lineage_is_checked(self):
        lineage = dict(self.eligibility.lineage)
        lineage["source_validation_id"] = "tampered-source-validation"
        source = self.eligibility.__class__(**{**self.eligibility.__dict__, "lineage": lineage})
        result = self._admit(source)
        self.assertIn("source validation lineage mismatch", result.reasons)

    def test_interpretation_lineage_is_checked(self):
        lineage = dict(self.eligibility.lineage)
        lineage["interpretation_id"] = "tampered-interpretation"
        source = self.eligibility.__class__(**{**self.eligibility.__dict__, "lineage": lineage})
        result = self._admit(source)
        self.assertIn("interpretation lineage mismatch", result.reasons)

    def test_inherited_provenance_is_checked(self):
        lineage = dict(self.eligibility.lineage)
        lineage["source_request_id"] = "tampered-source-request"
        lineage["source_validation_provenance_id"] = "tampered-source-validation"
        lineage["read_id"] = "tampered-read"
        lineage["consumption_request_id"] = "tampered-consumption-request"
        source = self.eligibility.__class__(**{**self.eligibility.__dict__, "lineage": lineage})
        result = self._admit(source)
        self.assertIn("source request provenance mismatch", result.reasons)
        self.assertIn("source validation provenance mismatch", result.reasons)
        self.assertIn("read lineage mismatch", result.reasons)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_payload_is_bounded(self):
        result = self._admit()
        self.assertEqual(dict(result.payload)["eligibility_id"], self.eligibility.eligibility_id)
        self.assertEqual(dict(result.payload)["execution_target_id"], "executor-1")
        self.assertEqual(
            dict(result.payload)["authorization_scope"],
            {"actions": ("execute",), "target": "executor-1"},
        )

    def test_payload_is_recursively_immutable(self):
        result = self._admit()
        self.assertIsInstance(result.payload, MappingProxyType)
        self.assertIsInstance(result.payload["authorization_scope"], MappingProxyType)
        self.assertIsInstance(result.payload["authorization_scope"]["actions"], tuple)
        with self.assertRaises(TypeError):
            result.payload["execution_target_id"] = "changed"

    def test_authorization_scope_is_recursively_immutable(self):
        result = self._admit(authorization_scope={"actions": ["execute", "inspect"]})
        self.assertIsInstance(result.authorization_scope, MappingProxyType)
        self.assertIsInstance(result.authorization_scope["actions"], tuple)

    def test_source_eligibility_is_not_mutated(self):
        before = dict(self.eligibility.lineage)
        self._admit()
        self.assertEqual(dict(self.eligibility.lineage), before)

    def test_explicit_reasons_are_preserved(self):
        result = self._admit(reasons=("approved bounded execution scope",))
        self.assertEqual(result.reasons, ("approved bounded execution scope",))

    def test_admitted_does_not_execute_or_mutate(self):
        result = self._admit()
        for name in (
            "invokes_executor", "invokes_learner", "schedules_work", "plans_work", "mutates_state",
            "persists_state", "reads_durable_state", "rereads_durable_state", "is_learning",
            "applies_learning", "authorizes_learning", "authorizes_retry", "updates_model",
            "mutates_memory", "mutates_policy", "establishes_truth", "establishes_correctness",
            "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_authorization_is_scoped_to_declared_target(self):
        result = self._admit()
        self.assertEqual(result.execution_target_id, self.eligibility.execution_target_id)
        self.assertEqual(result.payload["execution_target_id"], "executor-1")


if __name__ == "__main__":
    unittest.main()
