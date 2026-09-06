import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_signal_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status as I,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_eligibility_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Service as S,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Status as E,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_signal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status as L,
)


class M23_82ApplicationLearningEligibilityV3Tests(unittest.TestCase):
    def _integrity(self, status):
        rejected = status is L.REJECTION_SIGNAL
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3(
            integrity_id="integrity-82", signal_id="signal-82", evaluation_id="evaluation-82", feedback_id="feedback-82",
            classification_id="classification-82", source_integrity_id="source-integrity-82", application_id="application-82",
            decision_id="decision-82", proposal_id="proposal-82", source_proposal_id="source-proposal-82", eligibility_id="prior-eligibility-82",
            feedback_signal_id="feedback-signal-82", feedback_source_id="feedback-source-82", source_evaluation_id="source-evaluation-82",
            execution_id="execution-82", handoff_id="handoff-82", authorization_id="authorization-82", validation_id="validation-82",
            source_signal_id="source-signal-82", outcome_id="outcome-82", preparation_id="preparation-82", assessment_id="assessment-82",
            environment_id="environment-82", expected_model_id="expected-82", observed_model_id="observed-82", proposal_kind="ADAPTATION_CANDIDATE",
            proposal_status="PROPOSED", decision_status="ACCEPTED", application_status="APPLIED", integrity_status=status,
            outcome_status="SUCCESS", feedback_status="SUCCESS_SIGNAL", evaluation_status="SUCCESS_EVALUATION" if not rejected else "REJECTION_EVALUATION",
            signal_status=status if False else (L.REJECTION_SIGNAL if rejected else L.POSITIVE_SIGNAL), confidence=.82,
            signal_fingerprint="a"*64, upstream_proposal_fingerprint="b"*64, handoff_fingerprint="0"*64 if rejected else "c"*64,
            result_fingerprint="0"*64 if rejected else "d"*64, application_fingerprint="e"*64,
            authority_principal_id=None if rejected else "user:test", executor_id=None if rejected else "executor:test",
            failure_reason=None, status=status, reasons={"source":"test"}, lineage={"nested":{"id":"82"}},
        )

    def _eligible_integrity(self):
        return self._integrity(I.VALID)

    def test_valid_integrity_is_eligible(self):
        result=S().assess(self._eligible_integrity(), eligibility_id="eligibility-82")
        self.assertEqual(result.status, E.ELIGIBLE)

    def test_invalid_integrity_is_ineligible(self):
        result=S().assess(self._integrity(I.INVALID), eligibility_id="eligibility-82")
        self.assertEqual(result.status, E.INELIGIBLE)

    def test_blank_eligibility_id_is_rejected(self):
        with self.assertRaises(ValueError):
            S().assess(self._eligible_integrity(), eligibility_id=" ")

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            S().assess(object(), eligibility_id="eligibility-82")

    def test_full_application_provenance_is_preserved(self):
        source=self._eligible_integrity(); result=S().assess(source, eligibility_id="eligibility-82")
        for name in ("signal_id","evaluation_id","feedback_id","classification_id","application_id","decision_id","proposal_id","source_proposal_id","feedback_signal_id","feedback_source_id","source_evaluation_id","execution_id","handoff_id","authorization_id","validation_id","source_signal_id","outcome_id","preparation_id","environment_id","expected_model_id","observed_model_id","proposal_kind","proposal_status","decision_status","application_status","outcome_status","feedback_status","evaluation_status","signal_status","confidence","signal_fingerprint","upstream_proposal_fingerprint","handoff_fingerprint","result_fingerprint","application_fingerprint"):
            self.assertEqual(getattr(result,name),getattr(source,name))
        self.assertEqual(result.integrity_id, source.integrity_id)
        self.assertEqual(result.eligibility_source_id, source.integrity_id)

    def test_reasons_and_lineage_are_recursively_immutable(self):
        result=S().assess(self._eligible_integrity(), eligibility_id="eligibility-82", reasons={"outer":{"reason":"x"}}, lineage={"nested":{"items":[1,2]}})
        self.assertIsInstance(result.reasons, MappingProxyType); self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError): result.lineage["nested"]["items"]=()

    def test_source_is_unchanged(self):
        source=self._eligible_integrity(); before=dict(source.lineage); S().assess(source, eligibility_id="eligibility-82")
        self.assertEqual(dict(source.lineage),before); self.assertEqual(source.status,I.VALID)

    def test_eligibility_does_not_permit_learning_or_authority(self):
        result=S().assess(self._eligible_integrity(), eligibility_id="eligibility-82")
        self.assertTrue(result.is_advisory_only); self.assertFalse(result.is_learning); self.assertFalse(result.permits_learning); self.assertFalse(result.grants_authority)
        for prop in ("updates_model","mutates_memory","mutates_policy","mutates_persistence","schedules_work","executes_action"):
            self.assertFalse(getattr(result,prop))

    def test_status_mapping_is_enforced(self):
        source=self._eligible_integrity(); values=dict(source.__dict__)
        values.pop("integrity_evaluation_id", None)
        values["eligibility_id"]="eligibility-82"; values["eligibility_source_id"]=source.integrity_id; values["integrity_status"]=I.VALID; values["status"]=E.INELIGIBLE
        with self.assertRaises(ValueError): EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3(**values)

    def test_confidence_is_preserved(self):
        self.assertEqual(S().assess(self._eligible_integrity(), eligibility_id="eligibility-82").confidence,.82)

if __name__ == "__main__": unittest.main()
