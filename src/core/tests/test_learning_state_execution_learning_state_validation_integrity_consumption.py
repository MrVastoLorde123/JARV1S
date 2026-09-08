import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_validation_integrity import (
    LearningStateExecutionLearningStateValidationIntegrityStatus,
)
from src.core.learning_state_execution_learning_state_validation_integrity_consumption import (
    LearningStateExecutionLearningStateValidationIntegrityConsumptionService,
    LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus,
)
from src.core.tests.test_learning_state_execution_learning_state_validation_integrity import (
    M23_168LearningStateValidationIntegrityTests,
)


class M23_169LearningStateValidationIntegrityConsumptionTests(unittest.TestCase):
    def _make_integrity(self):
        return M23_168LearningStateValidationIntegrityTests()._integritize()

    def _consume(self, integrity=None, **kwargs):
        values = {
            "consumption_id": "validation-integrity-consumption-169",
            "consumer_id": "consumer-B",
            "consumption_purpose": "bounded-validation-integrity-inspection",
            "consumption_rationale": {"basis": "validated-integrity"},
        }
        values.update(kwargs)
        return LearningStateExecutionLearningStateValidationIntegrityConsumptionService().consume(
            integrity or self._make_integrity(), **values
        )

    def test_valid_integrity_is_consumed(self):
        result = self._consume()
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus.CONSUMED)
        self.assertTrue(result.is_consumed)
        self.assertTrue(result.consumes_validation_integrity)
        self.assertFalse(result.consumes_state)
        self.assertEqual(result.integrity_id, "validation-integrity-168")
        self.assertEqual(result.validation_id, "learning-state-validation-167")

    def test_exact_integrity_type_is_required(self):
        with self.assertRaises(TypeError):
            self._consume(integrity=object())

    def test_required_consumption_metadata_is_enforced(self):
        integrity = self._make_integrity()
        service = LearningStateExecutionLearningStateValidationIntegrityConsumptionService()
        for kwargs in (
            {"consumption_id": " ", "consumer_id": "consumer-B", "consumption_purpose": "inspect", "consumption_rationale": {"x": 1}},
            {"consumption_id": "c-169", "consumer_id": " ", "consumption_purpose": "inspect", "consumption_rationale": {"x": 1}},
            {"consumption_id": "c-169", "consumer_id": "consumer-B", "consumption_purpose": " ", "consumption_rationale": {"x": 1}},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    service.consume(integrity, **kwargs)
        with self.assertRaises(ValueError):
            service.consume(integrity, consumption_id="c-169", consumer_id="consumer-B", consumption_purpose="inspect", consumption_rationale=None)

    def test_invalid_integrity_fails_closed(self):
        integrity = self._make_integrity()
        object.__setattr__(integrity, "status", LearningStateExecutionLearningStateValidationIntegrityStatus.INVALID)
        result = self._consume(integrity)
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus.REJECTED)
        self.assertFalse(result.is_consumed)
        self.assertIn("learning-state validation integrity is not VALID", result.reasons)
        self.assertEqual(dict(result.consumed_metadata), {"rejected_integrity": True})

    def test_consumption_identity_must_be_distinct(self):
        integrity = self._make_integrity()
        result = self._consume(integrity, consumption_id=integrity.integrity_id)
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus.REJECTED)
        self.assertIn("consumption identity must be distinct from integrity identity", result.reasons)

    def test_anchored_lineage_is_rechecked(self):
        integrity = self._make_integrity()
        original = integrity.lineage
        expected_reasons = {
            "integrity_id": "integrity lineage mismatch",
            "validation_id": "validation lineage mismatch",
            "transition_id": "transition lineage mismatch",
            "evidence_id": "evidence lineage mismatch",
            "application_id": "application lineage mismatch",
            "source_integrity_id": "source integrity lineage mismatch",
            "source_validation_id": "source validation lineage mismatch",
        }
        for field, value in (
            ("integrity_id", "tampered-integrity"),
            ("validation_id", "tampered-validation"),
            ("transition_id", "tampered-transition"),
            ("evidence_id", "tampered-evidence"),
            ("application_id", "tampered-application"),
            ("source_integrity_id", "tampered-source-integrity"),
            ("source_validation_id", "tampered-source-validation"),
        ):
            tampered = dict(original)
            tampered[field] = value
            object.__setattr__(integrity, "lineage", MappingProxyType(tampered))
            result = self._consume(integrity)
            self.assertIs(result.status, LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus.REJECTED, msg=field)
            self.assertIn(expected_reasons[field], result.reasons, msg=field)
            object.__setattr__(integrity, "lineage", original)

    def test_malformed_fingerprint_fails_closed(self):
        integrity = self._make_integrity()
        object.__setattr__(integrity, "integrity_fingerprint", "not-sha256")
        result = self._consume(integrity)
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus.REJECTED)
        self.assertIn("integrity_fingerprint is not SHA-256", result.reasons)

    def test_fingerprint_mismatch_fails_closed(self):
        integrity = self._make_integrity()
        object.__setattr__(integrity, "computed_integrity_fingerprint", "d" * 64)
        result = self._consume(integrity)
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus.REJECTED)
        self.assertIn("integrity fingerprint mismatch", result.reasons)

    def test_custom_reasons_and_lineage_are_preserved_and_frozen(self):
        custom_lineage = {"consumption_id": "c-169", "integrity_id": "validation-integrity-168", "chain": ["a", {"step": 2}]}
        result = self._consume(consumption_id="c-169", reasons=("caller-supplied",), lineage=custom_lineage)
        self.assertEqual(result.reasons, ("caller-supplied",))
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.lineage["chain"], tuple)
        self.assertIsInstance(result.lineage["chain"][1], MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["x"] = "y"

    def test_consumed_metadata_preserves_integrity_identity_and_provenance(self):
        result = self._consume()
        for field in (
            "integrity_id", "validation_id", "transition_id", "evidence_id", "application_id",
            "decision_id", "proposal_id", "eligibility_id", "source_integrity_id", "source_validation_id",
            "state_key", "validation_purpose", "validator_id", "integrity_fingerprint",
        ):
            self.assertEqual(result.consumed_metadata[field], getattr(result, field))

    def test_integrity_source_is_not_mutated(self):
        integrity = self._make_integrity()
        before = integrity
        self._consume(integrity)
        self.assertEqual(integrity, before)

    def test_consumption_evidence_is_immutable(self):
        result = self._consume(consumption_rationale={"basis": ["validated", {"scope": "bounded"}]})
        self.assertIsInstance(result.consumption_rationale, MappingProxyType)
        self.assertIsInstance(result.consumption_rationale["basis"], tuple)
        self.assertIsInstance(result.consumed_metadata, MappingProxyType)
        with self.assertRaises(TypeError):
            result.consumed_metadata["x"] = "y"
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus.REJECTED

    def test_has_no_learning_or_authority_powers(self):
        result = self._consume()
        for name in (
            "mutates_state", "persists_state", "consumes_state", "is_learning", "applies_learning", "authorizes_learning",
            "authorizes_execution", "authorizes_retry", "invokes_learner", "invokes_executor", "schedules_work",
            "plans_work", "updates_model", "mutates_memory", "mutates_policy", "establishes_truth",
            "establishes_correctness", "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
