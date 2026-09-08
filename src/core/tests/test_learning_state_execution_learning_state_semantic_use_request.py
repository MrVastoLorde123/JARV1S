"""Focused M23.143 tests for the semantic-use request boundary."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_interpretation_validation_integrity import (
    LearningStateExecutionLearningStateInterpretationValidationIntegrity,
    LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus,
)
from src.core.learning_state_execution_learning_state_semantic_use_request import (
    LearningStateExecutionLearningStateSemanticUseRequest,
    LearningStateExecutionLearningStateSemanticUseRequestService,
    LearningStateExecutionLearningStateSemanticUseRequestStatus,
)


class M23_143LearningStateSemanticUseRequestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lineage = {
            "integrity_id": "interpretation-validation-integrity-142",
            "validation_id": "interpretation-validation-141",
            "interpretation_id": "interpretation-140",
            "request_id": "consumption-request-136",
            "source_request_id": "consumption-request-136",
            "source_validation_id": "consumption-validation-138",
            "read_id": "durable-read-137",
            "consumption_request_id": "consumption-request-136",
        }
        self.integrity = LearningStateExecutionLearningStateInterpretationValidationIntegrity(
            integrity_id="interpretation-validation-integrity-142",
            validation_id="interpretation-validation-141",
            interpretation_id="interpretation-140",
            source_request_id="consumption-request-136",
            source_validation_id="consumption-validation-138",
            read_id="durable-read-137",
            consumption_request_id="consumption-request-136",
            interpretation={"kind": "mapping", "keys": ("confidence", "state"), "size": 2},
            read_payload={"state": "ready", "confidence": 0.9},
            read_fingerprint="a" * 64,
            computed_read_fingerprint="a" * 64,
            validation_actor_id="validator-141",
            validation_purpose="validate interpretation",
            status=LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus.VALID,
            integrity_fingerprint="b" * 64,
            computed_integrity_fingerprint="b" * 64,
            reasons=("integrity verified",),
            lineage=self.lineage,
        )

    def _request(self, integrity=None, **kwargs):
        params = {
            "request_id": "semantic-use-request-143",
            "semantic_use_id": "semantic-use-144",
            "requester_id": "user-1",
            "request_purpose": "use validated state for downstream reasoning",
            "request_rationale": {"reason": "explicit downstream use"},
            "requested_use": {"operation": "summarize", "target": "planning-context"},
        }
        params.update(kwargs)
        return LearningStateExecutionLearningStateSemanticUseRequestService().request(
            integrity or self.integrity,
            **params,
        )

    def test_exact_integrity_type_is_required(self):
        with self.assertRaises(TypeError):
            self._request(integrity=object())

    def test_valid_integrity_produces_requested(self):
        result = self._request()
        self.assertIsInstance(result, LearningStateExecutionLearningStateSemanticUseRequest)
        self.assertEqual(result.status, LearningStateExecutionLearningStateSemanticUseRequestStatus.REQUESTED)
        self.assertTrue(result.is_requested)
        self.assertTrue(result.admits_semantic_use)

    def test_invalid_integrity_fails_closed(self):
        invalid = self.integrity.__class__(**{**self.integrity.__dict__, "status": LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus.INVALID})
        result = self._request(integrity=invalid)
        self.assertEqual(result.status, LearningStateExecutionLearningStateSemanticUseRequestStatus.REJECTED)
        self.assertFalse(result.admits_semantic_use)

    def test_request_identity_must_be_distinct_from_semantic_use_identity(self):
        result = self._request(semantic_use_id="semantic-use-request-143")
        self.assertTrue(result.is_rejected)
        self.assertIn("request identity must be distinct", result.reasons[0])

    def test_requester_identity_is_required(self):
        with self.assertRaises(ValueError):
            self._request(requester_id=" ")

    def test_request_purpose_is_required(self):
        with self.assertRaises(ValueError):
            self._request(request_purpose="")

    def test_request_rationale_is_required(self):
        with self.assertRaises(ValueError):
            self._request(request_rationale=None)

    def test_requested_use_is_required(self):
        with self.assertRaises(ValueError):
            self._request(requested_use=None)

    def test_integrity_lineage_mismatch_is_rejected(self):
        tampered = self.integrity.lineage.copy()
        tampered["validation_id"] = "tampered-validation"
        result = self._request(integrity=self.integrity.__class__(**{**self.integrity.__dict__, "lineage": tampered}))
        self.assertTrue(result.is_rejected)
        self.assertIn("validation lineage mismatch", result.reasons)

    def test_interpretation_lineage_mismatch_is_rejected(self):
        tampered = self.integrity.lineage.copy()
        tampered["interpretation_id"] = "tampered-interpretation"
        result = self._request(integrity=self.integrity.__class__(**{**self.integrity.__dict__, "lineage": tampered}))
        self.assertTrue(result.is_rejected)
        self.assertIn("interpretation lineage mismatch", result.reasons)

    def test_request_lineage_mismatch_is_rejected(self):
        tampered = self.integrity.lineage.copy()
        tampered["request_id"] = "tampered-request"
        result = self._request(integrity=self.integrity.__class__(**{**self.integrity.__dict__, "lineage": tampered}))
        self.assertTrue(result.is_rejected)
        self.assertIn("request lineage mismatch", result.reasons)

    def test_inherited_read_and_consumption_lineage_are_checked(self):
        tampered = self.integrity.lineage.copy()
        tampered["read_id"] = "tampered-read"
        tampered["consumption_request_id"] = "tampered-consumption"
        result = self._request(integrity=self.integrity.__class__(**{**self.integrity.__dict__, "lineage": tampered}))
        self.assertTrue(result.is_rejected)
        self.assertIn("read lineage mismatch", result.reasons)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_provenance_is_preserved(self):
        result = self._request()
        self.assertEqual(result.integrity_id, self.integrity.integrity_id)
        self.assertEqual(result.validation_id, self.integrity.validation_id)
        self.assertEqual(result.interpretation_id, self.integrity.interpretation_id)
        self.assertEqual(result.source_request_id, self.integrity.source_request_id)
        self.assertEqual(result.source_validation_id, self.integrity.source_validation_id)
        self.assertEqual(result.read_id, self.integrity.read_id)
        self.assertEqual(result.consumption_request_id, self.integrity.consumption_request_id)

    def test_semantic_use_request_payload_is_immutable(self):
        result = self._request()
        with self.assertRaises(TypeError):
            result.requested_use["operation"] = "changed"
        self.assertIsInstance(result.lineage, MappingProxyType)

    def test_explicit_reasons_are_preserved(self):
        result = self._request(reasons=("operator requested semantic review",))
        self.assertEqual(result.reasons, ("operator requested semantic review",))

    def test_lineage_is_new_evidence_and_does_not_mutate_source(self):
        source_lineage = dict(self.integrity.lineage)
        result = self._request()
        self.assertNotEqual(result.lineage["request_id"], self.integrity.integrity_id)
        self.assertEqual(dict(self.integrity.lineage), source_lineage)

    def test_request_has_no_authority_or_execution_power(self):
        result = self._request()
        for name in (
            "performs_semantic_use", "is_learning", "applies_learning", "authorizes_learning",
            "authorizes_execution", "authorizes_retry", "invokes_learner", "invokes_executor",
            "schedules_work", "plans_work", "mutates_state", "persists_state", "reads_durable_state",
            "interprets_state", "establishes_truth", "establishes_correctness", "establishes_certainty",
            "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_different_requests_preserve_distinct_identity(self):
        first = self._request(request_id="semantic-use-request-143")
        second = self._request(request_id="semantic-use-request-143-b")
        self.assertNotEqual(first.request_id, second.request_id)
        self.assertEqual(first.integrity_id, second.integrity_id)


if __name__ == "__main__":
    unittest.main()
