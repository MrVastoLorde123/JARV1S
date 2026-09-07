import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_consumption_read_validation import (
    LearningStateExecutionLearningStateConsumptionReadValidationService,
    LearningStateExecutionLearningStateConsumptionReadValidationStatus,
)
from src.core.learning_state_execution_learning_state_interpretation_request import (
    LearningStateExecutionLearningStateInterpretationRequestService,
    LearningStateExecutionLearningStateInterpretationRequestStatus,
)
from src.core.tests.test_learning_state_execution_learning_state_consumption_read_validation import (
    M23_138LearningStateConsumptionReadValidationTests,
)


class M23_139LearningStateInterpretationRequestTests(unittest.TestCase):
    def _make_validation(self, **kwargs):
        read = M23_138LearningStateConsumptionReadValidationTests()._make_read()
        defaults = {
            "validation_id": "read-validation-138",
            "validator_id": "validator-A",
            "validation_purpose": "validate-read-evidence",
            "validation_rationale": {"basis": "integrity-check"},
        }
        defaults.update(kwargs)
        return LearningStateExecutionLearningStateConsumptionReadValidationService().validate(read, **defaults)

    def _request(self, validation=None, **kwargs):
        defaults = {
            "request_id": "interpretation-request-139",
            "requester_id": "interpreter-A",
            "interpretation_purpose": "derive-state-meaning",
            "interpretation_rationale": {"basis": "validated-read-evidence"},
        }
        defaults.update(kwargs)
        return LearningStateExecutionLearningStateInterpretationRequestService().request(
            validation or self._make_validation(), **defaults
        )

    def test_validated_input_produces_requested_artifact(self):
        result = self._request()
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationRequestStatus.REQUESTED)
        self.assertTrue(result.is_requested)
        self.assertTrue(result.admits_interpretation)
        self.assertFalse(result.has_interpreted_payload)

    def test_exact_validation_type_is_required(self):
        with self.assertRaises(TypeError):
            self._request(object())

    def test_validation_status_must_be_validated(self):
        validation = self._make_validation()
        object.__setattr__(validation, "status", LearningStateExecutionLearningStateConsumptionReadValidationStatus.REJECTED)
        result = self._request(validation)
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationRequestStatus.REJECTED)
        self.assertIn("consumption read validation is not VALIDATED", result.reasons)

    def test_request_metadata_is_required(self):
        service = LearningStateExecutionLearningStateInterpretationRequestService()
        validation = self._make_validation()
        for kwargs in (
            {"request_id": " ", "requester_id": "requester-A", "interpretation_purpose": "inspect", "interpretation_rationale": {"x": 1}},
            {"request_id": "request-139", "requester_id": " ", "interpretation_purpose": "inspect", "interpretation_rationale": {"x": 1}},
            {"request_id": "request-139", "requester_id": "requester-A", "interpretation_purpose": " ", "interpretation_rationale": {"x": 1}},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    service.request(validation, **kwargs)
        with self.assertRaises(ValueError):
            service.request(
                validation,
                request_id="request-139",
                requester_id="requester-A",
                interpretation_purpose="inspect",
                interpretation_rationale=None,
            )

    def test_request_identity_must_be_distinct_from_validation(self):
        result = self._request(request_id="read-validation-138")
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationRequestStatus.REJECTED)
        self.assertIn("interpretation request identity must be distinct from validation identity", result.reasons)

    def test_request_identity_must_be_distinct_from_read(self):
        result = self._request(request_id="read-137")
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationRequestStatus.REJECTED)
        self.assertIn("interpretation request identity must be distinct from read identity", result.reasons)

    def test_source_validation_lineage_is_checked_fail_closed(self):
        validation = self._make_validation(lineage={"validation_id": "tampered", "read_id": "read-137", "consumption_request_id": "consume-136"})
        result = self._request(validation)
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationRequestStatus.REJECTED)
        self.assertIn("source validation lineage mismatch", result.reasons)

    def test_read_lineage_is_checked_fail_closed(self):
        validation = self._make_validation(lineage={"validation_id": "read-validation-138", "read_id": "tampered", "consumption_request_id": "consume-136"})
        result = self._request(validation)
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationRequestStatus.REJECTED)
        self.assertIn("read lineage mismatch", result.reasons)

    def test_consumption_request_lineage_is_checked_fail_closed(self):
        validation = self._make_validation(lineage={"validation_id": "read-validation-138", "read_id": "read-137", "consumption_request_id": "tampered"})
        result = self._request(validation)
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationRequestStatus.REJECTED)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_provenance_scope_and_payload_are_preserved(self):
        validation = self._make_validation()
        result = self._request(validation, requester_id="interpreter-B", interpretation_purpose="inspect-read")
        for field in (
            "source_validation_id", "read_id", "consumption_request_id", "integrity_id", "transition_id", "evidence_id",
            "state_key", "read_payload", "read_fingerprint", "computed_read_fingerprint", "reader_id", "read_purpose", "confidence",
        ):
            self.assertEqual(getattr(result, field), getattr(validation, field))
        self.assertEqual(result.requested_scope, validation.requested_scope)
        self.assertEqual(result.request_rationale, validation.request_rationale)
        self.assertEqual(result.requester_id, "interpreter-B")
        self.assertEqual(result.interpretation_purpose, "inspect-read")

    def test_request_evidence_is_recursively_immutable(self):
        result = self._request(
            interpretation_rationale={"nested": {"items": [1, 2]}}
        )
        self.assertIsInstance(result.read_payload, MappingProxyType)
        self.assertIsInstance(result.requested_scope, MappingProxyType)
        self.assertIsInstance(result.interpretation_rationale, MappingProxyType)
        with self.assertRaises(TypeError):
            result.read_payload["threshold"] = 99
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateInterpretationRequestStatus.REJECTED

    def test_source_validation_is_not_mutated(self):
        validation = self._make_validation()
        before = (validation.status, validation.lineage, validation.read_payload, validation.read_fingerprint)
        self._request(validation)
        self.assertEqual((validation.status, validation.lineage, validation.read_payload, validation.read_fingerprint), before)

    def test_caller_reasons_and_lineage_are_preserved(self):
        result = self._request(
            reasons=("caller-reason",),
            lineage={"request_id": "interpretation-request-139", "validation_id": "read-validation-138", "chain": {"step": 1}},
        )
        self.assertEqual(result.reasons, ("caller-reason",))
        self.assertEqual(result.lineage["chain"]["step"], 1)

    def test_invalid_caller_reason_is_rejected(self):
        with self.assertRaises(TypeError):
            self._request(reasons=(" ",))

    def test_request_is_deterministic_for_same_inputs(self):
        first = self._request()
        second = self._request()
        self.assertEqual(first, second)

    def test_rejected_validation_fails_closed_without_interpretation(self):
        validation = self._make_validation()
        object.__setattr__(validation, "status", LearningStateExecutionLearningStateConsumptionReadValidationStatus.REJECTED)
        result = self._request(validation)
        self.assertFalse(result.admits_interpretation)
        self.assertFalse(result.has_interpreted_payload)
        self.assertFalse(result.interprets_state)

    def test_request_has_no_interpretation_or_authority_powers(self):
        result = self._request()
        for name in (
            "interprets_state", "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
            "mutates_state", "persists_state", "reads_durable_state", "rereads_durable_state", "is_learning", "applies_learning",
            "authorizes_learning", "authorizes_execution", "authorizes_retry", "invokes_learner", "invokes_executor",
            "schedules_work", "plans_work", "updates_model", "mutates_memory", "mutates_policy",
        ):
            self.assertFalse(getattr(result, name))

    def test_request_identity_and_source_validation_are_distinct(self):
        result = self._request()
        self.assertNotEqual(result.request_id, result.source_validation_id)
        self.assertNotEqual(result.request_id, result.read_id)


if __name__ == "__main__":
    unittest.main()
