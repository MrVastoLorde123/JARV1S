import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_interpretation_request import (
    LearningStateExecutionLearningStateInterpretationRequestService,
    LearningStateExecutionLearningStateInterpretationRequestStatus,
)
from src.core.learning_state_execution_learning_state_interpretation import (
    LearningStateExecutionLearningStateInterpretationService,
    LearningStateExecutionLearningStateInterpretationStatus,
)


class M23_140LearningStateInterpretationTests(unittest.TestCase):
    def _make_request(self, **kwargs):
        from src.core.learning_state_execution_learning_state_consumption_read_validation import (
            LearningStateExecutionLearningStateConsumptionReadValidationService,
        )
        from src.core.tests.test_learning_state_execution_learning_state_consumption_read_validation import (
            M23_138LearningStateConsumptionReadValidationTests,
        )

        read = M23_138LearningStateConsumptionReadValidationTests()._make_read()
        validation = LearningStateExecutionLearningStateConsumptionReadValidationService().validate(
            read,
            validation_id="read-validation-138",
            validator_id="validator-A",
            validation_purpose="validate-read-evidence",
            validation_rationale={"basis": "integrity-check"},
        )
        defaults = {
            "request_id": "interpretation-request-139",
            "requester_id": "interpreter-A",
            "interpretation_purpose": "derive-state-meaning",
            "interpretation_rationale": {"basis": "validated-read-evidence"},
        }
        defaults.update(kwargs)
        return LearningStateExecutionLearningStateInterpretationRequestService().request(validation, **defaults)

    def _interpret(self, request=None, **kwargs):
        defaults = {
            "interpretation_id": "interpretation-140",
            "interpreter_id": "interpreter-A",
            "interpretation_purpose": "structural-inspection",
            "interpretation_rationale": {"basis": "bounded-request"},
        }
        defaults.update(kwargs)
        return LearningStateExecutionLearningStateInterpretationService().interpret(
            request or self._make_request(), **defaults
        )

    def test_requested_input_produces_interpreted_artifact(self):
        result = self._interpret()
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationStatus.INTERPRETED)
        self.assertTrue(result.is_interpreted)
        self.assertTrue(result.interprets_state)
        self.assertEqual(result.interpretation["kind"], "mapping")

    def test_exact_request_type_is_required(self):
        with self.assertRaises(TypeError):
            self._interpret(object())

    def test_request_status_must_be_requested(self):
        request = self._make_request()
        object.__setattr__(request, "status", LearningStateExecutionLearningStateInterpretationRequestStatus.REJECTED)
        result = self._interpret(request)
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationStatus.REJECTED)
        self.assertIn("interpretation request is not REQUESTED", result.reasons)
        self.assertEqual(result.interpretation, {"kind": "unavailable"})

    def test_interpretation_metadata_is_required(self):
        service = LearningStateExecutionLearningStateInterpretationService()
        request = self._make_request()
        for kwargs in (
            {"interpretation_id": " ", "interpreter_id": "interpreter-A", "interpretation_purpose": "inspect", "interpretation_rationale": {"x": 1}},
            {"interpretation_id": "interpretation-140", "interpreter_id": " ", "interpretation_purpose": "inspect", "interpretation_rationale": {"x": 1}},
            {"interpretation_id": "interpretation-140", "interpreter_id": "interpreter-A", "interpretation_purpose": " ", "interpretation_rationale": {"x": 1}},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    service.interpret(request, **kwargs)
        with self.assertRaises(ValueError):
            service.interpret(
                request,
                interpretation_id="interpretation-140",
                interpreter_id="interpreter-A",
                interpretation_purpose="inspect",
                interpretation_rationale=None,
            )

    def test_identity_must_be_distinct_from_sources(self):
        request = self._make_request()
        result = self._interpret(request, interpretation_id=request.request_id)
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationStatus.REJECTED)
        self.assertIn("interpretation identity must be distinct from request identity", result.reasons)

        result = self._interpret(request, interpretation_id=request.source_validation_id)
        self.assertIn("interpretation identity must be distinct from source validation identity", result.reasons)

    def test_request_lineage_is_checked_fail_closed(self):
        request = self._make_request(lineage={"request_id": "tampered", "validation_id": "read-validation-138", "read_id": "read-137", "consumption_request_id": "consumption-request-136"})
        result = self._interpret(request)
        self.assertIs(result.status, LearningStateExecutionLearningStateInterpretationStatus.REJECTED)
        self.assertIn("interpretation request lineage mismatch", result.reasons)

    def test_validation_lineage_is_checked_fail_closed(self):
        request = self._make_request(lineage={"request_id": "interpretation-request-139", "validation_id": "tampered", "read_id": "read-137", "consumption_request_id": "consumption-request-136"})
        result = self._interpret(request)
        self.assertIn("source validation lineage mismatch", result.reasons)

    def test_read_lineage_is_checked_fail_closed(self):
        request = self._make_request(lineage={"request_id": "interpretation-request-139", "validation_id": "read-validation-138", "read_id": "tampered", "consumption_request_id": "consumption-request-136"})
        result = self._interpret(request)
        self.assertIn("read lineage mismatch", result.reasons)

    def test_consumption_request_lineage_is_checked_fail_closed(self):
        request = self._make_request(lineage={"request_id": "interpretation-request-139", "validation_id": "read-validation-138", "read_id": "read-137", "consumption_request_id": "tampered"})
        result = self._interpret(request)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_provenance_and_payload_are_preserved(self):
        request = self._make_request()
        result = self._interpret(request)
        self.assertEqual(result.source_request_id, request.request_id)
        for field in (
            "source_validation_id", "read_id", "consumption_request_id", "integrity_id", "transition_id", "evidence_id",
            "state_key", "read_payload", "read_fingerprint", "computed_read_fingerprint",
            "reader_id", "read_purpose", "request_rationale", "confidence", "requester_id",
        ):
            self.assertEqual(getattr(result, field), getattr(request, field))

    def test_interpretation_is_deterministic_for_same_inputs(self):
        first = self._interpret()
        second = self._interpret()
        self.assertEqual(first, second)

    def test_interpretation_evidence_is_recursively_immutable(self):
        result = self._interpret(interpretation_rationale={"nested": {"items": [1, 2]}})
        self.assertIsInstance(result.interpretation, MappingProxyType)
        self.assertIsInstance(result.read_payload, MappingProxyType)
        with self.assertRaises(TypeError):
            result.interpretation["kind"] = "other"
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateInterpretationStatus.REJECTED

    def test_source_request_is_not_mutated(self):
        request = self._make_request()
        before = (request.status, request.lineage, request.read_payload, request.request_id)
        self._interpret(request)
        self.assertEqual((request.status, request.lineage, request.read_payload, request.request_id), before)

    def test_interpretation_has_no_truth_certainty_usefulness_or_authority_power(self):
        result = self._interpret()
        for name in (
            "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
            "mutates_state", "persists_state", "reads_durable_state", "rereads_durable_state",
            "is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "invokes_executor", "schedules_work", "plans_work", "updates_model",
            "mutates_memory", "mutates_policy",
        ):
            self.assertFalse(getattr(result, name))

    def test_interpretation_result_is_structural_not_semantic_truth(self):
        result = self._interpret()
        self.assertEqual(result.interpretation["keys"], ("mode", "threshold"))
        self.assertNotIn("meaning", result.interpretation)
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.establishes_correctness)
        self.assertFalse(result.establishes_certainty)
        self.assertFalse(result.establishes_usefulness)


if __name__ == "__main__":
    unittest.main()
