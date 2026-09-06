import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_outcome_classification_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_feedback_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_feedback_evaluation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_result_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status,
)


class M23_69AdaptationExecutionFeedbackEvaluationV2Tests(unittest.TestCase):
    def _make_feedback(self, status):
        rejected = status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.REJECTION_SIGNAL
        failed = status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.FAILURE_SIGNAL
        execution_status = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.FAILURE_SIGNAL: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.FAILED,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.REJECTION_SIGNAL: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.REJECTED,
        }[status]
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2(
            feedback_id="feedback-69",
            classification_id="classification-69",
            integrity_id="integrity-69",
            execution_id="execution-69",
            handoff_id="handoff-69",
            authorization_id="authorization-69",
            validation_id="validation-69",
            proposal_id="proposal-69",
            eligibility_id="eligibility-69",
            signal_id="signal-69",
            evaluation_id="evaluation-source-69",
            outcome_id="outcome-69",
            preparation_id="preparation-69",
            decision_id="decision-69",
            source_proposal_id="source-proposal-69",
            source_integrity_id="integrity-66",
            assessment_id="assessment-69",
            environment_id="env-69",
            expected_model_id="expected-69",
            observed_model_id="observed-69",
            execution_status=(
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS
                if status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL
                else EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.FAILURE
                if failed
                else EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.REJECTED
            ),
            feedback_status=status,
            confidence=0.88,
            signal_fingerprint="a" * 64,
            proposal_fingerprint="b" * 64,
            handoff_fingerprint=("0" * 64 if rejected else "c" * 64),
            result_fingerprint=("0" * 64 if not status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL else "d" * 64),
            authority_principal_id=None if rejected else "user:test",
            executor_id=None if rejected else "executor:test",
            failure_reason=("rejected" if rejected else "executor failed" if failed else None),
            reasons={"reason": "test"},
            lineage={"nested": {"id": "69"}},
        )

    def test_success_becomes_success_evaluation(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Service().evaluate(
            self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL),
            evaluation_id="evaluation-69",
        )
        self.assertEqual(result.evaluation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION)
        self.assertEqual(result.feedback_id, "feedback-69")

    def test_failure_becomes_failure_evaluation(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Service().evaluate(
            self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.FAILURE_SIGNAL),
            evaluation_id="evaluation-69",
        )
        self.assertEqual(result.evaluation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.FAILURE_EVALUATION)
        self.assertEqual(result.failure_reason, "executor failed")
        self.assertEqual(result.result_fingerprint, "0" * 64)

    def test_rejection_becomes_rejection_evaluation(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Service().evaluate(
            self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.REJECTION_SIGNAL),
            evaluation_id="evaluation-69",
        )
        self.assertEqual(result.evaluation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.REJECTION_EVALUATION)
        self.assertIsNone(result.authority_principal_id)
        self.assertIsNone(result.executor_id)
        self.assertEqual(result.result_fingerprint, "0" * 64)

    def test_blank_evaluation_id_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Service().evaluate(
                self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL),
                evaluation_id=" ",
            )

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Service().evaluate(object(), evaluation_id="evaluation-69")

    def test_confidence_is_bounded(self):
        service = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Service()
        source = self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL)
        with self.assertRaises(ValueError):
            service.evaluate(source, evaluation_id="evaluation-69", confidence=1.1)
        with self.assertRaises(ValueError):
            service.evaluate(source, evaluation_id="evaluation-69", confidence=-0.1)

    def test_evaluation_status_mismatch_is_rejected(self):
        source = self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2(
                evaluation_id="evaluation-69",
                feedback_id=source.feedback_id,
                classification_id=source.classification_id,
                integrity_id=source.integrity_id,
                execution_id=source.execution_id,
                handoff_id=source.handoff_id,
                authorization_id=source.authorization_id,
                validation_id=source.validation_id,
                proposal_id=source.proposal_id,
                eligibility_id=source.eligibility_id,
                signal_id=source.signal_id,
                outcome_id=source.outcome_id,
                preparation_id=source.preparation_id,
                decision_id=source.decision_id,
                source_proposal_id=source.source_proposal_id,
                source_integrity_id=source.source_integrity_id,
                assessment_id=source.assessment_id,
                environment_id=source.environment_id,
                expected_model_id=source.expected_model_id,
                observed_model_id=source.observed_model_id,
                execution_status=source.execution_status,
                feedback_status=source.feedback_status,
                evaluation_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.FAILURE_EVALUATION,
                confidence=1.0,
                signal_fingerprint=source.signal_fingerprint,
                proposal_fingerprint=source.proposal_fingerprint,
                handoff_fingerprint=source.handoff_fingerprint,
                result_fingerprint=source.result_fingerprint,
                authority_principal_id=source.authority_principal_id,
                executor_id=source.executor_id,
                failure_reason=source.failure_reason,
            )

    def test_full_provenance_and_fingerprints_are_preserved(self):
        source = self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL)
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Service().evaluate(source, evaluation_id="evaluation-69", confidence=0.73)
        for field in (
            "feedback_id", "classification_id", "integrity_id", "execution_id", "handoff_id", "authorization_id",
            "validation_id", "proposal_id", "eligibility_id", "signal_id", "outcome_id", "preparation_id", "decision_id",
            "source_proposal_id", "source_integrity_id", "environment_id", "expected_model_id", "observed_model_id",
            "signal_fingerprint", "proposal_fingerprint", "handoff_fingerprint", "result_fingerprint",
        ):
            self.assertEqual(getattr(result, field), getattr(source, field))
        self.assertEqual(result.confidence, 0.73)

    def test_reasons_and_lineage_are_immutable(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Service().evaluate(
            self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL),
            evaluation_id="evaluation-69",
            reasons={"outer": "reason"},
            lineage={"nested": {"x": [1, 2]}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["new"] = "blocked"
        with self.assertRaises(TypeError):
            result.lineage["new"] = "blocked"
        with self.assertRaises(TypeError):
            result.lineage["nested"]["new"] = "blocked"

    def test_source_is_unchanged(self):
        source = self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.FAILURE_SIGNAL)
        before = dict(source.lineage)
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Service().evaluate(source, evaluation_id="evaluation-69")
        self.assertEqual(dict(source.lineage), before)
        self.assertEqual(source.feedback_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.FAILURE_SIGNAL)

    def test_evaluation_does_not_create_learning_or_authority(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Service().evaluate(
            self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.FAILURE_SIGNAL),
            evaluation_id="evaluation-69",
        )
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.creates_learning_signal)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_memory)

    def test_rejection_evaluation_cannot_carry_authority_or_executor(self):
        source = self._make_feedback(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.REJECTION_SIGNAL)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2(
                evaluation_id="evaluation-69",
                feedback_id=source.feedback_id,
                classification_id=source.classification_id,
                integrity_id=source.integrity_id,
                execution_id=source.execution_id,
                handoff_id=source.handoff_id,
                authorization_id=source.authorization_id,
                validation_id=source.validation_id,
                proposal_id=source.proposal_id,
                eligibility_id=source.eligibility_id,
                signal_id=source.signal_id,
                outcome_id=source.outcome_id,
                preparation_id=source.preparation_id,
                decision_id=source.decision_id,
                source_proposal_id=source.source_proposal_id,
                source_integrity_id=source.source_integrity_id,
                assessment_id=source.assessment_id,
                environment_id=source.environment_id,
                expected_model_id=source.expected_model_id,
                observed_model_id=source.observed_model_id,
                execution_status=source.execution_status,
                feedback_status=source.feedback_status,
                evaluation_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.REJECTION_EVALUATION,
                confidence=1.0,
                signal_fingerprint=source.signal_fingerprint,
                proposal_fingerprint=source.proposal_fingerprint,
                handoff_fingerprint=source.handoff_fingerprint,
                result_fingerprint=source.result_fingerprint,
                authority_principal_id="user:should-not-pass",
                executor_id="executor:should-not-pass",
                failure_reason=source.failure_reason,
            )


if __name__ == "__main__":
    unittest.main()
