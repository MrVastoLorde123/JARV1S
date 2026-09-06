import unittest
from types import MappingProxyType

from src.core.learning_state_interpretation import LearningStateInterpretation, LearningStateInterpretationStatus
from src.core.learning_state_interpretation_validation import LearningStateInterpretationValidation, LearningStateInterpretationValidationStatus
from src.core.learning_state_interpretation_validation_integrity import (
    LearningStateInterpretationValidationIntegrityService,
    LearningStateInterpretationValidationIntegrityStatus,
)


class LearningStateInterpretationValidationIntegrityTests(unittest.TestCase):
    def _interpretation(self, *, status=LearningStateInterpretationStatus.INTERPRETED):
        return LearningStateInterpretation(
            interpretation_id="interpretation-108",
            request_id="interpret-request-107",
            read_validation_id="validation-106",
            read_id="read-105",
            consumption_request_id="request-104",
            source_validation_id="validation-source",
            integrity_id="integrity-99",
            transition_id="transition-98",
            evidence_id="evidence-97",
            application_id="application-96",
            state_key="learning-state",
            transition_fingerprint="a" * 64,
            source_application_fingerprint="b" * 64,
            computed_application_fingerprint="c" * 64,
            confidence=0.8,
            interpretation_status=status,
            interpretation={"trend": {"direction": "rising"}, "count": 3},
            failure_reason=None if status is LearningStateInterpretationStatus.INTERPRETED else "rejected interpretation",
            reasons={"interpretation_status": status.value},
            lineage={"interpretation_id": "interpretation-108"},
        )

    def _validation(self, *, status=LearningStateInterpretationValidationStatus.ACCEPTED, interpretation=None):
        source = self._interpretation()
        return LearningStateInterpretationValidation(
            validation_id="validation-109",
            interpretation_id=source.interpretation_id,
            request_id=source.request_id,
            read_validation_id=source.read_validation_id,
            read_id=source.read_id,
            consumption_request_id=source.consumption_request_id,
            source_validation_id=source.source_validation_id,
            integrity_id=source.integrity_id,
            transition_id=source.transition_id,
            evidence_id=source.evidence_id,
            application_id=source.application_id,
            state_key=source.state_key,
            transition_fingerprint=source.transition_fingerprint,
            source_application_fingerprint=source.source_application_fingerprint,
            computed_application_fingerprint=source.computed_application_fingerprint,
            confidence=source.confidence,
            interpretation_status=source.interpretation_status,
            interpretation=source.interpretation if interpretation is None else interpretation,
            validation_status=status,
            failure_reason=None if status is LearningStateInterpretationValidationStatus.ACCEPTED else "rejected validation",
            reasons={"validation_status": status.value},
            lineage={"validation_id": "validation-109"},
        )

    def test_accepted_validation_is_valid(self):
        result = LearningStateInterpretationValidationIntegrityService().validate(self._validation(), integrity_id="integrity-110")
        self.assertEqual(result.integrity_status, LearningStateInterpretationValidationIntegrityStatus.VALID)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.interpretation, MappingProxyType({"trend": MappingProxyType({"direction": "rising"}), "count": 3}))

    def test_rejected_validation_is_invalid(self):
        result = LearningStateInterpretationValidationIntegrityService().validate(
            self._validation(status=LearningStateInterpretationValidationStatus.REJECTED), integrity_id="integrity-110"
        )
        self.assertEqual(result.integrity_status, LearningStateInterpretationValidationIntegrityStatus.INVALID)
        self.assertIn("ACCEPTED", result.failure_reason)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            LearningStateInterpretationValidationIntegrityService().validate(object(), integrity_id="integrity-110")

    def test_blank_integrity_id_fails_closed(self):
        with self.assertRaises(ValueError):
            LearningStateInterpretationValidationIntegrityService().validate(self._validation(), integrity_id=" ")

    def test_provenance_and_fingerprints_are_preserved(self):
        source = self._validation()
        result = LearningStateInterpretationValidationIntegrityService().validate(source, integrity_id="integrity-110")
        for name in (
            "validation_id", "interpretation_id", "request_id", "read_validation_id", "read_id",
            "consumption_request_id", "source_validation_id", "source_integrity_id", "transition_id",
            "evidence_id", "application_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint", "confidence",
        ):
            expected = source.integrity_id if name == "source_integrity_id" else getattr(source, name)
            self.assertEqual(getattr(result, name), expected)
        self.assertEqual(result.integrity_id, "integrity-110")

    def test_interpretation_is_preserved_and_immutable(self):
        result = LearningStateInterpretationValidationIntegrityService().validate(self._validation(), integrity_id="integrity-110")
        with self.assertRaises(TypeError):
            result.interpretation["x"] = True
        with self.assertRaises(TypeError):
            result.interpretation["trend"]["direction"] = "falling"

    def test_source_validation_is_not_mutated(self):
        source = self._validation()
        before = source.interpretation
        LearningStateInterpretationValidationIntegrityService().validate(source, integrity_id="integrity-110")
        self.assertEqual(source.interpretation, before)
        self.assertEqual(source.validation_id, "validation-109")

    def test_reasons_and_lineage_are_immutable(self):
        result = LearningStateInterpretationValidationIntegrityService().validate(
            self._validation(),
            integrity_id="integrity-110",
            reasons={"nested": {"ok": True}},
            lineage={"nested": ["validation-109"]},
        )
        with self.assertRaises(TypeError):
            result.reasons["x"] = 1
        with self.assertRaises(TypeError):
            result.reasons["nested"]["ok"] = False
        self.assertEqual(result.lineage["nested"], ("validation-109",))

    def test_result_is_immutable(self):
        result = LearningStateInterpretationValidationIntegrityService().validate(self._validation(), integrity_id="integrity-110")
        with self.assertRaises(Exception):
            result.integrity_id = "changed"

    def test_deterministic_validation(self):
        service = LearningStateInterpretationValidationIntegrityService()
        first = service.validate(self._validation(), integrity_id="integrity-110")
        second = service.validate(self._validation(), integrity_id="integrity-110")
        self.assertEqual(first, second)

    def test_validation_does_not_judge_semantic_content(self):
        weird = {"completely": {"unknown": object()}}
        result = LearningStateInterpretationValidationIntegrityService().validate(self._validation(interpretation=weird), integrity_id="integrity-110")
        self.assertEqual(result.integrity_status, LearningStateInterpretationValidationIntegrityStatus.VALID)

    def test_integrity_declares_no_truth_correctness_or_authority(self):
        result = LearningStateInterpretationValidationIntegrityService().validate(self._validation(), integrity_id="integrity-110")
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.establishes_correctness)
        self.assertFalse(result.establishes_certainty)
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
            from src.core.learning_state_interpretation_validation_integrity import LearningStateInterpretationValidationIntegrity
            LearningStateInterpretationValidationIntegrity(
                integrity_id="integrity-110",
                validation_id="validation-109",
                interpretation_id="interpretation-108",
                request_id="interpret-request-107",
                read_validation_id="validation-106",
                read_id="read-105",
                consumption_request_id="request-104",
                source_validation_id="validation-source",
                source_integrity_id="integrity-99",
                transition_id="transition-98",
                evidence_id="evidence-97",
                application_id="application-96",
                state_key="learning-state",
                transition_fingerprint="a" * 64,
                source_application_fingerprint="b" * 64,
                computed_application_fingerprint="c" * 64,
                confidence=0.8,
                validation_status=LearningStateInterpretationValidationStatus.REJECTED,
                integrity_status=LearningStateInterpretationValidationIntegrityStatus.INVALID,
                interpretation=None,
                failure_reason=None,
                reasons={},
                lineage={},
            )

    def test_wrong_status_type_fails_closed(self):
        validation = self._validation()
        from src.core.learning_state_interpretation_validation_integrity import LearningStateInterpretationValidationIntegrity
        with self.assertRaises(TypeError):
            LearningStateInterpretationValidationIntegrity(
                integrity_id="integrity-110", validation_id=validation.validation_id,
                interpretation_id=validation.interpretation_id, request_id=validation.request_id,
                read_validation_id=validation.read_validation_id, read_id=validation.read_id,
                consumption_request_id=validation.consumption_request_id, source_validation_id=validation.source_validation_id,
                source_integrity_id=validation.integrity_id, transition_id=validation.transition_id,
                evidence_id=validation.evidence_id, application_id=validation.application_id,
                state_key=validation.state_key, transition_fingerprint=validation.transition_fingerprint,
                source_application_fingerprint=validation.source_application_fingerprint,
                computed_application_fingerprint=validation.computed_application_fingerprint,
                confidence=validation.confidence, validation_status=validation.validation_status,
                integrity_status="VALID", interpretation=validation.interpretation,
                failure_reason=None, reasons={}, lineage={},
            )

    def test_missing_interpretation_fails_closed_for_accepted_source(self):
        from src.core.learning_state_interpretation_validation_integrity import LearningStateInterpretationValidationIntegrity
        with self.assertRaises(TypeError):
            LearningStateInterpretationValidationIntegrity(
                integrity_id="integrity-110", validation_id="validation-109", interpretation_id="interpretation-108",
                request_id="interpret-request-107", read_validation_id="validation-106", read_id="read-105",
                consumption_request_id="request-104", source_validation_id="validation-source", source_integrity_id="integrity-99",
                transition_id="transition-98", evidence_id="evidence-97", application_id="application-96", state_key="learning-state",
                transition_fingerprint="a" * 64, source_application_fingerprint="b" * 64, computed_application_fingerprint="c" * 64,
                confidence=0.8, validation_status=LearningStateInterpretationValidationStatus.ACCEPTED,
                integrity_status=LearningStateInterpretationValidationIntegrityStatus.VALID,
                interpretation=None, failure_reason=None, reasons={}, lineage={},
            )

    def test_custom_reasons_and_lineage_are_preserved(self):
        result = LearningStateInterpretationValidationIntegrityService().validate(
            self._validation(), integrity_id="integrity-110", reasons={"reason": "bounded"}, lineage={"source": "validation-109"}
        )
        self.assertEqual(result.reasons["reason"], "bounded")
        self.assertEqual(result.lineage["source"], "validation-109")

    def test_integrity_status_is_required(self):
        from src.core.learning_state_interpretation_validation_integrity import LearningStateInterpretationValidationIntegrity
        validation = self._validation()
        with self.assertRaises(TypeError):
            LearningStateInterpretationValidationIntegrity(
                integrity_id="integrity-110", validation_id=validation.validation_id, interpretation_id=validation.interpretation_id,
                request_id=validation.request_id, read_validation_id=validation.read_validation_id, read_id=validation.read_id,
                consumption_request_id=validation.consumption_request_id, source_validation_id=validation.source_validation_id,
                source_integrity_id=validation.integrity_id, transition_id=validation.transition_id, evidence_id=validation.evidence_id,
                application_id=validation.application_id, state_key=validation.state_key,
                transition_fingerprint=validation.transition_fingerprint, source_application_fingerprint=validation.source_application_fingerprint,
                computed_application_fingerprint=validation.computed_application_fingerprint, confidence=validation.confidence,
                validation_status=validation.validation_status, integrity_status=None, interpretation=validation.interpretation,
                failure_reason=None, reasons={}, lineage={},
            )

    def test_non_sha256_fingerprint_fails_closed(self):
        validation = self._validation()
        from src.core.learning_state_interpretation_validation_integrity import LearningStateInterpretationValidationIntegrity
        with self.assertRaises(ValueError):
            LearningStateInterpretationValidationIntegrity(
                integrity_id="integrity-110", validation_id=validation.validation_id, interpretation_id=validation.interpretation_id,
                request_id=validation.request_id, read_validation_id=validation.read_validation_id, read_id=validation.read_id,
                consumption_request_id=validation.consumption_request_id, source_validation_id=validation.source_validation_id,
                source_integrity_id=validation.integrity_id, transition_id=validation.transition_id, evidence_id=validation.evidence_id,
                application_id=validation.application_id, state_key=validation.state_key, transition_fingerprint="x",
                source_application_fingerprint=validation.source_application_fingerprint, computed_application_fingerprint=validation.computed_application_fingerprint,
                confidence=validation.confidence, validation_status=validation.validation_status,
                integrity_status=LearningStateInterpretationValidationIntegrityStatus.VALID, interpretation=validation.interpretation,
                failure_reason=None, reasons={}, lineage={},
            )

if __name__ == "__main__":
    unittest.main()
