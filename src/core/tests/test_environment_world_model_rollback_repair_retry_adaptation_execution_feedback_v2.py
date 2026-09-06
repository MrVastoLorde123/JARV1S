import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_outcome_classification_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_feedback_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Error,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_result_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status,
)


class M23_68AdaptationExecutionFeedbackV2Tests(unittest.TestCase):
    def _make_classification(self, status):
        rejected = status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.REJECTED
        execution_status = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.FAILURE: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.FAILED,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.REJECTED: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.REJECTED,
        }[status]
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2(
            classification_id="classification-68",
            integrity_id="integrity-68",
            execution_id="execution-68",
            handoff_id="handoff-68",
            authorization_id="authorization-68",
            validation_id="validation-68",
            proposal_id="proposal-68",
            eligibility_id="eligibility-68",
            signal_id="signal-68",
            evaluation_id="evaluation-68",
            feedback_id="feedback-source-68",
            outcome_id="outcome-68",
            preparation_id="preparation-68",
            decision_id="decision-68",
            source_proposal_id="source-proposal-68",
            source_integrity_id="integrity-66",
            assessment_id="assessment-68",
            environment_id="env-68",
            expected_model_id="expected-68",
            observed_model_id="observed-68",
            execution_status=execution_status,
            integrity_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.VALID,
            classification_status=status,
            confidence=0.88,
            signal_fingerprint="a" * 64,
            proposal_kind="world_model_patch",
            proposal_fingerprint="b" * 64,
            handoff_fingerprint=("0" * 64 if rejected else "c" * 64),
            result_fingerprint=("0" * 64 if status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS else "d" * 64),
            authority_principal_id=None if rejected else "user:test",
            executor_id=None if rejected else "executor:test",
            failure_reason=("rejected" if rejected else ("executor failed" if status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.FAILURE else None)),
            reasons={"reason": "test"},
            lineage={"nested": {"id": "68"}},
        )

    def test_success_becomes_success_feedback(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Service().record(
            self._make_classification(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS),
            feedback_id="feedback-68",
        )
        self.assertEqual(result.feedback_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.SUCCESS_SIGNAL)
        self.assertEqual(result.classification_id, "classification-68")

    def test_failure_becomes_failure_feedback(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Service().record(
            self._make_classification(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.FAILURE),
            feedback_id="feedback-68",
        )
        self.assertEqual(result.feedback_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.FAILURE_SIGNAL)
        self.assertEqual(result.failure_reason, "executor failed")

    def test_rejected_becomes_rejection_feedback(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Service().record(
            self._make_classification(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.REJECTED),
            feedback_id="feedback-68",
        )
        self.assertEqual(result.feedback_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.REJECTION_SIGNAL)
        self.assertIsNone(result.authority_principal_id)
        self.assertIsNone(result.executor_id)

    def test_blank_feedback_id_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Service().record(
                self._make_classification(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS),
                feedback_id=" ",
            )

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Service().record(
                object(),
                feedback_id="feedback-68",
            )

    def test_confidence_is_bounded(self):
        service = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Service()
        with self.assertRaises(ValueError):
            service.record(self._make_classification(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS), feedback_id="feedback-68", confidence=1.1)
        with self.assertRaises(ValueError):
            service.record(self._make_classification(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS), feedback_id="feedback-68", confidence=-0.1)

    def test_feedback_status_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2(
                feedback_id="feedback-68",
                classification_id="classification-68",
                integrity_id="integrity-68",
                execution_id="execution-68",
                handoff_id="handoff-68",
                authorization_id="authorization-68",
                validation_id="validation-68",
                proposal_id="proposal-68",
                eligibility_id="eligibility-68",
                signal_id="signal-68",
                evaluation_id="evaluation-68",
                outcome_id="outcome-68",
                preparation_id="preparation-68",
                decision_id="decision-68",
                source_proposal_id="source-proposal-68",
                source_integrity_id="integrity-66",
                assessment_id="assessment-68",
                environment_id="env-68",
                expected_model_id="expected-68",
                observed_model_id="observed-68",
                execution_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS,
                feedback_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.FAILURE_SIGNAL,
                confidence=1.0,
                signal_fingerprint="a" * 64,
                proposal_fingerprint="b" * 64,
                handoff_fingerprint="c" * 64,
                result_fingerprint="d" * 64,
                authority_principal_id="user:test",
                executor_id="executor:test",
                failure_reason=None,
            )

    def test_full_provenance_and_fingerprints_are_preserved(self):
        source = self._make_classification(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS)
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Service().record(source, feedback_id="feedback-68", confidence=0.73)
        self.assertEqual(result.integrity_id, source.integrity_id)
        self.assertEqual(result.execution_id, source.execution_id)
        self.assertEqual(result.proposal_fingerprint, source.proposal_fingerprint)
        self.assertEqual(result.handoff_fingerprint, source.handoff_fingerprint)
        self.assertEqual(result.result_fingerprint, source.result_fingerprint)
        self.assertEqual(result.confidence, 0.73)

    def test_reasons_and_lineage_are_immutable(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Service().record(
            self._make_classification(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS),
            feedback_id="feedback-68",
            reasons={"outer": "reason"},
            lineage={"nested": {"x": [1, 2]}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["new"] = "blocked"
        with self.assertRaises(TypeError):
            result.lineage["new"] = "blocked"

    def test_source_is_unchanged(self):
        source = self._make_classification(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS)
        before = dict(source.lineage)
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Service().record(source, feedback_id="feedback-68")
        self.assertEqual(dict(source.lineage), before)
        self.assertEqual(source.classification_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.SUCCESS)

    def test_feedback_does_not_create_learning_or_authority(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Service().record(
            self._make_classification(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.FAILURE),
            feedback_id="feedback-68",
        )
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.creates_learning_signal)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_memory)

    def test_rejection_feedback_cannot_carry_authority_or_executor(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2(
                feedback_id="feedback-68",
                classification_id="classification-68",
                integrity_id="integrity-68",
                execution_id="execution-68",
                handoff_id="handoff-68",
                authorization_id="authorization-68",
                validation_id="validation-68",
                proposal_id="proposal-68",
                eligibility_id="eligibility-68",
                signal_id="signal-68",
                evaluation_id="evaluation-68",
                outcome_id="outcome-68",
                preparation_id="preparation-68",
                decision_id="decision-68",
                source_proposal_id="source-proposal-68",
                source_integrity_id="integrity-66",
                assessment_id="assessment-68",
                environment_id="env-68",
                expected_model_id="expected-68",
                observed_model_id="observed-68",
                execution_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionOutcomeClassificationV2Status.REJECTED,
                feedback_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackV2Status.REJECTION_SIGNAL,
                confidence=1.0,
                signal_fingerprint="a" * 64,
                proposal_fingerprint="b" * 64,
                handoff_fingerprint="0" * 64,
                result_fingerprint="0" * 64,
                authority_principal_id="user:test",
                executor_id="executor:test",
                failure_reason="rejected",
            )


if __name__ == "__main__":
    unittest.main()
