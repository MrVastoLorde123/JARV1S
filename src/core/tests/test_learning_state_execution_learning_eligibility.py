import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_execution_learning_signal import (
    LearningStateExecutionLearningSignalKind,
    LearningStateExecutionLearningSignalStatus,
)
from src.core.learning_state_execution_learning_state_execution_learning_signal_integrity import (
    LearningStateExecutionLearningSignalIntegrity,
    LearningStateExecutionLearningSignalIntegrityStatus,
)
from src.core.learning_state_execution_learning_eligibility import (
    LearningStateExecutionLearningEligibilityService,
    LearningStateExecutionLearningEligibilityStatus,
)


class M23_159LearningEligibilityTests(unittest.TestCase):
    def _make_integrity(self, *, status=LearningStateExecutionLearningSignalIntegrityStatus.VALID):
        return LearningStateExecutionLearningSignalIntegrity(
            integrity_id="integrity-158",
            signal_id="signal-157",
            evaluation_id="evaluation-156",
            feedback_id="feedback-155",
            outcome_id="outcome-154",
            attempt_id="attempt-153",
            admission_id="admission-152",
            eligibility_id="eligibility-151",
            handling_id="handling-150",
            consumption_id="consumption-149",
            receipt_id="receipt-148",
            handoff_id="handoff-147",
            inherited_integrity_id="integrity-previous",
            validation_id="validation-145",
            semantic_use_id="semantic-use-144",
            source_request_id="request-143",
            source_request_lineage_id="request-lineage-143",
            source_validation_id="source-validation-142",
            source_validation_lineage_id="source-validation-lineage-142",
            interpretation_id="interpretation-141",
            read_id="read-140",
            consumption_request_id="consumption-139",
            requester_id="requester-A",
            consumer_id="consumer-A",
            handoff_target_id="handoff-target-A",
            recipient_id="recipient-A",
            handling_target_id="handler-A",
            execution_target_id="executor-A",
            signal_kind=LearningStateExecutionLearningSignalKind.POSITIVE,
            signal_purpose="feed-learning",
            signal_context={"source": "execution-feedback", "features": ["stable", {"score": 0.9}]},
            signal_status=LearningStateExecutionLearningSignalStatus.RECORDED,
            source_signal_fingerprint="a" * 64,
            computed_signal_fingerprint="a" * 64,
            status=status,
            reasons=("learning-signal-integrity-verified",),
            lineage={
                "integrity_id": "integrity-158",
                "signal_id": "signal-157",
                "inherited_integrity_id": "integrity-previous",
            },
        )

    def _evaluate(self, integrity=None, **kwargs):
        params = {
            "eligibility_id": "learning-eligibility-159",
            "learner_id": "learner-A",
            "eligibility_purpose": "enter-future-learning",
        }
        params.update(kwargs)
        return LearningStateExecutionLearningEligibilityService().evaluate(
            integrity or self._make_integrity(), **params
        )

    def test_valid_integrity_is_eligible(self):
        result = self._evaluate()
        self.assertIs(result.status, LearningStateExecutionLearningEligibilityStatus.ELIGIBLE)
        self.assertTrue(result.is_eligible)
        self.assertTrue(result.admits_learning)
        self.assertFalse(result.is_learning)

    def test_invalid_integrity_fails_closed(self):
        result = self._evaluate(
            self._make_integrity(status=LearningStateExecutionLearningSignalIntegrityStatus.INVALID)
        )
        self.assertIs(result.status, LearningStateExecutionLearningEligibilityStatus.REJECTED)
        self.assertFalse(result.is_eligible)
        self.assertFalse(result.admits_learning)

    def test_exact_integrity_type_is_required(self):
        with self.assertRaises(TypeError):
            self._evaluate(object())

    def test_eligibility_identity_must_be_distinct(self):
        with self.assertRaises(ValueError):
            self._evaluate(eligibility_id="integrity-158")

    def test_required_learner_identity_and_purpose_are_enforced(self):
        service = LearningStateExecutionLearningEligibilityService()
        integrity = self._make_integrity()
        for kwargs in (
            {"eligibility_id": "learning-eligibility-159", "learner_id": " ", "eligibility_purpose": "enter-future-learning"},
            {"eligibility_id": "learning-eligibility-159", "learner_id": "learner-A", "eligibility_purpose": " "},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    service.evaluate(integrity, **kwargs)

    def test_upstream_provenance_and_signal_evidence_are_preserved(self):
        integrity = self._make_integrity()
        result = self._evaluate(integrity)
        for field in (
            "integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id",
            "handling_id", "consumption_id", "receipt_id", "handoff_id", "inherited_integrity_id", "validation_id",
            "semantic_use_id", "source_request_id", "source_request_lineage_id", "source_validation_id",
            "source_validation_lineage_id", "interpretation_id", "read_id", "consumption_request_id", "requester_id",
            "consumer_id", "handoff_target_id", "recipient_id", "handling_target_id", "execution_target_id",
            "signal_kind", "signal_purpose", "signal_context", "signal_status", "source_signal_fingerprint",
            "computed_signal_fingerprint",
        ):
            self.assertEqual(getattr(result, field), getattr(integrity, field))
        self.assertEqual(result.eligibility_source_id, integrity.integrity_id)
        self.assertEqual(result.learner_id, "learner-A")
        self.assertEqual(result.eligibility_purpose, "enter-future-learning")

    def test_immediate_integrity_identity_is_distinct_from_inherited_integrity(self):
        result = self._evaluate()
        self.assertEqual(result.eligibility_source_id, "integrity-158")
        self.assertEqual(result.integrity_id, "integrity-158")
        self.assertEqual(result.inherited_integrity_id, "integrity-previous")

    def test_custom_reasons_and_lineage_are_preserved_and_frozen(self):
        result = self._evaluate(
            reasons=("approved-for-next-learning-boundary",),
            lineage={"chain": ["integrity-158", {"upstream": "integrity-previous"}]},
        )
        self.assertEqual(result.reasons, ("approved-for-next-learning-boundary",))
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.lineage["chain"], tuple)
        self.assertIsInstance(result.lineage["chain"][1], MappingProxyType)

    def test_reason_validation_rejects_malformed_reasons(self):
        with self.assertRaises(TypeError):
            self._evaluate(reasons=("valid", " "))

    def test_artifact_is_immutable_and_source_is_not_mutated(self):
        integrity = self._make_integrity()
        source_status = integrity.status
        result = self._evaluate(integrity)
        self.assertIs(integrity.status, source_status)
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningEligibilityStatus.REJECTED
        with self.assertRaises(TypeError):
            result.lineage["x"] = "y"

    def test_eligibility_is_deterministic_for_same_inputs(self):
        first = self._evaluate()
        second = self._evaluate()
        self.assertEqual(first, second)

    def test_eligibility_has_no_learning_or_authority_power(self):
        result = self._evaluate()
        for name in (
            "proposes_adaptation", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "invokes_executor", "updates_model", "mutates_memory", "mutates_policy",
            "schedules_work", "plans_work", "is_learning", "establishes_truth", "establishes_correctness",
            "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
