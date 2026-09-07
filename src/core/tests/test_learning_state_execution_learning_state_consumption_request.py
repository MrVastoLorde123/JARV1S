import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_consumption_request import (
    LearningStateExecutionLearningStateConsumptionRequestService,
    LearningStateExecutionLearningStateConsumptionRequestStatus,
)
from src.core.learning_state_execution_learning_state_validation import (
    LearningStateExecutionLearningStateValidationService,
)
from src.core.tests.test_learning_state_execution_learning_state_validation import M23_135LearningStateValidationTests


class M23_136LearningStateConsumptionRequestTests(unittest.TestCase):
    def _make_validation(self):
        integrity = M23_135LearningStateValidationTests()._make_integrity()
        return LearningStateExecutionLearningStateValidationService().validate(
            integrity,
            validation_id="validation-135",
            validator_id="validator-A",
            validation_purpose="validate-state-transition",
            validation_rationale={"basis": "integrity-checked"},
            lineage={
                "validation_id": "validation-135",
                "integrity_id": integrity.integrity_id,
                "transition_id": integrity.transition_id,
                "evidence_id": integrity.evidence_id,
            },
        )

    def test_validated_input_produces_requested_consumption_request(self):
        result = LearningStateExecutionLearningStateConsumptionRequestService().request(
            self._make_validation(),
            consumption_request_id="consumption-request-136",
            requester_id="consumer-A",
            request_purpose="read-validated-learning-state",
            requested_scope={"state_key": "demo.state"},
            request_rationale={"basis": "validated-state"},
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionRequestStatus.REQUESTED)
        self.assertTrue(result.is_requested)
        self.assertTrue(result.admits_read)
        self.assertFalse(result.reads_state)
        self.assertFalse(result.consumes_state)

    def test_rejected_validation_fails_closed(self):
        validation = self._make_validation()
        object.__setattr__(validation, "status", type(validation.status).REJECTED)
        result = LearningStateExecutionLearningStateConsumptionRequestService().request(
            validation,
            consumption_request_id="consumption-request-136",
            requester_id="consumer-A",
            request_purpose="read-validated-learning-state",
            requested_scope={"state_key": "demo.state"},
            request_rationale={"basis": "rejected-source"},
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionRequestStatus.REJECTED)
        self.assertFalse(result.admits_read)
        self.assertFalse(result.reads_state)

    def test_exact_validation_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningStateConsumptionRequestService().request(
                object(),
                consumption_request_id="consumption-request-136",
                requester_id="consumer-A",
                request_purpose="read-validated-learning-state",
                requested_scope={"state_key": "demo.state"},
                request_rationale={"basis": "validated-state"},
            )

    def test_required_request_metadata_is_enforced(self):
        service = LearningStateExecutionLearningStateConsumptionRequestService()
        validation = self._make_validation()
        cases = (
            {"consumption_request_id": " ", "requester_id": "consumer-A", "request_purpose": "read", "requested_scope": {"x": 1}, "request_rationale": "why"},
            {"consumption_request_id": "request-136", "requester_id": " ", "request_purpose": "read", "requested_scope": {"x": 1}, "request_rationale": "why"},
            {"consumption_request_id": "request-136", "requester_id": "consumer-A", "request_purpose": " ", "requested_scope": {"x": 1}, "request_rationale": "why"},
        )
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    service.request(validation, **kwargs)

    def test_scope_and_rationale_are_required(self):
        service = LearningStateExecutionLearningStateConsumptionRequestService()
        validation = self._make_validation()
        with self.assertRaises(ValueError):
            service.request(validation, consumption_request_id="request-136", requester_id="consumer-A", request_purpose="read", requested_scope=None, request_rationale="why")
        with self.assertRaises(ValueError):
            service.request(validation, consumption_request_id="request-136", requester_id="consumer-A", request_purpose="read", requested_scope={"x": 1}, request_rationale=None)

    def test_validation_lineage_is_checked_fail_closed(self):
        validation = self._make_validation()
        object.__setattr__(validation, "lineage", {"validation_id": "tampered-validation", "integrity_id": validation.integrity_id, "transition_id": validation.transition_id, "evidence_id": validation.evidence_id})
        result = LearningStateExecutionLearningStateConsumptionRequestService().request(
            validation,
            consumption_request_id="consumption-request-136",
            requester_id="consumer-A",
            request_purpose="read",
            requested_scope={"state_key": "demo.state"},
            request_rationale="why",
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionRequestStatus.REJECTED)
        self.assertIn("validation lineage mismatch", result.reasons)

    def test_integrity_lineage_is_checked_fail_closed(self):
        validation = self._make_validation()
        object.__setattr__(validation, "lineage", {"validation_id": validation.validation_id, "integrity_id": "tampered-integrity", "transition_id": validation.transition_id, "evidence_id": validation.evidence_id})
        result = LearningStateExecutionLearningStateConsumptionRequestService().request(
            validation,
            consumption_request_id="consumption-request-136",
            requester_id="consumer-A",
            request_purpose="read",
            requested_scope={"state_key": "demo.state"},
            request_rationale="why",
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionRequestStatus.REJECTED)
        self.assertIn("integrity lineage mismatch", result.reasons)

    def test_transition_and_evidence_lineage_are_checked_fail_closed(self):
        service = LearningStateExecutionLearningStateConsumptionRequestService()
        for field, message in (("transition_id", "transition lineage mismatch"), ("evidence_id", "evidence lineage mismatch")):
            validation = self._make_validation()
            lineage = dict(validation.lineage)
            lineage[field] = "tampered"
            object.__setattr__(validation, "lineage", lineage)
            result = service.request(validation, consumption_request_id="request-136", requester_id="consumer-A", request_purpose="read", requested_scope={"state_key": "demo.state"}, request_rationale="why")
            self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionRequestStatus.REJECTED)
            self.assertIn(message, result.reasons)

    def test_request_identity_must_be_distinct_from_validation(self):
        validation = self._make_validation()
        result = LearningStateExecutionLearningStateConsumptionRequestService().request(
            validation,
            consumption_request_id=validation.validation_id,
            requester_id="consumer-A",
            request_purpose="read",
            requested_scope={"state_key": "demo.state"},
            request_rationale="why",
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionRequestStatus.REJECTED)
        self.assertIn("consumption request identity must be distinct from validation identity", result.reasons)

    def test_transition_fingerprint_mismatch_is_rejected_without_repair(self):
        validation = self._make_validation()
        object.__setattr__(validation, "transition_fingerprint", "tampered")
        result = LearningStateExecutionLearningStateConsumptionRequestService().request(
            validation,
            consumption_request_id="request-136",
            requester_id="consumer-A",
            request_purpose="read",
            requested_scope={"state_key": "demo.state"},
            request_rationale="why",
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionRequestStatus.REJECTED)
        self.assertIn("transition fingerprint mismatch", result.reasons)
        self.assertEqual(result.transition_fingerprint, "tampered")

    def test_identical_states_are_rejected(self):
        validation = self._make_validation()
        object.__setattr__(validation, "state_after", validation.state_before)
        result = LearningStateExecutionLearningStateConsumptionRequestService().request(validation, consumption_request_id="request-136", requester_id="consumer-A", request_purpose="read", requested_scope={"state_key": "demo.state"}, request_rationale="why")
        self.assertIs(result.status, LearningStateExecutionLearningStateConsumptionRequestStatus.REJECTED)
        self.assertIn("state before and after are identical", result.reasons)

    def test_provenance_and_request_fields_are_preserved(self):
        validation = self._make_validation()
        result = LearningStateExecutionLearningStateConsumptionRequestService().request(
            validation,
            consumption_request_id="consumption-request-136",
            requester_id="consumer-B",
            request_purpose="inspect-bounded-state",
            requested_scope={"state_key": "demo.state", "fields": ["threshold"]},
            request_rationale={"reason": ["validated", {"scope": "bounded"}]},
        )
        for field in (
            "validation_id", "integrity_id", "transition_id", "evidence_id", "state_key",
            "transition_fingerprint", "computed_transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "application_id", "decision_id", "proposal_id", "eligibility_id",
            "source_integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id",
            "admission_id", "source_validation_id", "use_id", "request_id", "interpretation_id", "source_request_id",
            "read_validation_id", "read_id", "confidence", "consumer_id", "execution_target_id",
        ):
            self.assertEqual(getattr(result, field), getattr(validation, field))
        self.assertEqual(result.requester_id, "consumer-B")
        self.assertEqual(result.request_purpose, "inspect-bounded-state")

    def test_scope_rationale_reasons_and_lineage_are_frozen(self):
        result = LearningStateExecutionLearningStateConsumptionRequestService().request(
            self._make_validation(),
            consumption_request_id="request-136",
            requester_id="consumer-A",
            request_purpose="read",
            requested_scope={"nested": [{"field": "threshold"}]},
            request_rationale={"nested": ["why", {"bounded": True}]},
            reasons=("explicit-request",),
            lineage={"chain": ["validation-135", {"source": "state-validation"}]},
        )
        self.assertIsInstance(result.requested_scope, MappingProxyType)
        self.assertIsInstance(result.request_rationale, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertEqual(result.reasons, ("explicit-request",))

    def test_source_validation_is_not_mutated(self):
        validation = self._make_validation()
        before = validation.lineage
        LearningStateExecutionLearningStateConsumptionRequestService().request(validation, consumption_request_id="request-136", requester_id="consumer-A", request_purpose="read", requested_scope={"state_key": "demo.state"}, request_rationale="why")
        self.assertEqual(validation.lineage, before)

    def test_request_is_deterministic_for_same_inputs(self):
        service = LearningStateExecutionLearningStateConsumptionRequestService()
        kwargs = dict(consumption_request_id="request-136", requester_id="consumer-A", request_purpose="read", requested_scope={"state_key": "demo.state"}, request_rationale="why")
        first = service.request(self._make_validation(), **kwargs)
        second = service.request(self._make_validation(), **kwargs)
        self.assertEqual(first, second)

    def test_request_artifact_is_immutable(self):
        result = LearningStateExecutionLearningStateConsumptionRequestService().request(self._make_validation(), consumption_request_id="request-136", requester_id="consumer-A", request_purpose="read", requested_scope={"state_key": "demo.state"}, request_rationale="why")
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateConsumptionRequestStatus.REJECTED

    def test_request_has_no_read_consumption_mutation_learning_or_execution_powers(self):
        result = LearningStateExecutionLearningStateConsumptionRequestService().request(self._make_validation(), consumption_request_id="request-136", requester_id="consumer-A", request_purpose="read", requested_scope={"state_key": "demo.state"}, request_rationale="why")
        for name in (
            "reads_state", "consumes_state", "mutates_state", "persists_state", "is_learning", "applies_learning",
            "authorizes_learning", "authorizes_execution", "authorizes_retry", "invokes_learner", "invokes_executor",
            "schedules_work", "plans_work", "updates_model", "mutates_memory", "mutates_policy", "interprets_state",
            "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_malformed_reasons_are_rejected(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningStateConsumptionRequestService().request(self._make_validation(), consumption_request_id="request-136", requester_id="consumer-A", request_purpose="read", requested_scope={"state_key": "demo.state"}, request_rationale="why", reasons=("ok", " "))


if __name__ == "__main__":
    unittest.main()
