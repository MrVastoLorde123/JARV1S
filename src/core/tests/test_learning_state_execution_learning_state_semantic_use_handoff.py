"""Focused M23.147 tests for semantic-use handoff."""
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
    LearningStateExecutionLearningStateSemanticUseValidationService,
)
from src.core.learning_state_execution_learning_state_semantic_use_validation_integrity import (
    LearningStateExecutionLearningStateSemanticUseValidationIntegrityService,
)
from src.core.learning_state_execution_learning_state_semantic_use_handoff import (
    LearningStateExecutionLearningStateSemanticUseHandoff,
    LearningStateExecutionLearningStateSemanticUseHandoffService,
    LearningStateExecutionLearningStateSemanticUseHandoffStatus,
)


class M23_147LearningStateSemanticUseHandoffTests(unittest.TestCase):
    def setUp(self) -> None:
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
            lineage={
                "request_id": "semantic-use-request-143",
                "integrity_id": "interpretation-validation-integrity-142",
                "validation_id": "interpretation-validation-141",
                "interpretation_id": "interpretation-140",
                "source_request_id": "consumption-request-136",
                "source_validation_id": "consumption-validation-138",
                "read_id": "durable-read-137",
                "consumption_request_id": "consumption-request-136",
            },
        )
        semantic_use = LearningStateExecutionLearningStateSemanticUseService().use(
            request,
            semantic_use_id="semantic-use-144",
            consumer_id="semantic-consumer-1",
            use_purpose="derive bounded downstream semantic context",
            use_rationale={"reason": "explicit requested use"},
        )
        validation = LearningStateExecutionLearningStateSemanticUseValidationService().validate(
            semantic_use,
            validation_id="semantic-use-validation-145",
        )
        self.integrity = LearningStateExecutionLearningStateSemanticUseValidationIntegrityService().validate(
            validation,
            integrity_id="semantic-use-validation-integrity-146",
        )

    def _handoff(self, integrity=None, **kwargs):
        params = {
            "handoff_id": "semantic-use-handoff-147",
            "handoff_target_id": "downstream-consumer-1",
            "handoff_purpose": "present verified semantic use downstream",
            "handoff_rationale": {"reason": "explicit downstream boundary"},
        }
        params.update(kwargs)
        return LearningStateExecutionLearningStateSemanticUseHandoffService().handoff(
            integrity or self.integrity,
            **params,
        )

    def test_exact_integrity_type_is_required(self):
        with self.assertRaises(TypeError):
            self._handoff(object())

    def test_valid_integrity_produces_handed_off(self):
        result = self._handoff()
        self.assertIsInstance(result, LearningStateExecutionLearningStateSemanticUseHandoff)
        self.assertEqual(result.status, LearningStateExecutionLearningStateSemanticUseHandoffStatus.HANDED_OFF)
        self.assertTrue(result.is_handed_off)

    def test_invalid_integrity_fails_closed(self):
        invalid = self.integrity.__class__(
            **{**self.integrity.__dict__, "status": self.integrity.status.__class__.INVALID}
        )
        result = self._handoff(invalid)
        self.assertTrue(result.is_rejected)
        self.assertIn("semantic-use validation integrity status must be VALID", result.reasons)

    def test_handoff_identity_must_be_distinct(self):
        result = self._handoff(handoff_id=self.integrity.integrity_id)
        self.assertTrue(result.is_rejected)
        self.assertIn("handoff identity must be distinct", result.reasons)

    def test_different_handoff_identities_remain_distinct(self):
        first = self._handoff(handoff_id="semantic-use-handoff-147-a")
        second = self._handoff(handoff_id="semantic-use-handoff-147-b")
        self.assertNotEqual(first.handoff_id, second.handoff_id)
        self.assertEqual(first.integrity_id, second.integrity_id)

    def test_target_identity_is_required(self):
        with self.assertRaises(ValueError):
            self._handoff(handoff_target_id=" ")

    def test_handoff_purpose_is_required(self):
        with self.assertRaises(ValueError):
            self._handoff(handoff_purpose="")

    def test_handoff_rationale_is_required(self):
        with self.assertRaises(ValueError):
            self._handoff(handoff_rationale=None)

    def test_integrity_lineage_is_checked(self):
        lineage = dict(self.integrity.lineage)
        lineage["integrity_id"] = "tampered-integrity"
        source = self.integrity.__class__(**{**self.integrity.__dict__, "lineage": lineage})
        result = self._handoff(source)
        self.assertIn("integrity lineage mismatch", result.reasons)

    def test_validation_lineage_is_checked(self):
        lineage = dict(self.integrity.lineage)
        lineage["validation_id"] = "tampered-validation"
        source = self.integrity.__class__(**{**self.integrity.__dict__, "lineage": lineage})
        result = self._handoff(source)
        self.assertIn("validation lineage mismatch", result.reasons)

    def test_semantic_use_lineage_is_checked(self):
        lineage = dict(self.integrity.lineage)
        lineage["semantic_use_id"] = "tampered-semantic-use"
        source = self.integrity.__class__(**{**self.integrity.__dict__, "lineage": lineage})
        result = self._handoff(source)
        self.assertIn("semantic-use lineage mismatch", result.reasons)

    def test_source_request_lineage_is_checked(self):
        lineage = dict(self.integrity.lineage)
        lineage["request_id"] = "tampered-request"
        source = self.integrity.__class__(**{**self.integrity.__dict__, "lineage": lineage})
        result = self._handoff(source)
        self.assertIn("source request lineage mismatch", result.reasons)

    def test_upstream_integrity_lineage_is_preserved(self):
        lineage = dict(self.integrity.lineage)
        lineage["upstream_integrity_id"] = "tampered-upstream"
        source = self.integrity.__class__(**{**self.integrity.__dict__, "lineage": lineage})
        result = self._handoff(source)
        self.assertTrue(result.is_handed_off)
        self.assertEqual(result.lineage["upstream_integrity_id"], "tampered-upstream")

    def test_source_validation_lineage_is_checked(self):
        lineage = dict(self.integrity.lineage)
        lineage["source_validation_id"] = "tampered-source-validation"
        source = self.integrity.__class__(**{**self.integrity.__dict__, "lineage": lineage})
        result = self._handoff(source)
        self.assertIn("source validation lineage mismatch", result.reasons)

    def test_inherited_provenance_is_checked(self):
        lineage = dict(self.integrity.lineage)
        lineage["source_request_id"] = "tampered-source-request"
        lineage["source_validation_provenance_id"] = "tampered-source-validation"
        lineage["read_id"] = "tampered-read"
        lineage["consumption_request_id"] = "tampered-consumption"
        source = self.integrity.__class__(**{**self.integrity.__dict__, "lineage": lineage})
        result = self._handoff(source)
        self.assertIn("source request provenance mismatch", result.reasons)
        self.assertIn("source validation provenance mismatch", result.reasons)
        self.assertIn("read lineage mismatch", result.reasons)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_payload_is_bounded(self):
        result = self._handoff()
        self.assertEqual(
            dict(result.payload),
            {
                "validation_id": self.integrity.validation_id,
                "semantic_use_id": self.integrity.semantic_use_id,
                "handoff_target_id": "downstream-consumer-1",
            },
        )

    def test_handoff_payload_is_recursively_immutable(self):
        result = self._handoff()
        self.assertIsInstance(result.payload, MappingProxyType)
        with self.assertRaises(TypeError):
            result.payload["handoff_target_id"] = "changed"

    def test_source_integrity_is_not_mutated(self):
        before = dict(self.integrity.lineage)
        self._handoff()
        self.assertEqual(dict(self.integrity.lineage), before)

    def test_explicit_reasons_are_preserved(self):
        result = self._handoff(reasons=("operator requested bounded handoff",))
        self.assertEqual(result.reasons, ("operator requested bounded handoff",))

    def test_handoff_has_no_truth_learning_authority_or_execution_power(self):
        result = self._handoff()
        for name in (
            "is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "invokes_executor", "schedules_work", "plans_work", "mutates_state", "persists_state",
            "reads_durable_state", "rereads_durable_state", "interprets_state", "updates_model", "mutates_memory",
            "mutates_policy", "establishes_truth", "establishes_correctness", "establishes_certainty",
            "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
