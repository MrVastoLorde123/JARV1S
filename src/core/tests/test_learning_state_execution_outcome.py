import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_admission import LearningStateExecutionAdmissionStatus
from src.core.learning_state_execution_attempt import (
    LearningStateExecutionAttempt,
    LearningStateExecutionAttemptStatus,
)
from src.core.learning_state_execution_outcome import (
    LearningStateExecutionOutcome,
    LearningStateExecutionOutcomeService,
    LearningStateExecutionOutcomeStatus,
)


class M23_122ExecutionOutcomeTests(unittest.TestCase):
    def _attempt(self, *, status=LearningStateExecutionAttemptStatus.ATTEMPTED):
        return LearningStateExecutionAttempt(
            attempt_id="attempt-121",
            admission_id="admission-120",
            eligibility_id="eligibility-119",
            handling_id="handling-118",
            consumption_id="consumption-117",
            receipt_id="receipt-116",
            handoff_id="handoff-115",
            integrity_id="integrity-114",
            validation_id="validation-113",
            use_id="use-112",
            request_id="semantic-use-111",
            interpretation_id="interpretation-108",
            source_request_id="request-107",
            read_validation_id="read-validation-106",
            read_id="read-105",
            consumption_request_id="consumption-104",
            source_validation_id="source-validation-103",
            source_integrity_id="source-integrity-102",
            transition_id="transition-98",
            evidence_id="evidence-97",
            application_id="application-96",
            state_key="demo.state",
            transition_fingerprint="a" * 64,
            source_application_fingerprint="b" * 64,
            computed_application_fingerprint="c" * 64,
            confidence=0.91,
            consumer_id="consumer-A",
            use_purpose="downstream-semantic-use",
            downstream_recipient_id="receiver-X",
            downstream_handler_id="handler-X",
            handling_purpose="route-for-processing",
            execution_target_id="executor-X",
            execution_purpose="perform-bounded-work",
            admission_status=LearningStateExecutionAdmissionStatus.AUTHORIZED,
            attempt_status=status,
            executor_output={"executor": "raw", "nested": {"value": 7}},
            failure_type="RuntimeError" if status is LearningStateExecutionAttemptStatus.FAILED else None,
            failure_message="device unavailable" if status is LearningStateExecutionAttemptStatus.FAILED else None,
            reasons={"source": "m23.121"},
            lineage={"parent": "attempt-121"},
        )

    def _observe(self, **kwargs):
        defaults = {
            "outcome_id": "outcome-122",
            "outcome_status": LearningStateExecutionOutcomeStatus.SUCCESS,
            "observed_consequence": {"device_state": "changed", "nested": {"value": 9}},
            "observation_source_id": "sensor-X",
            "observation_purpose": "observe-device-state",
        }
        defaults.update(kwargs)
        return LearningStateExecutionOutcomeService().observe(self._attempt(), **defaults)

    def test_successful_observation_is_recorded_without_reexecution(self):
        outcome = self._observe()
        self.assertEqual(outcome.outcome_status, LearningStateExecutionOutcomeStatus.SUCCESS)
        self.assertTrue(outcome.is_observed)
        self.assertFalse(outcome.invokes_executor)

    def test_failure_partial_and_unknown_are_explicit_statuses(self):
        service = LearningStateExecutionOutcomeService()
        for status in (
            LearningStateExecutionOutcomeStatus.FAILURE,
            LearningStateExecutionOutcomeStatus.PARTIAL,
            LearningStateExecutionOutcomeStatus.UNKNOWN,
        ):
            outcome = service.observe(
                self._attempt(), outcome_id=f"outcome-{status.value.lower()}", outcome_status=status,
                observed_consequence={"raw": status.value}, observation_source_id="observer-X",
                observation_purpose="observe-execution-consequence"
            )
            self.assertEqual(outcome.outcome_status, status)

    def test_failed_attempt_can_have_an_observed_outcome(self):
        attempt = self._attempt(status=LearningStateExecutionAttemptStatus.FAILED)
        outcome = LearningStateExecutionOutcomeService().observe(
            attempt,
            outcome_id="outcome-122",
            outcome_status=LearningStateExecutionOutcomeStatus.FAILURE,
            observed_consequence={"device_state": "unchanged"},
            observation_source_id="sensor-X",
            observation_purpose="observe-device-state",
        )
        self.assertEqual(outcome.attempt_status, LearningStateExecutionAttemptStatus.FAILED)
        self.assertEqual(outcome.failure_type, "RuntimeError")

    def test_rejected_attempt_cannot_produce_execution_outcome(self):
        attempt = self._attempt(status=LearningStateExecutionAttemptStatus.REJECTED)
        with self.assertRaises(ValueError):
            LearningStateExecutionOutcomeService().observe(
                attempt,
                outcome_id="outcome-122",
                outcome_status=LearningStateExecutionOutcomeStatus.UNKNOWN,
                observed_consequence={"raw": "none"},
                observation_source_id="observer-X",
                observation_purpose="observe",
            )

    def test_exact_attempt_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionOutcomeService().observe(
                object(), outcome_id="outcome-122",
                outcome_status=LearningStateExecutionOutcomeStatus.UNKNOWN,
                observed_consequence=None, observation_source_id="observer-X",
                observation_purpose="observe",
            )

    def test_outcome_status_type_is_required(self):
        with self.assertRaises(TypeError):
            self._observe(outcome_status="SUCCESS")

    def test_required_identity_and_observation_fields_are_non_empty(self):
        service = LearningStateExecutionOutcomeService()
        base = dict(
            outcome_status=LearningStateExecutionOutcomeStatus.SUCCESS,
            observed_consequence={"raw": True}, observation_source_id="observer-X",
            observation_purpose="observe",
        )
        for field in ("outcome_id", "observation_source_id", "observation_purpose"):
            kwargs = dict(base)
            kwargs[field] = " "
            with self.assertRaises(ValueError):
                service.observe(self._attempt(), outcome_id=kwargs.pop("outcome_id", "outcome-122"), **kwargs)

    def test_observed_consequence_is_preserved_recursively_and_immutable(self):
        consequence = {"state": {"value": 7}, "items": [1, 2]}
        outcome = self._observe(observed_consequence=consequence)
        self.assertIsInstance(outcome.observed_consequence, MappingProxyType)
        self.assertIsInstance(outcome.observed_consequence["state"], MappingProxyType)
        self.assertEqual(outcome.observed_consequence["items"], (1, 2))
        with self.assertRaises(TypeError):
            outcome.observed_consequence["new"] = True

    def test_executor_output_is_preserved_as_attempt_provenance(self):
        outcome = self._observe()
        self.assertEqual(outcome.executor_output["executor"], "raw")
        self.assertIsInstance(outcome.executor_output, MappingProxyType)

    def test_provenance_and_fingerprints_are_preserved(self):
        source = self._attempt()
        outcome = self._observe()
        for field in (
            "attempt_id", "admission_id", "eligibility_id", "handling_id", "consumption_id", "receipt_id",
            "handoff_id", "integrity_id", "validation_id", "use_id", "request_id", "interpretation_id",
            "transition_id", "evidence_id", "application_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint", "execution_target_id",
            "execution_purpose", "confidence", "consumer_id", "downstream_handler_id",
        ):
            self.assertEqual(getattr(outcome, field), getattr(source, field))

    def test_source_attempt_is_not_mutated(self):
        source = self._attempt()
        before = source.executor_output
        self._observe()
        self.assertEqual(source.executor_output, before)

    def test_outcome_has_no_truth_or_learning_power(self):
        outcome = self._observe()
        for property_name in (
            "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
            "authorizes_execution", "authorizes_retry", "invokes_executor", "schedules_work", "plans_work",
            "transforms_semantic_result", "interprets_semantic_result", "invokes_learner", "updates_model",
            "mutates_memory", "mutates_policy",
        ):
            self.assertFalse(getattr(outcome, property_name))

    def test_outcome_artifact_is_immutable(self):
        outcome = self._observe()
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            outcome.outcome_status = LearningStateExecutionOutcomeStatus.FAILURE

    def test_reasons_and_lineage_are_recursively_frozen(self):
        outcome = self._observe(
            reasons={"reason": {"nested": True}},
            lineage={"chain": ["attempt-121"]},
        )
        self.assertIsInstance(outcome.reasons, MappingProxyType)
        self.assertIsInstance(outcome.reasons["reason"], MappingProxyType)
        self.assertIsInstance(outcome.lineage, MappingProxyType)
        self.assertEqual(outcome.lineage["chain"], ("attempt-121",))

    def test_deterministic_for_same_inputs(self):
        left = self._observe()
        right = self._observe()
        self.assertEqual(left, right)

    def test_observation_does_not_require_or_invoke_an_executor(self):
        called = []
        outcome = LearningStateExecutionOutcomeService().observe(
            self._attempt(), outcome_id="outcome-122",
            outcome_status=LearningStateExecutionOutcomeStatus.SUCCESS,
            observed_consequence={"raw": "observed"},
            observation_source_id="observer-X", observation_purpose="observe",
        )
        self.assertEqual(called, [])
        self.assertFalse(outcome.invokes_executor)


if __name__ == "__main__":
    unittest.main()
