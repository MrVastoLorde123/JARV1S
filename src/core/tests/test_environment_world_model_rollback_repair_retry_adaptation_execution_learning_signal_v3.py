import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_feedback_evaluation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_feedback_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_outcome_classification_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_signal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Error,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status,
)


class M23_70AdaptationExecutionLearningSignalV3Tests(unittest.TestCase):
    def _make_evaluation(self, status):
        rejected = status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.REJECTION_EVALUATION
        feedback_status = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.FAILURE_EVALUATION: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.FAILURE_SIGNAL,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.REJECTION_EVALUATION: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.REJECTION_SIGNAL,
        }[status]
        execution_status = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.FAILURE_EVALUATION: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.FAILURE,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.REJECTION_EVALUATION: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.REJECTED,
        }[status]
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2(
            evaluation_id="evaluation-70",
            feedback_id="feedback-70",
            classification_id="classification-70",
            integrity_id="integrity-70",
            execution_id="execution-70",
            handoff_id="handoff-70",
            authorization_id="authorization-70",
            validation_id="validation-70",
            proposal_id="proposal-70",
            eligibility_id="eligibility-70",
            signal_id="source-signal-70",
            outcome_id="outcome-70",
            preparation_id="preparation-70",
            decision_id="decision-70",
            source_proposal_id="source-proposal-70",
            source_integrity_id="integrity-66",
            assessment_id="assessment-70",
            environment_id="env-70",
            expected_model_id="expected-70",
            observed_model_id="observed-70",
            execution_status=execution_status,
            feedback_status=feedback_status,
            evaluation_status=status,
            confidence=0.84,
            signal_fingerprint="a" * 64,
            proposal_fingerprint="b" * 64,
            handoff_fingerprint=("0" * 64 if rejected else "c" * 64),
            result_fingerprint=("0" * 64 if status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION else "d" * 64),
            authority_principal_id=None if rejected else "user:test",
            executor_id=None if rejected else "executor:test",
            failure_reason=("rejected" if rejected else ("executor failed" if status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.FAILURE_EVALUATION else None)),
            reasons={"reason": "test"},
            lineage={"nested": {"id": "70"}},
        )

    def test_success_becomes_positive_signal(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Service().emit(
            self._make_evaluation(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION),
            signal_id="signal-70",
        )
        self.assertEqual(result.signal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL)
        self.assertEqual(result.source_signal_id, "source-signal-70")

    def test_failure_becomes_negative_signal(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Service().emit(
            self._make_evaluation(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.FAILURE_EVALUATION),
            signal_id="signal-70",
        )
        self.assertEqual(result.signal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.NEGATIVE_SIGNAL)
        self.assertEqual(result.failure_reason, "executor failed")

    def test_rejection_becomes_rejection_signal(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Service().emit(
            self._make_evaluation(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.REJECTION_EVALUATION),
            signal_id="signal-70",
        )
        self.assertEqual(result.signal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.REJECTION_SIGNAL)
        self.assertIsNone(result.authority_principal_id)
        self.assertIsNone(result.executor_id)

    def test_blank_signal_id_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Service().emit(
                self._make_evaluation(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION),
                signal_id=" ",
            )

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Service().emit(object(), signal_id="signal-70")

    def test_conflicting_signal_status_is_rejected(self):
        source = self._make_evaluation(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3(
                **{**source.__dict__, "signal_id": "signal-70", "source_signal_id": source.signal_id,
                   "signal_status": EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.NEGATIVE_SIGNAL},
            )

    def test_positive_requires_result_evidence(self):
        source = self._make_evaluation(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3(
                signal_id="signal-70", evaluation_id=source.evaluation_id, feedback_id=source.feedback_id,
                classification_id=source.classification_id, integrity_id=source.integrity_id, execution_id=source.execution_id,
                handoff_id=source.handoff_id, authorization_id=source.authorization_id, validation_id=source.validation_id,
                proposal_id=source.proposal_id, eligibility_id=source.eligibility_id, source_signal_id=source.signal_id,
                outcome_id=source.outcome_id, preparation_id=source.preparation_id, decision_id=source.decision_id,
                source_proposal_id=source.source_proposal_id, source_integrity_id=source.source_integrity_id,
                assessment_id=source.assessment_id, environment_id=source.environment_id, expected_model_id=source.expected_model_id,
                observed_model_id=source.observed_model_id, execution_status=source.execution_status,
                feedback_status=source.feedback_status, evaluation_status=source.evaluation_status,
                signal_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL,
                confidence=source.confidence, signal_fingerprint=source.signal_fingerprint,
                proposal_fingerprint=source.proposal_fingerprint, handoff_fingerprint=source.handoff_fingerprint,
                result_fingerprint="0" * 64, authority_principal_id=source.authority_principal_id,
                executor_id=source.executor_id, failure_reason=None,
            )

    def test_confidence_is_bounded(self):
        source = self._make_evaluation(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION)
        service = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Service()
        with self.assertRaises(ValueError):
            source_bad = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2(**{**source.__dict__, "confidence": 1.1})
            service.emit(source_bad, signal_id="signal-70")
        with self.assertRaises(ValueError):
            source_bad = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2(**{**source.__dict__, "confidence": -0.1})
            service.emit(source_bad, signal_id="signal-70")

    def test_full_provenance_and_fingerprints_are_preserved(self):
        source = self._make_evaluation(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION)
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Service().emit(source, signal_id="signal-70")
        self.assertEqual(result.evaluation_id, source.evaluation_id)
        self.assertEqual(result.classification_id, source.classification_id)
        self.assertEqual(result.proposal_fingerprint, source.proposal_fingerprint)
        self.assertEqual(result.handoff_fingerprint, source.handoff_fingerprint)
        self.assertEqual(result.result_fingerprint, source.result_fingerprint)
        self.assertEqual(result.confidence, source.confidence)

    def test_reasons_and_lineage_are_immutable(self):
        source = self._make_evaluation(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION)
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Service().emit(
            source, signal_id="signal-70", reasons={"outer": "reason"}, lineage={"nested": {"x": [1, 2]}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["new"] = "blocked"
        with self.assertRaises(TypeError):
            result.lineage["new"] = "blocked"

    def test_source_is_unchanged(self):
        source = self._make_evaluation(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION)
        before = dict(source.lineage)
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Service().emit(source, signal_id="signal-70")
        self.assertEqual(dict(source.lineage), before)
        self.assertEqual(source.evaluation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION)

    def test_rejection_signal_cannot_carry_authority_or_executor(self):
        source = self._make_evaluation(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.REJECTION_EVALUATION)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3(**{**source.__dict__, "signal_id": "signal-70", "source_signal_id": source.signal_id, "signal_status": EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.REJECTION_SIGNAL, "authority_principal_id": "user:test"})
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3(**{**source.__dict__, "signal_id": "signal-70", "source_signal_id": source.signal_id, "signal_status": EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.REJECTION_SIGNAL, "executor_id": "executor:test"})

    def test_learning_signal_has_no_authority_or_mutation(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Service().emit(
            self._make_evaluation(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.FAILURE_EVALUATION), signal_id="signal-70",
        )
        self.assertTrue(result.is_observational)
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.recommends_retry)
        self.assertFalse(result.requests_retry)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)


if __name__ == "__main__":
    unittest.main()
