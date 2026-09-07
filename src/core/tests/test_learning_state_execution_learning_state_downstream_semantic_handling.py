"""Focused M23.150 tests for downstream semantic handling."""
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
    LearningStateExecutionLearningStateSemanticUseHandoffService,
)
from src.core.learning_state_execution_learning_state_semantic_use_receipt import (
    LearningStateExecutionLearningStateSemanticUseReceiptService,
)
from src.core.learning_state_execution_learning_state_semantic_use_consumption import (
    LearningStateExecutionLearningStateSemanticUseConsumptionService,
)
from src.core.learning_state_execution_learning_state_downstream_semantic_handling import (
    LearningStateExecutionLearningStateDownstreamSemanticHandling,
    LearningStateExecutionLearningStateDownstreamSemanticHandlingService,
    LearningStateExecutionLearningStateDownstreamSemanticHandlingStatus,
)


class M23_150DownstreamSemanticHandlingTests(unittest.TestCase):
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
        handoff = LearningStateExecutionLearningStateSemanticUseHandoffService().handoff(
            integrity,
            handoff_id="semantic-use-handoff-147",
            handoff_target_id="downstream-consumer-1",
            handoff_purpose="present verified semantic use downstream",
            handoff_rationale={"reason": "explicit downstream boundary"},
        )
        receipt = LearningStateExecutionLearningStateSemanticUseReceiptService().receive(
            handoff,
            receipt_id="semantic-use-receipt-148",
            recipient_id="downstream-recipient-1",
            receipt_purpose="acknowledge downstream receipt",
            receipt_rationale={"reason": "explicit receipt boundary"},
        )
        self.consumption = LearningStateExecutionLearningStateSemanticUseConsumptionService().consume(
            receipt,
            consumption_id="semantic-use-consumption-149",
            consumer_id="downstream-consumer-1",
            consumption_purpose="consume bounded semantic-use evidence",
            consumption_rationale={"reason": "explicit downstream consumption"},
        )

    def _handle(self, consumption=None, **kwargs):
        params = {
            "handling_id": "downstream-semantic-handling-150",
            "handling_target_id": "semantic-context-1",
            "handling_purpose": "prepare bounded downstream semantic context",
            "handling_rationale": {"reason": "explicit semantic handling boundary"},
        }
        params.update(kwargs)
        return LearningStateExecutionLearningStateDownstreamSemanticHandlingService().handle(
            consumption or self.consumption,
            **params,
        )

    def test_exact_consumption_type_is_required(self):
        with self.assertRaises(TypeError):
            self._handle(object())

    def test_consumed_produces_handled(self):
        result = self._handle()
        self.assertIsInstance(result, LearningStateExecutionLearningStateDownstreamSemanticHandling)
        self.assertEqual(result.status, LearningStateExecutionLearningStateDownstreamSemanticHandlingStatus.HANDLED)
        self.assertTrue(result.is_handled)

    def test_rejected_consumption_fails_closed(self):
        invalid = self.consumption.__class__(
            **{**self.consumption.__dict__, "status": self.consumption.status.__class__.REJECTED}
        )
        result = self._handle(invalid)
        self.assertTrue(result.is_rejected)
        self.assertIn("semantic-use consumption status must be CONSUMED", result.reasons)

    def test_handling_identity_must_be_distinct(self):
        result = self._handle(handling_id=self.consumption.consumption_id)
        self.assertTrue(result.is_rejected)
        self.assertIn("handling identity must be distinct", result.reasons)

    def test_different_handling_identities_remain_distinct(self):
        first = self._handle(handling_id="downstream-semantic-handling-150-a")
        second = self._handle(handling_id="downstream-semantic-handling-150-b")
        self.assertNotEqual(first.handling_id, second.handling_id)
        self.assertEqual(first.consumption_id, second.consumption_id)

    def test_handling_target_is_required(self):
        with self.assertRaises(ValueError):
            self._handle(handling_target_id=" ")

    def test_handling_purpose_is_required(self):
        with self.assertRaises(ValueError):
            self._handle(handling_purpose="")

    def test_handling_rationale_is_required(self):
        with self.assertRaises(ValueError):
            self._handle(handling_rationale=None)

    def test_consumption_lineage_is_checked(self):
        lineage = dict(self.consumption.lineage)
        lineage["consumption_id"] = "tampered-consumption"
        source = self.consumption.__class__(**{**self.consumption.__dict__, "lineage": lineage})
        result = self._handle(source)
        self.assertIn("consumption lineage mismatch", result.reasons)

    def test_receipt_lineage_is_checked(self):
        lineage = dict(self.consumption.lineage)
        lineage["receipt_id"] = "tampered-receipt"
        source = self.consumption.__class__(**{**self.consumption.__dict__, "lineage": lineage})
        result = self._handle(source)
        self.assertIn("receipt lineage mismatch", result.reasons)

    def test_handoff_lineage_is_checked(self):
        lineage = dict(self.consumption.lineage)
        lineage["handoff_id"] = "tampered-handoff"
        source = self.consumption.__class__(**{**self.consumption.__dict__, "lineage": lineage})
        result = self._handle(source)
        self.assertIn("handoff lineage mismatch", result.reasons)

    def test_integrity_lineage_is_checked(self):
        lineage = dict(self.consumption.lineage)
        lineage["integrity_id"] = "tampered-integrity"
        source = self.consumption.__class__(**{**self.consumption.__dict__, "lineage": lineage})
        result = self._handle(source)
        self.assertIn("integrity lineage mismatch", result.reasons)

    def test_validation_lineage_is_checked(self):
        lineage = dict(self.consumption.lineage)
        lineage["validation_id"] = "tampered-validation"
        source = self.consumption.__class__(**{**self.consumption.__dict__, "lineage": lineage})
        result = self._handle(source)
        self.assertIn("validation lineage mismatch", result.reasons)

    def test_semantic_use_lineage_is_checked(self):
        lineage = dict(self.consumption.lineage)
        lineage["semantic_use_id"] = "tampered-semantic-use"
        source = self.consumption.__class__(**{**self.consumption.__dict__, "lineage": lineage})
        result = self._handle(source)
        self.assertIn("semantic-use lineage mismatch", result.reasons)

    def test_source_request_lineage_is_checked(self):
        lineage = dict(self.consumption.lineage)
        lineage["request_id"] = "tampered-request"
        source = self.consumption.__class__(**{**self.consumption.__dict__, "lineage": lineage})
        result = self._handle(source)
        self.assertIn("source request lineage mismatch", result.reasons)

    def test_source_validation_lineage_is_checked(self):
        lineage = dict(self.consumption.lineage)
        lineage["source_validation_id"] = "tampered-source-validation"
        source = self.consumption.__class__(**{**self.consumption.__dict__, "lineage": lineage})
        result = self._handle(source)
        self.assertIn("source validation lineage mismatch", result.reasons)

    def test_interpretation_lineage_is_checked(self):
        lineage = dict(self.consumption.lineage)
        lineage["interpretation_id"] = "tampered-interpretation"
        source = self.consumption.__class__(**{**self.consumption.__dict__, "lineage": lineage})
        result = self._handle(source)
        self.assertIn("interpretation lineage mismatch", result.reasons)

    def test_inherited_provenance_is_checked(self):
        lineage = dict(self.consumption.lineage)
        lineage["source_request_id"] = "tampered-source-request"
        lineage["source_validation_provenance_id"] = "tampered-source-validation"
        lineage["read_id"] = "tampered-read"
        lineage["consumption_request_id"] = "tampered-consumption-request"
        source = self.consumption.__class__(**{**self.consumption.__dict__, "lineage": lineage})
        result = self._handle(source)
        self.assertIn("source request provenance mismatch", result.reasons)
        self.assertIn("source validation provenance mismatch", result.reasons)
        self.assertIn("read lineage mismatch", result.reasons)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_payload_is_bounded(self):
        result = self._handle()
        self.assertEqual(
            dict(result.payload),
            {
                "consumption_id": self.consumption.consumption_id,
                "handling_target_id": "semantic-context-1",
            },
        )

    def test_payload_is_recursively_immutable(self):
        result = self._handle()
        self.assertIsInstance(result.payload, MappingProxyType)
        with self.assertRaises(TypeError):
            result.payload["handling_target_id"] = "changed"

    def test_source_consumption_is_not_mutated(self):
        before = dict(self.consumption.lineage)
        self._handle()
        self.assertEqual(dict(self.consumption.lineage), before)

    def test_explicit_reasons_are_preserved(self):
        result = self._handle(reasons=("operator requested bounded semantic handling",))
        self.assertEqual(result.reasons, ("operator requested bounded semantic handling",))

    def test_handling_has_no_truth_learning_authority_or_execution_power(self):
        result = self._handle()
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
