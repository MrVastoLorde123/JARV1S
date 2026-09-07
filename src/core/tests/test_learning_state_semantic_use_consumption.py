import unittest
from types import MappingProxyType

from src.core.learning_state_semantic_use_handoff import (
    LearningStateSemanticUseHandoff,
    LearningStateSemanticUseHandoffStatus,
)
from src.core.learning_state_semantic_use_receipt import (
    LearningStateSemanticUseReceipt,
    LearningStateSemanticUseReceiptStatus,
)
from src.core.learning_state_semantic_use_consumption import (
    LearningStateSemanticUseConsumptionService,
    LearningStateSemanticUseConsumptionStatus,
)


class M23_117SemanticUseConsumptionTests(unittest.TestCase):
    def _handoff(self, *, handoff_id="handoff-115", recipient="receiver-X"):
        return LearningStateSemanticUseHandoff(
            handoff_id=handoff_id,
            integrity_id="integrity-114",
            validation_id="validation-113",
            use_id="use-112",
            request_id="semantic-use-111",
            interpretation_id="interpretation-108",
            source_request_id="request-107",
            read_validation_id="read-validation-106",
            read_id="read-105",
            consumption_request_id="consumption-104",
            source_validation_id="source-validation-103",
            source_integrity_id="source-integrity-102",
            transition_id="transition-98",
            evidence_id="evidence-97",
            application_id="application-96",
            state_key="demo.state",
            transition_fingerprint="a" * 64,
            source_application_fingerprint="b" * 64,
            computed_application_fingerprint="c" * 64,
            confidence=0.91,
            consumer_id="consumer-A",
            use_purpose="downstream-semantic-use",
            downstream_recipient_id=recipient,
            handoff_status=LearningStateSemanticUseHandoffStatus.READY,
            integrity_status=__import__(
                "src.core.learning_state_semantic_use_validation_integrity",
                fromlist=["LearningStateSemanticUseIntegrityStatus"],
            ).LearningStateSemanticUseIntegrityStatus.VALID,
            result={"output": "opaque", "nested": {"score": 3}},
            reasons={"source": "test"},
            lineage={"test": "m23.115"},
        )

    def _receipt(self, *, handoff_id="handoff-115", integrity_id="integrity-114", recipient="receiver-X"):
        return LearningStateSemanticUseReceipt(
            receipt_id="receipt-116",
            handoff_id=handoff_id,
            integrity_id=integrity_id,
            validation_id="validation-113",
            use_id="use-112",
            request_id="semantic-use-111",
            interpretation_id="interpretation-108",
            source_request_id="request-107",
            read_validation_id="read-validation-106",
            read_id="read-105",
            consumption_request_id="consumption-104",
            source_validation_id="source-validation-103",
            source_integrity_id="source-integrity-102",
            transition_id="transition-98",
            evidence_id="evidence-97",
            application_id="application-96",
            state_key="demo.state",
            transition_fingerprint="a" * 64,
            source_application_fingerprint="b" * 64,
            computed_application_fingerprint="c" * 64,
            confidence=0.91,
            consumer_id="consumer-A",
            use_purpose="downstream-semantic-use",
            downstream_recipient_id=recipient,
            receipt_status=LearningStateSemanticUseReceiptStatus.RECEIVED,
            handoff_status=LearningStateSemanticUseHandoffStatus.READY,
            reasons={"source": "test"},
            lineage={"test": "m23.116"},
        )

    def test_received_handoff_is_consumed(self):
        result = LearningStateSemanticUseConsumptionService().consume(
            self._handoff(), self._receipt(), consumption_id="consumption-117"
        )
        self.assertEqual(result.consumption_status, LearningStateSemanticUseConsumptionStatus.CONSUMED)
        self.assertTrue(result.is_consumed)

    def test_exact_handoff_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateSemanticUseConsumptionService().consume(
                object(), self._receipt(), consumption_id="consumption-117"
            )

    def test_exact_receipt_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateSemanticUseConsumptionService().consume(
                self._handoff(), object(), consumption_id="consumption-117"
            )

    def test_handoff_must_be_ready(self):
        handoff = self._handoff()
        object.__setattr__(handoff, "handoff_status", LearningStateSemanticUseHandoffStatus.REJECTED)
        with self.assertRaises(ValueError):
            LearningStateSemanticUseConsumptionService().consume(
                handoff, self._receipt(), consumption_id="consumption-117"
            )

    def test_receipt_must_be_received(self):
        receipt = self._receipt()
        object.__setattr__(receipt, "receipt_status", LearningStateSemanticUseReceiptStatus.REJECTED)
        with self.assertRaises(ValueError):
            LearningStateSemanticUseConsumptionService().consume(
                self._handoff(), receipt, consumption_id="consumption-117"
            )

    def test_consumption_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseConsumptionService().consume(
                self._handoff(), self._receipt(), consumption_id=" "
            )

    def test_handoff_and_receipt_identity_must_match(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseConsumptionService().consume(
                self._handoff(handoff_id="handoff-A"), self._receipt(handoff_id="handoff-B"), consumption_id="consumption-117"
            )

    def test_integrity_identity_must_match(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseConsumptionService().consume(
                self._handoff(), self._receipt(integrity_id="integrity-other"), consumption_id="consumption-117"
            )

    def test_recipient_identity_must_match(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseConsumptionService().consume(
                self._handoff(recipient="receiver-X"), self._receipt(recipient="receiver-Y"), consumption_id="consumption-117"
            )

    def test_semantic_result_is_read_and_preserved(self):
        result = LearningStateSemanticUseConsumptionService().consume(
            self._handoff(), self._receipt(), consumption_id="consumption-117"
        )
        self.assertTrue(result.reads_semantic_result)
        self.assertEqual(dict(result.result), {"output": "opaque", "nested": {"score": 3}})

    def test_result_is_recursively_frozen(self):
        result = LearningStateSemanticUseConsumptionService().consume(
            self._handoff(), self._receipt(), consumption_id="consumption-117"
        )
        self.assertIsInstance(result.result, MappingProxyType)
        self.assertIsInstance(result.result["nested"], MappingProxyType)
        with self.assertRaises(TypeError):
            result.result["new"] = "value"

    def test_provenance_and_fingerprints_are_preserved(self):
        handoff = self._handoff()
        receipt = self._receipt()
        result = LearningStateSemanticUseConsumptionService().consume(
            handoff, receipt, consumption_id="consumption-117"
        )
        self.assertEqual(result.handoff_id, handoff.handoff_id)
        self.assertEqual(result.receipt_id, receipt.receipt_id)
        self.assertEqual(result.integrity_id, handoff.integrity_id)
        self.assertEqual(result.transition_fingerprint, handoff.transition_fingerprint)
        self.assertEqual(result.computed_application_fingerprint, handoff.computed_application_fingerprint)

    def test_source_artifacts_are_not_mutated(self):
        handoff = self._handoff()
        receipt = self._receipt()
        original = dict(handoff.result)
        LearningStateSemanticUseConsumptionService().consume(
            handoff, receipt, consumption_id="consumption-117"
        )
        self.assertEqual(dict(handoff.result), original)
        self.assertEqual(receipt.handoff_id, "handoff-115")

    def test_deterministic_for_same_inputs(self):
        service = LearningStateSemanticUseConsumptionService()
        first = service.consume(self._handoff(), self._receipt(), consumption_id="consumption-117")
        second = service.consume(self._handoff(), self._receipt(), consumption_id="consumption-117")
        self.assertEqual(first, second)

    def test_consumption_does_not_transform_or_interpret_result(self):
        result = LearningStateSemanticUseConsumptionService().consume(
            self._handoff(), self._receipt(), consumption_id="consumption-117"
        )
        self.assertFalse(result.transforms_semantic_result)
        self.assertFalse(result.interprets_semantic_result)

    def test_consumption_has_no_learning_memory_authority_or_execution_powers(self):
        result = LearningStateSemanticUseConsumptionService().consume(
            self._handoff(), self._receipt(), consumption_id="consumption-117"
        )
        self.assertFalse(result.invokes_learner)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)

    def test_consumption_is_not_semantic_judgment(self):
        result = LearningStateSemanticUseConsumptionService().consume(
            self._handoff(), self._receipt(), consumption_id="consumption-117"
        )
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.establishes_correctness)
        self.assertFalse(result.establishes_certainty)
        self.assertFalse(result.establishes_usefulness)

    def test_reasons_and_lineage_are_frozen(self):
        result = LearningStateSemanticUseConsumptionService().consume(
            self._handoff(), self._receipt(), consumption_id="consumption-117",
            reasons={"boundary": {"stage": "consumption"}},
            lineage={"parent": {"receipt_id": "receipt-116"}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.reasons["boundary"], MappingProxyType)


if __name__ == "__main__":
    unittest.main()
