import unittest

from src.core.environment_world_model_rollback_repair_retry_feedback_evaluation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2,
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Service,
    EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_feedback_v2 import (
    EnvironmentWorldModelRollbackRepairRetryFeedbackV2,
    EnvironmentWorldModelRollbackRepairRetryFeedbackV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_outcome_v2 import (
    EnvironmentWorldModelRollbackRepairRetryOutcomeV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_signal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2,
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Service,
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status,
)


class M23_58LearningSignalV2Tests(unittest.TestCase):
    def _make_evaluation(self, *, success: bool = True):
        feedback = EnvironmentWorldModelRollbackRepairRetryFeedbackV2(
            feedback_id="feedback-1",
            outcome_id="outcome-1",
            integrity_id="integrity-1",
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
            result_fingerprint="fingerprint-1" if success else None,
            failure_reason=None if success else "provider unavailable",
            worker_id="worker-1",
        )
        return EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Service().evaluate(
            feedback,
            evaluation_id="evaluation-1",
            confidence=0.8,
            reasons={"origin": "test", "nested": "frozen"},
            lineage={"chain": {"evaluation": "evaluation-1"}},
        )

    def test_success_evaluation_becomes_positive_signal_and_preserves_chain(self):
        evaluation = self._make_evaluation(success=True)
        signal = EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Service().emit(
            evaluation, signal_id="signal-1"
        )
        self.assertEqual(signal.signal_status, EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.POSITIVE_SIGNAL)
        self.assertEqual(signal.evaluation_status, EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.SUCCESS_EVALUATION)
        self.assertEqual(signal.confidence, 0.8)
        self.assertEqual(signal.result_fingerprint, "fingerprint-1")
        self.assertIsNone(signal.failure_reason)
        self.assertEqual(signal.decision_id, "decision-1")
        self.assertEqual(signal.integrity_decision_id, "integrity-decision-1")

    def test_failure_evaluation_becomes_negative_signal_and_preserves_reason(self):
        evaluation = self._make_evaluation(success=False)
        signal = EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Service().emit(
            evaluation, signal_id="signal-1"
        )
        self.assertEqual(signal.signal_status, EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.NEGATIVE_SIGNAL)
        self.assertEqual(signal.evaluation_status, EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.FAILURE_EVALUATION)
        self.assertEqual(signal.failure_reason, "provider unavailable")
        self.assertIsNone(signal.result_fingerprint)

    def test_confidence_is_preserved_and_signal_is_immutable(self):
        evaluation = self._make_evaluation(success=True)
        signal = EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Service().emit(
            evaluation, signal_id="signal-1"
        )
        self.assertEqual(signal.confidence, 0.8)
        with self.assertRaises((AttributeError, TypeError)):
            signal.confidence = 0.4

    def test_nested_reasons_and_lineage_are_frozen_and_source_is_unchanged(self):
        reasons = {"nested": {"inner": "value"}}
        lineage = {"levels": [{"id": "evaluation-1"}]}
        evaluation = self._make_evaluation(success=True)
        signal = EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Service().emit(
            evaluation, signal_id="signal-1", reasons=reasons, lineage=lineage
        )
        self.assertEqual(evaluation.reasons["origin"], "test")
        with self.assertRaises(TypeError):
            signal.reasons["nested"] = {"other": "x"}
        with self.assertRaises(TypeError):
            signal.lineage["levels"] = []

    def test_learning_signal_has_no_authority_or_mutation_capability(self):
        signal = EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Service().emit(
            self._make_evaluation(success=False), signal_id="signal-1"
        )
        self.assertTrue(signal.is_observational)
        self.assertFalse(signal.recommends_retry)
        self.assertFalse(signal.requests_retry)
        self.assertFalse(signal.grants_authority)
        self.assertFalse(signal.mutates_policy)
        self.assertFalse(signal.mutates_persistence)
        self.assertFalse(signal.updates_model)
        self.assertFalse(signal.mutates_memory)

    def test_signal_id_is_required_and_wrong_source_type_fails_closed(self):
        evaluation = self._make_evaluation(success=True)
        service = EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Service()
        with self.assertRaises(ValueError):
            service.emit(evaluation, signal_id=" ")
        with self.assertRaises(TypeError):
            service.emit(object(), signal_id="signal-1")

    def test_constructor_rejects_mismatched_status(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryLearningSignalV2(
                signal_id="signal-1",
                evaluation_id="evaluation-1",
                feedback_id="feedback-1",
                outcome_id="outcome-1",
                integrity_id="integrity-1",
                execution_id="execution-1",
                preparation_id="preparation-1",
                decision_id="decision-1",
                integrity_decision_id=None,
                proposal_id="proposal-1",
                assessment_id=None,
                environment_id="env-1",
                expected_model_id="expected",
                observed_model_id="observed",
                evaluation_status=EnvironmentWorldModelRollbackRepairRetryFeedbackEvaluationV2Status.FAILURE_EVALUATION,
                signal_status=EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.POSITIVE_SIGNAL,
                confidence=1.0,
                result_fingerprint="fingerprint-1",
                failure_reason=None,
            )

    def test_constructor_rejects_confidence_out_of_bounds(self):
        evaluation = self._make_evaluation(success=True)
        payload = {
            key: value
            for key, value in evaluation.__dict__.items()
            if key not in {"feedback_status", "confidence", "evaluation_status"}
        }
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryLearningSignalV2(
                **payload,
                signal_id="signal-1",
                evaluation_status=evaluation.evaluation_status,
                signal_status=EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.POSITIVE_SIGNAL,
                confidence=1.1,
            )

    def test_source_evaluation_remains_unchanged(self):
        evaluation = self._make_evaluation(success=True)
        before = evaluation
        signal = EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Service().emit(
            evaluation, signal_id="signal-1"
        )
        self.assertEqual(signal.evaluation_id, before.evaluation_id)
        self.assertEqual(signal.feedback_id, before.feedback_id)
        self.assertEqual(signal.lineage["evaluation_id"], before.evaluation_id)


if __name__ == "__main__":
    unittest.main()
