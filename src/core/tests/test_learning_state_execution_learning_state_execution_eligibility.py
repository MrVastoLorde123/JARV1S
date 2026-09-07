"""Focused M23.151 tests for execution eligibility."""
from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_downstream_semantic_handling import (
    LearningStateExecutionLearningStateDownstreamSemanticHandlingService,
)
from src.core.learning_state_execution_learning_state_semantic_use_consumption import (
    LearningStateExecutionLearningStateSemanticUseConsumptionService,
)
from src.core.learning_state_execution_learning_state_semantic_use_receipt import (
    LearningStateExecutionLearningStateSemanticUseReceiptService,
)
from src.core.learning_state_execution_learning_state_semantic_use_handoff import (
    LearningStateExecutionLearningStateSemanticUseHandoffService,
)
from src.core.learning_state_execution_learning_state_semantic_use_validation_integrity import (
    LearningStateExecutionLearningStateSemanticUseValidationIntegrityService,
)
from src.core.learning_state_execution_learning_state_semantic_use_validation import (
    LearningStateExecutionLearningStateSemanticUseValidationService,
)
from src.core.learning_state_execution_learning_state_semantic_use import (
    LearningStateExecutionLearningStateSemanticUseService,
)
from src.core.learning_state_execution_learning_state_semantic_use_request import (
    LearningStateExecutionLearningStateSemanticUseRequest,
    LearningStateExecutionLearningStateSemanticUseRequestStatus,
)
from src.core.learning_state_execution_learning_state_downstream_semantic_handling import (
    LearningStateExecutionLearningStateDownstreamSemanticHandling,
    LearningStateExecutionLearningStateDownstreamSemanticHandlingStatus,
)
from src.core.learning_state_execution_learning_state_semantic_use_consumption import (
    LearningStateExecutionLearningStateSemanticUseConsumption,
)
from src.core.learning_state_execution_learning_state_semantic_use_receipt import (
    LearningStateExecutionLearningStateSemanticUseReceipt,
)
from src.core.learning_state_execution_learning_state_semantic_use_handoff import (
    LearningStateExecutionLearningStateSemanticUseHandoff,
)
from src.core.learning_state_execution_learning_state_semantic_use_validation import (
    LearningStateExecutionLearningStateSemanticUseValidationStatus,
)
from src.core.learning_state_execution_learning_state_semantic_use_validation_integrity import (
    LearningStateExecutionLearningStateSemanticUseValidationIntegrityStatus,
)
from src.core.learning_state_execution_learning_state_execution_eligibility import (
    LearningStateExecutionEligibility,
    LearningStateExecutionEligibilityService,
    LearningStateExecutionEligibilityStatus,
)


