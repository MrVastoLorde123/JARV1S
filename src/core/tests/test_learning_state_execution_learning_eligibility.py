import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_signal import (
    LearningStateExecutionLearningSignalKind,
    LearningStateExecutionLearningSignalService,
)
from src.core.learning_state_execution_learning_signal_integrity import (
    LearningStateExecutionLearningSignalIntegrityService,
    LearningStateExecutionLearningSignalIntegrityStatus,
)
from src.core.learning_state_execution_learning_eligibility import (
    LearningStateExecutionLearningEligibilityService,
    LearningStateExecutionLearningEligibilityStatus,
)


class M23_127LearningEligibilityTests(unittest.TestCase):
    def _make_integrity(self, *, status=None):
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
        signal = LearningStateExecutionLearningSignalService().create(
            evaluation,
            signal_id="signal-125",
            signal_kind=LearningStateExecutionLearningSignalKind.POSITIVE,
            signal_purpose="feed-learning",
        )
        integrity = LearningStateExecutionLearningSignalIntegrityService().validate(
            signal, integrity_id="integrity-126"
        )
        if status is LearningStateExecutionLearningSignalIntegrityStatus.INVALID:
            object.__setattr__(integrity, "status", LearningStateExecutionLearningSignalIntegrityStatus.INVALID)
        return integrity

    def test_valid_integrity_is_eligible(self):
        result = LearningStateExecutionLearningEligibilityService().evaluate(
            self._make_integrity(),
            eligibility_id="learning-eligibility-127",
            learner_id="learner-A",
            eligibility_purpose="future-learning",
        )
        self.assertIs(result.status, LearningStateExecutionLearningEligibilityStatus.ELIGIBLE)
        self.assertTrue(result.is_eligible)
        self.assertTrue(result.admits_learning)
        self.assertFalse(result.is_learning)

    def test_invalid_integrity_is_rejected_fail_closed(self):
        result = LearningStateExecutionLearningEligibilityService().evaluate(
            self._make_integrity(status=LearningStateExecutionLearningSignalIntegrityStatus.INVALID),
            eligibility_id="learning-eligibility-127",
            learner_id="learner-A",
            eligibility_purpose="future-learning",
        )
        self.assertIs(result.status, LearningStateExecutionLearningEligibilityStatus.REJECTED)
        self.assertFalse(result.is_eligible)
        self.assertFalse(result.admits_learning)

    def test_exact_integrity_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningEligibilityService().evaluate(
                object(), eligibility_id="learning-eligibility-127", learner_id="learner-A", eligibility_purpose="future-learning"
            )

    def test_required_identifiers_and_purpose_are_enforced(self):
        service = LearningStateExecutionLearningEligibilityService()
        integrity = self._make_integrity()
        for kwargs in (
            {"eligibility_id": " ", "learner_id": "learner-A", "eligibility_purpose": "future-learning"},
            {"eligibility_id": "learning-eligibility-127", "learner_id": " ", "eligibility_purpose": "future-learning"},
            {"eligibility_id": "learning-eligibility-127", "learner_id": "learner-A", "eligibility_purpose": " "},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    service.evaluate(integrity, **kwargs)

    def test_upstream_provenance_and_fingerprints_are_preserved(self):
        integrity = self._make_integrity()
        result = LearningStateExecutionLearningEligibilityService().evaluate(
            integrity, eligibility_id="learning-eligibility-127", learner_id="learner-A", eligibility_purpose="future-learning"
        )
        for field in (
            "integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id",
            "admission_id", "source_integrity_id", "validation_id", "use_id", "request_id", "interpretation_id",
            "source_request_id", "read_validation_id", "read_id", "consumption_request_id", "source_validation_id",
            "transition_id", "evidence_id", "application_id", "state_key", "transition_fingerprint",
            "source_application_fingerprint", "computed_application_fingerprint", "confidence", "consumer_id",
            "execution_target_id", "execution_purpose", "objective", "evaluator_id", "evaluation_purpose",
            "signal_kind", "signal_purpose",
        ):
            self.assertEqual(getattr(result, field), getattr(integrity, field))
        self.assertEqual(result.eligibility_source_id, integrity.integrity_id)
        self.assertEqual(result.learner_id, "learner-A")
        self.assertEqual(result.eligibility_purpose, "future-learning")

    def test_caller_reasons_and_lineage_are_preserved_and_frozen(self):
        result = LearningStateExecutionLearningEligibilityService().evaluate(
            self._make_integrity(),
            eligibility_id="learning-eligibility-127",
            learner_id="learner-A",
            eligibility_purpose="future-learning",
            reasons=("approved-for-next-boundary",),
            lineage={"chain": ["integrity-126", {"source": "signal-125"}]},
        )
        self.assertEqual(result.reasons, ("approved-for-next-boundary",))
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertEqual(result.lineage["chain"][1]["source"], "signal-125")

    def test_artifact_and_source_are_immutable(self):
        integrity = self._make_integrity()
        before = integrity.lineage
        result = LearningStateExecutionLearningEligibilityService().evaluate(
            integrity, eligibility_id="learning-eligibility-127", learner_id="learner-A", eligibility_purpose="future-learning"
        )
        self.assertEqual(integrity.lineage, before)
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningEligibilityStatus.REJECTED

    def test_eligibility_is_deterministic_for_same_inputs(self):
        service = LearningStateExecutionLearningEligibilityService()
        first = service.evaluate(
            self._make_integrity(), eligibility_id="learning-eligibility-127", learner_id="learner-A", eligibility_purpose="future-learning"
        )
        second = service.evaluate(
            self._make_integrity(), eligibility_id="learning-eligibility-127", learner_id="learner-A", eligibility_purpose="future-learning"
        )
        self.assertEqual(first, second)

    def test_reason_validation_rejects_malformed_reasons(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningEligibilityService().evaluate(
                self._make_integrity(),
                eligibility_id="learning-eligibility-127",
                learner_id="learner-A",
                eligibility_purpose="future-learning",
                reasons=("ok", " "),
            )

    def test_eligibility_has_no_learning_or_authority_powers(self):
        result = LearningStateExecutionLearningEligibilityService().evaluate(
            self._make_integrity(), eligibility_id="learning-eligibility-127", learner_id="learner-A", eligibility_purpose="future-learning"
        )
        for name in (
            "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
            "is_learning", "proposes_adaptation", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "updates_model", "mutates_memory", "mutates_policy", "invokes_executor",
            "schedules_work", "plans_work",
        ):
            self.assertFalse(getattr(result, name))

    def test_eligibility_does_not_mutate_integrity_status(self):
        integrity = self._make_integrity()
        before = integrity.status
        LearningStateExecutionLearningEligibilityService().evaluate(
            integrity, eligibility_id="learning-eligibility-127", learner_id="learner-A", eligibility_purpose="future-learning"
        )
        self.assertIs(integrity.status, before)


if __name__ == "__main__":
    unittest.main()
