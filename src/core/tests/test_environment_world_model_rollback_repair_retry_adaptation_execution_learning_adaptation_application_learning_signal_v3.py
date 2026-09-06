import unittest
from types import MappingProxyType
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_feedback_evaluation_v3 import EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3Status as E
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_feedback_v3 import EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status as F
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_integrity_v3 import EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status as I
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_signal_v3 import EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Service as S, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status as L
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_outcome_classification_v3 import EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Status as O
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_v3 import EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status as A
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_decision_v3 import EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status as D

class M23_80ApplicationLearningSignalV3Tests(unittest.TestCase):
    def _evaluation(self, status):
        rej=status is E.REJECTION_EVALUATION; fail=status is E.FAILURE_EVALUATION
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackEvaluationV3(
            evaluation_id="evaluation-80",feedback_id="feedback-80",classification_id="classification-80",integrity_id="integrity-76",application_id="application-80",decision_id="decision-80",proposal_id="proposal-80",source_proposal_id="source-proposal-80",eligibility_id="eligibility-80",source_integrity_id="source-integrity-80",signal_id="signal-80",source_evaluation_id="evaluation-source-80",feedback_source_id="feedback-source-80",execution_id="execution-80",handoff_id="handoff-80",authorization_id="authorization-80",validation_id="validation-80",source_signal_id="source-signal-80",outcome_id="outcome-80",preparation_id="preparation-80",assessment_id="assessment-80",environment_id="environment-80",expected_model_id="expected-80",observed_model_id="observed-80",confidence=.87,signal_fingerprint="a"*64,upstream_proposal_fingerprint="b"*64,handoff_fingerprint="0"*64 if rej else "c"*64,result_fingerprint="0"*64 if (rej or fail) else "d"*64,application_fingerprint="e"*64,authority_principal_id=None if rej else "user:test",executor_id=None if rej else "executor:test",proposal_kind="ADAPTATION_CANDIDATE",proposal_status="PROPOSED",decision_status=D.REJECTED if rej else D.ACCEPTED,application_status=A.BLOCKED if rej else A.NOT_APPLIED if fail else A.APPLIED,integrity_status=I.VALID,outcome_status=O.REJECTED if rej else O.FAILURE if fail else O.SUCCESS,feedback_status=F.REJECTION_SIGNAL if rej else F.FAILURE_SIGNAL if fail else F.SUCCESS_SIGNAL,evaluation_status=status,failure_reason="applier failed" if fail else None)
    def test_success_maps_to_positive_signal(self): self.assertEqual(S().emit(self._evaluation(E.SUCCESS_EVALUATION),signal_id="signal-new").signal_status,L.POSITIVE_SIGNAL)
    def test_failure_maps_to_negative_signal(self):
        r=S().emit(self._evaluation(E.FAILURE_EVALUATION),signal_id="signal-new"); self.assertEqual(r.signal_status,L.NEGATIVE_SIGNAL); self.assertEqual(r.failure_reason,"applier failed")
    def test_rejection_maps_without_failure_evidence(self):
        r=S().emit(self._evaluation(E.REJECTION_EVALUATION),signal_id="signal-new"); self.assertEqual(r.signal_status,L.REJECTION_SIGNAL); self.assertIsNone(r.failure_reason); self.assertIsNone(r.authority_principal_id); self.assertIsNone(r.executor_id)
    def test_blank_signal_id_is_rejected(self):
        with self.assertRaises(ValueError): S().emit(self._evaluation(E.SUCCESS_EVALUATION),signal_id=" ")
    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError): S().emit(object(),signal_id="signal-new")
    def test_full_provenance_is_preserved(self):
        s=self._evaluation(E.FAILURE_EVALUATION); r=S().emit(s,signal_id="signal-new")
        for f in ("evaluation_id","feedback_id","classification_id","integrity_id","application_id","decision_id","proposal_id","source_proposal_id","eligibility_id","source_integrity_id","feedback_source_id","source_evaluation_id","execution_id","handoff_id","authorization_id","validation_id","source_signal_id","outcome_id","preparation_id","environment_id","expected_model_id","observed_model_id","signal_fingerprint","upstream_proposal_fingerprint","handoff_fingerprint","result_fingerprint","application_fingerprint"): self.assertEqual(getattr(r,f),getattr(s,f))
        self.assertEqual(r.feedback_signal_id,s.signal_id)
    def test_reasons_and_lineage_are_recursively_immutable(self):
        r=S().emit(self._evaluation(E.SUCCESS_EVALUATION),signal_id="signal-new",reasons={"x":"y"},lineage={"nested":{"id":"80"}}); self.assertIsInstance(r.reasons,MappingProxyType)
        with self.assertRaises(TypeError): r.lineage["nested"]["x"]="blocked"
    def test_source_is_unchanged(self):
        s=self._evaluation(E.FAILURE_EVALUATION); before=dict(s.lineage); S().emit(s,signal_id="signal-new"); self.assertEqual(dict(s.lineage),before)
    def test_signal_is_advisory_only(self):
        r=S().emit(self._evaluation(E.FAILURE_EVALUATION),signal_id="signal-new"); self.assertTrue(r.is_advisory_only); self.assertTrue(r.is_observational)
        for p in ("recommends_retry","requests_retry","grants_authority","updates_model","mutates_memory","mutates_policy","mutates_persistence","schedules_work","executes_action"): self.assertFalse(getattr(r,p))
    def test_confidence_is_preserved(self): self.assertEqual(S().emit(self._evaluation(E.SUCCESS_EVALUATION),signal_id="signal-new").confidence,.87)
    def test_signal_status_mismatch_is_rejected(self):
        s=self._evaluation(E.SUCCESS_EVALUATION); k=dict(s.__dict__); k.update(signal_id="signal-new",feedback_signal_id=s.signal_id,signal_status=L.NEGATIVE_SIGNAL)
        with self.assertRaises(ValueError): EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3(**k)
    def test_rejection_signal_rejects_failure_evidence(self):
        s=self._evaluation(E.REJECTION_EVALUATION); k=dict(s.__dict__); k.update(signal_id="signal-new",feedback_signal_id=s.signal_id,signal_status=L.REJECTION_SIGNAL,failure_reason="bad")
        with self.assertRaises(ValueError): EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3(**k)
    def test_invalid_integrity_is_rejected(self):
        s=self._evaluation(E.SUCCESS_EVALUATION); k=dict(s.__dict__); k.update(signal_id="signal-new",feedback_signal_id=s.signal_id,signal_status=L.POSITIVE_SIGNAL,integrity_status=I.INVALID)
        with self.assertRaises(ValueError): EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3(**k)
    def test_non_mapping_lineage_is_rejected(self):
        s=self._evaluation(E.SUCCESS_EVALUATION); k=dict(s.__dict__); k.update(signal_id="signal-new",feedback_signal_id=s.signal_id,signal_status=L.POSITIVE_SIGNAL,lineage=[])
        with self.assertRaises(TypeError): EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3(**k)

if __name__ == "__main__": unittest.main()
