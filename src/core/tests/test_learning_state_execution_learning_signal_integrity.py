import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_signal import (
    LearningStateExecutionLearningSignal,
    LearningStateExecutionLearningSignalKind,
    LearningStateExecutionLearningSignalService,
)
from src.core.learning_state_execution_learning_signal_integrity import (
    LearningStateExecutionLearningSignalIntegrity,
    LearningStateExecutionLearningSignalIntegrityService,
    LearningStateExecutionLearningSignalIntegrityStatus,
)


class M23_126LearningSignalIntegrityTests(unittest.TestCase):
    def _make_signal(self, **overrides):
        kwargs = dict(
            signal_id="signal-125",
            signal_kind=LearningStateExecutionLearningSignalKind.POSITIVE,
            signal_purpose="feed-learning",
        )
        kwargs.update(overrides)
        evaluation = __import__(
            "src.core.learning_state_execution_evaluation",
            fromlist=["LearningStateExecutionEvaluation"],
        ).LearningStateExecutionEvaluation(
            evaluation_id="evaluation-124", feedback_id="feedback-123", outcome_id="outcome-122",
            attempt_id="attempt-121", admission_id="admission-120", eligibility_id="eligibility-119",
            handling_id="handling-118", consumption_id="consumption-117", receipt_id="receipt-116",
            handoff_id="handoff-115", integrity_id="integrity-114", validation_id="validation-113",
            use_id="use-112", request_id="semantic-use-111", interpretation_id="interpretation-108",
            source_request_id="request-107", read_validation_id="read-validation-106", read_id="read-105",
            consumption_request_id="consumption-104", source_validation_id="source-validation-103",
            source_integrity_id="source-integrity-102", transition_id="transition-98", evidence_id="evidence-97",
            application_id="application-96", state_key="demo.state", transition_fingerprint="a" * 64,
            source_application_fingerprint="b" * 64, computed_application_fingerprint="c" * 64, confidence=0.91,
            consumer_id="consumer-A", use_purpose="semantic-use", downstream_recipient_id="receiver-X",
            downstream_handler_id="handler-X", handling_purpose="route", execution_target_id="executor-X",
            execution_purpose="perform", outcome_status=__import__(
                "src.core.learning_state_execution_outcome", fromlist=["LearningStateExecutionOutcomeStatus"]
            ).LearningStateExecutionOutcomeStatus.SUCCESS,
            feedback_kind=__import__(
                "src.core.learning_state_execution_feedback", fromlist=["LearningStateExecutionFeedbackKind"]
            ).LearningStateExecutionFeedbackKind.SUCCESS_FEEDBACK,
            observed_consequence={"state": "changed"}, executor_output={"raw": "result"},
            failure_type=None, failure_message=None, objective="reach-target", evaluator_id="evaluator-A",
            evaluation_purpose="assess", evaluation_judgment={"score": 0.8},
            evaluation_context={"objective": "reach-target"}, reasons={"source": "m23.124"},
            lineage={"evaluation_id": "evaluation-124"},
        )
        return LearningStateExecutionLearningSignalService().create(evaluation, **kwargs)

    def test_valid_signal_produces_valid_integrity(self):
        signal = self._make_signal()
        integrity = LearningStateExecutionLearningSignalIntegrityService().validate(
            signal, integrity_id="integrity-126"
        )
        self.assertIs(integrity.status, LearningStateExecutionLearningSignalIntegrityStatus.VALID)
        self.assertTrue(integrity.is_valid)
        self.assertTrue(integrity.validates_signal)

    def test_exact_signal_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningSignalIntegrityService().validate(object(), integrity_id="integrity-126")

    def test_integrity_id_is_required(self):
        with self.assertRaises(ValueError):
            LearningStateExecutionLearningSignalIntegrityService().validate(self._make_signal(), integrity_id=" ")

    def test_signal_provenance_is_preserved(self):
        signal = self._make_signal()
        integrity = LearningStateExecutionLearningSignalIntegrityService().validate(signal, integrity_id="integrity-126")
        for field in (
            "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id",
            "eligibility_id", "handling_id", "consumption_id", "receipt_id", "handoff_id", "source_integrity_id",
            "validation_id", "transition_id", "evidence_id", "application_id", "state_key",
            "transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint",
            "confidence", "consumer_id", "execution_target_id", "execution_purpose", "objective",
            "evaluator_id", "evaluation_purpose", "signal_purpose", "signal_kind",
        ):
            self.assertEqual(getattr(integrity, field), getattr(signal, field))

    def test_integrity_preserves_evaluation_and_observation_evidence(self):
        signal = self._make_signal()
        integrity = LearningStateExecutionLearningSignalIntegrityService().validate(signal, integrity_id="integrity-126")
        self.assertEqual(integrity.evaluation_judgment, signal.evaluation_judgment)
        self.assertEqual(integrity.observed_consequence, signal.observed_consequence)
        self.assertEqual(integrity.executor_output, signal.executor_output)
        self.assertEqual(integrity.outcome_status, signal.outcome_status)
        self.assertEqual(integrity.feedback_kind, signal.feedback_kind)

    def test_fingerprints_and_signal_kind_are_validated(self):
        signal = self._make_signal()
        integrity = LearningStateExecutionLearningSignalIntegrityService().validate(signal, integrity_id="integrity-126")
        self.assertEqual(len(integrity.transition_fingerprint), 64)
        self.assertEqual(len(integrity.source_application_fingerprint), 64)
        self.assertEqual(len(integrity.computed_application_fingerprint), 64)
        self.assertIsInstance(integrity.signal_kind, LearningStateExecutionLearningSignalKind)

    def test_invalid_provenance_is_reported_without_repair(self):
        signal = self._make_signal()
        object.__setattr__(signal, "lineage", MappingProxyType({"evaluation_id": "different-evaluation"}))
        integrity = LearningStateExecutionLearningSignalIntegrityService().validate(signal, integrity_id="integrity-126")
        self.assertIs(integrity.status, LearningStateExecutionLearningSignalIntegrityStatus.INVALID)
        self.assertTrue(any("mismatch" in reason for reason in integrity.reasons))

    def test_explicit_invalid_reasons_are_preserved(self):
        integrity = LearningStateExecutionLearningSignalIntegrityService().validate(
            self._make_signal(), integrity_id="integrity-126", reasons=("caller-declared-check",)
        )
        self.assertEqual(integrity.reasons, ("caller-declared-check",))

    def test_reasons_and_lineage_are_immutable(self):
        integrity = LearningStateExecutionLearningSignalIntegrityService().validate(
            self._make_signal(), integrity_id="integrity-126", lineage={"chain": ["signal-125"]}
        )
        self.assertIsInstance(integrity.lineage, MappingProxyType)
        self.assertEqual(integrity.lineage["chain"], ("signal-125",))

    def test_evidence_is_recursively_frozen(self):
        signal = self._make_signal()
        object.__setattr__(signal, "evaluation_judgment", MappingProxyType({"nested": MappingProxyType({"x": 1})}))
        integrity = LearningStateExecutionLearningSignalIntegrityService().validate(signal, integrity_id="integrity-126")
        self.assertIsInstance(integrity.evaluation_judgment, MappingProxyType)
        self.assertIsInstance(integrity.evaluation_judgment["nested"], MappingProxyType)

    def test_integrity_artifact_is_immutable(self):
        integrity = LearningStateExecutionLearningSignalIntegrityService().validate(self._make_signal(), integrity_id="integrity-126")
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            integrity.status = LearningStateExecutionLearningSignalIntegrityStatus.INVALID

    def test_source_signal_is_not_mutated(self):
        signal = self._make_signal()
        before = signal.signal_context
        LearningStateExecutionLearningSignalIntegrityService().validate(signal, integrity_id="integrity-126")
        self.assertEqual(signal.signal_context, before)

    def test_integrity_is_deterministic_for_same_inputs(self):
        service = LearningStateExecutionLearningSignalIntegrityService()
        self.assertEqual(
            service.validate(self._make_signal(), integrity_id="integrity-126"),
            service.validate(self._make_signal(), integrity_id="integrity-126"),
        )

    def test_integrity_has_no_learning_authority_or_execution_power(self):
        integrity = LearningStateExecutionLearningSignalIntegrityService().validate(self._make_signal(), integrity_id="integrity-126")
        for name in (
            "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
            "is_learning", "proposes_adaptation", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "updates_model", "mutates_memory", "mutates_policy", "invokes_executor",
            "schedules_work", "plans_work",
        ):
            self.assertFalse(getattr(integrity, name))

    def test_integrity_does_not_change_source_signal_kind(self):
        signal = self._make_signal(signal_kind=LearningStateExecutionLearningSignalKind.UNKNOWN)
        integrity = LearningStateExecutionLearningSignalIntegrityService().validate(signal, integrity_id="integrity-126")
        self.assertIs(integrity.signal_kind, LearningStateExecutionLearningSignalKind.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
