import unittest

from src.core.learning_state_interpretation_validation import LearningStateInterpretationValidationStatus
from src.core.learning_state_interpretation_validation_integrity import LearningStateInterpretationValidationIntegrityStatus
from src.core.learning_state_semantic_use_request import LearningStateSemanticUseRequest, LearningStateSemanticUseRequestStatus
from src.core.learning_state_semantic_use import LearningStateSemanticUseService, LearningStateSemanticUseStatus


class M23_112SemanticUseTests(unittest.TestCase):
    def _request(self, *, ready=True):
        return LearningStateSemanticUseRequest(
            request_id="semantic-use-request-111", integrity_id="integrity-110", validation_id="validation-109",
            interpretation_id="interpretation-108", source_request_id="request-107", read_validation_id="read-validation-106",
            read_id="read-105", consumption_request_id="consumption-104", source_validation_id="source-validation-103",
            source_integrity_id="source-integrity-102", transition_id="transition-98", evidence_id="evidence-97",
            application_id="application-96", state_key="demo.state", transition_fingerprint="a" * 64,
            source_application_fingerprint="b" * 64, computed_application_fingerprint="c" * 64, confidence=0.91,
            consumer_id="consumer-A", use_purpose="downstream-semantic-use",
            request_status=LearningStateSemanticUseRequestStatus.READY if ready else LearningStateSemanticUseRequestStatus.REJECTED,
            validation_status=LearningStateInterpretationValidationStatus.ACCEPTED,
            integrity_status=LearningStateInterpretationValidationIntegrityStatus.VALID,
            interpretation={"meaning": "unchanged", "nested": {"score": 3}},
            reasons={"source": "test"}, lineage={"test": "m23.112"},
        )

    def test_ready_request_produces_used_evidence(self):
        calls = []
        def consumer(state):
            calls.append(state)
            return {"used": True, "score": state["nested"]["score"]}
        result = LearningStateSemanticUseService().use(self._request(), use_id="use-112", consumer=consumer)
        self.assertEqual(result.use_status, LearningStateSemanticUseStatus.USED)
        self.assertTrue(result.is_used)
        self.assertEqual(len(calls), 1)

    def test_exact_request_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateSemanticUseService().use(object(), use_id="u", consumer=lambda value: {})

    def test_use_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateSemanticUseService().use(self._request(), use_id=" ", consumer=lambda value: {})

    def test_non_callable_consumer_is_rejected(self):
        result = LearningStateSemanticUseService().use(self._request(), use_id="u", consumer=None)
        self.assertEqual(result.use_status, LearningStateSemanticUseStatus.REJECTED)
        self.assertIn("callable consumer", result.failure_reason)

    def test_non_mapping_consumer_result_is_rejected(self):
        result = LearningStateSemanticUseService().use(self._request(), use_id="u", consumer=lambda value: 7)
        self.assertEqual(result.use_status, LearningStateSemanticUseStatus.REJECTED)
        self.assertIsNotNone(result.failure_reason)

    def test_consumer_exception_is_rejected(self):
        def consumer(value):
            raise RuntimeError("boom")
        result = LearningStateSemanticUseService().use(self._request(), use_id="u", consumer=consumer)
        self.assertEqual(result.use_status, LearningStateSemanticUseStatus.REJECTED)
        self.assertIn("raised an exception", result.failure_reason)

    def test_not_ready_request_is_not_consumed(self):
        called = []
        def consumer(value):
            called.append(value)
            return {}
        result = LearningStateSemanticUseService().use(self._request(ready=False), use_id="u", consumer=consumer)
        self.assertEqual(result.use_status, LearningStateSemanticUseStatus.REJECTED)
        self.assertEqual(called, [])

    def test_input_is_recursively_frozen(self):
        observed = []
        def consumer(value):
            observed.append(value)
            return {"echo": value}
        result = LearningStateSemanticUseService().use(self._request(), use_id="u", consumer=consumer)
        self.assertTrue(result.is_used)
        with self.assertRaises(TypeError):
            observed[0]["nested"] = {}
        self.assertEqual(result.result["echo"]["nested"]["score"], 3)

    def test_result_is_recursively_frozen(self):
        result = LearningStateSemanticUseService().use(self._request(), use_id="u", consumer=lambda value: {"nested": {"items": [1, 2]}})
        with self.assertRaises(TypeError):
            result.result["nested"] = {}
        self.assertEqual(result.result["nested"]["items"], (1, 2))

    def test_provenance_and_use_metadata_are_preserved(self):
        result = LearningStateSemanticUseService().use(self._request(), use_id="u", consumer=lambda value: {"ok": True})
        self.assertEqual(result.request_id, "semantic-use-request-111")
        self.assertEqual(result.integrity_id, "integrity-110")
        self.assertEqual(result.consumer_id, "consumer-A")
        self.assertEqual(result.use_purpose, "downstream-semantic-use")
        self.assertEqual(result.state_key, "demo.state")
        self.assertEqual(result.transition_fingerprint, "a" * 64)

    def test_reasons_and_lineage_are_frozen(self):
        result = LearningStateSemanticUseService().use(self._request(), use_id="u", consumer=lambda value: {}, reasons={"r": {"x": 1}}, lineage={"l": [1, 2]})
        with self.assertRaises(TypeError):
            result.reasons["r"] = {}
        with self.assertRaises(TypeError):
            result.lineage["l"] = []

    def test_used_evidence_establishes_no_semantic_certainty(self):
        result = LearningStateSemanticUseService().use(self._request(), use_id="u", consumer=lambda value: {"classification": "A"})
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.establishes_correctness)
        self.assertFalse(result.establishes_certainty)
        self.assertFalse(result.establishes_usefulness)

    def test_used_evidence_has_no_learning_or_authority_powers(self):
        result = LearningStateSemanticUseService().use(self._request(), use_id="u", consumer=lambda value: {})
        self.assertFalse(result.invokes_interpreter)
        self.assertFalse(result.invokes_learner)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)

    def test_consumer_invoked_at_most_once(self):
        calls = []
        def consumer(value):
            calls.append(1)
            return {"count": len(calls)}
        LearningStateSemanticUseService().use(self._request(), use_id="u", consumer=consumer)
        self.assertEqual(calls, [1])

    def test_equivalent_use_is_deterministic(self):
        def consumer(value):
            return {"fixed": True}
        first = LearningStateSemanticUseService().use(self._request(), use_id="u", consumer=consumer)
        second = LearningStateSemanticUseService().use(self._request(), use_id="u", consumer=consumer)
        self.assertEqual(first.request_id, second.request_id)
        self.assertEqual(first.result, second.result)
        self.assertEqual(first.reasons, second.reasons)
        self.assertEqual(first.lineage, second.lineage)

    def test_semantic_values_are_not_inspected_by_boundary(self):
        result = LearningStateSemanticUseService().use(self._request(), use_id="u", consumer=lambda value: {"accepted": True})
        self.assertTrue(result.is_used)


if __name__ == "__main__":
    unittest.main()
