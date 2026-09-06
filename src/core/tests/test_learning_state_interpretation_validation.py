import unittest
from types import MappingProxyType

from src.core.learning_state_interpretation import LearningStateInterpretation, LearningStateInterpretationStatus
from src.core.learning_state_interpretation_validation import (
    LearningStateInterpretationValidationService,
    LearningStateInterpretationValidationStatus,
)
from src.core.learning_state_interpretation_request import LearningStateInterpretationRequest, LearningStateInterpretationRequestStatus


class LearningStateInterpretationValidationTests(unittest.TestCase):
    def _interpretation(self, *, status=LearningStateInterpretationStatus.INTERPRETED, interpretation=None):
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
            interpretation={"trend": {"direction": "rising"}, "count": 3} if interpretation is None else interpretation,
            failure_reason=None if status is LearningStateInterpretationStatus.INTERPRETED else "interpreter failed",
            reasons={"interpretation_status": status.value},
            lineage={"interpretation_id": "interpretation-108"},
        )

    def test_interpreted_mapping_is_accepted(self):
        result = LearningStateInterpretationValidationService().validate(self._interpretation(), validation_id="validation-109")
        self.assertEqual(result.validation_status, LearningStateInterpretationValidationStatus.ACCEPTED)
        self.assertEqual(result.interpretation, MappingProxyType({"trend": MappingProxyType({"direction": "rising"}), "count": 3}))

    def test_rejected_interpretation_is_rejected(self):
        result = LearningStateInterpretationValidationService().validate(
            self._interpretation(status=LearningStateInterpretationStatus.REJECTED), validation_id="validation-109"
        )
        self.assertEqual(result.validation_status, LearningStateInterpretationValidationStatus.REJECTED)
        self.assertIsNone(result.interpretation)
        self.assertIn("INTERPRETED mapping", result.failure_reason)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            LearningStateInterpretationValidationService().validate(object(), validation_id="validation-109")

    def test_blank_validation_id_fails_closed(self):
        with self.assertRaises(ValueError):
            LearningStateInterpretationValidationService().validate(self._interpretation(), validation_id=" ")

    def test_provenance_and_fingerprints_are_preserved(self):
        source = self._interpretation()
        result = LearningStateInterpretationValidationService().validate(source, validation_id="validation-109")
        for name in (
            "interpretation_id", "request_id", "read_validation_id", "read_id", "consumption_request_id",
            "source_validation_id", "integrity_id", "transition_id", "evidence_id", "application_id",
            "state_key", "transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "confidence", "interpretation_status",
        ):
            self.assertEqual(getattr(result, name), getattr(source, name))
        self.assertEqual(result.validation_id, "validation-109")

    def test_interpretation_is_recursively_immutable(self):
        source = self._interpretation(interpretation={"outer": {"items": ["a", {"n": 1}]}})
        result = LearningStateInterpretationValidationService().validate(source, validation_id="validation-109")
        self.assertIsInstance(result.interpretation, MappingProxyType)
        with self.assertRaises(TypeError):
            result.interpretation["new"] = "x"
        with self.assertRaises(TypeError):
            result.interpretation["outer"]["items"] = ()

    def test_reasons_and_lineage_are_immutable(self):
        result = LearningStateInterpretationValidationService().validate(
            self._interpretation(),
            validation_id="validation-109",
            reasons={"nested": {"ok": True}},
            lineage={"chain": ["a", "b"]},
        )
        with self.assertRaises(TypeError):
            result.reasons["new"] = True
        with self.assertRaises(TypeError):
            result.lineage["new"] = True

    def test_source_interpretation_is_not_mutated(self):
        source = self._interpretation()
        before = source.interpretation
        LearningStateInterpretationValidationService().validate(source, validation_id="validation-109")
        self.assertEqual(source.interpretation, before)

    def test_deterministic_validation(self):
        first = LearningStateInterpretationValidationService().validate(self._interpretation(), validation_id="validation-109")
        second = LearningStateInterpretationValidationService().validate(self._interpretation(), validation_id="validation-109")
        self.assertEqual(first, second)

    def test_validation_does_not_judge_semantic_content(self):
        result = LearningStateInterpretationValidationService().validate(
            self._interpretation(interpretation={"statement": "this is definitely true", "confidence": 0.0}),
            validation_id="validation-109",
        )
        self.assertEqual(result.validation_status, LearningStateInterpretationValidationStatus.ACCEPTED)
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.establishes_correctness)
        self.assertFalse(result.establishes_certainty)
        self.assertFalse(result.establishes_usefulness)

    def test_result_declares_no_interpreter_learning_or_authority_power(self):
        result = LearningStateInterpretationValidationService().validate(self._interpretation(), validation_id="validation-109")
        self.assertFalse(result.invokes_interpreter)
        self.assertFalse(result.invokes_learner)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)

    def test_result_is_immutable(self):
        result = LearningStateInterpretationValidationService().validate(self._interpretation(), validation_id="validation-109")
        with self.assertRaises(Exception):
            result.validation_id = "changed"

    def test_rejected_validation_requires_failure_reason(self):
        with self.assertRaises(ValueError):
            from src.core.learning_state_interpretation_validation import LearningStateInterpretationValidation
            LearningStateInterpretationValidation(
                validation_id="validation-109", interpretation_id="interpretation-108", request_id="interpret-request-107",
                read_validation_id="validation-106", read_id="read-105", consumption_request_id="request-104",
                source_validation_id="validation-source", integrity_id="integrity-99", transition_id="transition-98",
                evidence_id="evidence-97", application_id="application-96", state_key="learning-state",
                transition_fingerprint="a" * 64, source_application_fingerprint="b" * 64,
                computed_application_fingerprint="c" * 64, confidence=0.8,
                interpretation_status=LearningStateInterpretationStatus.REJECTED, interpretation=None,
                validation_status=LearningStateInterpretationValidationStatus.REJECTED, failure_reason="",
                reasons={}, lineage={},
            )

    def test_accepted_validation_requires_interpreted_status(self):
        with self.assertRaises(ValueError):
            from src.core.learning_state_interpretation_validation import LearningStateInterpretationValidation
            LearningStateInterpretationValidation(
                validation_id="validation-109", interpretation_id="interpretation-108", request_id="interpret-request-107",
                read_validation_id="validation-106", read_id="read-105", consumption_request_id="request-104",
                source_validation_id="validation-source", integrity_id="integrity-99", transition_id="transition-98",
                evidence_id="evidence-97", application_id="application-96", state_key="learning-state",
                transition_fingerprint="a" * 64, source_application_fingerprint="b" * 64,
                computed_application_fingerprint="c" * 64, confidence=0.8,
                interpretation_status=LearningStateInterpretationStatus.REJECTED, interpretation=None,
                validation_status=LearningStateInterpretationValidationStatus.ACCEPTED, failure_reason=None,
                reasons={}, lineage={},
            )

    def test_wrong_status_type_fails_closed(self):
        with self.assertRaises(TypeError):
            from src.core.learning_state_interpretation_validation import LearningStateInterpretationValidation
            LearningStateInterpretationValidation(
                validation_id="validation-109", interpretation_id="interpretation-108", request_id="interpret-request-107",
                read_validation_id="validation-106", read_id="read-105", consumption_request_id="request-104",
                source_validation_id="validation-source", integrity_id="integrity-99", transition_id="transition-98",
                evidence_id="evidence-97", application_id="application-96", state_key="learning-state",
                transition_fingerprint="a" * 64, source_application_fingerprint="b" * 64,
                computed_application_fingerprint="c" * 64, confidence=0.8,
                interpretation_status=LearningStateInterpretationStatus.INTERPRETED, interpretation={"x": 1},
                validation_status="ACCEPTED", failure_reason=None, reasons={}, lineage={},
            )

    def test_non_mapping_accepted_payload_fails_closed(self):
        with self.assertRaises(TypeError):
            from src.core.learning_state_interpretation_validation import LearningStateInterpretationValidation
            LearningStateInterpretationValidation(
                validation_id="validation-109", interpretation_id="interpretation-108", request_id="interpret-request-107",
                read_validation_id="validation-106", read_id="read-105", consumption_request_id="request-104",
                source_validation_id="validation-source", integrity_id="integrity-99", transition_id="transition-98",
                evidence_id="evidence-97", application_id="application-96", state_key="learning-state",
                transition_fingerprint="a" * 64, source_application_fingerprint="b" * 64,
                computed_application_fingerprint="c" * 64, confidence=0.8,
                interpretation_status=LearningStateInterpretationStatus.INTERPRETED, interpretation=["not", "mapping"],
                validation_status=LearningStateInterpretationValidationStatus.ACCEPTED, failure_reason=None, reasons={}, lineage={},
            )

    def test_validation_status_is_required(self):
        with self.assertRaises(TypeError):
            from src.core.learning_state_interpretation_validation import LearningStateInterpretationValidation
            LearningStateInterpretationValidation(
                validation_id="validation-109", interpretation_id="interpretation-108", request_id="interpret-request-107",
                read_validation_id="validation-106", read_id="read-105", consumption_request_id="request-104",
                source_validation_id="validation-source", integrity_id="integrity-99", transition_id="transition-98",
                evidence_id="evidence-97", application_id="application-96", state_key="learning-state",
                transition_fingerprint="a" * 64, source_application_fingerprint="b" * 64,
                computed_application_fingerprint="c" * 64, confidence=0.8,
                interpretation_status=LearningStateInterpretationStatus.INTERPRETED, interpretation={"x": 1},
                validation_status=None, failure_reason=None, reasons={}, lineage={},
            )


if __name__ == "__main__":
    unittest.main()
