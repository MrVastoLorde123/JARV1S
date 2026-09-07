"""Focused M23.145 tests for semantic-use validation."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_semantic_use_request import (
    LearningStateExecutionLearningStateSemanticUseRequest,
    LearningStateExecutionLearningStateSemanticUseRequestStatus,
)
from src.core.learning_state_execution_learning_state_semantic_use import (
    LearningStateExecutionLearningStateSemanticUseService,
    LearningStateExecutionLearningStateSemanticUseStatus,
)
from src.core.learning_state_execution_learning_state_semantic_use_validation import (
    LearningStateExecutionLearningStateSemanticUseValidation,
    LearningStateExecutionLearningStateSemanticUseValidationService,
    LearningStateExecutionLearningStateSemanticUseValidationStatus,
)


class M23_145LearningStateSemanticUseValidationTests(unittest.TestCase):
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
        self.semantic_use = LearningStateExecutionLearningStateSemanticUseService().use(
            request,
            semantic_use_id="semantic-use-144",
            consumer_id="semantic-consumer-1",
            use_purpose="derive bounded downstream semantic context",
            use_rationale={"reason": "explicit requested use"},
        )

    def _validate(self, semantic_use=None, **kwargs):
        params = {"validation_id": "semantic-use-validation-145"}
        params.update(kwargs)
        return LearningStateExecutionLearningStateSemanticUseValidationService().validate(
            semantic_use or self.semantic_use,
            **params,
        )

    def test_exact_semantic_use_type_is_required(self):
        with self.assertRaises(TypeError):
            self._validate(object())

    def test_valid_used_evidence_produces_validated(self):
        result = self._validate()
        self.assertIsInstance(result, LearningStateExecutionLearningStateSemanticUseValidation)
        self.assertEqual(result.status, LearningStateExecutionLearningStateSemanticUseValidationStatus.VALIDATED)
        self.assertTrue(result.is_validated)
        self.assertTrue(result.validates_semantic_use)

    def test_rejected_semantic_use_fails_closed(self):
        rejected = self.semantic_use.__class__(**{**self.semantic_use.__dict__, "status": LearningStateExecutionLearningStateSemanticUseStatus.REJECTED})
        result = self._validate(rejected)
        self.assertTrue(result.is_invalid)
        self.assertIn("semantic-use status must be USED", result.reasons)

    def test_validation_identity_must_be_distinct(self):
        result = self._validate(validation_id=self.semantic_use.semantic_use_id)
        self.assertTrue(result.is_invalid)
        self.assertIn("validation identity must be distinct", result.reasons)

    def test_semantic_use_lineage_is_checked(self):
        lineage = dict(self.semantic_use.lineage)
        lineage["semantic_use_id"] = "tampered-semantic-use"
        source = self.semantic_use.__class__(**{**self.semantic_use.__dict__, "lineage": lineage})
        result = self._validate(source)
        self.assertIn("semantic-use lineage mismatch", result.reasons)

    def test_source_request_lineage_is_checked(self):
        lineage = dict(self.semantic_use.lineage)
        lineage["request_id"] = "tampered-source-request-lineage"
        source = self.semantic_use.__class__(**{**self.semantic_use.__dict__, "lineage": lineage})
        result = self._validate(source)
        self.assertIn("source request lineage mismatch", result.reasons)

    def test_integrity_validation_and_interpretation_lineage_are_checked(self):
        lineage = dict(self.semantic_use.lineage)
        lineage["integrity_id"] = "tampered-integrity"
        lineage["validation_id"] = "tampered-validation"
        lineage["interpretation_id"] = "tampered-interpretation"
        source = self.semantic_use.__class__(**{**self.semantic_use.__dict__, "lineage": lineage})
        result = self._validate(source)
        self.assertIn("integrity lineage mismatch", result.reasons)
        self.assertIn("source validation lineage mismatch", result.reasons)
        self.assertIn("interpretation lineage mismatch", result.reasons)

    def test_inherited_provenance_is_checked(self):
        lineage = dict(self.semantic_use.lineage)
        lineage["source_request_id"] = "tampered-source-request"
        lineage["source_validation_id"] = "tampered-source-validation"
        lineage["read_id"] = "tampered-read"
        lineage["consumption_request_id"] = "tampered-consumption"
        source = self.semantic_use.__class__(**{**self.semantic_use.__dict__, "lineage": lineage})
        result = self._validate(source)
        self.assertIn("source request provenance mismatch", result.reasons)
        self.assertIn("source validation provenance mismatch", result.reasons)
        self.assertIn("read lineage mismatch", result.reasons)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_semantic_input_interpretation_mismatch_is_rejected(self):
        payload = dict(self.semantic_use.semantic_input)
        payload["interpretation_id"] = "tampered-interpretation"
        source = self.semantic_use.__class__(**{**self.semantic_use.__dict__, "semantic_input": payload})
        result = self._validate(source)
        self.assertIn("semantic input interpretation mismatch", result.reasons)

    def test_semantic_input_requested_use_mismatch_is_rejected(self):
        payload = dict(self.semantic_use.semantic_input)
        payload["requested_use"] = {"operation": "tampered"}
        source = self.semantic_use.__class__(**{**self.semantic_use.__dict__, "semantic_input": payload})
        result = self._validate(source)
        self.assertIn("semantic input requested-use mismatch", result.reasons)

    def test_semantic_output_structure_is_checked(self):
        payload = dict(self.semantic_use.semantic_output)
        payload["purpose"] = "tampered-purpose"
        source = self.semantic_use.__class__(**{**self.semantic_use.__dict__, "semantic_output": payload})
        result = self._validate(source)
        self.assertIn("semantic output structural mismatch", result.reasons)

    def test_provenance_is_preserved(self):
        result = self._validate()
        for name in (
            "semantic_use_id", "source_request_id", "source_request_lineage_id", "integrity_id",
            "source_validation_id", "interpretation_id", "read_id", "consumption_request_id",
            "requester_id", "consumer_id",
        ):
            self.assertEqual(getattr(result, name), getattr(self.semantic_use, name))
        self.assertEqual(result.source_validation_lineage_id, self.semantic_use.validation_id)

    def test_validation_payload_is_recursively_immutable(self):
        result = self._validate()
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.requested_use["operation"] = "changed"

    def test_explicit_reasons_are_preserved(self):
        result = self._validate(reasons=("operator requested independent semantic-use review",))
        self.assertEqual(result.reasons, ("operator requested independent semantic-use review",))

    def test_different_validation_identities_remain_distinct(self):
        first = self._validate(validation_id="semantic-use-validation-145-a")
        second = self._validate(validation_id="semantic-use-validation-145-b")
        self.assertNotEqual(first.validation_id, second.validation_id)
        self.assertEqual(first.semantic_use_id, second.semantic_use_id)

    def test_source_semantic_use_is_not_mutated(self):
        before = dict(self.semantic_use.lineage)
        self._validate()
        self.assertEqual(dict(self.semantic_use.lineage), before)

    def test_validation_has_no_truth_learning_or_authority_power(self):
        result = self._validate()
        for name in (
            "is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "invokes_executor", "schedules_work", "plans_work", "mutates_state", "persists_state",
            "reads_durable_state", "rereads_durable_state", "interprets_state", "updates_model", "mutates_memory",
            "mutates_policy", "establishes_truth", "establishes_correctness", "establishes_certainty",
            "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_invalid_lineage_does_not_repair_or_reread(self):
        lineage = dict(self.semantic_use.lineage)
        lineage["read_id"] = "tampered-read"
        source = self.semantic_use.__class__(**{**self.semantic_use.__dict__, "lineage": lineage})
        result = self._validate(source)
        self.assertTrue(result.is_invalid)
        self.assertEqual(result.read_id, source.read_id)


if __name__ == "__main__":
    unittest.main()
