import unittest

from src.core.environment_world_model_rollback_repair_retry_feedback_evaluation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_signal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2,
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Service,
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_signal_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2,
    EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Service,
    EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status,
)


class M23_59LearningSignalIntegrityV2Tests(unittest.TestCase):
    def _make_signal(self, *, success: bool = True):
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
                if success
                else EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status.FAILURE
            ),
            feedback_status=(
                EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.SUCCESS_SIGNAL
                if success
                else EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status.FAILURE_SIGNAL
            ),
            result_fingerprint="result-fp-1" if success else None,
            failure_reason=None if success else "provider unavailable",
            worker_id="worker-1",
        )
        evaluation = EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Service().evaluate(
            feedback,
            evaluation_id="evaluation-1",
            confidence=0.8,
            reasons={"origin": "test"},
            lineage={"chain": {"evaluation": "evaluation-1"}},
        )
        return EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Service().emit(
            evaluation,
            signal_id="signal-1",
            reasons={"origin": "test"},
            lineage={"chain": {"evaluation": "evaluation-1"}},
        )

    def test_success_signal_becomes_valid_integrity_and_fingerprints_deterministically(self):
        signal = self._make_signal(success=True)
        integrity = EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Service().verify(
            signal, integrity_id="learning-integrity-1"
        )
        self.assertEqual(integrity.status, EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status.VALID)
        self.assertEqual(integrity.signal_status, EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.POSITIVE_SIGNAL)
        self.assertEqual(integrity.evaluation_status, EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.SUCCESS_EVALUATION)
        self.assertEqual(len(integrity.signal_fingerprint), 64)

    def test_same_signal_produces_same_fingerprint(self):
        signal = self._make_signal(success=True)
        service = EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Service()
        first = service.verify(signal, integrity_id="learning-integrity-1")
        second = service.verify(signal, integrity_id="learning-integrity-2")
        self.assertEqual(first.signal_fingerprint, second.signal_fingerprint)

    def test_failure_signal_preserves_failure_reason(self):
        signal = self._make_signal(success=False)
        integrity = EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Service().verify(
            signal, integrity_id="learning-integrity-1"
        )
        self.assertEqual(integrity.status, EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status.VALID)
        self.assertEqual(integrity.signal_status, EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.NEGATIVE_SIGNAL)
        self.assertEqual(signal.failure_reason, "provider unavailable")
        self.assertIsNone(signal.result_fingerprint)

    def test_provenance_is_preserved(self):
        signal = self._make_signal(success=True)
        integrity = EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Service().verify(
            signal, integrity_id="learning-integrity-1"
        )
        self.assertEqual(integrity.signal_id, signal.signal_id)
        self.assertEqual(integrity.evaluation_id, signal.evaluation_id)
        self.assertEqual(integrity.feedback_id, signal.feedback_id)
        self.assertEqual(integrity.outcome_id, signal.outcome_id)
        self.assertEqual(integrity.source_integrity_id, signal.integrity_id)
        self.assertEqual(integrity.execution_id, signal.execution_id)
        self.assertEqual(integrity.preparation_id, signal.preparation_id)
        self.assertEqual(integrity.decision_id, signal.decision_id)

    def test_confidence_is_preserved_and_bounded(self):
        signal = self._make_signal(success=True)
        integrity = EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Service().verify(
            signal, integrity_id="learning-integrity-1"
        )
        self.assertEqual(integrity.confidence, 0.8)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2(
                **{**integrity.__dict__, "confidence": 1.1}
            )

    def test_nested_reasons_and_lineage_are_frozen(self):
        signal = self._make_signal(success=True)
        integrity = EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Service().verify(
            signal,
            integrity_id="learning-integrity-1",
            reasons={"nested": {"inner": "value"}},
            lineage={"levels": [{"id": "signal-1"}]},
        )
        with self.assertRaises(TypeError):
            integrity.reasons["nested"] = {"other": "x"}
        with self.assertRaises(TypeError):
            integrity.lineage["levels"] = []

    def test_integrity_is_immutable_and_advisory(self):
        signal = self._make_signal(success=True)
        integrity = EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Service().verify(
            signal, integrity_id="learning-integrity-1"
        )
        with self.assertRaises((AttributeError, TypeError)):
            integrity.status = EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status.INVALID
        self.assertTrue(integrity.is_advisory_only)
        self.assertFalse(integrity.grants_authority)
        self.assertFalse(integrity.requests_retry)
        self.assertFalse(integrity.updates_model)
        self.assertFalse(integrity.mutates_memory)
        self.assertFalse(integrity.mutates_policy)
        self.assertFalse(integrity.mutates_persistence)

    def test_signal_id_is_required_and_wrong_source_type_fails_closed(self):
        service = EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Service()
        with self.assertRaises(ValueError):
            service.verify(self._make_signal(), integrity_id=" ")
        with self.assertRaises(TypeError):
            service.verify(object(), integrity_id="learning-integrity-1")

    def test_integrity_id_cannot_be_blank(self):
        signal = self._make_signal(success=True)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Service().verify(
                signal, integrity_id="   "
            )

    def test_source_signal_remains_unchanged(self):
        signal = self._make_signal(success=True)
        before = signal
        EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Service().verify(
            signal, integrity_id="learning-integrity-1"
        )
        self.assertEqual(signal, before)


if __name__ == "__main__":
    unittest.main()
