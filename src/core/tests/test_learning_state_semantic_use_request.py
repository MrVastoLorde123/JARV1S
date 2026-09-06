import unittest

from src.core.learning_state_interpretation_validation import LearningStateInterpretationValidationStatus
from src.core.learning_state_interpretation_validation_integrity import (
    LearningStateInterpretationValidationIntegrityStatus,
    LearningStateInterpretationValidationIntegrity,
)
from src.core.learning_state_semantic_use_request import (
    LearningStateSemanticUseRequestError,
    LearningStateSemanticUseRequestService,
    LearningStateSemanticUseRequestStatus,
)


class M23_111SemanticUseRequestTests(unittest.TestCase):
    def _integrity(self, *, valid=True, interpretation=None):
        return LearningStateInterpretationValidationIntegrity(
            integrity_id="integrity-110",
            validation_id="validation-109",
            interpretation_id="interpretation-108",
            request_id="request-107",
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
            validation_status=LearningStateInterpretationValidationStatus.ACCEPTED if valid else LearningStateInterpretationValidationStatus.REJECTED,
            integrity_status=LearningStateInterpretationValidationIntegrityStatus.VALID if valid else LearningStateInterpretationValidationIntegrityStatus.INVALID,
            interpretation=interpretation if interpretation is not None else ({"meaning": "unchanged", "nested": {"score": 3}} if valid else {"meaning": "rejected"}),
            failure_reason=None if valid else "rejected",
            reasons={"source": "test"},
            lineage={"test": "m23.111"},
        )

    def test_valid_integrity_produces_ready_request(self):
        result = LearningStateSemanticUseRequestService().request(
            self._integrity(), request_id="semantic-use-111", consumer_id="consumer-A", use_purpose="downstream-semantic-use"
        )
        self.assertEqual(result.request_status, LearningStateSemanticUseRequestStatus.READY)
        self.assertTrue(result.is_ready)

    def test_invalid_integrity_is_rejected(self):
        with self.assertRaises(LearningStateSemanticUseRequestError):
            LearningStateSemanticUseRequestService().request(
                self._integrity(valid=False), request_id="semantic-use-111", consumer_id="consumer-A", use_purpose="x"
            )

    def test_exact_integrity_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateSemanticUseRequestService().request(object(), request_id="r", consumer_id="c", use_purpose="p")

    def test_request_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseRequestService().request(self._integrity(), request_id=" ", consumer_id="c", use_purpose="p")

    def test_consumer_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseRequestService().request(self._integrity(), request_id="r", consumer_id=" ", use_purpose="p")

    def test_use_purpose_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseRequestService().request(self._integrity(), request_id="r", consumer_id="c", use_purpose=" ")

    def test_provenance_is_preserved(self):
        result = LearningStateSemanticUseRequestService().request(
            self._integrity(), request_id="r", consumer_id="c", use_purpose="p"
        )
        self.assertEqual(result.validation_id, "validation-109")
        self.assertEqual(result.interpretation_id, "interpretation-108")
        self.assertEqual(result.source_request_id, "request-107")
        self.assertEqual(result.transition_id, "transition-98")
        self.assertEqual(result.integrity_id, "integrity-110")

    def test_fingerprints_and_state_are_preserved(self):
        result = LearningStateSemanticUseRequestService().request(
            self._integrity(), request_id="r", consumer_id="c", use_purpose="p"
        )
        self.assertEqual(result.state_key, "demo.state")
        self.assertEqual(result.transition_fingerprint, "a" * 64)
        self.assertEqual(result.source_application_fingerprint, "b" * 64)
        self.assertEqual(result.computed_application_fingerprint, "c" * 64)
        self.assertEqual(result.confidence, 0.91)

    def test_interpretation_is_recursively_frozen(self):
        result = LearningStateSemanticUseRequestService().request(
            self._integrity(), request_id="r", consumer_id="c", use_purpose="p"
        )
        with self.assertRaises(TypeError):
            result.interpretation["meaning"] = "changed"
        with self.assertRaises(TypeError):
            result.interpretation["nested"]["score"] = 4

    def test_reasons_and_lineage_are_frozen(self):
        result = LearningStateSemanticUseRequestService().request(
            self._integrity(), request_id="r", consumer_id="c", use_purpose="p", reasons={"x": {"y": 1}}, lineage={"a": [1, 2]}
        )
        with self.assertRaises(TypeError):
            result.reasons["x"]["y"] = 2
        with self.assertRaises(TypeError):
            result.lineage["a"] = (3,)

    def test_identity_and_use_metadata_are_preserved(self):
        result = LearningStateSemanticUseRequestService().request(
            self._integrity(), request_id="semantic-111", consumer_id="consumer-A", use_purpose="compare-with-current"
        )
        self.assertEqual(result.request_id, "semantic-111")
        self.assertEqual(result.consumer_id, "consumer-A")
        self.assertEqual(result.use_purpose, "compare-with-current")

    def test_request_does_not_interpret(self):
        result = LearningStateSemanticUseRequestService().request(
            self._integrity(interpretation={"raw": {"value": 42}}), request_id="r", consumer_id="c", use_purpose="p"
        )
        self.assertFalse(result.interprets_state)
        self.assertEqual(result.interpretation["raw"]["value"], 42)

    def test_request_does_not_establish_semantic_claims(self):
        result = LearningStateSemanticUseRequestService().request(self._integrity(), request_id="r", consumer_id="c", use_purpose="p")
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.establishes_correctness)
        self.assertFalse(result.establishes_certainty)
        self.assertFalse(result.establishes_usefulness)

    def test_request_has_no_learning_or_authority_powers(self):
        result = LearningStateSemanticUseRequestService().request(self._integrity(), request_id="r", consumer_id="c", use_purpose="p")
        self.assertFalse(result.invokes_interpreter)
        self.assertFalse(result.invokes_learner)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)

    def test_equivalent_requests_are_deterministic(self):
        service = LearningStateSemanticUseRequestService()
        first = service.request(self._integrity(), request_id="r", consumer_id="c", use_purpose="p")
        second = service.request(self._integrity(), request_id="r", consumer_id="c", use_purpose="p")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
