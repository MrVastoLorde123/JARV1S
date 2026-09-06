import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_feedback_evaluation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_signal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_signal_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status,
)


class M23_71AdaptationExecutionLearningSignalIntegrityV3Tests(unittest.TestCase):
    def _make_signal(self, status):
        rejected = status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.REJECTION_SIGNAL
        evaluation_status = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.NEGATIVE_SIGNAL:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.FAILURE_EVALUATION,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.REJECTION_SIGNAL:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.REJECTION_EVALUATION,
        }[status]
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3(
            signal_id="signal-71",
            evaluation_id="evaluation-71",
            feedback_id="feedback-71",
            classification_id="classification-71",
            integrity_id="integrity-source-71",
            execution_id="execution-71",
            handoff_id="handoff-71",
            authorization_id="authorization-71",
            validation_id="validation-71",
            proposal_id="proposal-71",
            eligibility_id="eligibility-71",
            source_signal_id="source-signal-71",
            outcome_id="outcome-71",
            preparation_id="preparation-71",
            decision_id="decision-71",
            source_proposal_id="source-proposal-71",
            source_integrity_id="integrity-66",
            assessment_id="assessment-71",
            environment_id="env-71",
            expected_model_id="expected-71",
            observed_model_id="observed-71",
            execution_status="REJECTED" if rejected else ("FAILURE" if status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.NEGATIVE_SIGNAL else "SUCCESS"),
            feedback_status="REJECTION_SIGNAL" if rejected else ("FAILURE_SIGNAL" if status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.NEGATIVE_SIGNAL else "SUCCESS_SIGNAL"),
            evaluation_status=evaluation_status,
            signal_status=status,
            confidence=0.81,
            signal_fingerprint="a" * 64,
            proposal_fingerprint="b" * 64,
            handoff_fingerprint="0" * 64 if rejected else "c" * 64,
            result_fingerprint="0" * 64 if status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL else "d" * 64,
            authority_principal_id=None if rejected else "user:test",
            executor_id=None if rejected else "executor:test",
            failure_reason="rejected" if rejected else ("executor failed" if status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.NEGATIVE_SIGNAL else None),
            reasons={"reason": "test"},
            lineage={"nested": {"id": "71"}},
        )

    def test_positive_signal_is_valid(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Service().verify(
            self._make_signal(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL),
            integrity_id="integrity-71",
        )
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID)
        self.assertEqual(len(result.signal_fingerprint), 64)

    def test_negative_signal_is_valid(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Service().verify(
            self._make_signal(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.NEGATIVE_SIGNAL),
            integrity_id="integrity-71",
        )
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID)
        self.assertEqual(result.source_integrity_id, "integrity-source-71")

    def test_rejection_signal_is_valid(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Service().verify(
            self._make_signal(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.REJECTION_SIGNAL),
            integrity_id="integrity-71",
        )
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID)
        self.assertEqual(result.result_fingerprint, "0" * 64)

    def test_fingerprint_is_deterministic(self):
        source = self._make_signal(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL)
        service = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Service()
        first = service.verify(source, integrity_id="integrity-71")
        second = service.verify(source, integrity_id="another-integrity-71")
        self.assertEqual(first.signal_fingerprint, second.signal_fingerprint)

    def test_blank_integrity_id_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Service().verify(
                self._make_signal(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL),
                integrity_id=" ",
            )

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Service().verify(
                object(), integrity_id="integrity-71"
            )

    def test_full_provenance_is_preserved(self):
        source = self._make_signal(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL)
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Service().verify(source, integrity_id="integrity-71")
        self.assertEqual(result.signal_id, source.signal_id)
        self.assertEqual(result.evaluation_id, source.evaluation_id)
        self.assertEqual(result.feedback_id, source.feedback_id)
        self.assertEqual(result.classification_id, source.classification_id)
        self.assertEqual(result.execution_id, source.execution_id)
        self.assertEqual(result.handoff_id, source.handoff_id)
        self.assertEqual(result.proposal_id, source.proposal_id)

    def test_reasons_and_lineage_are_immutable(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Service().verify(
            self._make_signal(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL),
            integrity_id="integrity-71",
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
        source = self._make_signal(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL)
        before = dict(source.lineage)
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Service().verify(source, integrity_id="integrity-71")
        self.assertEqual(dict(source.lineage), before)
        self.assertEqual(source.signal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL)

    def test_integrity_has_no_authority_or_mutation(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Service().verify(
            self._make_signal(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.NEGATIVE_SIGNAL),
            integrity_id="integrity-71",
        )
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.requests_retry)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)


if __name__ == "__main__":
    unittest.main()