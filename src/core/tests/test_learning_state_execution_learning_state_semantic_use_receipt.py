"""Focused M23.148 tests for semantic-use receipt."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_semantic_use import LearningStateExecutionLearningStateSemanticUseService
from src.core.learning_state_execution_learning_state_semantic_use_request import (
    LearningStateExecutionLearningStateSemanticUseRequest,
    LearningStateExecutionLearningStateSemanticUseRequestStatus,
)
from src.core.learning_state_execution_learning_state_semantic_use_validation import LearningStateExecutionLearningStateSemanticUseValidationService
from src.core.learning_state_execution_learning_state_semantic_use_validation_integrity import LearningStateExecutionLearningStateSemanticUseValidationIntegrityService
from src.core.learning_state_execution_learning_state_semantic_use_handoff import (
    LearningStateExecutionLearningStateSemanticUseHandoffService,
    LearningStateExecutionLearningStateSemanticUseHandoffStatus,
)
from src.core.learning_state_execution_learning_state_semantic_use_receipt import (
    LearningStateExecutionLearningStateSemanticUseReceipt,
    LearningStateExecutionLearningStateSemanticUseReceiptService,
    LearningStateExecutionLearningStateSemanticUseReceiptStatus,
)


class M23_148LearningStateSemanticUseReceiptTests(unittest.TestCase):
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
        integrity = LearningStateExecutionLearningStateSemanticUseValidationIntegrityService().validate(
            validation,
            integrity_id="semantic-use-validation-integrity-146",
        )
        self.handoff = LearningStateExecutionLearningStateSemanticUseHandoffService().handoff(
            integrity,
            handoff_id="semantic-use-handoff-147",
            handoff_target_id="downstream-consumer-1",
            handoff_purpose="present verified semantic use downstream",
            handoff_rationale={"reason": "explicit downstream boundary"},
        )

    def _receive(self, handoff=None, **kwargs):
        params = {
            "receipt_id": "semantic-use-receipt-148",
            "recipient_id": "downstream-consumer-1",
            "receipt_purpose": "acknowledge downstream receipt",
            "receipt_rationale": {"reason": "declared recipient boundary"},
        }
        params.update(kwargs)
        return LearningStateExecutionLearningStateSemanticUseReceiptService().receive(
            handoff or self.handoff,
            **params,
        )

    def test_exact_handoff_type_is_required(self):
        with self.assertRaises(TypeError):
            self._receive(object())

    def test_handed_off_produces_received(self):
        result = self._receive()
        self.assertIsInstance(result, LearningStateExecutionLearningStateSemanticUseReceipt)
        self.assertEqual(result.status, LearningStateExecutionLearningStateSemanticUseReceiptStatus.RECEIVED)
        self.assertTrue(result.is_received)

    def test_rejected_handoff_fails_closed(self):
        invalid = self.handoff.__class__(
            **{**self.handoff.__dict__, "status": self.handoff.status.__class__.REJECTED}
        )
        result = self._receive(invalid)
        self.assertTrue(result.is_rejected)
        self.assertIn("semantic-use handoff status must be HANDED_OFF", result.reasons)

    def test_receipt_identity_must_be_distinct(self):
        result = self._receive(receipt_id=self.handoff.handoff_id)
        self.assertIn("receipt identity must be distinct", result.reasons)

    def test_different_receipt_identities_remain_distinct(self):
        first = self._receive(receipt_id="semantic-use-receipt-148-a")
        second = self._receive(receipt_id="semantic-use-receipt-148-b")
        self.assertNotEqual(first.receipt_id, second.receipt_id)
        self.assertEqual(first.handoff_id, second.handoff_id)

    def test_recipient_identity_is_required(self):
        with self.assertRaises(ValueError):
            self._receive(recipient_id=" ")

    def test_receipt_purpose_is_required(self):
        with self.assertRaises(ValueError):
            self._receive(receipt_purpose="")

    def test_receipt_rationale_is_required(self):
        with self.assertRaises(ValueError):
            self._receive(receipt_rationale=None)

    def test_handoff_lineage_is_checked(self):
        lineage = dict(self.handoff.lineage)
        lineage["handoff_id"] = "tampered-handoff"
        source = self.handoff.__class__(**{**self.handoff.__dict__, "lineage": lineage})
        result = self._receive(source)
        self.assertIn("handoff lineage mismatch", result.reasons)

    def test_integrity_lineage_is_checked(self):
        lineage = dict(self.handoff.lineage)
        lineage["integrity_id"] = "tampered-integrity"
        source = self.handoff.__class__(**{**self.handoff.__dict__, "lineage": lineage})
        result = self._receive(source)
        self.assertIn("integrity lineage mismatch", result.reasons)

    def test_validation_lineage_is_checked(self):
        lineage = dict(self.handoff.lineage)
        lineage["validation_id"] = "tampered-validation"
        source = self.handoff.__class__(**{**self.handoff.__dict__, "lineage": lineage})
        result = self._receive(source)
        self.assertIn("validation lineage mismatch", result.reasons)

    def test_semantic_use_lineage_is_checked(self):
        lineage = dict(self.handoff.lineage)
        lineage["semantic_use_id"] = "tampered-semantic-use"
        source = self.handoff.__class__(**{**self.handoff.__dict__, "lineage": lineage})
        result = self._receive(source)
        self.assertIn("semantic-use lineage mismatch", result.reasons)

    def test_source_request_lineage_is_checked(self):
        lineage = dict(self.handoff.lineage)
        lineage["request_id"] = "tampered-request"
        source = self.handoff.__class__(**{**self.handoff.__dict__, "lineage": lineage})
        result = self._receive(source)
        self.assertIn("source request lineage mismatch", result.reasons)

    def test_source_validation_lineage_is_checked(self):
        lineage = dict(self.handoff.lineage)
        lineage["source_validation_id"] = "tampered-source-validation"
        source = self.handoff.__class__(**{**self.handoff.__dict__, "lineage": lineage})
        result = self._receive(source)
        self.assertIn("source validation lineage mismatch", result.reasons)

    def test_inherited_provenance_is_checked(self):
        lineage = dict(self.handoff.lineage)
        lineage["source_request_id"] = "tampered-source-request"
        lineage["source_validation_provenance_id"] = "tampered-source-validation"
        lineage["read_id"] = "tampered-read"
        lineage["consumption_request_id"] = "tampered-consumption"
        source = self.handoff.__class__(**{**self.handoff.__dict__, "lineage": lineage})
        result = self._receive(source)
        self.assertIn("source request provenance mismatch", result.reasons)
        self.assertIn("source validation provenance mismatch", result.reasons)
        self.assertIn("read lineage mismatch", result.reasons)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_interpretation_lineage_is_checked(self):
        lineage = dict(self.handoff.lineage)
        lineage["interpretation_id"] = "tampered-interpretation"
        source = self.handoff.__class__(**{**self.handoff.__dict__, "lineage": lineage})
        result = self._receive(source)
        self.assertIn("interpretation lineage mismatch", result.reasons)

    def test_payload_is_bounded(self):
        result = self._receive()
        self.assertEqual(dict(result.payload), {"handoff_id": self.handoff.handoff_id, "recipient_id": "downstream-consumer-1"})

    def test_payload_is_recursively_immutable(self):
        result = self._receive()
        self.assertIsInstance(result.payload, MappingProxyType)
        with self.assertRaises(TypeError):
            result.payload["recipient_id"] = "changed"

    def test_source_handoff_is_not_mutated(self):
        before = dict(self.handoff.lineage)
        self._receive()
        self.assertEqual(dict(self.handoff.lineage), before)

    def test_explicit_reasons_are_preserved(self):
        result = self._receive(reasons=("recipient acknowledged bounded receipt",))
        self.assertEqual(result.reasons, ("recipient acknowledged bounded receipt",))

    def test_receipt_has_no_truth_learning_authority_or_execution_power(self):
        result = self._receive()
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
