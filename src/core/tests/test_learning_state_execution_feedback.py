import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_feedback import (
    LearningStateExecutionFeedback,
    LearningStateExecutionFeedbackKind,
    LearningStateExecutionFeedbackService,
)
from src.core.learning_state_execution_outcome import (
    LearningStateExecutionOutcome,
    LearningStateExecutionOutcomeStatus,
)


class M23_123ExecutionOutcomeFeedbackTests(unittest.TestCase):
    def _make_outcome(self, *, status=LearningStateExecutionOutcomeStatus.SUCCESS):
        return LearningStateExecutionOutcome(
            outcome_id="outcome-122",
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
            admission_status=__import__(
                "src.core.learning_state_execution_admission",
                fromlist=["LearningStateExecutionAdmissionStatus"],
            ).LearningStateExecutionAdmissionStatus.AUTHORIZED,
            attempt_status=__import__(
                "src.core.learning_state_execution_attempt",
                fromlist=["LearningStateExecutionAttemptStatus"],
            ).LearningStateExecutionAttemptStatus.ATTEMPTED,
            outcome_status=status,
            executor_output={"raw": "executor", "nested": {"value": 7}},
            failure_type="RuntimeError" if status is LearningStateExecutionOutcomeStatus.FAILURE else None,
            failure_message="device unavailable" if status is LearningStateExecutionOutcomeStatus.FAILURE else None,
            observed_consequence={"device_state": "changed", "nested": {"value": 9}},
            observation_source_id="sensor-X",
            observation_purpose="observe-device-state",
            reasons={"source": "m23.122"},
            lineage={"parent": "outcome-122"},
        )

    def test_success_maps_to_success_feedback(self):
        feedback = LearningStateExecutionFeedbackService().record(self._make_outcome(), feedback_id="feedback-123")
        self.assertEqual(feedback.feedback_kind, LearningStateExecutionFeedbackKind.SUCCESS_FEEDBACK)
        self.assertEqual(feedback.outcome_status, LearningStateExecutionOutcomeStatus.SUCCESS)

    def test_all_outcome_statuses_map_explicitly(self):
        expected = {
            LearningStateExecutionOutcomeStatus.SUCCESS: LearningStateExecutionFeedbackKind.SUCCESS_FEEDBACK,
            LearningStateExecutionOutcomeStatus.FAILURE: LearningStateExecutionFeedbackKind.FAILURE_FEEDBACK,
            LearningStateExecutionOutcomeStatus.PARTIAL: LearningStateExecutionFeedbackKind.PARTIAL_FEEDBACK,
            LearningStateExecutionOutcomeStatus.UNKNOWN: LearningStateExecutionFeedbackKind.UNKNOWN_FEEDBACK,
        }
        service = LearningStateExecutionFeedbackService()
        for status, kind in expected.items():
            feedback = service.record(self._make_outcome(status=status), feedback_id=f"feedback-{status.value.lower()}")
            self.assertIs(feedback.feedback_kind, kind)

    def test_exact_outcome_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionFeedbackService().record(object(), feedback_id="feedback-123")

    def test_feedback_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateExecutionFeedbackService().record(self._make_outcome(), feedback_id=" ")

    def test_feedback_context_is_recursively_frozen(self):
        feedback = LearningStateExecutionFeedbackService().record(
            self._make_outcome(),
            feedback_id="feedback-123",
            feedback_context={"nested": {"value": 1}, "items": [1, 2]},
        )
        self.assertIsInstance(feedback.feedback_context, MappingProxyType)
        self.assertIsInstance(feedback.feedback_context["nested"], MappingProxyType)
        self.assertEqual(feedback.feedback_context["items"], (1, 2))

    def test_reasons_and_lineage_are_recursively_frozen(self):
        feedback = LearningStateExecutionFeedbackService().record(
            self._make_outcome(),
            feedback_id="feedback-123",
            reasons={"nested": {"ok": True}},
            lineage={"chain": ["outcome-122"]},
        )
        self.assertIsInstance(feedback.reasons, MappingProxyType)
        self.assertIsInstance(feedback.lineage, MappingProxyType)
        self.assertIsInstance(feedback.reasons["nested"], MappingProxyType)
        self.assertEqual(feedback.lineage["chain"], ("outcome-122",))

    def test_observed_consequence_and_executor_output_are_preserved(self):
        outcome = self._make_outcome()
        feedback = LearningStateExecutionFeedbackService().record(outcome, feedback_id="feedback-123")
        self.assertEqual(feedback.observed_consequence, outcome.observed_consequence)
        self.assertEqual(feedback.executor_output, outcome.executor_output)

    def test_provenance_and_fingerprints_are_preserved(self):
        outcome = self._make_outcome()
        feedback = LearningStateExecutionFeedbackService().record(outcome, feedback_id="feedback-123")
        for field in (
            "outcome_id", "attempt_id", "admission_id", "eligibility_id", "handling_id", "consumption_id",
            "receipt_id", "handoff_id", "integrity_id", "validation_id", "use_id", "request_id",
            "interpretation_id", "transition_id", "evidence_id", "application_id", "state_key",
            "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint",
            "execution_target_id", "execution_purpose", "confidence", "consumer_id", "downstream_handler_id",
        ):
            self.assertEqual(getattr(feedback, field), getattr(outcome, field))

    def test_feedback_artifact_is_immutable(self):
        feedback = LearningStateExecutionFeedbackService().record(self._make_outcome(), feedback_id="feedback-123")
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            feedback.feedback_kind = LearningStateExecutionFeedbackKind.FAILURE_FEEDBACK

    def test_feedback_has_no_truth_learning_or_authority_power(self):
        feedback = LearningStateExecutionFeedbackService().record(self._make_outcome(), feedback_id="feedback-123")
        for property_name in (
            "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
            "invokes_executor", "authorizes_execution", "authorizes_retry", "revokes_authority",
            "invokes_learner", "updates_model", "mutates_memory", "mutates_policy", "schedules_work", "plans_work",
        ):
            self.assertFalse(getattr(feedback, property_name))

    def test_feedback_does_not_reexecute(self):
        service = LearningStateExecutionFeedbackService()
        feedback = service.record(self._make_outcome(), feedback_id="feedback-123")
        self.assertFalse(feedback.invokes_executor)

    def test_source_outcome_is_not_mutated(self):
        outcome = self._make_outcome()
        before = outcome.observed_consequence
        LearningStateExecutionFeedbackService().record(outcome, feedback_id="feedback-123")
        self.assertEqual(outcome.observed_consequence, before)

    def test_feedback_is_deterministic_for_same_inputs(self):
        service = LearningStateExecutionFeedbackService()
        left = service.record(self._make_outcome(), feedback_id="feedback-123")
        right = service.record(self._make_outcome(), feedback_id="feedback-123")
        self.assertEqual(left, right)

    def test_feedback_kind_cannot_mismatch_source_outcome(self):
        with self.assertRaises(ValueError):
            LearningStateExecutionFeedback(
                **{
                    **self._feedback_kwargs(),
                    "feedback_kind": LearningStateExecutionFeedbackKind.FAILURE_FEEDBACK,
                }
            )

    def _feedback_kwargs(self):
        outcome = self._make_outcome()
        return {
            "feedback_id": "feedback-123",
            "outcome_id": outcome.outcome_id,
            "attempt_id": outcome.attempt_id,
            "admission_id": outcome.admission_id,
            "eligibility_id": outcome.eligibility_id,
            "handling_id": outcome.handling_id,
            "consumption_id": outcome.consumption_id,
            "receipt_id": outcome.receipt_id,
            "handoff_id": outcome.handoff_id,
            "integrity_id": outcome.integrity_id,
            "validation_id": outcome.validation_id,
            "use_id": outcome.use_id,
            "request_id": outcome.request_id,
            "interpretation_id": outcome.interpretation_id,
            "source_request_id": outcome.source_request_id,
            "read_validation_id": outcome.read_validation_id,
            "read_id": outcome.read_id,
            "consumption_request_id": outcome.consumption_request_id,
            "source_validation_id": outcome.source_validation_id,
            "source_integrity_id": outcome.source_integrity_id,
            "transition_id": outcome.transition_id,
            "evidence_id": outcome.evidence_id,
            "application_id": outcome.application_id,
            "state_key": outcome.state_key,
            "transition_fingerprint": outcome.transition_fingerprint,
            "source_application_fingerprint": outcome.source_application_fingerprint,
            "computed_application_fingerprint": outcome.computed_application_fingerprint,
            "confidence": outcome.confidence,
            "consumer_id": outcome.consumer_id,
            "use_purpose": outcome.use_purpose,
            "downstream_recipient_id": outcome.downstream_recipient_id,
            "downstream_handler_id": outcome.downstream_handler_id,
            "handling_purpose": outcome.handling_purpose,
            "execution_target_id": outcome.execution_target_id,
            "execution_purpose": outcome.execution_purpose,
            "outcome_status": outcome.outcome_status,
            "feedback_kind": LearningStateExecutionFeedbackKind.SUCCESS_FEEDBACK,
            "observed_consequence": outcome.observed_consequence,
            "executor_output": outcome.executor_output,
            "failure_type": outcome.failure_type,
            "failure_message": outcome.failure_message,
            "feedback_context": {"kind": "success"},
            "reasons": {"source": "m23.122"},
            "lineage": {"feedback_id": "feedback-123"},
        }


if __name__ == "__main__":
    unittest.main()
