"""Focused M23.146 tests for semantic-use validation integrity."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_semantic_use_request import (
    LearningStateExecutionLearningStateSemanticUseRequest,
    LearningStateExecutionLearningStateSemanticUseRequestStatus,
)
from src.core.learning_state_execution_learning_state_semantic_use import (
    LearningStateExecutionLearningStateSemanticUseService,
)
from src.core.learning_state_execution_learning_state_semantic_use_validation import (
    LearningStateExecutionLearningStateSemanticUseValidation,
    LearningStateExecutionLearningStateSemanticUseValidationService,
    LearningStateExecutionLearningStateSemanticUseValidationStatus,
)
from src.core.learning_state_execution_learning_state_semantic_use_validation_integrity import (
    LearningStateExecutionLearningStateSemanticUseValidationIntegrity,
    LearningStateExecutionLearningStateSemanticUseValidationIntegrityService,
    LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus,
)


class M23_146LearningStateSemanticUseValidationIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        lineage = {
            "request_id": "semantic-use-request-143",
            "integrity_id": "interpretation-validation-integrity-142",
            "validation_id": "interpretation-validation-141",
            "interpretation_id": "interpretation-140",
            "source_request_id": "consumption-request-136",
            "source_validation_id": "consumption-validation-138",
            "read_id": "durable-read-137",
            "consumption_request_id": "consumption-request-136",
        }
        request = LearningStateExecutionLearningStateSemanticUseRequest(
            request_id="semantic-use-request-143",
            integrity_id="interpretation-validation-integrity-142",
            validation_id="interpretation-validation-141",
            interpretation_id="interpretation-140",
            source_request_id="consumption-request-136",
            source_validation_id="consumption-validation-138",
            read_id="durable-read-137",
            consumption_request_id="consumption-request-136",
            semantic_use_id="semantic-use-144",
            requester_id="user-1",
            request_purpose="use validated state for downstream reasoning",
            request_rationale={"reason": "explicit downstream use"},
            requested_use={"operation": "summarize", "target": "planning-context"},
            status=LearningStateExecutionLearningStateSemanticUseRequestStatus.REQUESTED,
            reasons=("semantic use requested",),
            lineage=lineage,
        )
        semantic_use = LearningStateExecutionLearningStateSemanticUseService().use(
            request,
            semantic_use_id="semantic-use-144",
            consumer_id="semantic-consumer-1",
            use_purpose="derive bounded downstream semantic context",
            use_rationale={"reason": "explicit requested use"},
        )
        self.validation = LearningStateExecutionLearningStateSemanticUseValidationService().validate(
            semantic_use,
            validation_id="semantic-use-validation-145",
        )

    def _integrity(self, validation=None, **kwargs):
        params = {"integrity_id": "semantic-use-validation-integrity-146"}
        params.update(kwargs)
        return LearningStateExecutionLearningStateSemanticUseValidationIntegrityService().validate(
            validation or self.validation,
            **params,
        )

    def test_exact_validation_type_is_required(self):
        with self.assertRaises(TypeError):
            self._integrity(object())

    def test_validated_source_produces_valid_integrity(self):
        result = self._integrity()
        self.assertIsInstance(result, LearningStateExecutionLearningStateSemanticUseValidationIntegrity)
        self.assertEqual(result.status, LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus.VALID)
        self.assertTrue(result.is_valid)
        self.assertTrue(result.validates_validation_integrity)

    def test_invalid_validation_fails_closed(self):
        invalid = self.validation.__class__(
            **{**self.validation.__dict__, "status": LearningStateExecutionLearningStateSemanticUseValidationStatus.INVALID}
        )
        result = self._integrity(invalid)
        self.assertTrue(result.is_invalid if hasattr(result, "is_invalid") else result.status is LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus.INVALID)
        self.assertIn("semantic-use validation status must be VALIDATED", result.reasons)

    def test_integrity_identity_must_be_distinct(self):
        result = self._integrity(integrity_id=self.validation.validation_id)
        self.assertTrue(result.is_invalid if hasattr(result, "is_invalid") else result.status is LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus.INVALID)
        self.assertIn("integrity identity must be distinct", result.reasons)

    def test_validation_lineage_is_checked(self):
        lineage = dict(self.validation.lineage)
        lineage["validation_id"] = "tampered-validation"
        source = self.validation.__class__(**{**self.validation.__dict__, "lineage": lineage})
        result = self._integrity(source)
        self.assertIn("validation lineage mismatch", result.reasons)

    def test_semantic_use_lineage_is_checked(self):
        lineage = dict(self.validation.lineage)
        lineage["semantic_use_id"] = "tampered-semantic-use"
        source = self.validation.__class__(**{**self.validation.__dict__, "lineage": lineage})
        result = self._integrity(source)
        self.assertIn("semantic-use lineage mismatch", result.reasons)

    def test_source_request_lineage_is_checked(self):
        lineage = dict(self.validation.lineage)
        lineage["request_id"] = "tampered-request-lineage"
        source = self.validation.__class__(**{**self.validation.__dict__, "lineage": lineage})
        result = self._integrity(source)
        self.assertIn("source request lineage mismatch", result.reasons)

    def test_upstream_integrity_lineage_is_checked(self):
        lineage = dict(self.validation.lineage)
        lineage["integrity_id"] = "tampered-upstream-integrity"
        source = self.validation.__class__(**{**self.validation.__dict__, "lineage": lineage})
        result = self._integrity(source)
        self.assertIn("upstream integrity lineage mismatch", result.reasons)

    def test_source_validation_lineage_is_checked(self):
        lineage = dict(self.validation.lineage)
        lineage["source_validation_id"] = "tampered-source-validation-lineage"
        source = self.validation.__class__(**{**self.validation.__dict__, "lineage": lineage})
        result = self._integrity(source)
        self.assertIn("source validation lineage mismatch", result.reasons)

    def test_inherited_provenance_is_checked(self):
        lineage = dict(self.validation.lineage)
        lineage["source_request_id"] = "tampered-source-request"
        lineage["source_validation_provenance_id"] = "tampered-source-validation"
        lineage["read_id"] = "tampered-read"
        lineage["consumption_request_id"] = "tampered-consumption"
        source = self.validation.__class__(**{**self.validation.__dict__, "lineage": lineage})
        result = self._integrity(source)
        self.assertIn("source request provenance mismatch", result.reasons)
        self.assertIn("source validation provenance mismatch", result.reasons)
        self.assertIn("read lineage mismatch", result.reasons)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_interpretation_lineage_is_checked(self):
        lineage = dict(self.validation.lineage)
        lineage["interpretation_id"] = "tampered-interpretation"
        source = self.validation.__class__(**{**self.validation.__dict__, "lineage": lineage})
        result = self._integrity(source)
        self.assertIn("interpretation lineage mismatch", result.reasons)

    def test_fingerprint_is_deterministic(self):
        first = self._integrity(integrity_id="semantic-use-validation-integrity-146-a")
        second = self._integrity(integrity_id="semantic-use-validation-integrity-146-b")
        self.assertEqual(first.validation_fingerprint, second.validation_fingerprint)
        self.assertEqual(first.validation_fingerprint, first.computed_validation_fingerprint)
        self.assertEqual(len(first.validation_fingerprint), 64)

    def test_tampered_validation_payload_changes_fingerprint(self):
        tampered = self.validation.__class__(
            **{
                **self.validation.__dict__,
                "use_purpose": "tampered-purpose",
            }
        )
        original = self._integrity()
        changed = self._integrity(tampered)
        self.assertNotEqual(original.validation_fingerprint, changed.validation_fingerprint)

    def test_source_validation_is_not_mutated(self):
        before = dict(self.validation.lineage)
        self._integrity()
        self.assertEqual(dict(self.validation.lineage), before)
        self.assertEqual(self.validation.status, LearningStateExecutionLearningStateSemanticUseValidationStatus.VALIDATED)

    def test_integrity_payload_is_recursively_immutable(self):
        result = self._integrity()
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["integrity_id"] = "changed"

    def test_explicit_reasons_are_preserved(self):
        result = self._integrity(reasons=("operator requested integrity review",))
        self.assertEqual(result.reasons, ("operator requested integrity review",))

    def test_different_integrity_identities_remain_distinct(self):
        first = self._integrity(integrity_id="semantic-use-validation-integrity-146-a")
        second = self._integrity(integrity_id="semantic-use-validation-integrity-146-b")
        self.assertNotEqual(first.integrity_id, second.integrity_id)
        self.assertEqual(first.validation_id, second.validation_id)

    def test_integrity_has_no_truth_learning_authority_or_execution_power(self):
        result = self._integrity()
        for name in (
            "is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "invokes_executor", "schedules_work", "plans_work", "mutates_state", "persists_state",
            "reads_durable_state", "rereads_durable_state", "interprets_state", "updates_model", "mutates_memory",
            "mutates_policy", "establishes_truth", "establishes_correctness", "establishes_certainty",
            "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_rejected_integrity_does_not_repair_source(self):
        lineage = dict(self.validation.lineage)
        lineage["read_id"] = "tampered-read"
        source = self.validation.__class__(**{**self.validation.__dict__, "lineage": lineage})
        result = self._integrity(source)
        self.assertTrue(result.status is LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus.INVALID)
        self.assertEqual(result.read_id, source.read_id)


if __name__ == "__main__":
    unittest.main()