class M23_151ExecutionEligibilityTests(unittest.TestCase):
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
            receipt_purpose="acknowledge downstream handoff",
            receipt_rationale={"reason": "explicit receipt boundary"},
        )
        consumption = LearningStateExecutionLearningStateSemanticUseConsumptionService().consume(
            receipt,
            consumption_id="semantic-use-consumption-149",
            consumer_id="downstream-consumer-1",
            consumption_purpose="consume received semantic use downstream",
            consumption_rationale={"reason": "explicit consumption boundary"},
        )
        self.handling = LearningStateExecutionLearningStateDownstreamSemanticHandlingService().handle(
            consumption,
            handling_id="downstream-semantic-handling-150",
            handling_target_id="execution-context-1",
            handling_purpose="prepare bounded context for execution eligibility",
            handling_rationale={"reason": "explicit eligibility consideration"},
        )

    def _evaluate(self, handling=None, **kwargs):
        params = {
            "eligibility_id": "execution-eligibility-151",
            "execution_target_id": "executor-1",
            "eligibility_purpose": "determine bounded eligibility for later admission",
            "eligibility_rationale": {"reason": "explicit structural preconditions"},
        }
        params.update(kwargs)
        return LearningStateExecutionEligibilityService().evaluate(
            handling or self.handling,
            **params,
        )

    def test_exact_handling_type_is_required(self):
        with self.assertRaises(TypeError):
            self._evaluate(object())

    def test_handled_produces_eligible(self):
        result = self._evaluate()
        self.assertIsInstance(result, LearningStateExecutionEligibility)
        self.assertEqual(result.status, LearningStateExecutionEligibilityStatus.ELIGIBLE)
        self.assertTrue(result.is_eligible)

    def test_rejected_handling_fails_closed(self):
        rejected = self.handling.__class__(
            **{**self.handling.__dict__, "status": self.handling.status.__class__.REJECTED}
        )
        result = self._evaluate(rejected)
        self.assertTrue(result.is_ineligible)
        self.assertIn("downstream semantic handling status must be HANDLED", result.reasons)

    def test_eligibility_identity_must_be_distinct(self):
        result = self._evaluate(eligibility_id=self.handling.handling_id)
        self.assertTrue(result.is_ineligible)
        self.assertIn("eligibility identity must be distinct", result.reasons)

    def test_different_eligibility_identities_remain_distinct(self):
        first = self._evaluate(eligibility_id="execution-eligibility-151-a")
        second = self._evaluate(eligibility_id="execution-eligibility-151-b")
        self.assertNotEqual(first.eligibility_id, second.eligibility_id)
        self.assertEqual(first.handling_id, second.handling_id)

    def test_execution_target_is_required(self):
        with self.assertRaises(ValueError):
            self._evaluate(execution_target_id=" ")

    def test_eligibility_purpose_is_required(self):
        with self.assertRaises(ValueError):
            self._evaluate(eligibility_purpose="")

    def test_eligibility_rationale_is_required(self):
        with self.assertRaises(ValueError):
            self._evaluate(eligibility_rationale=None)

    def test_handling_lineage_is_checked(self):
        lineage = dict(self.handling.lineage)
        lineage["handling_id"] = "tampered-handling"
        source = self.handling.__class__(**{**self.handling.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("handling lineage mismatch", result.reasons)

    def test_consumption_lineage_is_checked(self):
        lineage = dict(self.handling.lineage)
        lineage["consumption_id"] = "tampered-consumption"
        source = self.handling.__class__(**{**self.handling.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("consumption lineage mismatch", result.reasons)

    def test_receipt_lineage_is_checked(self):
        lineage = dict(self.handling.lineage)
        lineage["receipt_id"] = "tampered-receipt"
        source = self.handling.__class__(**{**self.handling.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("receipt lineage mismatch", result.reasons)

    def test_handoff_lineage_is_checked(self):
        lineage = dict(self.handling.lineage)
        lineage["handoff_id"] = "tampered-handoff"
        source = self.handling.__class__(**{**self.handling.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("handoff lineage mismatch", result.reasons)

    def test_integrity_lineage_is_checked(self):
        lineage = dict(self.handling.lineage)
        lineage["integrity_id"] = "tampered-integrity"
        source = self.handling.__class__(**{**self.handling.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("integrity lineage mismatch", result.reasons)

    def test_validation_lineage_is_checked(self):
        lineage = dict(self.handling.lineage)
        lineage["validation_id"] = "tampered-validation"
        source = self.handling.__class__(**{**self.handling.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("validation lineage mismatch", result.reasons)

    def test_semantic_use_lineage_is_checked(self):
        lineage = dict(self.handling.lineage)
        lineage["semantic_use_id"] = "tampered-semantic-use"
        source = self.handling.__class__(**{**self.handling.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("semantic-use lineage mismatch", result.reasons)

    def test_source_request_lineage_is_checked(self):
        lineage = dict(self.handling.lineage)
        lineage["request_id"] = "tampered-request"
        source = self.handling.__class__(**{**self.handling.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("source request lineage mismatch", result.reasons)

    def test_source_validation_lineage_is_checked(self):
        lineage = dict(self.handling.lineage)
        lineage["source_validation_id"] = "tampered-source-validation"
        source = self.handling.__class__(**{**self.handling.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("source validation lineage mismatch", result.reasons)

    def test_interpretation_lineage_is_checked(self):
        lineage = dict(self.handling.lineage)
        lineage["interpretation_id"] = "tampered-interpretation"
        source = self.handling.__class__(**{**self.handling.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("interpretation lineage mismatch", result.reasons)

    def test_inherited_provenance_is_checked(self):
        lineage = dict(self.handling.lineage)
        lineage["source_request_id"] = "tampered-source-request"
        lineage["source_validation_provenance_id"] = "tampered-source-validation"
        lineage["read_id"] = "tampered-read"
        lineage["consumption_request_id"] = "tampered-consumption-request"
        source = self.handling.__class__(**{**self.handling.__dict__, "lineage": lineage})
        result = self._evaluate(source)
        self.assertIn("source request provenance mismatch", result.reasons)
        self.assertIn("source validation provenance mismatch", result.reasons)
        self.assertIn("read lineage mismatch", result.reasons)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_payload_is_bounded(self):
        result = self._evaluate()
        self.assertEqual(
            dict(result.payload),
            {
                "handling_id": self.handling.handling_id,
                "execution_target_id": "executor-1",
            },
        )

    def test_payload_is_recursively_immutable(self):
        result = self._evaluate()
        self.assertIsInstance(result.payload, MappingProxyType)
        with self.assertRaises(TypeError):
            result.payload["execution_target_id"] = "changed"

    def test_source_handling_is_not_mutated(self):
        before = dict(self.handling.lineage)
        self._evaluate()
        self.assertEqual(dict(self.handling.lineage), before)

    def test_explicit_reasons_are_preserved(self):
        result = self._evaluate(reasons=("operator requested eligibility evaluation",))
        self.assertEqual(result.reasons, ("operator requested eligibility evaluation",))

    def test_eligibility_has_no_truth_learning_authority_or_execution_power(self):
        result = self._evaluate()
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
