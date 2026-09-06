import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_feedback_evaluation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_signal_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_eligibility_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_signal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status,
)


class M23_72LearningEligibilityV3Tests(unittest.TestCase):
    def _make_integrity(self, status):
        signal_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3(
            integrity_id="integrity-72",
            signal_id="signal-72",
            evaluation_id="evaluation-72",
            feedback_id="feedback-72",
            classification_id="classification-72",
            source_integrity_id="source-integrity-72",
            execution_id="execution-72",
            handoff_id="handoff-72",
            authorization_id="authorization-72",
            validation_id="validation-72",
            proposal_id="proposal-72",
            eligibility_id="upstream-eligibility-72",
            source_signal_id="source-signal-72",
            outcome_id="outcome-72",
            preparation_id="preparation-72",
            decision_id="decision-72",
            source_proposal_id="source-proposal-72",
            assessment_id="assessment-72",
            environment_id="env-72",
            expected_model_id="expected-72",
            observed_model_id="observed-72",
            execution_status="SUCCESS",
            feedback_status="SUCCESS_SIGNAL",
            evaluation_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionFeedbackEvaluationV2Status.SUCCESS_EVALUATION,
            signal_status=signal_status,
            confidence=0.84,
            signal_fingerprint="a" * 64,
            proposal_fingerprint="b" * 64,
            handoff_fingerprint="c" * 64,
            result_fingerprint="d" * 64,
            authority_principal_id="user:test",
            executor_id="executor:test",
            failure_reason=None,
            status=status,
            reasons={"source": "test"},
            lineage={"nested": {"id": "72"}},
        )

    def test_valid_integrity_is_eligible(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Service().assess(
            self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID),
            eligibility_id="eligibility-72",
        )
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.ELIGIBLE)
        self.assertEqual(result.integrity_id, "integrity-72")

    def test_invalid_integrity_is_ineligible(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Service().assess(
            self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.INVALID),
            eligibility_id="eligibility-72",
        )
        self.assertEqual(result.status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.INELIGIBLE)

    def test_blank_eligibility_id_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Service().assess(
                self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID),
                eligibility_id=" ",
            )

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Service().assess(
                object(), eligibility_id="eligibility-72"
            )

    def test_provenance_is_preserved(self):
        source = self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID)
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Service().assess(
            source, eligibility_id="eligibility-72"
        )
        for name in ("signal_id", "evaluation_id", "feedback_id", "classification_id", "execution_id", "handoff_id", "proposal_id", "source_signal_id"):
            self.assertEqual(getattr(result, name), getattr(source, name))
        self.assertEqual(result.signal_fingerprint, source.signal_fingerprint)
        self.assertEqual(result.result_fingerprint, source.result_fingerprint)

    def test_reasons_and_lineage_are_immutable(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Service().assess(
            self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID),
            eligibility_id="eligibility-72",
            reasons={"outer": "reason"},
            lineage={"nested": {"items": [1, 2]}},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["new"] = "blocked"
        with self.assertRaises(TypeError):
            result.lineage["new"] = "blocked"
        with self.assertRaises(TypeError):
            result.lineage["nested"]["items"] = ()

    def test_source_is_unchanged(self):
        source = self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID)
        before = dict(source.lineage)
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Service().assess(
            source, eligibility_id="eligibility-72"
        )
        self.assertEqual(dict(source.lineage), before)
        self.assertEqual(source.status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID)

    def test_eligibility_does_not_permit_learning(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Service().assess(
            self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID),
            eligibility_id="eligibility-72",
        )
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.is_learning)
        self.assertFalse(result.permits_learning)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)

    def test_status_mapping_is_enforced(self):
        source = self._make_integrity(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID)
        values = dict(source.__dict__)
        values.pop("integrity_evaluation_id", None)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3(
                **{
                    **values,
                    "eligibility_id": "eligibility-72",
                    "status": EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.INELIGIBLE,
                }
            )


if __name__ == "__main__":
    unittest.main()
