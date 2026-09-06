import unittest

from src.core.environment_world_model_rollback_repair_retry_feedback_evaluation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Service,
)
from src.core.environment_world_model_rollback_repair_retry_feedback_v2 import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackV2,
    EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_outcome_v2 import (
    EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_signal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Service,
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_signal_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Service,
    EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_eligibility_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2,
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Service,
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status,
)


class M23_60LearningEligibilityV2Tests(unittest.TestCase):
    def _make_integrity(self, *, success: bool = True):
        feedback = EnvironmentWorldModelRollbackRepairRetryFeedbackV2(
            feedback_id="feedback-1",
            outcome_id="outcome-1",
            integrity_id="upstream-integrity-1",
            execution_id="execution-1",
            preparation_id="preparation-1",
            decision_id="decision-1",
            integrity_decision_id="integrity-decision-1",
            proposal_id="proposal-1",
            assessment_id="assessment-1",
            evaluation_id="evaluation-1",
            environment_id="env-1",
            expected_model_id="model-expected",
            observed_model_id="model-observed",
            outcome_status=(
                EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.SUCCESS
                if success else EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.FAILURE
            ),
            feedback_status=(
                EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.SUCCESS_SIGNAL
                if success else EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.FAILURE_SIGNAL
            ),
            result_fingerprint="result-fp-1" if success else None,
            failure_reason=None if success else "provider unavailable",
            worker_id="worker-1",
        )
        evaluation = EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Service().evaluate(
            feedback, evaluation_id="evaluation-1", confidence=0.8
        )
        signal = EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Service().emit(
            evaluation, signal_id="signal-1"
        )
        return EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Service().verify(
            signal, integrity_id="signal-integrity-1"
        )

    def test_valid_integrity_becomes_eligible_without_adaptation_permission(self):
        eligibility = EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Service().evaluate(
            self._make_integrity(), eligibility_id="eligibility-1"
        )
        self.assertEqual(
            eligibility.eligibility_status,
            EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE,
        )
        self.assertFalse(eligibility.permits_adaptation)
        self.assertFalse(eligibility.requests_adaptation)
        self.assertTrue(eligibility.is_advisory_only)

    def test_failure_signal_remains_eligible_for_future_learning_consideration(self):
        eligibility = EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Service().evaluate(
            self._make_integrity(success=False), eligibility_id="eligibility-1"
        )
        self.assertEqual(eligibility.signal_status, EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.NEGATIVE_SIGNAL)
        self.assertEqual(eligibility.eligibility_status, EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE)

    def test_provenance_and_confidence_are_preserved(self):
        integrity = self._make_integrity()
        eligibility = EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Service().evaluate(
            integrity,
            eligibility_id="eligibility-1",
            reasons={"origin": "m23.59"},
            lineage={"upstream": {"integrity_id": integrity.integrity_id}},
        )
        self.assertEqual(eligibility.integrity_id, integrity.integrity_id)
        self.assertEqual(eligibility.signal_id, integrity.signal_id)
        self.assertEqual(eligibility.evaluation_id, integrity.evaluation_id)
        self.assertEqual(eligibility.feedback_id, integrity.feedback_id)
        self.assertEqual(eligibility.outcome_id, integrity.outcome_id)
        self.assertEqual(eligibility.decision_id, integrity.decision_id)
        self.assertEqual(eligibility.confidence, integrity.confidence)
        self.assertEqual(eligibility.signal_fingerprint, integrity.signal_fingerprint)

    def test_nested_reasons_and_lineage_are_frozen(self):
        eligibility = EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Service().evaluate(
            self._make_integrity(),
            eligibility_id="eligibility-1",
            reasons={"nested": {"inner": "value"}},
            lineage={"levels": [{"id": "integrity-1"}]},
        )
        with self.assertRaises(TypeError):
            eligibility.reasons["nested"] = {"other": "x"}
        with self.assertRaises(TypeError):
            eligibility.lineage["levels"] = []

    def test_eligibility_is_immutable_and_inert(self):
        eligibility = EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Service().evaluate(
            self._make_integrity(), eligibility_id="eligibility-1"
        )
        with self.assertRaises((AttributeError, TypeError)):
            eligibility.confidence = 0.2
        self.assertFalse(eligibility.grants_authority)
        self.assertFalse(eligibility.updates_model)
        self.assertFalse(eligibility.mutates_memory)
        self.assertFalse(eligibility.mutates_policy)
        self.assertFalse(eligibility.mutates_persistence)
        self.assertFalse(eligibility.schedules_work)

    def test_wrong_source_type_fails_closed(self):
        service = EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Service()
        with self.assertRaises(TypeError):
            service.evaluate(object(), eligibility_id="eligibility-1")

    def test_eligibility_id_is_required(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Service().evaluate(
                self._make_integrity(), eligibility_id=" "
            )

    def test_constructor_rejects_eligible_invalid_integrity(self):
        integrity = self._make_integrity()
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2(
                eligibility_id="eligibility-1",
                integrity_id=integrity.integrity_id,
                signal_id=integrity.signal_id,
                evaluation_id=integrity.evaluation_id,
                feedback_id=integrity.feedback_id,
                outcome_id=integrity.outcome_id,
                execution_id=integrity.execution_id,
                preparation_id=integrity.preparation_id,
                decision_id=integrity.decision_id,
                proposal_id=integrity.proposal_id,
                assessment_id=integrity.assessment_id,
                environment_id=integrity.environment_id,
                expected_model_id=integrity.expected_model_id,
                observed_model_id=integrity.observed_model_id,
                signal_integrity_status=EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status.INVALID,
                signal_status=integrity.signal_status,
                confidence=integrity.confidence,
                signal_fingerprint=integrity.signal_fingerprint,
                eligibility_status=EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE,
            )

    def test_source_integrity_remains_unchanged(self):
        integrity = self._make_integrity()
        before = integrity
        eligibility = EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Service().evaluate(
            integrity, eligibility_id="eligibility-1"
        )
        self.assertEqual(integrity, before)
        self.assertEqual(eligibility.signal_fingerprint, before.signal_fingerprint)


if __name__ == "__main__":
    unittest.main()
