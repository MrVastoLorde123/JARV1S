import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Service as S,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status as A,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Service as DS,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_proposal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Service as PS,
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


class _Applier:
    def __init__(self):
        self.calls = []

    def apply(self, payload):
        self.calls.append(payload)
        return {"updated": True, "keys": tuple(sorted(payload))}


class _FailingApplier:
    def apply(self, payload):
        raise RuntimeError("learning applier failed")


class M23_85ApplicationLearningAdaptationApplicationV3Tests(unittest.TestCase):
    def _proposal(self, eligible=True):
        integrity = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningSignalIntegrityV3(
            integrity_id="integrity-85", signal_id="signal-85", evaluation_id="evaluation-85", feedback_id="feedback-85",
            classification_id="classification-85", source_integrity_id="source-integrity-85", application_id="application-source-85",
            decision_id="decision-source-85", proposal_id="proposal-source-85", source_proposal_id="source-proposal-85", eligibility_id="prior-85",
            feedback_signal_id="feedback-signal-85", feedback_source_id="feedback-source-85", source_evaluation_id="source-evaluation-85",
            execution_id="execution-85", handoff_id="handoff-85", authorization_id="authorization-85", validation_id="validation-85",
            source_signal_id="source-signal-85", outcome_id="outcome-85", preparation_id="preparation-85", assessment_id="assessment-85",
            environment_id="environment-85", expected_model_id="expected-85", observed_model_id="observed-85", proposal_kind="ADAPTATION_CANDIDATE",
            proposal_status="PROPOSED", decision_status="ACCEPTED", application_status="APPLIED", integrity_status=I.VALID if eligible else I.INVALID,
            outcome_status="SUCCESS", feedback_status="SUCCESS_SIGNAL", evaluation_status="SUCCESS_EVALUATION", signal_status=L.POSITIVE_SIGNAL,
            confidence=.85, signal_fingerprint="a"*64, upstream_proposal_fingerprint="b"*64, handoff_fingerprint="c"*64,
            result_fingerprint="d"*64, application_fingerprint="e"*64, authority_principal_id="user:test", executor_id="executor:test",
            failure_reason=None, status=I.VALID if eligible else I.INVALID, reasons={"source":"test"}, lineage={"nested":{"id":"85"}},
        )
        eligibility = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3(
            eligibility_id="eligibility-85", integrity_id=integrity.integrity_id, signal_id=integrity.signal_id,
            evaluation_id=integrity.evaluation_id, feedback_id=integrity.feedback_id, classification_id=integrity.classification_id,
            source_integrity_id=integrity.source_integrity_id, application_id=integrity.application_id, decision_id=integrity.decision_id,
            proposal_id=integrity.proposal_id, source_proposal_id=integrity.source_proposal_id, feedback_signal_id=integrity.feedback_signal_id,
            feedback_source_id=integrity.feedback_source_id, source_evaluation_id=integrity.source_evaluation_id,
            eligibility_source_id=integrity.integrity_id, execution_id=integrity.execution_id, handoff_id=integrity.handoff_id,
            authorization_id=integrity.authorization_id, validation_id=integrity.validation_id, source_signal_id=integrity.source_signal_id,
            outcome_id=integrity.outcome_id, preparation_id=integrity.preparation_id, assessment_id=integrity.assessment_id,
            environment_id=integrity.environment_id, expected_model_id=integrity.expected_model_id, observed_model_id=integrity.observed_model_id,
            proposal_kind=integrity.proposal_kind, proposal_status=integrity.proposal_status, decision_status=integrity.decision_status,
            application_status=integrity.application_status, integrity_status=integrity.status, outcome_status=integrity.outcome_status,
            feedback_status=integrity.feedback_status, evaluation_status=integrity.evaluation_status, signal_status=integrity.signal_status,
            confidence=integrity.confidence, signal_fingerprint=integrity.signal_fingerprint,
            upstream_proposal_fingerprint=integrity.upstream_proposal_fingerprint, handoff_fingerprint=integrity.handoff_fingerprint,
            result_fingerprint=integrity.result_fingerprint, application_fingerprint=integrity.application_fingerprint,
            authority_principal_id=integrity.authority_principal_id, executor_id=integrity.executor_id, failure_reason=integrity.failure_reason,
            status=E.ELIGIBLE if eligible else E.INELIGIBLE, reasons=dict(integrity.reasons), lineage=dict(integrity.lineage),
        )
        return PS().propose(eligibility, proposal_id="proposal-85", proposal_payload={"learning_rate": .2} if eligible else None)

    def _decision(self, proposal, accept):
        return DS().decide(proposal, decision_id="decision-85", accept=accept)

    def test_accepted_applies_learning_update(self):
        proposal = self._proposal()
        decision = self._decision(proposal, True)
        applier = _Applier()
        result = S().apply(decision, proposal, application_id="application-85", learning_applier=applier)
        self.assertEqual(result.application_status, A.APPLIED)
        self.assertTrue(result.mutates_learning_state)
        self.assertEqual(applier.calls, [{"learning_rate": .2}])
        self.assertEqual(result.applied_learning_update, {"learning_rate": .2})

    def test_rejected_does_not_invoke_learning_applier(self):
        proposal = self._proposal()
        decision = self._decision(proposal, False)
        applier = _Applier()
        result = S().apply(decision, proposal, application_id="application-85", learning_applier=applier)
        self.assertEqual(result.application_status, A.NOT_APPLIED)
        self.assertFalse(result.mutates_learning_state)
        self.assertEqual(applier.calls, [])

    def test_blocked_does_not_invoke_learning_applier(self):
        proposal = self._proposal(False)
        decision = self._decision(proposal, True)
        applier = _Applier()
        result = S().apply(decision, proposal, application_id="application-85", learning_applier=applier)
        self.assertEqual(result.application_status, A.BLOCKED)
        self.assertFalse(result.mutates_learning_state)
        self.assertEqual(applier.calls, [])

    def test_accepted_requires_learning_applier(self):
        proposal = self._proposal()
        decision = self._decision(proposal, True)
        with self.assertRaises(ValueError):
            S().apply(decision, proposal, application_id="application-85")

    def test_applier_failure_becomes_not_applied_failure_evidence(self):
        proposal = self._proposal()
        decision = self._decision(proposal, True)
        result = S().apply(decision, proposal, application_id="application-85", learning_applier=_FailingApplier())
        self.assertEqual(result.application_status, A.NOT_APPLIED)
        self.assertEqual(result.failure_reason, "learning applier failed")
        self.assertIsNone(result.applied_learning_update)

    def test_identity_mismatch_fails_closed(self):
        proposal = self._proposal()
        decision = self._decision(proposal, True)
        other = self._proposal()
        object.__setattr__(other, "proposal_id", "other-proposal")
        with self.assertRaises(ValueError):
            S().apply(decision, other, application_id="application-85", learning_applier=_Applier())

    def test_artifact_freezes_update_result_reasons_and_lineage(self):
        proposal = self._proposal()
        decision = self._decision(proposal, True)
        result = S().apply(
            decision, proposal, application_id="application-85", learning_applier=_Applier(),
            reasons={"nested": {"r": [1]}}, lineage={"nested": {"l": [2]}},
        )
        self.assertIsInstance(result.applied_learning_update, MappingProxyType)
        self.assertIsInstance(result.application_result, MappingProxyType)
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["nested"] = {}

    def test_provenance_and_fingerprints_are_preserved(self):
        proposal = self._proposal()
        decision = self._decision(proposal, True)
        result = S().apply(decision, proposal, application_id="application-85", learning_applier=_Applier())
        self.assertEqual(result.decision_id, decision.decision_id)
        for name in (
            "proposal_id", "source_proposal_id", "eligibility_id", "eligibility_source_id", "integrity_id",
            "signal_id", "evaluation_id", "feedback_id", "classification_id", "source_integrity_id",
            "feedback_signal_id", "feedback_source_id", "source_evaluation_id", "execution_id", "handoff_id",
            "authorization_id", "validation_id", "source_signal_id", "outcome_id", "preparation_id", "environment_id",
            "expected_model_id", "observed_model_id", "proposal_kind", "source_signal_status", "confidence",
            "signal_fingerprint", "upstream_proposal_fingerprint", "handoff_fingerprint", "result_fingerprint",
            "application_fingerprint", "authority_principal_id", "executor_id",
        ):
            self.assertEqual(getattr(result, name), getattr(proposal, name))
        self.assertEqual(result.application_source_id, proposal.proposal_id)

    def test_learning_application_does_not_authorize_or_execute_capabilities(self):
        proposal = self._proposal()
        decision = self._decision(proposal, True)
        result = S().apply(decision, proposal, application_id="application-85", learning_applier=_Applier())
        self.assertTrue(result.mutates_learning_state)
        self.assertFalse(result.authorizes_adaptation)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.executes_capability)
        self.assertFalse(result.schedules_work)

    def test_constructor_rejects_applied_without_update_or_result(self):
        proposal = self._proposal()
        decision = self._decision(proposal, True)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3(
                application_id="application-85", decision_id=decision.decision_id, proposal_id=proposal.proposal_id,
                source_proposal_id=proposal.source_proposal_id, eligibility_id=proposal.eligibility_id,
                eligibility_source_id=proposal.eligibility_source_id, integrity_id=proposal.integrity_id, signal_id=proposal.signal_id,
                evaluation_id=proposal.evaluation_id, feedback_id=proposal.feedback_id, classification_id=proposal.classification_id,
                application_source_id=proposal.proposal_id, source_integrity_id=proposal.source_integrity_id,
                feedback_signal_id=proposal.feedback_signal_id, feedback_source_id=proposal.feedback_source_id,
                source_evaluation_id=proposal.source_evaluation_id, execution_id=proposal.execution_id, handoff_id=proposal.handoff_id,
                authorization_id=proposal.authorization_id, validation_id=proposal.validation_id, source_signal_id=proposal.source_signal_id,
                outcome_id=proposal.outcome_id, preparation_id=proposal.preparation_id, assessment_id=proposal.assessment_id,
                environment_id=proposal.environment_id, expected_model_id=proposal.expected_model_id, observed_model_id=proposal.observed_model_id,
                proposal_kind=proposal.proposal_kind, proposal_status=proposal.proposal_status, decision_status=decision.decision_status,
                application_status=A.APPLIED, applied_learning_update=None, application_result=None,
                source_signal_status=proposal.source_signal_status, confidence=proposal.confidence,
                signal_fingerprint=proposal.signal_fingerprint, upstream_proposal_fingerprint=proposal.upstream_proposal_fingerprint,
                handoff_fingerprint=proposal.handoff_fingerprint, result_fingerprint=proposal.result_fingerprint,
                application_fingerprint=proposal.application_fingerprint, authority_principal_id=proposal.authority_principal_id,
                executor_id=proposal.executor_id, failure_reason=None,
            )


if __name__ == "__main__":
    unittest.main()
