import unittest
from types import MappingProxyType

from src.core.learning_state_consumption_read import LearningStateConsumptionReadStatus
from src.core.learning_state_consumption_read_validation import (
    LearningStateConsumptionReadValidation,
    LearningStateConsumptionReadValidationStatus,
)
from src.core.learning_state_interpretation_request import (
    LearningStateInterpretationRequest,
    LearningStateInterpretationRequestService,
    LearningStateInterpretationRequestStatus,
)
from src.core.learning_state_interpretation import (
    LearningStateInterpretationService,
    LearningStateInterpretationStatus,
)


class LearningStateInterpretationTests(unittest.TestCase):
    def _validation(self, *, status=LearningStateConsumptionReadValidationStatus.ACCEPTED):
        return LearningStateConsumptionReadValidation(
            validation_id="validation-106",
            read_id="read-105",
            request_id="request-104",
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
            read_status=LearningStateConsumptionReadStatus.CONSUMED,
            state={"temperature": {"trend": "rising"}, "count": 3},
            validation_status=status,
            failure_reason=None if status is LearningStateConsumptionReadValidationStatus.ACCEPTED else "rejected read",
            reasons={"validation_status": status.value},
            lineage={"validation_id": "validation-106"},
        )

    def _request(self, *, status=LearningStateConsumptionReadValidationStatus.ACCEPTED):
        validation = self._validation(status=status)
        return LearningStateInterpretationRequestService().request(validation, request_id="interpret-request-107")

    def test_ready_request_is_interpreted(self):
        request = self._request()
        calls = []
        result = LearningStateInterpretationService().interpret(
            request,
            interpretation_id="interpretation-108",
            interpreter=lambda state: calls.append(state) or {"trend": state["temperature"]["trend"]},
        )
        self.assertEqual(result.interpretation_status, LearningStateInterpretationStatus.INTERPRETED)
        self.assertEqual(result.interpretation, MappingProxyType({"trend": "rising"}))
        self.assertEqual(len(calls), 1)

    def test_rejected_request_does_not_call_interpreter(self):
        request = self._request(status=LearningStateConsumptionReadValidationStatus.REJECTED)
        calls = []
        result = LearningStateInterpretationService().interpret(
            request,
            interpretation_id="interpretation-108",
            interpreter=lambda state: calls.append(state) or {"unused": True},
        )
        self.assertEqual(result.interpretation_status, LearningStateInterpretationStatus.REJECTED)
        self.assertEqual(calls, [])
        self.assertIsNone(result.interpretation)

    def test_missing_interpreter_fails_closed(self):
        result = LearningStateInterpretationService().interpret(
            self._request(),
            interpretation_id="interpretation-108",
            interpreter=None,
        )
        self.assertEqual(result.interpretation_status, LearningStateInterpretationStatus.REJECTED)
        self.assertIn("callable interpreter", result.failure_reason)

    def test_non_mapping_interpretation_fails_closed(self):
        result = LearningStateInterpretationService().interpret(
            self._request(),
            interpretation_id="interpretation-108",
            interpreter=lambda state: "meaning",
        )
        self.assertEqual(result.interpretation_status, LearningStateInterpretationStatus.REJECTED)
        self.assertIn("non-mapping", result.failure_reason)

    def test_interpreter_exception_fails_closed(self):
        def broken(_state):
            raise RuntimeError("boom")

        result = LearningStateInterpretationService().interpret(
            self._request(),
            interpretation_id="interpretation-108",
            interpreter=broken,
        )
        self.assertEqual(result.interpretation_status, LearningStateInterpretationStatus.REJECTED)
        self.assertIn("raised an exception", result.failure_reason)

    def test_interpreter_is_invoked_exactly_once(self):
        calls = []
        request = self._request()
        LearningStateInterpretationService().interpret(
            request,
            interpretation_id="interpretation-108",
            interpreter=lambda state: calls.append(state) or {"ok": True},
        )
        self.assertEqual(len(calls), 1)

    def test_request_provenance_and_fingerprints_are_preserved(self):
        request = self._request()
        result = LearningStateInterpretationService().interpret(
            request,
            interpretation_id="interpretation-108",
            interpreter=lambda state: {"trend": "rising"},
        )
        for name in (
            "request_id", "read_validation_id", "read_id", "consumption_request_id",
            "source_validation_id", "integrity_id", "transition_id", "evidence_id",
            "application_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint", "confidence",
        ):
            self.assertEqual(getattr(result, name), getattr(request, name))

    def test_interpretation_is_recursively_immutable(self):
        source = {"nested": {"values": [1, {"x": True}]}}
        result = LearningStateInterpretationService().interpret(
            self._request(),
            interpretation_id="interpretation-108",
            interpreter=lambda state: source,
        )
        self.assertIsInstance(result.interpretation, MappingProxyType)
        self.assertIsInstance(result.interpretation["nested"], MappingProxyType)
        self.assertIsInstance(result.interpretation["nested"]["values"], tuple)
        with self.assertRaises(TypeError):
            result.interpretation["new"] = 1

    def test_source_request_is_not_mutated(self):
        request = self._request()
        before = request.state
        LearningStateInterpretationService().interpret(
            request,
            interpretation_id="interpretation-108",
            interpreter=lambda state: {"trend": "rising"},
        )
        self.assertEqual(request.state, before)
        self.assertEqual(request.request_status, LearningStateInterpretationRequestStatus.READY)

    def test_interpreter_owns_semantic_transformation(self):
        request = self._request()
        marker = {"meaning": "semantic-result"}
        result = LearningStateInterpretationService().interpret(
            request,
            interpretation_id="interpretation-108",
            interpreter=lambda state: marker,
        )
        self.assertEqual(result.interpretation["meaning"], "semantic-result")
        self.assertEqual(request.state["temperature"]["trend"], "rising")

    def test_result_declares_no_truth_learning_or_authority(self):
        result = LearningStateInterpretationService().interpret(
            self._request(),
            interpretation_id="interpretation-108",
            interpreter=lambda state: {"trend": "rising"},
        )
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.establishes_correctness)
        self.assertFalse(result.establishes_certainty)
        self.assertFalse(result.invokes_learner)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)

    def test_reasons_and_lineage_are_immutable(self):
        result = LearningStateInterpretationService().interpret(
            self._request(),
            interpretation_id="interpretation-108",
            interpreter=lambda state: {"trend": "rising"},
            reasons={"nested": {"x": 1}},
            lineage={"chain": ["request"]},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["new"] = 1
        with self.assertRaises(TypeError):
            result.lineage["new"] = 1

    def test_result_is_immutable(self):
        result = LearningStateInterpretationService().interpret(
            self._request(),
            interpretation_id="interpretation-108",
            interpreter=lambda state: {"trend": "rising"},
        )
        with self.assertRaises(Exception):
            result.interpretation_status = LearningStateInterpretationStatus.REJECTED

    def test_deterministic_construction(self):
        request = self._request()
        interpreter = lambda state: {"trend": state["temperature"]["trend"], "count": state["count"]}
        first = LearningStateInterpretationService().interpret(request, interpretation_id="interpretation-108", interpreter=interpreter)
        second = LearningStateInterpretationService().interpret(request, interpretation_id="interpretation-108", interpreter=interpreter)
        self.assertEqual(first, second)

    def test_blank_interpretation_id_fails_closed(self):
        with self.assertRaises(ValueError):
            LearningStateInterpretationService().interpret(
                self._request(),
                interpretation_id=" ",
                interpreter=lambda state: {"ok": True},
            )


if __name__ == "__main__":
    unittest.main()
