import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_proposal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Service as PS,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status as P,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Service as S,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status as D,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_eligibility_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Status as E,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_signal_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status as I,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_signal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status as L,
)


class M23_84ApplicationLearningAdaptationDecisionV3Tests(unittest.TestCase):
    def _eligibility(self, eligible=True):
        integrity=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3(
            integrity_id="integrity-84", signal_id="signal-84", evaluation_id="evaluation-84", feedback_id="feedback-84",
            classification_id="classification-84", source_integrity_id="source-integrity-84", application_id="application-84",
            decision_id="decision-source-84", proposal_id="proposal-source-84", source_proposal_id="source-proposal-84", eligibility_id="prior-84",
            feedback_signal_id="feedback-signal-84", feedback_source_id="feedback-source-84", source_evaluation_id="source-evaluation-84",
            execution_id="execution-84", handoff_id="handoff-84", authorization_id="authorization-84", validation_id="validation-84",
            source_signal_id="source-signal-84", outcome_id="outcome-84", preparation_id="preparation-84", assessment_id="assessment-84",
            environment_id="environment-84", expected_model_id="expected-84", observed_model_id="observed-84", proposal_kind="ADAPTATION_CANDIDATE",
            proposal_status="PROPOSED", decision_status="ACCEPTED", application_status="APPLIED", integrity_status=I.VALID if eligible else I.INVALID,
            outcome_status="SUCCESS", feedback_status="SUCCESS_SIGNAL", evaluation_status="SUCCESS_EVALUATION", signal_status=L.POSITIVE_SIGNAL,
            confidence=.84, signal_fingerprint="a"*64, upstream_proposal_fingerprint="b"*64, handoff_fingerprint="c"*64,
            result_fingerprint="d"*64, application_fingerprint="e"*64, authority_principal_id="user:test", executor_id="executor:test",
            failure_reason=None, status=I.VALID if eligible else I.INVALID, reasons={"source":"test"}, lineage={"nested":{"id":"84"}},
        )
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3(
            eligibility_id="eligibility-84", integrity_id=integrity.integrity_id, signal_id=integrity.signal_id, evaluation_id=integrity.evaluation_id,
            feedback_id=integrity.feedback_id, classification_id=integrity.classification_id, source_integrity_id=integrity.source_integrity_id,
            application_id=integrity.application_id, decision_id=integrity.decision_id, proposal_id=integrity.proposal_id,
            source_proposal_id=integrity.source_proposal_id, feedback_signal_id=integrity.feedback_signal_id, feedback_source_id=integrity.feedback_source_id,
            source_evaluation_id=integrity.source_evaluation_id, eligibility_source_id=integrity.integrity_id, execution_id=integrity.execution_id,
            handoff_id=integrity.handoff_id, authorization_id=integrity.authorization_id, validation_id=integrity.validation_id,
            source_signal_id=integrity.source_signal_id, outcome_id=integrity.outcome_id, preparation_id=integrity.preparation_id,
            assessment_id=integrity.assessment_id, environment_id=integrity.environment_id, expected_model_id=integrity.expected_model_id,
            observed_model_id=integrity.observed_model_id, proposal_kind=integrity.proposal_kind, proposal_status=integrity.proposal_status,
            decision_status=integrity.decision_status, application_status=integrity.application_status, integrity_status=integrity.status,
            outcome_status=integrity.outcome_status, feedback_status=integrity.feedback_status, evaluation_status=integrity.evaluation_status,
            signal_status=integrity.signal_status, confidence=integrity.confidence, signal_fingerprint=integrity.signal_fingerprint,
            upstream_proposal_fingerprint=integrity.upstream_proposal_fingerprint, handoff_fingerprint=integrity.handoff_fingerprint,
            result_fingerprint=integrity.result_fingerprint, application_fingerprint=integrity.application_fingerprint,
            authority_principal_id=integrity.authority_principal_id, executor_id=integrity.executor_id, failure_reason=integrity.failure_reason,
            status=E.ELIGIBLE if eligible else E.INELIGIBLE, reasons=dict(integrity.reasons), lineage=dict(integrity.lineage),
        )

    def _proposal(self, eligible=True):
        source=self._eligibility(eligible)
        return PS().propose(source, proposal_id="proposal-84", proposal_payload={"change":"x"} if eligible else None)

    def test_proposed_accepts(self):
        result=S().decide(self._proposal(), decision_id="decision-84", accept=True)
        self.assertEqual(result.decision_status,D.ACCEPTED)

    def test_proposed_rejects_without_acceptance(self):
        result=S().decide(self._proposal(), decision_id="decision-84", accept=False)
        self.assertEqual(result.decision_status,D.REJECTED)

    def test_blocked_proposal_stays_blocked(self):
        result=S().decide(self._proposal(False), decision_id="decision-84", accept=True)
        self.assertEqual(result.decision_status,D.BLOCKED)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError): S().decide(object(), decision_id="decision-84")

    def test_blank_decision_id_rejected(self):
        with self.assertRaises(ValueError): S().decide(self._proposal(), decision_id=" ")

    def test_provenance_and_fingerprints_preserved(self):
        source=self._proposal(); result=S().decide(source, decision_id="decision-84", accept=True)
        for name in ("proposal_id","source_proposal_id","eligibility_id","eligibility_source_id","integrity_id","signal_id","evaluation_id","feedback_id","classification_id","application_id","source_integrity_id","feedback_signal_id","feedback_source_id","source_evaluation_id","execution_id","handoff_id","authorization_id","validation_id","source_signal_id","outcome_id","preparation_id","environment_id","expected_model_id","observed_model_id","proposal_kind","source_application_status","source_decision_status","source_outcome_status","source_feedback_status","source_evaluation_status","source_signal_status","confidence","signal_fingerprint","upstream_proposal_fingerprint","handoff_fingerprint","result_fingerprint","application_fingerprint","authority_principal_id","executor_id","failure_reason"):
            self.assertEqual(getattr(result,name),getattr(source,name))

    def test_decision_basis_reasons_lineage_are_immutable(self):
        result=S().decide(self._proposal(), decision_id="decision-84", accept=True, decision_basis={"nested":{"x":1}}, reasons={"nested":{"r":1}}, lineage={"nested":{"l":[1]}})
        self.assertIsInstance(result.decision_basis,MappingProxyType); self.assertIsInstance(result.reasons,MappingProxyType); self.assertIsInstance(result.lineage,MappingProxyType)
        with self.assertRaises(TypeError): result.decision_basis["nested"]["x"]=2

    def test_source_remains_unchanged(self):
        source=self._proposal(); before=dict(source.lineage); S().decide(source, decision_id="decision-84", accept=True)
        self.assertEqual(dict(source.lineage),before); self.assertEqual(source.proposal_status,P.PROPOSED)

    def test_blocked_decision_cannot_be_constructed_from_proposed_status(self):
        source=self._proposal(); values=dict(S().decide(source, decision_id="decision-84").__dict__); values["decision_status"]=D.BLOCKED
        with self.assertRaises(ValueError): EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3(**values)

    def test_decision_is_advisory_only(self):
        result=S().decide(self._proposal(), decision_id="decision-84", accept=True)
        self.assertTrue(result.is_advisory_only)
        for prop in ("authorizes_adaptation","grants_authority","updates_model","mutates_memory","mutates_policy","mutates_persistence","schedules_work","executes_action"):
            self.assertFalse(getattr(result,prop))

if __name__ == "__main__": unittest.main()
