import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

import src.core.tests.test_learning_state_execution_learning_state_interpretation as m23_140
from src.core.learning_state_execution_learning_state_interpretation import (
    LearningStateExecutionLearningStateInterpretationStatus,
)
from src.core.learning_state_execution_learning_state_interpretation_validation import (
    LearningStateExecutionLearningStateInterpretationValidationService,
    LearningStateExecutionLearningStateInterpretationValidationStatus,
)


class M23_141LearningStateInterpretationValidationTests(unittest.TestCase):
    def _make_interpretation(self, **kwargs):
        return m23_140.M23_140LearningStateInterpretationTests()._interpret(**kwargs)

    def _validate(self, interpretation=None, **kwargs):
        defaults = {
            "validation_id": "interpretation-validation-141",
            "validation_actor_id": "validator-A",
            "validation_purpose": "validate-interpretation-evidence",
            "validation_rationale": {"basis": "structural-contract"},
        }
        defaults.update(kwargs)
        return LearningStateExecutionLearningStateInterpretationValidationService().validate(
            interpretation or self._make_interpretation(), **defaults
        )

    def test_valid_interpretation_produces_validated_evidence(self):
        result = self._validate()
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationValidationStatus.VALIDATED)
        self.assertTrue(result.is_validated)
        self.assertTrue(result.admits_interpretation_validation_integrity)

    def test_exact_interpretation_type_is_required(self):
        with self.assertRaises(TypeError):
            self._validate(object())

    def test_interpretation_status_must_be_interpreted(self):
        interpretation = self._make_interpretation()
        object.__setattr__(interpretation, "status", LearningStateExecutionLearningStateInterpretationStatus.REJECTED)
        result = self._validate(interpretation)
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationValidationStatus.REJECTED)
        self.assertIn("learning-state interpretation is not INTERPRETED", result.reasons)

    def test_validation_metadata_is_required(self):
        service = LearningStateExecutionLearningStateInterpretationValidationService()
        interpretation = self._make_interpretation()
        for kwargs in (
            {"validation_id": " ", "validation_actor_id": "validator-A", "validation_purpose": "validate", "validation_rationale": {"x": 1}},
            {"validation_id": "validation-141", "validation_actor_id": " ", "validation_purpose": "validate", "validation_rationale": {"x": 1}},
            {"validation_id": "validation-141", "validation_actor_id": "validator-A", "validation_purpose": " ", "validation_rationale": {"x": 1}},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    service.validate(interpretation, **kwargs)
        with self.assertRaises(ValueError):
            service.validate(interpretation, validation_id="validation-141", validation_actor_id="validator-A", validation_purpose="validate", validation_rationale=None)

    def test_validation_identity_must_be_distinct_from_interpretation(self):
        interpretation = self._make_interpretation()
        result = self._validate(interpretation, validation_id=interpretation.interpretation_id)
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationValidationStatus.REJECTED)
        self.assertIn("validation identity must be distinct from interpretation identity", result.reasons)

    def test_interpretation_lineage_is_checked_fail_closed(self):
        interpretation = self._make_interpretation()
        object.__setattr__(interpretation, "lineage", {**dict(interpretation.lineage), "interpretation_id": "tampered"})
        result = self._validate(interpretation)
        self.assertIn("interpretation lineage mismatch", result.reasons)

    def test_request_lineage_is_checked_fail_closed(self):
        interpretation = self._make_interpretation()
        object.__setattr__(interpretation, "lineage", {**dict(interpretation.lineage), "request_id": "tampered"})
        result = self._validate(interpretation)
        self.assertIn("request lineage mismatch", result.reasons)

    def test_source_validation_lineage_is_checked_without_conflating_upstream_identity(self):
        interpretation = self._make_interpretation()
        direct_validation_id = interpretation.lineage.get("validation_id")
        self.assertIsInstance(direct_validation_id, str)
        self.assertNotEqual(direct_validation_id, interpretation.source_validation_id)
        lineage = dict(interpretation.lineage)
        lineage.pop("validation_id", None)
        object.__setattr__(interpretation, "lineage", lineage)
        result = self._validate(interpretation)
        self.assertIn("source validation lineage mismatch", result.reasons)

    def test_read_lineage_is_checked_fail_closed(self):
        interpretation = self._make_interpretation()
        object.__setattr__(interpretation, "lineage", {**dict(interpretation.lineage), "read_id": "tampered"})
        result = self._validate(interpretation)
        self.assertIn("read lineage mismatch", result.reasons)

    def test_consumption_request_lineage_is_checked_fail_closed(self):
        interpretation = self._make_interpretation()
        object.__setattr__(interpretation, "lineage", {**dict(interpretation.lineage), "consumption_request_id": "tampered"})
        result = self._validate(interpretation)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_read_fingerprint_is_checked_without_reread(self):
        interpretation = self._make_interpretation()
        result = self._validate(interpretation)
        self.assertEqual(result.read_fingerprint, interpretation.read_fingerprint)
        self.assertEqual(result.computed_read_fingerprint, interpretation.computed_read_fingerprint)
        self.assertFalse(result.reads_durable_state)
        self.assertFalse(result.rereads_durable_state)

    def test_tampered_read_fingerprint_is_rejected_without_repair(self):
        interpretation = self._make_interpretation()
        object.__setattr__(interpretation, "read_fingerprint", "f" * 64)
        original = interpretation.read_fingerprint
        result = self._validate(interpretation)
        self.assertIn("read fingerprint mismatch", result.reasons)
        self.assertEqual(interpretation.read_fingerprint, original)

    def test_interpretation_must_match_supplied_payload(self):
        interpretation = self._make_interpretation()
        object.__setattr__(interpretation, "interpretation", {"kind": "tampered"})
        result = self._validate(interpretation)
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationValidationStatus.REJECTED)
        self.assertIn("interpretation is inconsistent with supplied read payload", result.reasons)

    def test_provenance_and_payload_are_preserved(self):
        interpretation = self._make_interpretation()
        result = self._validate(interpretation)
        for field in (
            "interpretation_id", "source_request_id", "source_validation_id", "read_id", "consumption_request_id",
            "integrity_id", "transition_id", "evidence_id", "state_key", "requested_scope", "read_payload",
            "read_fingerprint", "computed_read_fingerprint", "reader_id", "read_purpose", "request_rationale",
            "confidence", "requester_id", "interpretation_purpose", "interpretation_rationale", "interpretation", "interpreter_id",
        ):
            self.assertEqual(getattr(result, field), getattr(interpretation, field))
        self.assertEqual(result.validation_actor_id, "validator-A")

    def test_validation_evidence_is_recursively_immutable(self):
        result = self._validate(validation_rationale={"nested": {"items": [1, 2]}})
        self.assertIsInstance(result.interpretation, MappingProxyType)
        self.assertIsInstance(result.validation_rationale, MappingProxyType)
        with self.assertRaises(TypeError):
            result.interpretation["kind"] = "other"
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateInterpretationValidationStatus.REJECTED

    def test_source_interpretation_is_not_mutated(self):
        interpretation = self._make_interpretation()
        before = (interpretation.status, interpretation.lineage, interpretation.interpretation, interpretation.interpretation_id)
        self._validate(interpretation)
        self.assertEqual((interpretation.status, interpretation.lineage, interpretation.interpretation, interpretation.interpretation_id), before)

    def test_validation_is_deterministic_for_same_inputs(self):
        first = self._validate()
        second = self._validate()
        self.assertEqual(first, second)

    def test_validation_has_no_truth_certainty_usefulness_or_authority_power(self):
        result = self._validate()
        for name in (
            "mutates_state", "persists_state", "reads_durable_state", "rereads_durable_state", "interprets_state",
            "is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "invokes_executor", "schedules_work", "plans_work", "updates_model", "mutates_memory",
            "mutates_policy", "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
