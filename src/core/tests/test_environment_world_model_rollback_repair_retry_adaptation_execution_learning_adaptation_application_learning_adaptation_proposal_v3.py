import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_eligibility_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Status as E,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_proposal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Service as S,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status as P,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_signal_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3Status as I,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_signal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalV3Status as L,
)


class M23_83ApplicationLearningAdaptationProposalV3Tests(unittest.TestCase):
    def _integrity(self, status=I.VALID):
        signal_status = L.NEGATIVE_SIGNAL if status is I.INVALID else L.POSITIVE_SIGNAL
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3(
            integrity_id="integrity-83", signal_id="signal-83", evaluation_id="evaluation-83", feedback_id="feedback-83",
            classification_id="classification-83", source_integrity_id="source-integrity-83", application_id="application-83",
            decision_id="decision-83", proposal_id="proposal-83", source_proposal_id="source-proposal-83", eligibility_id="prior-83",
            feedback_signal_id="feedback-signal-83", feedback_source_id="feedback-source-83", source_evaluation_id="source-evaluation-83",
            execution_id="execution-83", handoff_id="handoff-83", authorization_id="authorization-83", validation_id="validation-83",
            source_signal_id="source-signal-83", outcome_id="outcome-83", preparation_id="preparation-83", assessment_id="assessment-83",
            environment_id="environment-83", expected_model_id="expected-83", observed_model_id="observed-83", proposal_kind="ADAPTATION_CANDIDATE",
            proposal_status="PROPOSED", decision_status="ACCEPTED", application_status="APPLIED", integrity_status=status,
            outcome_status="SUCCESS", feedback_status="SUCCESS_SIGNAL", evaluation_status="SUCCESS_EVALUATION", signal_status=signal_status,
            confidence=.83, signal_fingerprint="a"*64, upstream_proposal_fingerprint="b"*64, handoff_fingerprint="c"*64,
            result_fingerprint="d"*64, application_fingerprint="e"*64, authority_principal_id="user:test", executor_id="executor:test",
            failure_reason=None, status=status, reasons={"source":"test"}, lineage={"nested":{"id":"83"}},
        )

    def _eligibility(self, status=E.ELIGIBLE):
        source=self._integrity(I.VALID if status is E.ELIGIBLE else I.INVALID)
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3(
            eligibility_id="eligibility-83", integrity_id=source.integrity_id, signal_id=source.signal_id,
            evaluation_id=source.evaluation_id, feedback_id=source.feedback_id, classification_id=source.classification_id,
            source_integrity_id=source.source_integrity_id, application_id=source.application_id, decision_id=source.decision_id,
            proposal_id=source.proposal_id, source_proposal_id=source.source_proposal_id, feedback_signal_id=source.feedback_signal_id,
            feedback_source_id=source.feedback_source_id, source_evaluation_id=source.source_evaluation_id,
            eligibility_source_id=source.integrity_id, execution_id=source.execution_id, handoff_id=source.handoff_id,
            authorization_id=source.authorization_id, validation_id=source.validation_id, source_signal_id=source.source_signal_id,
            outcome_id=source.outcome_id, preparation_id=source.preparation_id, assessment_id=source.assessment_id,
            environment_id=source.environment_id, expected_model_id=source.expected_model_id, observed_model_id=source.observed_model_id,
            proposal_kind=source.proposal_kind, proposal_status=source.proposal_status, decision_status=source.decision_status,
            application_status=source.application_status, integrity_status=source.integrity_status, outcome_status=source.outcome_status,
            feedback_status=source.feedback_status, evaluation_status=source.evaluation_status, signal_status=source.signal_status,
            confidence=source.confidence, signal_fingerprint=source.signal_fingerprint,
            upstream_proposal_fingerprint=source.upstream_proposal_fingerprint, handoff_fingerprint=source.handoff_fingerprint,
            result_fingerprint=source.result_fingerprint, application_fingerprint=source.application_fingerprint,
            authority_principal_id=source.authority_principal_id, executor_id=source.executor_id, failure_reason=source.failure_reason,
            status=status, reasons=dict(source.reasons), lineage=dict(source.lineage),
        )

    def test_eligible_becomes_proposed(self):
        result=S().propose(self._eligibility(), proposal_id="proposal-new", proposal_payload={"change":"x"})
        self.assertEqual(result.proposal_status, P.PROPOSED)
        self.assertEqual(result.proposal_kind, "ADAPTATION_CANDIDATE")

    def test_ineligible_becomes_blocked_without_payload(self):
        result=S().propose(self._eligibility(E.INELIGIBLE), proposal_id="proposal-new", proposal_payload={"change":"x"})
        self.assertEqual(result.proposal_status, P.BLOCKED)
        self.assertIsNone(result.proposal_payload)
        self.assertEqual(result.proposal_kind, "BLOCKED_ADAPTATION_CANDIDATE")

    def test_eligible_requires_mapping_payload(self):
        with self.assertRaises(ValueError): S().propose(self._eligibility(), proposal_id="proposal-new")

    def test_blocked_constructor_rejects_payload(self):
        values=dict(self._build_blocked().__dict__)
        values["proposal_payload"]={"bad":True}
        with self.assertRaises(ValueError): EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3(**values)

    def _build_blocked(self):
        return S().propose(self._eligibility(E.INELIGIBLE), proposal_id="proposal-blocked")

    def test_blank_proposal_id_rejected(self):
        with self.assertRaises(ValueError): S().propose(self._eligibility(), proposal_id=" ", proposal_payload={"x":1})

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError): S().propose(object(), proposal_id="proposal-new", proposal_payload={"x":1})

    def test_provenance_and_fingerprint_chain_preserved(self):
        source=self._eligibility(); result=S().propose(source, proposal_id="proposal-new", proposal_payload={"x":1})
        same=("eligibility_id","eligibility_source_id","integrity_id","signal_id","evaluation_id","feedback_id","classification_id","application_id","decision_id","execution_id","handoff_id","authorization_id","validation_id","source_signal_id","outcome_id","preparation_id","assessment_id","environment_id","expected_model_id","observed_model_id","confidence","signal_fingerprint","upstream_proposal_fingerprint","handoff_fingerprint","result_fingerprint","application_fingerprint","authority_principal_id","executor_id","failure_reason")
        for name in same: self.assertEqual(getattr(result,name), getattr(source,name))
        self.assertEqual(result.source_proposal_id, source.proposal_id)
        self.assertEqual(result.feedback_signal_id, source.feedback_signal_id)
        self.assertEqual(result.feedback_source_id, source.feedback_source_id)
        self.assertEqual(result.source_evaluation_id, source.source_evaluation_id)
        self.assertEqual(result.source_integrity_id, source.integrity_id)

    def test_payload_reasons_lineage_are_immutable(self):
        result=S().propose(self._eligibility(), proposal_id="proposal-new", proposal_payload={"nested":{"values":[1,2]}}, reasons={"nested":{"r":"x"}}, lineage={"nested":{"l":[1]}})
        self.assertIsInstance(result.proposal_payload, MappingProxyType)
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError): result.proposal_payload["nested"]["values"]=()

    def test_source_remains_unchanged(self):
        source=self._eligibility(); before=dict(source.lineage); S().propose(source, proposal_id="proposal-new", proposal_payload={"x":1})
        self.assertEqual(dict(source.lineage), before); self.assertEqual(source.status,E.ELIGIBLE)

    def test_proposal_is_advisory_only(self):
        result=S().propose(self._eligibility(), proposal_id="proposal-new", proposal_payload={"x":1})
        self.assertTrue(result.is_advisory_only)
        for prop in ("authorizes_adaptation","grants_authority","updates_model","mutates_memory","mutates_policy","mutates_persistence","schedules_work","executes_action"):
            self.assertFalse(getattr(result,prop))

if __name__ == "__main__": unittest.main()
