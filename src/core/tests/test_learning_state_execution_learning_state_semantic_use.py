"""Focused M23.144 tests for the semantic-use boundary."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_semantic_use_request import (
    LearningStateExecutionLearningStateSemanticUseRequest,
    LearningStateExecutionLearningStateSemanticUseRequestStatus,
)
from src.core.learning_state_execution_learning_state_semantic_use import (
    LearningStateExecutionLearningStateSemanticUse,
    LearningStateExecutionLearningStateSemanticUseService,
    LearningStateExecutionLearningStateSemanticUseStatus,
)


class M23_144LearningStateSemanticUseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lineage = {
            "request_id": "semantic-use-request-143",
            "integrity_id": "interpretation-validation-integrity-142",
            "validation_id": "interpretation-validation-141",
            "interpretation_id": "interpretation-140",
            "source_request_id": "consumption-request-136",
            "source_validation_id": "consumption-validation-138",
            "read_id": "durable-read-137",
            "consumption_request_id": "consumption-request-136",
        }
        self.request = LearningStateExecutionLearningStateSemanticUseRequest(
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
            lineage=self.lineage,
        )

    def _use(self, request=None, **kwargs):
        params = {
            "semantic_use_id": "semantic-use-144",
            "consumer_id": "semantic-consumer-1",
            "use_purpose": "derive bounded downstream semantic context",
            "use_rationale": {"reason": "explicit requested use"},
        }
        params.update(kwargs)
        return LearningStateExecutionLearningStateSemanticUseService().use(
            request or self.request,
            **params,
        )

    def test_exact_request_type_is_required(self):
        with self.assertRaises(TypeError):
            self._use(request=object())

    def test_valid_request_produces_used(self):
        result = self._use()
        self.assertIsInstance(result, LearningStateExecutionLearningStateSemanticUse)
        self.assertEqual(result.status, LearningStateExecutionLearningStateSemanticUseStatus.USED)
        self.assertTrue(result.is_used)
        self.assertTrue(result.performs_semantic_use)

    def test_rejected_request_fails_closed(self):
        rejected = self.request.__class__(**{**self.request.__dict__, "status": LearningStateExecutionLearningStateSemanticUseRequestStatus.REJECTED})
        result = self._use(request=rejected)
        self.assertEqual(result.status, LearningStateExecutionLearningStateSemanticUseStatus.REJECTED)
        self.assertFalse(result.performs_semantic_use)

    def test_semantic_use_identity_must_be_distinct_from_request(self):
        result = self._use(semantic_use_id="semantic-use-request-143")
        self.assertTrue(result.is_rejected)
        self.assertIn("semantic-use identity must be distinct", result.reasons)

    def test_consumer_identity_is_required(self):
        with self.assertRaises(ValueError):
            self._use(consumer_id=" ")

    def test_use_purpose_is_required(self):
        with self.assertRaises(ValueError):
            self._use(use_purpose="")

    def test_use_rationale_is_required(self):
        with self.assertRaises(ValueError):
            self._use(use_rationale=None)

    def test_request_lineage_mismatch_is_rejected(self):
        tampered = self.request.lineage.copy()
        tampered["request_id"] = "tampered-request"
        source = self.request.__class__(**{**self.request.__dict__, "lineage": tampered})
        result = self._use(request=source)
        self.assertTrue(result.is_rejected)
        self.assertIn("request lineage mismatch", result.reasons)

    def test_integrity_and_validation_lineage_mismatch_is_rejected(self):
        tampered = self.request.lineage.copy()
        tampered["integrity_id"] = "tampered-integrity"
        tampered["validation_id"] = "tampered-validation"
        source = self.request.__class__(**{**self.request.__dict__, "lineage": tampered})
        result = self._use(request=source)
        self.assertTrue(result.is_rejected)
        self.assertIn("integrity lineage mismatch", result.reasons)
        self.assertIn("validation lineage mismatch", result.reasons)

    def test_interpretation_lineage_mismatch_is_rejected(self):
        tampered = self.request.lineage.copy()
        tampered["interpretation_id"] = "tampered-interpretation"
        source = self.request.__class__(**{**self.request.__dict__, "lineage": tampered})
        result = self._use(request=source)
        self.assertTrue(result.is_rejected)
        self.assertIn("interpretation lineage mismatch", result.reasons)

    def test_inherited_provenance_lineage_is_checked(self):
        tampered = self.request.lineage.copy()
        tampered["source_request_id"] = "tampered-source-request"
        tampered["source_validation_id"] = "tampered-source-validation"
        tampered["read_id"] = "tampered-read"
        tampered["consumption_request_id"] = "tampered-consumption"
        source = self.request.__class__(**{**self.request.__dict__, "lineage": tampered})
        result = self._use(request=source)
        self.assertTrue(result.is_rejected)
        self.assertIn("source request lineage mismatch", result.reasons)
        self.assertIn("source validation lineage mismatch", result.reasons)
        self.assertIn("read lineage mismatch", result.reasons)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_provenance_is_preserved(self):
        result = self._use()
        for name in (
            "source_request_id", "integrity_id", "validation_id", "interpretation_id",
            "source_validation_id", "read_id", "consumption_request_id", "requester_id",
        ):
            self.assertEqual(getattr(result, name), getattr(self.request, name))

    def test_semantic_use_payload_is_immutable(self):
        result = self._use()
        with self.assertRaises(TypeError):
            result.semantic_output["use"] = "changed"
        self.assertIsInstance(result.lineage, MappingProxyType)

    def test_semantic_output_is_structural(self):
        result = self._use()
        self.assertEqual(result.semantic_output["interpretation_id"], self.request.interpretation_id)
        self.assertEqual(result.semantic_output["purpose"], "derive bounded downstream semantic context")
        self.assertEqual(result.semantic_output["use"]["kind"], "mapping")

    def test_explicit_reasons_are_preserved(self):
        result = self._use(reasons=("operator approved bounded semantic review",))
        self.assertEqual(result.reasons, ("operator approved bounded semantic review",))

    def test_semantic_use_creates_new_evidence_without_mutating_source(self):
        source_lineage = dict(self.request.lineage)
        result = self._use()
        self.assertNotEqual(result.semantic_use_id, self.request.request_id)
        self.assertEqual(dict(self.request.lineage), source_lineage)

    def test_no_authority_learning_or_execution_power(self):
        result = self._use()
        for name in (
            "is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "invokes_executor", "schedules_work", "plans_work", "mutates_state", "persists_state",
            "reads_durable_state", "rereads_durable_state", "interprets_state", "updates_model", "mutates_memory",
            "mutates_policy", "establishes_truth", "establishes_correctness", "establishes_certainty",
            "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_different_uses_preserve_distinct_identity(self):
        first = self._use(semantic_use_id="semantic-use-144-a")
        second = self._use(semantic_use_id="semantic-use-144-b")
        self.assertNotEqual(first.semantic_use_id, second.semantic_use_id)
        self.assertEqual(first.source_request_id, second.source_request_id)

    def test_lineage_is_new_evidence(self):
        result = self._use()
        self.assertEqual(result.lineage["semantic_use_id"], result.semantic_use_id)
        self.assertEqual(result.lineage["request_id"], self.request.request_id)


if __name__ == "__main__":
    unittest.main()
