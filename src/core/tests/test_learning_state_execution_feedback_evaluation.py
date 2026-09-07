import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_admission import LearningStateExecutionAdmissionStatus
from src.core.learning_state_execution_attempt import LearningStateExecutionAttemptStatus
from src.core.learning_state_execution_evaluation import (
    LearningStateExecutionEvaluationService,
)
from src.core.learning_state_execution_feedback import (
    LearningStateExecutionFeedback,
    LearningStateExecutionFeedbackKind,
    LearningStateExecutionFeedbackService,
)
from src.core.learning_state_execution_outcome import (
    LearningStateExecutionOutcome,
    LearningStateExecutionOutcomeStatus,
)


class M23_124ExecutionFeedbackEvaluationTests(unittest.TestCase):
    def _make_feedback(self, *, status=LearningStateExecutionOutcomeStatus.SUCCESS):
        outcome = LearningStateExecutionOutcome(
            outcome_id="outcome-122", attempt_id="attempt-121", admission_id="admission-120",
            eligibility_id="eligibility-119", handling_id="handling-118", consumption_id="consumption-117",
            receipt_id="receipt-116", handoff_id="handoff-115", integrity_id="integrity-114",
            validation_id="validation-113", use_id="use-112", request_id="semantic-use-111",
            interpretation_id="interpretation-108", source_request_id="request-107", read_validation_id="read-validation-106",
            read_id="read-105", consumption_request_id="consumption-104", source_validation_id="source-validation-103",
            source_integrity_id="source-integrity-102", transition_id="transition-98", evidence_id="evidence-97",
            application_id="application-96", state_key="demo.state", transition_fingerprint="a" * 64,
            source_application_fingerprint="b" * 64, computed_application_fingerprint="c" * 64, confidence=0.91,
            consumer_id="consumer-A", use_purpose="downstream-semantic-use", downstream_recipient_id="receiver-X",
            downstream_handler_id="handler-X", handling_purpose="route-for-processing", execution_target_id="executor-X",
            execution_purpose="perform-bounded-work", admission_status=LearningStateExecutionAdmissionStatus.AUTHORIZED,
            attempt_status=LearningStateExecutionAttemptStatus.ATTEMPTED, outcome_status=status,
            executor_output={"raw": "executor"}, failure_type="RuntimeError" if status is LearningStateExecutionOutcomeStatus.FAILURE else None,
            failure_message="failed" if status is LearningStateExecutionOutcomeStatus.FAILURE else None,
            observed_consequence={"state": "changed", "nested": {"value": 9}}, observation_source_id="sensor-X",
            observation_purpose="observe-device-state", reasons={"source": "m23.122"}, lineage={"parent": "outcome-122"},
        )
        return LearningStateExecutionFeedbackService().record(outcome, feedback_id="feedback-123")

    def _evaluate(self, feedback=None, **kwargs):
        defaults = dict(
            evaluation_id="evaluation-124", objective="reach-target-state", evaluator_id="evaluator-A",
            evaluation_purpose="assess-objective", evaluation_judgment={"alignment": "partial", "score": 0.5},
        )
        defaults.update(kwargs)
        return LearningStateExecutionEvaluationService().evaluate(feedback or self._make_feedback(), **defaults)

    def test_exact_feedback_type_is_required(self):
        with self.assertRaises(TypeError):
            self._evaluate(object())

    def test_explicit_evaluation_identity_and_objective_fields_are_required(self):
        for field in ("evaluation_id", "objective", "evaluator_id", "evaluation_purpose"):
            kwargs = dict(evaluation_id="evaluation-124", objective="reach-target-state", evaluator_id="evaluator-A", evaluation_purpose="assess-objective", evaluation_judgment={"alignment": "partial"})
            kwargs[field] = " "
            with self.assertRaises(ValueError):
                LearningStateExecutionEvaluationService().evaluate(self._make_feedback(), **kwargs)

    def test_evaluation_judgment_is_explicitly_recorded(self):
        evaluation = self._evaluate()
        self.assertEqual(evaluation.objective, "reach-target-state")
        self.assertEqual(evaluation.evaluator_id, "evaluator-A")
        self.assertEqual(evaluation.evaluation_judgment["alignment"], "partial")

    def test_evaluation_preserves_feedback_and_observation_provenance(self):
        feedback = self._make_feedback()
        evaluation = self._evaluate(feedback)
        for field in (
            "feedback_id", "outcome_id", "attempt_id", "admission_id", "eligibility_id", "handling_id",
            "consumption_id", "receipt_id", "handoff_id", "integrity_id", "validation_id", "use_id",
            "request_id", "interpretation_id", "transition_id", "evidence_id", "application_id", "state_key",
            "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint",
            "execution_target_id", "execution_purpose", "confidence", "consumer_id", "downstream_handler_id",
            "feedback_kind", "outcome_status", "observed_consequence", "executor_output",
        ):
            self.assertEqual(getattr(evaluation, field), getattr(feedback, field))

    def test_evaluation_artifact_is_immutable(self):
        evaluation = self._evaluate()
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            evaluation.objective = "changed"

    def test_evaluation_payload_is_recursively_frozen(self):
        evaluation = self._evaluate(
            evaluation_judgment={"nested": {"score": 0.5}},
            evaluation_context={"nested": {"objective": True}, "items": [1, 2]},
            reasons={"nested": {"reason": True}}, lineage={"chain": ["feedback-123"]},
        )
        self.assertIsInstance(evaluation.evaluation_judgment, MappingProxyType)
        self.assertIsInstance(evaluation.evaluation_judgment["nested"], MappingProxyType)
        self.assertIsInstance(evaluation.evaluation_context, MappingProxyType)
        self.assertIsInstance(evaluation.reasons, MappingProxyType)
        self.assertIsInstance(evaluation.lineage, MappingProxyType)

    def test_evaluation_has_no_truth_learning_or_authority_power(self):
        evaluation = self._evaluate()
        for property_name in (
            "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
            "authorizes_execution", "authorizes_retry", "invokes_executor", "invokes_learner", "updates_model",
            "mutates_memory", "mutates_policy", "schedules_work", "plans_work",
        ):
            self.assertFalse(getattr(evaluation, property_name))

    def test_evaluation_does_not_invoke_execution(self):
        evaluation = self._evaluate()
        self.assertFalse(evaluation.invokes_executor)

    def test_source_feedback_is_not_mutated(self):
        feedback = self._make_feedback()
        before = feedback.observed_consequence
        self._evaluate(feedback)
        self.assertEqual(feedback.observed_consequence, before)

    def test_evaluation_is_deterministic_for_same_inputs(self):
        kwargs = dict(evaluation_id="evaluation-124", objective="reach-target-state", evaluator_id="evaluator-A", evaluation_purpose="assess-objective", evaluation_judgment={"alignment": "partial", "score": 0.5})
        service = LearningStateExecutionEvaluationService()
        self.assertEqual(service.evaluate(self._make_feedback(), **kwargs), service.evaluate(self._make_feedback(), **kwargs))

    def test_evaluation_retains_failure_feedback_as_evidence_without_reinterpreting_failure(self):
        feedback = self._make_feedback(status=LearningStateExecutionOutcomeStatus.FAILURE)
        evaluation = self._evaluate(feedback, evaluation_judgment={"alignment": "missed-objective"})
        self.assertIs(evaluation.feedback_kind, LearningStateExecutionFeedbackKind.FAILURE_FEEDBACK)
        self.assertEqual(evaluation.failure_type, "RuntimeError")
        self.assertEqual(evaluation.failure_message, "failed")

    def test_evaluation_does_not_require_a_learning_signal(self):
        evaluation = self._evaluate()
        self.assertFalse(evaluation.invokes_learner)


if __name__ == "__main__":
    unittest.main()
