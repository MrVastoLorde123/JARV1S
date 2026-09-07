import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_consumption_read_validation import (
    LearningStateExecutionLearningStateConsumptionReadValidationService,
    LearningStateExecutionLearningStateConsumptionReadValidationStatus,
)
from src.core.learning_state_execution_learning_state_durable_read_consumption import (
    LearningStateExecutionLearningStateDurableReadConsumptionService,
    LearningStateExecutionLearningStateDurableReadConsumptionStatus,
)
from src.core.tests.test_learning_state_execution_learning_state_durable_read_consumption import M23_137LearningStateDurableReadConsumptionTests


class M23_138LearningStateConsumptionReadValidationTests(unittest.TestCase):
    def _make_read(self, *, scope=None, durable_state=None):
        request = M23_137LearningStateDurableReadConsumptionTests()._make_request(
            scope if scope is not None else {"state_key": "demo.state"}
        )
        return LearningStateExecutionLearningStateDurableReadConsumptionService().read(
            request,
            durable_state if durable_state is not None else {"demo.state": {"threshold": 42, "mode": "safe"}},
            read_id="read-137",
            reader_id="reader-A",
            read_purpose="bounded-state-inspection",
        )

    def _validate(self, read=None, **kwargs):
        defaults = {
            "validation_id": "read-validation-138",
            "validator_id": "validator-A",
            "validation_purpose": "validate-read-evidence",
            "validation_rationale": {"basis": "integrity-check"},
        }
        defaults.update(kwargs)
        return LearningStateExecutionLearningStateConsumptionReadValidationService().validate(
            read or self._make_read(), **defaults
        )

    def test_valid_read_produces_validated_evidence(self):
        result = self._validate()
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionReadValidationStatus.VALIDATED)
        self.assertTrue(result.is_validated)
        self.assertTrue(result.admits_interpretation_request)

    def test_exact_read_type_is_required(self):
        with self.assertRaises(TypeError):
            self._validate(object())

    def test_read_status_must_be_read(self):
        read = self._make_read()
        object.__setattr__(read, "status", LearningStateExecutionLearningStateDurableReadConsumptionStatus.REJECTED)
        result = self._validate(read)
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionReadValidationStatus.REJECTED)
        self.assertIn("durable-state read is not READ", result.reasons)

    def test_validation_metadata_is_required(self):
        service = LearningStateExecutionLearningStateConsumptionReadValidationService()
        read = self._make_read()
        for kwargs in (
            {"validation_id": " ", "validator_id": "validator-A", "validation_purpose": "validate", "validation_rationale": {"x": 1}},
            {"validation_id": "validation-138", "validator_id": " ", "validation_purpose": "validate", "validation_rationale": {"x": 1}},
            {"validation_id": "validation-138", "validator_id": "validator-A", "validation_purpose": " ", "validation_rationale": {"x": 1}},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    service.validate(read, **kwargs)
        with self.assertRaises(ValueError):
            service.validate(
                read,
                validation_id="validation-138",
                validator_id="validator-A",
                validation_purpose="validate",
                validation_rationale=None,
            )

    def test_validation_identity_must_be_distinct_from_read(self):
        result = self._validate(validation_id="read-137")
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionReadValidationStatus.REJECTED)
        self.assertIn("validation identity must be distinct from read identity", result.reasons)

    def test_read_lineage_is_checked_fail_closed(self):
        read = self._make_read()
        object.__setattr__(read, "lineage", {"read_id": "tampered", "consumption_request_id": read.consumption_request_id, "validation_id": read.validation_id})
        result = self._validate(read)
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionReadValidationStatus.REJECTED)
        self.assertIn("read lineage mismatch", result.reasons)

    def test_consumption_request_lineage_is_checked_fail_closed(self):
        read = self._make_read()
        object.__setattr__(read, "lineage", {"read_id": read.read_id, "consumption_request_id": "tampered", "validation_id": read.validation_id})
        result = self._validate(read)
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionReadValidationStatus.REJECTED)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_source_validation_lineage_is_checked_fail_closed(self):
        read = self._make_read()
        object.__setattr__(read, "lineage", {"read_id": read.read_id, "consumption_request_id": read.consumption_request_id, "validation_id": "tampered"})
        result = self._validate(read)
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionReadValidationStatus.REJECTED)
        self.assertIn("source validation lineage mismatch", result.reasons)

    def test_read_fingerprint_is_recomputed(self):
        result = self._validate()
        self.assertEqual(result.computed_read_fingerprint, result.read_fingerprint)
        self.assertEqual(len(result.computed_read_fingerprint), 64)
        self.assertTrue(all(char in "0123456789abcdef" for char in result.computed_read_fingerprint))

    def test_tampered_read_fingerprint_is_rejected_without_repair(self):
        read = self._make_read()
        object.__setattr__(read, "read_fingerprint", "f" * 64)
        original = read.read_fingerprint
        result = self._validate(read)
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionReadValidationStatus.REJECTED)
        self.assertIn("read fingerprint mismatch", result.reasons)
        self.assertEqual(read.read_fingerprint, original)

    def test_tampered_computed_fingerprint_is_rejected_without_repair(self):
        read = self._make_read()
        object.__setattr__(read, "computed_read_fingerprint", "e" * 64)
        result = self._validate(read)
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionReadValidationStatus.REJECTED)
        self.assertIn("computed read fingerprint mismatch", result.reasons)

    def test_read_payload_must_exist_for_read_status(self):
        read = self._make_read()
        object.__setattr__(read, "read_payload", None)
        result = self._validate(read)
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionReadValidationStatus.REJECTED)
        self.assertIn("READ evidence requires non-empty payload evidence", result.reasons)

    def test_read_fingerprint_length_must_be_sha256(self):
        read = self._make_read()
        object.__setattr__(read, "read_fingerprint", "abc")
        result = self._validate(read)
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionReadValidationStatus.REJECTED)
        self.assertIn("read fingerprint mismatch", result.reasons)
        self.assertIn("read fingerprint is not SHA-256", result.reasons)

    def test_source_read_is_not_mutated(self):
        read = self._make_read()
        before = (read.read_fingerprint, read.lineage, read.read_payload)
        self._validate(read)
        self.assertEqual((read.read_fingerprint, read.lineage, read.read_payload), before)

    def test_validation_evidence_is_recursively_immutable(self):
        result = self._validate(validation_rationale={"nested": {"items": [1, 2]}})
        self.assertIsInstance(result.read_payload, MappingProxyType)
        self.assertIsInstance(result.requested_scope, MappingProxyType)
        self.assertIsInstance(result.validation_rationale, MappingProxyType)
        with self.assertRaises(TypeError):
            result.read_payload["threshold"] = 99
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateConsumptionReadValidationStatus.REJECTED

    def test_provenance_and_scope_are_preserved(self):
        read = self._make_read(scope={"state_key": "demo.state", "fields": ["threshold"]})
        result = self._validate(read, validator_id="validator-B", validation_purpose="inspect-read")
        for field in ("read_id", "consumption_request_id", "source_validation_id", "integrity_id", "transition_id", "evidence_id", "state_key", "reader_id", "read_purpose", "confidence"):
            self.assertEqual(getattr(result, field), getattr(read, field))
        self.assertEqual(result.requested_scope, read.requested_scope)
        self.assertEqual(result.request_rationale, read.request_rationale)
        self.assertEqual(result.validator_id, "validator-B")
        self.assertEqual(result.validation_purpose, "inspect-read")

    def test_caller_reasons_and_lineage_are_preserved_and_frozen(self):
        result = self._validate(reasons=("caller-reason",), lineage={"validation_id": "read-validation-138", "read_id": "read-137", "chain": {"step": 1}})
        self.assertEqual(result.reasons, ("caller-reason",))
        self.assertEqual(result.lineage["chain"]["step"], 1)
        with self.assertRaises(TypeError):
            self._validate(reasons=(" ",))

    def test_validation_is_deterministic_for_same_inputs(self):
        first = self._validate()
        second = self._validate()
        self.assertEqual(first, second)

    def test_validation_has_no_reread_interpretation_learning_or_authority_powers(self):
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
