import unittest

from src.core.learning_state_semantic_use import LearningStateSemanticUse, LearningStateSemanticUseStatus
from src.core.learning_state_semantic_use_request import LearningStateSemanticUseRequestStatus
from src.core.learning_state_semantic_use_validation import (
    LearningStateSemanticUseValidationService,
    LearningStateSemanticUseValidationStatus,
)


class M23_113SemanticUseValidationTests(unittest.TestCase):
    def _use(self, *, used=True, result=None):
        return LearningStateSemanticUse(
            use_id="use-112",
            request_id="semantic-use-111",
            integrity_id="integrity-110",
            validation_id="validation-109",
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
            request_status=LearningStateSemanticUseRequestStatus.READY,
            use_status=LearningStateSemanticUseStatus.USED if used else LearningStateSemanticUseStatus.REJECTED,
            result=(result if result is not None else {"output": "opaque", "nested": {"score": 3}}) if used else None,
            failure_reason=None if used else "consumer rejected",
            reasons={"source": "test"},
            lineage={"test": "m23.113"},
        )

    def test_used_result_is_accepted(self):
        result = LearningStateSemanticUseValidationService().validate(self._use(), validation_id="validation-113")
        self.assertEqual(result.validation_status, LearningStateSemanticUseValidationStatus.ACCEPTED)
        self.assertTrue(result.is_accepted)

    def test_rejected_use_is_rejected(self):
        result = LearningStateSemanticUseValidationService().validate(self._use(used=False), validation_id="validation-113")
        self.assertEqual(result.validation_status, LearningStateSemanticUseValidationStatus.REJECTED)
        self.assertFalse(result.is_accepted)

    def test_exact_use_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateSemanticUseValidationService().validate(object(), validation_id="validation-113")

    def test_validation_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseValidationService().validate(self._use(), validation_id=" ")

    def test_provenance_is_preserved(self):
        result = LearningStateSemanticUseValidationService().validate(self._use(), validation_id="validation-113")
        self.assertEqual(result.use_id, "use-112")
        self.assertEqual(result.request_id, "semantic-use-111")
        self.assertEqual(result.integrity_id, "integrity-110")
        self.assertEqual(result.consumer_id, "consumer-A")

    def test_fingerprints_and_state_are_preserved(self):
        result = LearningStateSemanticUseValidationService().validate(self._use(), validation_id="validation-113")
        self.assertEqual(result.state_key, "demo.state")
        self.assertEqual(result.transition_fingerprint, "a" * 64)
        self.assertEqual(result.computed_application_fingerprint, "c" * 64)

    def test_result_is_recursively_frozen(self):
        result = LearningStateSemanticUseValidationService().validate(self._use(), validation_id="validation-113")
        with self.assertRaises(TypeError):
            result.result["nested"]["score"] = 8

    def test_reasons_and_lineage_are_frozen(self):
        result = LearningStateSemanticUseValidationService().validate(
            self._use(), validation_id="validation-113", reasons={"items": [1]}, lineage={"chain": {"step": "use"}}
        )
        with self.assertRaises(TypeError):
            result.reasons["new"] = True
        with self.assertRaises(TypeError):
            result.lineage["chain"]["step"] = "other"

    def test_semantic_values_are_not_inspected(self):
        result = LearningStateSemanticUseValidationService().validate(
            self._use(result={"arbitrary": object(), "nested": [None, {"x": 7}]}), validation_id="validation-113"
        )
        self.assertTrue(result.is_accepted)

    def test_no_semantic_claims_are_established(self):
        result = LearningStateSemanticUseValidationService().validate(self._use(), validation_id="validation-113")
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.establishes_correctness)
        self.assertFalse(result.establishes_certainty)
        self.assertFalse(result.establishes_usefulness)

    def test_no_learning_or_authority_powers(self):
        result = LearningStateSemanticUseValidationService().validate(self._use(), validation_id="validation-113")
        self.assertFalse(result.invokes_consumer)
        self.assertFalse(result.invokes_interpreter)
        self.assertFalse(result.invokes_learner)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)

    def test_validation_does_not_consume_again(self):
        result = LearningStateSemanticUseValidationService().validate(self._use(), validation_id="validation-113")
        self.assertEqual(result.use_id, "use-112")

    def test_equivalent_validation_is_deterministic(self):
        service = LearningStateSemanticUseValidationService()
        a = service.validate(self._use(), validation_id="validation-113")
        b = service.validate(self._use(), validation_id="validation-113")
        self.assertEqual(a, b)

    def test_confidence_is_preserved(self):
        result = LearningStateSemanticUseValidationService().validate(self._use(), validation_id="validation-113")
        self.assertEqual(result.confidence, 0.91)

    def test_use_metadata_is_preserved(self):
        result = LearningStateSemanticUseValidationService().validate(self._use(), validation_id="validation-113")
        self.assertEqual(result.use_purpose, "downstream-semantic-use")
        self.assertEqual(result.result["output"], "opaque")


if __name__ == "__main__":
    unittest.main()
