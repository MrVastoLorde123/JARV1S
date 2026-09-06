import unittest
from types import MappingProxyType

from src.core.learning_state_semantic_use_handoff import (
    LearningStateSemanticUseHandoff,
    LearningStateSemanticUseHandoffStatus,
)
from src.core.learning_state_semantic_use_receipt import (
    LearningStateSemanticUseReceiptService,
    LearningStateSemanticUseReceiptStatus,
)


class M23_116SemanticUseReceiptTests(unittest.TestCase):
    def _handoff(self, *, status=LearningStateSemanticUseHandoffStatus.READY, recipient="receiver-X"):
        return LearningStateSemanticUseHandoff(
            handoff_id="handoff-115",
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
            handoff_status=status,
            integrity_status=type("IntegrityStatus", (), {"VALID": "VALID"}) if False else __import__(
                "src.core.learning_state_semantic_use_validation_integrity",
                fromlist=["LearningStateSemanticUseIntegrityStatus"],
            ).LearningStateSemanticUseIntegrityStatus.VALID,
            result={"output": "opaque"},
            reasons={"source": "test"},
            lineage={"test": "m23.115"},
        )

    def test_ready_handoff_is_received(self):
        receipt = LearningStateSemanticUseReceiptService().receive(
            self._handoff(), receipt_id="receipt-116", recipient_id="receiver-X"
        )
        self.assertEqual(receipt.receipt_status, LearningStateSemanticUseReceiptStatus.RECEIVED)
        self.assertTrue(receipt.is_received)
        self.assertTrue(receipt.acknowledges_receipt)

    def test_non_ready_handoff_is_rejected(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseReceiptService().receive(
                self._handoff(status=LearningStateSemanticUseHandoffStatus.REJECTED),
                receipt_id="receipt-116", recipient_id="receiver-X",
            )

    def test_exact_handoff_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateSemanticUseReceiptService().receive(
                object(), receipt_id="receipt-116", recipient_id="receiver-X"
            )

    def test_receipt_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseReceiptService().receive(
                self._handoff(), receipt_id=" ", recipient_id="receiver-X"
            )

    def test_recipient_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseReceiptService().receive(
                self._handoff(), receipt_id="receipt-116", recipient_id=""
            )

    def test_recipient_must_match_named_downstream_recipient(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseReceiptService().receive(
                self._handoff(), receipt_id="receipt-116", recipient_id="receiver-Y"
            )

    def test_provenance_and_fingerprints_are_preserved(self):
        handoff = self._handoff()
        receipt = LearningStateSemanticUseReceiptService().receive(
            handoff, receipt_id="receipt-116", recipient_id="receiver-X"
        )
        self.assertEqual(receipt.handoff_id, handoff.handoff_id)
        self.assertEqual(receipt.integrity_id, handoff.integrity_id)
        self.assertEqual(receipt.transition_fingerprint, handoff.transition_fingerprint)
        self.assertEqual(receipt.computed_application_fingerprint, handoff.computed_application_fingerprint)
        self.assertEqual(receipt.interpretation_id, handoff.interpretation_id)

    def test_reasons_and_lineage_are_frozen(self):
        receipt = LearningStateSemanticUseReceiptService().receive(
            self._handoff(), receipt_id="receipt-116", recipient_id="receiver-X",
            reasons={"boundary": {"stage": "receipt"}},
            lineage={"parent": {"handoff_id": "handoff-115"}},
        )
        self.assertIsInstance(receipt.reasons, MappingProxyType)
        self.assertIsInstance(receipt.lineage, MappingProxyType)
        self.assertIsInstance(receipt.reasons["boundary"], MappingProxyType)

    def test_deterministic_for_same_inputs(self):
        service = LearningStateSemanticUseReceiptService()
        first = service.receive(self._handoff(), receipt_id="receipt-116", recipient_id="receiver-X")
        second = service.receive(self._handoff(), receipt_id="receipt-116", recipient_id="receiver-X")
        self.assertEqual(first, second)

    def test_receipt_does_not_read_semantic_result(self):
        receipt = LearningStateSemanticUseReceiptService().receive(
            self._handoff(), receipt_id="receipt-116", recipient_id="receiver-X"
        )
        self.assertFalse(receipt.reads_semantic_result)

    def test_receipt_does_not_transform_semantic_result(self):
        receipt = LearningStateSemanticUseReceiptService().receive(
            self._handoff(), receipt_id="receipt-116", recipient_id="receiver-X"
        )
        self.assertFalse(receipt.transforms_semantic_result)

    def test_receipt_does_not_invoke_recipient(self):
        receipt = LearningStateSemanticUseReceiptService().receive(
            self._handoff(), receipt_id="receipt-116", recipient_id="receiver-X"
        )
        self.assertFalse(receipt.invokes_downstream_recipient)

    def test_receipt_is_not_semantic_judgment(self):
        receipt = LearningStateSemanticUseReceiptService().receive(
            self._handoff(), receipt_id="receipt-116", recipient_id="receiver-X"
        )
        self.assertFalse(receipt.establishes_truth)
        self.assertFalse(receipt.establishes_correctness)
        self.assertFalse(receipt.establishes_certainty)
        self.assertFalse(receipt.establishes_usefulness)

    def test_receipt_has_no_learning_powers(self):
        receipt = LearningStateSemanticUseReceiptService().receive(
            self._handoff(), receipt_id="receipt-116", recipient_id="receiver-X"
        )
        self.assertFalse(receipt.invokes_learner)
        self.assertFalse(receipt.updates_model)
        self.assertFalse(receipt.mutates_memory)
        self.assertFalse(receipt.mutates_policy)

    def test_receipt_has_no_authority_or_execution_powers(self):
        receipt = LearningStateSemanticUseReceiptService().receive(
            self._handoff(), receipt_id="receipt-116", recipient_id="receiver-X"
        )
        self.assertFalse(receipt.grants_authority)
        self.assertFalse(receipt.schedules_work)
        self.assertFalse(receipt.executes_action)

    def test_receipt_has_no_semantic_result_field(self):
        receipt = LearningStateSemanticUseReceiptService().receive(
            self._handoff(), receipt_id="receipt-116", recipient_id="receiver-X"
        )
        self.assertFalse(hasattr(receipt, "result"))


if __name__ == "__main__":
    unittest.main()
