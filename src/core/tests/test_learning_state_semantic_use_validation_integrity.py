import unittest
from types import MappingProxyType

from src.core.learning_state_semantic_use import LearningStateSemanticUseStatus
from src.core.learning_state_semantic_use_request import LearningStateSemanticUseRequestStatus
from src.core.learning_state_semantic_use_validation import (
    LearningStateSemanticUseValidation,
    LearningStateSemanticUseValidationStatus,
)
from src.core.learning_state_semantic_use_validation_integrity import (
    LearningStateSemanticUseIntegrity,
    LearningStateSemanticUseIntegrityService,
    LearningStateSemanticUseIntegrityStatus,
)


class M23_114SemanticUseIntegrityTests(unittest.TestCase):
    def _validation(self, *, status=LearningStateSemanticUseValidationStatus.ACCEPTED, result=None):
        return LearningStateSemanticUseValidation(
            validation_id="validation-113",
            use_id="use-112",
            request_id="semantic-use-111",
            integrity_id="integrity-110",
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
            use_status=LearningStateSemanticUseStatus.USED,
            result=(result if result is not None else {"output": "opaque", "nested": {"score": 3}}),
            validation_status=status,
            failure_reason=None if status is LearningStateSemanticUseValidationStatus.ACCEPTED else "rejected validation",
            reasons={"source": "test"},
            lineage={"test": "m23.113"},
        )

    def test_accepted_validation_is_valid(self):
        result = LearningStateSemanticUseIntegrityService().validate(self._validation(), integrity_id="integrity-114")
        self.assertEqual(result.integrity_status, LearningStateSemanticUseIntegrityStatus.VALID)
        self.assertTrue(result.is_valid)

    def test_rejected_validation_is_invalid(self):
        result = LearningStateSemanticUseIntegrityService().validate(
            self._validation(status=LearningStateSemanticUseValidationStatus.REJECTED), integrity_id="integrity-114"
        )
        self.assertEqual(result.integrity_status, LearningStateSemanticUseIntegrityStatus.INVALID)
        self.assertIn("ACCEPTED", result.failure_reason)

    def test_exact_validation_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateSemanticUseIntegrityService().validate(object(), integrity_id="integrity-114")

    def test_integrity_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseIntegrityService().validate(self._validation(), integrity_id=" ")

    def test_provenance_and_fingerprints_are_preserved(self):
        source = self._validation()
        result = LearningStateSemanticUseIntegrityService().validate(source, integrity_id="integrity-114")
        for name in (
            "validation_id", "use_id", "request_id", "interpretation_id", "source_request_id",
            "read_validation_id", "read_id", "consumption_request_id", "source_validation_id",
            "transition_id", "evidence_id", "application_id", "state_key",
            "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint",
            "confidence", "consumer_id", "use_purpose",
        ):
            self.assertEqual(getattr(result, name), getattr(source, name))
        self.assertEqual(result.source_integrity_id, source.integrity_id)
        self.assertEqual(result.integrity_id, "integrity-114")

    def test_result_is_recursively_frozen(self):
        result = LearningStateSemanticUseIntegrityService().validate(self._validation(), integrity_id="integrity-114")
        self.assertEqual(result.result, MappingProxyType({"output": "opaque", "nested": MappingProxyType({"score": 3})}))
        with self.assertRaises(TypeError):
            result.result["nested"]["score"] = 8

    def test_reasons_and_lineage_are_frozen(self):
        result = LearningStateSemanticUseIntegrityService().validate(
            self._validation(), integrity_id="integrity-114",
            reasons={"nested": {"ok": True}}, lineage={"chain": ["validation-113"]},
        )
        with self.assertRaises(TypeError):
            result.reasons["new"] = True
        with self.assertRaises(TypeError):
            result.reasons["nested"]["ok"] = False
        self.assertEqual(result.lineage["chain"], ("validation-113",))

    def test_source_validation_is_not_mutated(self):
        source = self._validation()
        before = source.result
        LearningStateSemanticUseIntegrityService().validate(source, integrity_id="integrity-114")
        self.assertEqual(source.result, before)
        self.assertEqual(source.validation_id, "validation-113")

    def test_deterministic_integrity(self):
        service = LearningStateSemanticUseIntegrityService()
        first = service.validate(self._validation(), integrity_id="integrity-114")
        second = service.validate(self._validation(), integrity_id="integrity-114")
        self.assertEqual(first, second)

    def test_semantic_values_are_not_judged(self):
        result = LearningStateSemanticUseIntegrityService().validate(
            self._validation(result={"arbitrary": object(), "meaning": {"anything": [1, 2, 3]}}),
            integrity_id="integrity-114",
        )
        self.assertEqual(result.integrity_status, LearningStateSemanticUseIntegrityStatus.VALID)

    def test_no_truth_correctness_certainty_or_usefulness_claims(self):
        result = LearningStateSemanticUseIntegrityService().validate(self._validation(), integrity_id="integrity-114")
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.establishes_correctness)
        self.assertFalse(result.establishes_certainty)
        self.assertFalse(result.establishes_usefulness)

    def test_no_learning_authority_or_execution_powers(self):
        result = LearningStateSemanticUseIntegrityService().validate(self._validation(), integrity_id="integrity-114")
        self.assertFalse(result.invokes_consumer)
        self.assertFalse(result.invokes_interpreter)
        self.assertFalse(result.invokes_learner)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)

    def test_invalid_integrity_requires_failure_reason(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseIntegrity(
                integrity_id="integrity-114",
                validation_id="validation-113",
                use_id="use-112",
                request_id="semantic-use-111",
                source_integrity_id="integrity-110",
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
                request_status=LearningStateSemanticUseRequestStatus.READY,
                use_status=LearningStateSemanticUseStatus.REJECTED,
                validation_status=LearningStateSemanticUseValidationStatus.REJECTED,
                integrity_status=LearningStateSemanticUseIntegrityStatus.INVALID,
                result=None,
                failure_reason=None,
                reasons={},
                lineage={},
            )

    def test_wrong_integrity_status_type_fails_closed(self):
        source = self._validation()
        with self.assertRaises(TypeError):
            LearningStateSemanticUseIntegrity(
                integrity_id="integrity-114", validation_id=source.validation_id, use_id=source.use_id,
                request_id=source.request_id, source_integrity_id=source.integrity_id,
                interpretation_id=source.interpretation_id, source_request_id=source.source_request_id,
                read_validation_id=source.read_validation_id, read_id=source.read_id,
                consumption_request_id=source.consumption_request_id, source_validation_id=source.source_validation_id,
                transition_id=source.transition_id, evidence_id=source.evidence_id, application_id=source.application_id,
                state_key=source.state_key, transition_fingerprint=source.transition_fingerprint,
                source_application_fingerprint=source.source_application_fingerprint,
                computed_application_fingerprint=source.computed_application_fingerprint, confidence=source.confidence,
                consumer_id=source.consumer_id, use_purpose=source.use_purpose,
                request_status=source.request_status, use_status=source.use_status,
                validation_status=source.validation_status, integrity_status="VALID", result=source.result,
                failure_reason=None, reasons={}, lineage={},
            )

    def test_non_sha256_fingerprint_fails_closed(self):
        source = self._validation()
        with self.assertRaises(ValueError):
            LearningStateSemanticUseIntegrity(
                integrity_id="integrity-114", validation_id=source.validation_id, use_id=source.use_id,
                request_id=source.request_id, source_integrity_id=source.integrity_id,
                interpretation_id=source.interpretation_id, source_request_id=source.source_request_id,
                read_validation_id=source.read_validation_id, read_id=source.read_id,
                consumption_request_id=source.consumption_request_id, source_validation_id=source.source_validation_id,
                transition_id=source.transition_id, evidence_id=source.evidence_id, application_id=source.application_id,
                state_key=source.state_key, transition_fingerprint="bad",
                source_application_fingerprint=source.source_application_fingerprint,
                computed_application_fingerprint=source.computed_application_fingerprint, confidence=source.confidence,
                consumer_id=source.consumer_id, use_purpose=source.use_purpose,
                request_status=source.request_status, use_status=source.use_status,
                validation_status=source.validation_status, integrity_status=LearningStateSemanticUseIntegrityStatus.VALID,
                result=source.result, failure_reason=None, reasons={}, lineage={},
            )

if __name__ == "__main__":
    unittest.main()
