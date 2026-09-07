import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_consumption_request import (
    LearningStateExecutionLearningStateConsumptionRequestService,
)
from src.core.learning_state_execution_learning_state_durable_read_consumption import (
    LearningStateExecutionLearningStateDurableReadConsumptionService,
    LearningStateExecutionLearningStateDurableReadConsumptionStatus,
)
from src.core.tests.test_learning_state_execution_learning_state_consumption_request import M23_136LearningStateConsumptionRequestTests


class _TrackingMapping(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.accesses = []

    def __contains__(self, key):
        self.accesses.append(("contains", key))
        return super().__contains__(key)

    def __getitem__(self, key):
        self.accesses.append(("getitem", key))
        return super().__getitem__(key)


class M23_137LearningStateDurableReadConsumptionTests(unittest.TestCase):
    def _make_request(self, scope=None):
        validation = M23_136LearningStateConsumptionRequestTests()._make_validation()
        return LearningStateExecutionLearningStateConsumptionRequestService().request(
            validation,
            consumption_request_id="consumption-request-136",
            requester_id="consumer-A",
            request_purpose="read-validated-learning-state",
            requested_scope=scope if scope is not None else {"state_key": "demo.state"},
            request_rationale={"basis": "validated-state"},
        )

    def _read(self, request=None, durable_state=None, **kwargs):
        return LearningStateExecutionLearningStateDurableReadConsumptionService().read(
            request or self._make_request(),
            durable_state if durable_state is not None else {"demo.state": {"threshold": 42, "mode": "safe"}},
            read_id=kwargs.pop("read_id", "read-137"),
            reader_id=kwargs.pop("reader_id", "reader-A"),
            read_purpose=kwargs.pop("read_purpose", "bounded-state-inspection"),
            **kwargs,
        )

    def test_requested_input_produces_read_evidence(self):
        result = self._read()
        self.assertIs(result.status, LearningStateExecutionLearningStateDurableReadConsumptionStatus.READ)
        self.assertTrue(result.is_read)
        self.assertTrue(result.reads_state)
        self.assertTrue(result.consumes_state)
        self.assertEqual(dict(result.read_payload), {"threshold": 42, "mode": "safe"})

    def test_rejected_request_fails_closed_without_read(self):
        request = self._make_request()
        object.__setattr__(request, "status", type(request.status).REJECTED)
        durable_state = _TrackingMapping({"demo.state": {"threshold": 42}})
        result = self._read(request=request, durable_state=durable_state)
        self.assertIs(result.status, LearningStateExecutionLearningStateDurableReadConsumptionStatus.REJECTED)
        self.assertFalse(result.reads_state)
        self.assertFalse(result.consumes_state)
        self.assertEqual(durable_state.accesses, [])
        self.assertIn("consumption request is not REQUESTED", result.reasons)

    def test_exact_request_type_is_required(self):
        with self.assertRaises(TypeError):
            self._read(request=object())

    def test_required_read_metadata_is_enforced(self):
        request = self._make_request()
        service = LearningStateExecutionLearningStateDurableReadConsumptionService()
        for kwargs in (
            {"read_id": " ", "reader_id": "reader-A", "read_purpose": "read"},
            {"read_id": "read-137", "reader_id": " ", "read_purpose": "read"},
            {"read_id": "read-137", "reader_id": "reader-A", "read_purpose": " "},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    service.read(request, {"demo.state": {"x": 1}}, **kwargs)

    def test_durable_state_must_be_a_mapping(self):
        with self.assertRaises(TypeError):
            self._read(durable_state=[("demo.state", {"x": 1})])

    def test_missing_state_key_is_rejected_without_payload(self):
        result = self._read(durable_state={"other.state": {"x": 1}})
        self.assertIs(result.status, LearningStateExecutionLearningStateDurableReadConsumptionStatus.REJECTED)
        self.assertIsNone(result.read_payload)
        self.assertIn("requested state key is absent from durable state", result.reasons)

    def test_scope_state_key_must_match_request(self):
        request = self._make_request({"state_key": "other.state"})
        result = self._read(request=request, durable_state={"demo.state": {"x": 1}, "other.state": {"x": 2}})
        self.assertIs(result.status, LearningStateExecutionLearningStateDurableReadConsumptionStatus.REJECTED)
        self.assertIn("requested scope state key mismatch", result.reasons)

    def test_field_bounded_read_returns_only_requested_fields(self):
        request = self._make_request({"state_key": "demo.state", "fields": ["threshold"]})
        result = self._read(request=request)
        self.assertIs(result.status, LearningStateExecutionLearningStateDurableReadConsumptionStatus.READ)
        self.assertEqual(dict(result.read_payload), {"threshold": 42})

    def test_missing_requested_field_is_rejected(self):
        request = self._make_request({"state_key": "demo.state", "fields": ["missing"]})
        result = self._read(request=request)
        self.assertIs(result.status, LearningStateExecutionLearningStateDurableReadConsumptionStatus.REJECTED)
        self.assertIsNone(result.read_payload)
        self.assertIn("requested scope field is absent from durable state", result.reasons)

    def test_field_bounded_read_requires_mapping_at_state_key(self):
        request = self._make_request({"state_key": "demo.state", "fields": ["threshold"]})
        result = self._read(request=request, durable_state={"demo.state": 42})
        self.assertIs(result.status, LearningStateExecutionLearningStateDurableReadConsumptionStatus.REJECTED)
        self.assertIn("field-bounded read requires mapped state at requested state key", result.reasons)

    def test_malformed_scope_fields_fail_closed(self):
        service = LearningStateExecutionLearningStateDurableReadConsumptionService()
        for fields in ([], ["ok", "ok"], [" "]):
            with self.subTest(fields=fields):
                request = self._make_request({"state_key": "demo.state", "fields": fields})
                result = service.read(request, {"demo.state": {"ok": 1}}, read_id="read-137", reader_id="reader-A", read_purpose="read")
                self.assertIs(result.status, LearningStateExecutionLearningStateDurableReadConsumptionStatus.REJECTED)

    def test_read_identity_must_be_distinct(self):
        request = self._make_request()
        result = self._read(request=request, read_id=request.consumption_request_id)
        self.assertIs(result.status, LearningStateExecutionLearningStateDurableReadConsumptionStatus.REJECTED)
        self.assertIn("read identity must be distinct from consumption request identity", result.reasons)

    def test_request_lineage_is_checked_fail_closed(self):
        request = self._make_request()
        object.__setattr__(request, "lineage", {"consumption_request_id": "tampered", "validation_id": request.validation_id})
        result = self._read(request=request)
        self.assertIs(result.status, LearningStateExecutionLearningStateDurableReadConsumptionStatus.REJECTED)
        self.assertIn("consumption request lineage mismatch", result.reasons)

    def test_validation_lineage_is_checked_fail_closed(self):
        request = self._make_request()
        object.__setattr__(request, "lineage", {"consumption_request_id": request.consumption_request_id, "validation_id": "tampered"})
        result = self._read(request=request)
        self.assertIs(result.status, LearningStateExecutionLearningStateDurableReadConsumptionStatus.REJECTED)
        self.assertIn("validation lineage mismatch", result.reasons)

    def test_read_evidence_is_recursively_immutable(self):
        result = self._read()
        self.assertIsInstance(result.read_payload, MappingProxyType)
        self.assertIsInstance(result.requested_scope, MappingProxyType)
        with self.assertRaises(TypeError):
            result.read_payload["threshold"] = 99
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateDurableReadConsumptionStatus.REJECTED

    def test_read_fingerprint_is_sha256_and_deterministic(self):
        first = self._read()
        second = self._read()
        self.assertEqual(first.read_fingerprint, first.computed_read_fingerprint)
        self.assertEqual(first.read_fingerprint, second.read_fingerprint)
        self.assertEqual(len(first.read_fingerprint), 64)
        self.assertTrue(all(char in "0123456789abcdef" for char in first.read_fingerprint))

    def test_source_request_and_durable_state_are_not_mutated(self):
        request = self._make_request({"state_key": "demo.state", "fields": ["threshold"]})
        durable_state = {"demo.state": {"threshold": 42, "mode": "safe"}}
        request_before = request.lineage
        durable_before = {"demo.state": dict(durable_state["demo.state"])}
        self._read(request=request, durable_state=durable_state)
        self.assertEqual(request.lineage, request_before)
        self.assertEqual(durable_state, durable_before)

    def test_provenance_scope_and_request_metadata_are_preserved(self):
        request = self._make_request({"state_key": "demo.state", "fields": ["threshold"]})
        result = self._read(request=request, reader_id="reader-B", read_purpose="inspect-threshold")
        for field in ("consumption_request_id", "validation_id", "integrity_id", "transition_id", "evidence_id", "state_key", "confidence"):
            self.assertEqual(getattr(result, field), getattr(request, field))
        self.assertEqual(result.requested_scope, request.requested_scope)
        self.assertEqual(result.request_rationale, request.request_rationale)
        self.assertEqual(result.reader_id, "reader-B")
        self.assertEqual(result.read_purpose, "inspect-threshold")

    def test_read_has_no_mutation_persistence_learning_interpretation_or_authority_powers(self):
        result = self._read()
        for name in (
            "mutates_state", "persists_state", "is_learning", "applies_learning", "authorizes_learning",
            "authorizes_execution", "authorizes_retry", "invokes_learner", "invokes_executor", "schedules_work",
            "plans_work", "updates_model", "mutates_memory", "mutates_policy", "interprets_state",
            "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
