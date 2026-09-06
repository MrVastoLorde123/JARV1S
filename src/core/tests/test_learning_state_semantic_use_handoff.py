import unittest
from types import MappingProxyType

from src.core.learning_state_semantic_use_validation import LearningStateSemanticUseValidationStatus
from src.core.learning_state_semantic_use_validation_integrity import (
    LearningStateSemanticUseIntegrity,
    LearningStateSemanticUseIntegrityStatus,
)
from src.core.learning_state_semantic_use_handoff import (
    LearningStateSemanticUseHandoffService,
    LearningStateSemanticUseHandoffStatus,
)


class M23_115SemanticUseHandoffTests(unittest.TestCase):
    def _integrity(self, *, status=LearningStateSemanticUseIntegrityStatus.VALID):
        return LearningStateSemanticUseIntegrity(
            integrity_id="integrity-114",
            validation_id="validation-113",
            use_id="use-112",
            request_id="semantic-use-111",
            source_integrity_id="source-integrity-110",
            interpretation_id="interpretation-108",
            source_request_id="request-107",
            read_validation_id="read-validation-106",
            read_id="read-105",
            consumption_request_id="consumption-104",
            source_validation_id="source-validation-103",
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
            request_status="READY",
            use_status="USED",
            validation_status=LearningStateSemanticUseValidationStatus.ACCEPTED,
            integrity_status=status,
            result={"output": "opaque", "nested": {"score": 3}},
            failure_reason=None if status is LearningStateSemanticUseIntegrityStatus.VALID else "invalid integrity",
            reasons={"source": "test"},
            lineage={"test": "m23.114"},
        )

    def test_valid_integrity_creates_ready_handoff(self):
        handoff = LearningStateSemanticUseHandoffService().handoff(
            self._integrity(), handoff_id="handoff-115", downstream_recipient_id="receiver-X"
        )
        self.assertEqual(handoff.handoff_status, LearningStateSemanticUseHandoffStatus.READY)
        self.assertTrue(handoff.is_ready)

    def test_invalid_integrity_is_rejected(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseHandoffService().handoff(
                self._integrity(status=LearningStateSemanticUseIntegrityStatus.INVALID),
                handoff_id="handoff-115", downstream_recipient_id="receiver-X",
            )

    def test_exact_integrity_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateSemanticUseHandoffService().handoff(
                object(), handoff_id="handoff-115", downstream_recipient_id="receiver-X"
            )

    def test_handoff_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseHandoffService().handoff(
                self._integrity(), handoff_id=" ", downstream_recipient_id="receiver-X"
            )

    def test_recipient_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseHandoffService().handoff(
                self._integrity(), handoff_id="handoff-115", downstream_recipient_id=""
            )

    def test_provenance_and_fingerprints_are_preserved(self):
        source = self._integrity()
        handoff = LearningStateSemanticUseHandoffService().handoff(
            source, handoff_id="handoff-115", downstream_recipient_id="receiver-X"
        )
        self.assertEqual(handoff.integrity_id, source.integrity_id)
        self.assertEqual(handoff.transition_fingerprint, source.transition_fingerprint)
        self.assertEqual(handoff.computed_application_fingerprint, source.computed_application_fingerprint)
        self.assertEqual(handoff.interpretation_id, source.interpretation_id)

    def test_result_is_recursively_frozen(self):
        handoff = LearningStateSemanticUseHandoffService().handoff(
            self._integrity(), handoff_id="handoff-115", downstream_recipient_id="receiver-X"
        )
        self.assertIsInstance(handoff.result, MappingProxyType)
        self.assertIsInstance(handoff.result["nested"], MappingProxyType)
        with self.assertRaises(TypeError):
            handoff.result["new"] = "value"

    def test_source_is_not_mutated(self):
        source = self._integrity()
        original = source.result
        LearningStateSemanticUseHandoffService().handoff(
            source, handoff_id="handoff-115", downstream_recipient_id="receiver-X"
        )
        self.assertEqual(dict(original), {"output": "opaque", "nested": {"score": 3}})

    def test_deterministic_for_same_inputs(self):
        service = LearningStateSemanticUseHandoffService()
        first = service.handoff(self._integrity(), handoff_id="handoff-115", downstream_recipient_id="receiver-X")
        second = service.handoff(self._integrity(), handoff_id="handoff-115", downstream_recipient_id="receiver-X")
        self.assertEqual(first, second)

    def test_handoff_does_not_invoke_downstream_recipient(self):
        handoff = LearningStateSemanticUseHandoffService().handoff(
            self._integrity(), handoff_id="handoff-115", downstream_recipient_id="receiver-X"
        )
        self.assertFalse(handoff.invokes_downstream_recipient)

    def test_handoff_does_not_transform_semantic_result(self):
        source = self._integrity()
        handoff = LearningStateSemanticUseHandoffService().handoff(
            source, handoff_id="handoff-115", downstream_recipient_id="receiver-X"
        )
        self.assertEqual(dict(handoff.result), dict(source.result))
        self.assertFalse(handoff.transforms_semantic_result)

    def test_handoff_is_not_semantic_judgment(self):
        handoff = LearningStateSemanticUseHandoffService().handoff(
            self._integrity(), handoff_id="handoff-115", downstream_recipient_id="receiver-X"
        )
        self.assertFalse(handoff.establishes_truth)
        self.assertFalse(handoff.establishes_correctness)
        self.assertFalse(handoff.establishes_certainty)
        self.assertFalse(handoff.establishes_usefulness)

    def test_handoff_has_no_learning_powers(self):
        handoff = LearningStateSemanticUseHandoffService().handoff(
            self._integrity(), handoff_id="handoff-115", downstream_recipient_id="receiver-X"
        )
        self.assertFalse(handoff.invokes_learner)
        self.assertFalse(handoff.updates_model)
        self.assertFalse(handoff.mutates_memory)
        self.assertFalse(handoff.mutates_policy)

    def test_handoff_has_no_authority_or_execution_powers(self):
        handoff = LearningStateSemanticUseHandoffService().handoff(
            self._integrity(), handoff_id="handoff-115", downstream_recipient_id="receiver-X"
        )
        self.assertFalse(handoff.grants_authority)
        self.assertFalse(handoff.schedules_work)
        self.assertFalse(handoff.executes_action)

    def test_handoff_preserves_consumer_and_purpose_identity(self):
        handoff = LearningStateSemanticUseHandoffService().handoff(
            self._integrity(), handoff_id="handoff-115", downstream_recipient_id="receiver-X"
        )
        self.assertEqual(handoff.consumer_id, "consumer-A")
        self.assertEqual(handoff.use_purpose, "downstream-semantic-use")
        self.assertEqual(handoff.downstream_recipient_id, "receiver-X")

    def test_reasons_and_lineage_are_frozen(self):
        handoff = LearningStateSemanticUseHandoffService().handoff(
            self._integrity(), handoff_id="handoff-115", downstream_recipient_id="receiver-X",
            reasons={"boundary": {"stage": "handoff"}},
            lineage={"parent": {"integrity_id": "integrity-114"}},
        )
        self.assertIsInstance(handoff.reasons, MappingProxyType)
        self.assertIsInstance(handoff.lineage, MappingProxyType)
        self.assertIsInstance(handoff.reasons["boundary"], MappingProxyType)


if __name__ == "__main__":
    unittest.main()
