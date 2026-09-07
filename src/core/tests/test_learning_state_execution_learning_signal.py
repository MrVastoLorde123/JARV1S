import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_evaluation import LearningStateExecutionEvaluation
from src.core.learning_state_execution_feedback import LearningStateExecutionFeedbackKind
from src.core.learning_state_execution_learning_signal import (
    LearningStateExecutionLearningSignal,
    LearningStateExecutionLearningSignalKind,
    LearningStateExecutionLearningSignalService,
)


class M23_125EvaluationLearningSignalTests(unittest.TestCase):
    def _make_evaluation(self):
        return LearningStateExecutionEvaluation(
            evaluation_id="evaluation-124",
            feedback_id="feedback-123",
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
            outcome_status="SUCCESS",
            feedback_kind=LearningStateExecutionFeedbackKind.SUCCESS_FEEDBACK,
            observed_consequence={"device_state": "changed"},
            executor_output={"executor": "raw"},
            failure_type=None,
            failure_message=None,
            objective="achieve intended device state",
            evaluator_id="evaluator-X",
            evaluation_purpose="compare-observation-to-objective",
            evaluation_judgment={"alignment": "positive", "score": 0.8},
            evaluation_context={"objective": "achieve intended device state"},
            reasons={"source": "m23.124"},
            lineage={"parent": "evaluation-124"},
        )

    def _make_signal(self, **overrides):
        evaluation = self._make_evaluation()
        kwargs = dict(
            signal_id="signal-125",
            signal_kind=LearningStateExecutionLearningSignalKind.POSITIVE,
            signal_purpose="feed-bounded-learning-pipeline",
        )
        kwargs.update(overrides)
        return LearningStateExecutionLearningSignalService().create(evaluation, **kwargs)

    def test_signal_kind_is_explicit(self):
        for kind in LearningStateExecutionLearningSignalKind:
            signal = self._make_signal(signal_id=f"signal-{kind.value.lower()}", signal_kind=kind)
            self.assertIs(signal.signal_kind, kind)

    def test_exact_evaluation_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningSignalService().create(
                object(),
                signal_id="signal-125",
                signal_kind=LearningStateExecutionLearningSignalKind.UNKNOWN,
                signal_purpose="feed-learning",
            )

    def test_signal_identity_and_purpose_are_required(self):
        service = LearningStateExecutionLearningSignalService()
        for field, value in (("signal_id", " "), ("signal_purpose", " ")):
            kwargs = dict(
                signal_id="signal-125",
                signal_kind=LearningStateExecutionLearningSignalKind.POSITIVE,
                signal_purpose="feed-learning",
            )
            kwargs[field] = value
            with self.assertRaises(ValueError):
                service.create(self._make_evaluation(), **kwargs)

    def test_signal_kind_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningSignalService().create(
                self._make_evaluation(),
                signal_id="signal-125",
                signal_kind="POSITIVE",
                signal_purpose="feed-learning",
            )

    def test_evaluation_evidence_is_preserved(self):
        evaluation = self._make_evaluation()
        signal = self._make_signal()
        for field in (
            "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id", "eligibility_id",
            "handling_id", "consumption_id", "receipt_id", "handoff_id", "integrity_id", "validation_id",
            "use_id", "request_id", "interpretation_id", "transition_id", "evidence_id", "application_id",
            "state_key", "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint",
            "confidence", "consumer_id", "objective", "evaluator_id", "evaluation_purpose", "feedback_kind",
            "outcome_status",
        ):
            self.assertEqual(getattr(signal, field), getattr(evaluation, field))

    def test_judgment_observation_and_execution_evidence_are_preserved(self):
        evaluation = self._make_evaluation()
        signal = self._make_signal()
        self.assertEqual(signal.evaluation_judgment, evaluation.evaluation_judgment)
        self.assertEqual(signal.observed_consequence, evaluation.observed_consequence)
        self.assertEqual(signal.executor_output, evaluation.executor_output)

    def test_payload_is_recursively_frozen(self):
        signal = self._make_signal(
            evaluation_context={"nested": {"value": 1}},
            signal_context={"nested": {"value": 2}, "items": [1, 2]},
            reasons={"nested": {"ok": True}},
            lineage={"chain": ["evaluation-124"]},
        )
        self.assertIsInstance(signal.signal_context, MappingProxyType)
        self.assertIsInstance(signal.signal_context["nested"], MappingProxyType)
        self.assertEqual(signal.signal_context["items"], (1, 2))
        self.assertIsInstance(signal.reasons, MappingProxyType)
        self.assertIsInstance(signal.lineage, MappingProxyType)

    def test_signal_artifact_is_immutable(self):
        signal = self._make_signal()
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            signal.signal_kind = LearningStateExecutionLearningSignalKind.NEGATIVE

    def test_source_evaluation_is_not_mutated(self):
        evaluation = self._make_evaluation()
        before = evaluation.evaluation_judgment
        self._make_signal()
        self.assertEqual(evaluation.evaluation_judgment, before)

    def test_signal_is_deterministic_for_same_inputs(self):
        left = self._make_signal()
        right = self._make_signal()
        self.assertEqual(left, right)

    def test_signal_has_no_learning_adaptation_truth_or_authority_power(self):
        signal = self._make_signal()
        for property_name in (
            "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
            "is_learning", "proposes_adaptation", "authorizes_execution", "authorizes_retry",
            "invokes_executor", "invokes_learner", "updates_model", "mutates_memory", "mutates_policy",
            "schedules_work", "plans_work",
        ):
            self.assertFalse(getattr(signal, property_name))

    def test_signal_does_not_infer_kind_from_judgment(self):
        signal = self._make_signal(
            signal_kind=LearningStateExecutionLearningSignalKind.UNKNOWN,
            signal_context={"judgment": "positive-looking content"},
        )
        self.assertIs(signal.signal_kind, LearningStateExecutionLearningSignalKind.UNKNOWN)

    def test_learning_signal_does_not_invoke_a_learner(self):
        signal = self._make_signal()
        self.assertFalse(signal.invokes_learner)
        self.assertFalse(signal.is_learning)


if __name__ == "__main__":
    unittest.main()
