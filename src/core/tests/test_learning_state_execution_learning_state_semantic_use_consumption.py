"""Focused M23.149 tests for semantic-use consumption."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_semantic_use_receipt import (
    LearningStateExecutionLearningStateSemanticUseReceipt,
    LearningStateExecutionLearningStateSemanticUseReceiptService,
    LearningStateExecutionLearningStateSemanticUseReceiptStatus,
)
from src.core.learning_state_execution_learning_state_semantic_use_handoff import (
    LearningStateExecutionLearningStateSemanticUseHandoffService,
)
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
from src.core.learning_state_execution_learning_state_semantic_use_consumption import (
    LearningStateExecutionLearningStateSemanticUseConsumption,
    LearningStateExecutionLearningStateSemanticUseConsumptionService,
    LearningStateExecutionLearningStateSemanticUseConsumptionStatus,
)


class M23_149LearningStateSemanticUseConsumptionTests(unittest.TestCase):
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

    def _consume(self, receipt=None, **kwargs):
        params = {
            "consumption_id": "semantic-use-consumption-149",
            "consumer_id": "downstream-consumer-1",
            "consumption_purpose": "consume received semantic use",
            "consumption_rationale": {"reason": "explicit downstream consumption"},
        }
        params.update(kwargs)
        return LearningStateExecutionLearningStateSemanticUseConsumptionService().consume(
            receipt or LearningStateExecutionLearningStateSemanticUseReceiptService().receive(
                self.handoff,
                receipt_id="semantic-use-receipt-148",
                recipient_id="downstream-recipient-1",
                receipt_purpose="acknowledge downstream receipt",
                receipt_rationale={"reason": "explicit receipt"},
            ),
            **params,
        )

    def test_exact_receipt_type_is_required(self):
        with self.assertRaises(TypeError):
            self._consume(object())

    def test_received_produces_consumed(self):
        result = self._consume()
        self.assertIsInstance(result, LearningStateExecutionLearningStateSemanticUseConsumption)
        self.assertEqual(result.status, LearningStateExecutionLearningStateSemanticUseConsumptionStatus.CONSUMED)
        self.assertTrue(result.is_consumed)

    def test_rejected_receipt_fails_closed(self):
        invalid = self.handoff
        receipt = LearningStateExecutionLearningStateSemanticUseReceiptService().receive(
            invalid,
            receipt_id="semantic-use-receipt-148-invalid",
            recipient_id="downstream-recipient-1",
            receipt_purpose="acknowledge downstream receipt",
            receipt_rationale={"reason": "explicit receipt"},
            lineage={"handoff_id": "tampered-handoff"},
        )
        result = self._consume(receipt)
        self.assertTrue(result.is_rejected)
        self.assertIn("handoff lineage mismatch", result.reasons)

    def test_consumption_identity_must_be_distinct(self):
        receipt = LearningStateExecutionLearningStateSemanticUseReceiptService().receive(
            self.handoff,
            receipt_id="semantic-use-receipt-148",
            recipient_id="downstream-recipient-1",
            receipt_purpose="acknowledge downstream receipt",
            receipt_rationale={"reason": "explicit receipt"},
        )
        result = self._consume(receipt, consumption_id=receipt.receipt_id)
        self.assertTrue(result.is_rejected)
        self.assertIn("consumption identity must be distinct", result.reasons)

    def test_different_consumption_identities_remain_distinct(self):
        first = self._consume(consumption_id="semantic-use-consumption-149-a")
        second = self._consume(consumption_id="semantic-use-consumption-149-b")
        self.assertNotEqual(first.consumption_id, second.consumption_id)
        self.assertEqual(first.receipt_id, second.receipt_id)

    def test_consumer_identity_is_required(self):
        with self.assertRaises(ValueError):
            self._consume(consumer_id=" ")

    def test_consumption_purpose_is_required(self):
        with self.assertRaises(ValueError):
            self._consume(consumption_purpose="")

    def test_consumption_rationale_is_required(self):
        with self.assertRaises(ValueError):
            self._consume(consumption_rationale=None)

    def test_receipt_lineage_is_checked(self):
        receipt = LearningStateExecutionLearningStateSemanticUseReceiptService().receive(
            self.handoff,
            receipt_id="semantic-use-receipt-148",
            recipient_id="downstream-recipient-1",
            receipt_purpose="acknowledge downstream receipt",
            receipt_rationale={"reason": "explicit receipt"},
        )
        lineage = dict(receipt.lineage)
        lineage["receipt_id"] = "tampered-receipt"
        source = receipt.__class__(**{**receipt.__dict__, "lineage": lineage})
        result = self._consume(source)
        self.assertIn("receipt lineage mismatch", result.reasons)

    def test_handoff_lineage_is_checked(self):
        receipt = LearningStateExecutionLearningStateSemanticUseReceiptService().receive(
            self.handoff,
            receipt_id="semantic-use-receipt-148",
            recipient_id="downstream-recipient-1",
            receipt_purpose="acknowledge downstream receipt",
            receipt_rationale={"reason": "explicit receipt"},
        )
        lineage = dict(receipt.lineage)
        lineage["handoff_id"] = "tampered-handoff"
        source = receipt.__class__(**{**receipt.__dict__, "lineage": lineage})
        result = self._consume(source)
        self.assertIn("handoff lineage mismatch", result.reasons)

    def test_integrity_lineage_is_checked(self):
        receipt = LearningStateExecutionLearningStateSemanticUseReceiptService().receive(
            self.handoff, receipt_id="semantic-use-receipt-148", recipient_id="downstream-recipient-1",
            receipt_purpose="acknowledge downstream receipt", receipt_rationale={"reason": "explicit receipt"},
        )
        lineage = dict(receipt.lineage); lineage["integrity_id"] = "tampered-integrity"
        result = self._consume(receipt.__class__(**{**receipt.__dict__, "lineage": lineage}))
        self.assertIn("integrity lineage mismatch", result.reasons)

    def test_validation_lineage_is_checked(self):
        receipt = LearningStateExecutionLearningStateSemanticUseReceiptService().receive(
            self.handoff, receipt_id="semantic-use-receipt-148", recipient_id="downstream-recipient-1",
            receipt_purpose="acknowledge downstream receipt", receipt_rationale={"reason": "explicit receipt"},
        )
        lineage = dict(receipt.lineage); lineage["validation_id"] = "tampered-validation"
        result = self._consume(receipt.__class__(**{**receipt.__dict__, "lineage": lineage}))
        self.assertIn("validation lineage mismatch", result.reasons)

    def test_semantic_use_lineage_is_checked(self):
        receipt = LearningStateExecutionLearningStateSemanticUseReceiptService().receive(
            self.handoff, receipt_id="semantic-use-receipt-148", recipient_id="downstream-recipient-1",
            receipt_purpose="acknowledge downstream receipt", receipt_rationale={"reason": "explicit receipt"},
        )
        lineage = dict(receipt.lineage); lineage["semantic_use_id"] = "tampered-semantic-use"
        result = self._consume(receipt.__class__(**{**receipt.__dict__, "lineage": lineage}))
        self.assertIn("semantic-use lineage mismatch", result.reasons)

    def test_source_request_lineage_is_checked(self):
        receipt = LearningStateExecutionLearningStateSemanticUseReceiptService().receive(
            self.handoff, receipt_id="semantic-use-receipt-148", recipient_id="downstream-recipient-1",
            receipt_purpose="acknowledge downstream receipt", receipt_rationale={"reason": "explicit receipt"},
        )
        lineage = dict(receipt.lineage); lineage["request_id"] = "tampered-request"
        result = self._consume(receipt.__class__(**{**receipt.__dict__, "lineage": lineage}))
        self.assertIn("source request lineage mismatch", result.reasons)

    def test_source_validation_lineage_is_checked(self):
        receipt = LearningStateExecutionLearningStateSemanticUseReceiptService().receive(
            self.handoff, receipt_id="semantic-use-receipt-148", recipient_id="downstream-recipient-1",
            receipt_purpose="acknowledge downstream receipt", receipt_rationale={"reason": "explicit receipt"},
        )
        lineage = dict(receipt.lineage); lineage["source_validation_id"] = "tampered-source-validation"
        result = self._consume(receipt.__class__(**{**receipt.__dict__, "lineage": lineage}))
        self.assertIn("source validation lineage mismatch", result.reasons)

    def test_interpretation_lineage_is_checked(self):
        receipt = LearningStateExecutionLearningStateSemanticUseReceiptService().receive(
            self.handoff, receipt_id="semantic-use-receipt-148", recipient_id="downstream-recipient-1",
            receipt_purpose="acknowledge downstream receipt", receipt_rationale={"reason": "explicit receipt"},
        )
        lineage = dict(receipt.lineage); lineage["interpretation_id"] = "tampered-interpretation"
        result = self._consume(receipt.__class__(**{**receipt.__dict__, "lineage": lineage}))
        self.assertIn("interpretation lineage mismatch", result.reasons)

    def test_inherited_provenance_is_checked(self):
        receipt = LearningStateExecutionLearningStateSemanticUseReceiptService().receive(
            self.handoff, receipt_id="semantic-use-receipt-148", recipient_id="downstream-recipient-1",
            receipt_purpose="acknowledge downstream receipt", receipt_rationale={"reason": "explicit receipt"},
        )
        lineage = dict(receipt.lineage)
        lineage.update({
            "source_request_id": "tampered-source-request",
            "source_validation_provenance_id": "tampered-source-validation",
            "read_id": "tampered-read",
            "consumption_request_id": "tampered-consumption",
        })
        result = self._consume(receipt.__class__(**{**receipt.__dict__, "lineage": lineage}))
        self.assertIn("source request provenance mismatch", result.reasons)
        self.assertIn("source validation provenance mismatch", result.reasons)
        self.assertIn("read lineage mismatch", result.reasons)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_payload_is_bounded(self):
        result = self._consume()
        self.assertEqual(dict(result.payload), {"receipt_id": self.handoff.handoff_id if False else "semantic-use-receipt-148", "consumer_id": "downstream-consumer-1"})

    def test_payload_is_recursively_immutable(self):
        result = self._consume()
        self.assertIsInstance(result.payload, MappingProxyType)
        with self.assertRaises(TypeError):
            result.payload["consumer_id"] = "changed"

    def test_source_receipt_is_not_mutated(self):
        receipt = LearningStateExecutionLearningStateSemanticUseReceiptService().receive(
            self.handoff, receipt_id="semantic-use-receipt-148", recipient_id="downstream-recipient-1",
            receipt_purpose="acknowledge downstream receipt", receipt_rationale={"reason": "explicit receipt"},
        )
        before = dict(receipt.lineage)
        self._consume(receipt)
        self.assertEqual(dict(receipt.lineage), before)

    def test_explicit_reasons_are_preserved(self):
        result = self._consume(reasons=("operator requested bounded consumption",))
        self.assertEqual(result.reasons, ("operator requested bounded consumption",))

    def test_consumption_has_no_truth_learning_authority_or_execution_power(self):
        result = self._consume()
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
