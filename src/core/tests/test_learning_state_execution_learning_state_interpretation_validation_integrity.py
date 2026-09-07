import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

import src.core.tests.test_learning_state_execution_learning_state_interpretation_validation as m23_141
from src.core.learning_state_execution_learning_state_interpretation_validation import (
    LearningStateExecutionLearningStateInterpretationValidationStatus,
)
from src.core.learning_state_execution_learning_state_interpretation_validation_integrity import (
    LearningStateExecutionLearningStateInterpretationValidationIntegrityService,
    LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus,
)


class M23_142LearningStateInterpretationValidationIntegrityTests(unittest.TestCase):
    def _make_validation(self, **kwargs):
        return m23_141.M23_141LearningStateInterpretationValidationTests()._validate(**kwargs)

    def _check(self, validation=None, **kwargs):
        params = {"integrity_id": "interpretation-validation-integrity-142"}
        params.update(kwargs)
        return LearningStateExecutionLearningStateInterpretationValidationIntegrityService().validate(
            validation or self._make_validation(),
            **params,
        )

    def test_valid_validation_produces_valid_integrity(self):
        result = self._check()
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus.VALID)
        self.assertTrue(result.is_valid)
        self.assertTrue(result.validates_integrity)
        self.assertEqual(len(result.integrity_fingerprint), 64)
        self.assertEqual(result.integrity_fingerprint, result.computed_integrity_fingerprint)

    def test_exact_validation_type_is_required(self):
        with self.assertRaises(TypeError):
            self._check(object())

    def test_integrity_metadata_is_required(self):
        service = LearningStateExecutionLearningStateInterpretationValidationIntegrityService()
        validation = self._make_validation()
        with self.assertRaises(ValueError):
            service.validate(validation, integrity_id=" ")
        with self.assertRaises(TypeError):
            service.validate(validation, integrity_id="integrity-142", reasons=["bad"])

    def test_integrity_identity_must_be_distinct_from_validation(self):
        result = self._check(integrity_id="interpretation-validation-141")
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus.INVALID)
        self.assertIn("integrity identity must be distinct from validation identity", result.reasons)

    def test_validation_status_must_be_validated(self):
        validation = self._make_validation()
        object.__setattr__(validation, "status", LearningStateExecutionLearningStateInterpretationValidationStatus.REJECTED)
        result = self._check(validation)
        self.assertIn("interpretation validation is not VALIDATED", result.reasons)

    def test_validation_lineage_is_checked_fail_closed(self):
        validation = self._make_validation()
        object.__setattr__(validation, "lineage", {**dict(validation.lineage), "validation_id": "tampered"})
        result = self._check(validation)
        self.assertIn("validation lineage mismatch", result.reasons)

    def test_interpretation_lineage_is_checked_fail_closed(self):
        validation = self._make_validation()
        object.__setattr__(validation, "lineage", {**dict(validation.lineage), "interpretation_id": "tampered"})
        result = self._check(validation)
        self.assertIn("interpretation lineage mismatch", result.reasons)

    def test_request_lineage_is_checked_fail_closed(self):
        validation = self._make_validation()
        object.__setattr__(validation, "lineage", {**dict(validation.lineage), "request_id": "tampered"})
        result = self._check(validation)
        self.assertIn("request lineage mismatch", result.reasons)

    def test_source_validation_lineage_is_checked_fail_closed(self):
        validation = self._make_validation()
        object.__setattr__(validation, "lineage", {**dict(validation.lineage), "source_validation_id": "tampered"})
        result = self._check(validation)
        self.assertIn("source validation lineage mismatch", result.reasons)

    def test_read_and_consumption_lineage_are_checked(self):
        validation = self._make_validation()
        object.__setattr__(validation, "lineage", {**dict(validation.lineage), "read_id": "tampered"})
        result = self._check(validation)
        self.assertIn("read lineage mismatch", result.reasons)
        object.__setattr__(validation, "lineage", {**dict(validation.lineage), "consumption_request_id": "tampered"})
        result = self._check(validation)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_read_fingerprint_is_checked_without_reread(self):
        validation = self._make_validation()
        result = self._check(validation)
        self.assertEqual(result.read_fingerprint, validation.read_fingerprint)
        self.assertEqual(result.computed_read_fingerprint, validation.computed_read_fingerprint)
        self.assertFalse(result.reads_durable_state)
        self.assertFalse(result.rereads_durable_state)

    def test_tampered_read_fingerprint_is_rejected_without_repair(self):
        validation = self._make_validation()
        object.__setattr__(validation, "read_fingerprint", "f" * 64)
        original = validation.read_fingerprint
        result = self._check(validation)
        self.assertIn("read fingerprint mismatch", result.reasons)
        self.assertEqual(validation.read_fingerprint, original)

    def test_provenance_and_payload_are_preserved(self):
        validation = self._make_validation()
        result = self._check(validation)
        for field in (
            "validation_id", "interpretation_id", "source_request_id", "source_validation_id", "read_id",
            "consumption_request_id", "interpretation", "read_payload", "read_fingerprint",
            "computed_read_fingerprint", "validation_actor_id", "validation_purpose",
        ):
            self.assertEqual(getattr(result, field), getattr(validation, field))

    def test_integrity_evidence_is_recursively_immutable(self):
        result = self._check()
        self.assertIsInstance(result.interpretation, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.interpretation["kind"] = "other"
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateInterpretationValidationIntegrityStatus.INVALID

    def test_source_validation_is_not_mutated(self):
        validation = self._make_validation()
        before = (validation.status, validation.lineage, validation.interpretation, validation.validation_id)
        self._check(validation)
        self.assertEqual((validation.status, validation.lineage, validation.interpretation, validation.validation_id), before)

    def test_integrity_is_deterministic_for_same_inputs(self):
        first = self._check()
        second = self._check()
        self.assertEqual(first, second)

    def test_integrity_has_no_truth_learning_or_authority_power(self):
        result = self._check()
        for name in (
            "mutates_state", "persists_state", "reads_durable_state", "rereads_durable_state", "interprets_state",
            "is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "invokes_executor", "schedules_work", "plans_work", "updates_model", "mutates_memory",
            "mutates_policy", "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()