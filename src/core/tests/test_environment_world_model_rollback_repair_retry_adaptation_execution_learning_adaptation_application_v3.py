import unittest

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_proposal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_eligibility_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_signal_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_signal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status,
)


BASE = dict(
    eligibility_id="eligibility-1", integrity_id="integrity-1", signal_id="signal-1", evaluation_id="evaluation-1",
    feedback_id="feedback-1", classification_id="classification-1", execution_id="execution-1", handoff_id="handoff-1",
    authorization_id="authorization-1", validation_id="validation-1", source_signal_id="source-signal-1", outcome_id="outcome-1",
    preparation_id="preparation-1", decision_id="upstream-decision-1", source_proposal_id="source-proposal-1",
    source_integrity_id="source-integrity-1", assessment_id=None, environment_id="environment-1", expected_model_id="expected-1",
    observed_model_id="observed-1", execution_status="SUCCESS", feedback_status="SUCCESS", evaluation_status="SUCCESS",
    integrity_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID,
    eligibility_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.ELIGIBLE,
    signal_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL,
    confidence=0.9, signal_fingerprint="signal-fp", upstream_proposal_fingerprint="proposal-fp", handoff_fingerprint="handoff-fp",
    result_fingerprint="result-fp", authority_principal_id=None, executor_id=None, failure_reason=None,
    proposal_kind="ADAPTATION_CANDIDATE", proposal_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.PROPOSED,
)


class _Applier:
    def __init__(self):
        self.calls = []

    def apply(self, payload):
        self.calls.append(payload)
        return {"applied": True, "keys": tuple(sorted(payload))}


class _FailingApplier:
    def apply(self, payload):
        raise RuntimeError("applier failed")


def proposal(payload=None, blocked=False):
    values = dict(BASE)
    if blocked:
        values.update(
            eligibility_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.INELIGIBLE,
            proposal_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.BLOCKED,
            proposal_kind="BLOCKED_ADAPTATION_CANDIDATE",
        )
    return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3(
        proposal_id="proposal-1", proposal_payload=None if blocked else (payload or {"learning_rate": 0.2}),
        reasons={"source": "test"}, lineage={"root": "test"}, **values
    )


def decision(source, accept):
    return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service().decide(
        source, decision_id="decision-1", accept=accept
    )


class M23_75AdaptationApplicationV3Tests(unittest.TestCase):
    def test_accepted_decision_invokes_applier_and_returns_applied(self):
        p = proposal({"learning_rate": 0.2})
        d = decision(p, True)
        a = _Applier()
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Service().apply(
            d, p, application_id="application-1", applier=a
        )
        self.assertEqual(result.application_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.APPLIED)
        self.assertTrue(result.mutates_learning_state)
        self.assertEqual(a.calls, [{"learning_rate": 0.2}])

    def test_rejected_decision_is_not_applied_and_does_not_invoke_applier(self):
        p = proposal()
        d = decision(p, False)
        a = _Applier()
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Service().apply(
            d, p, application_id="application-1", applier=a
        )
        self.assertEqual(result.application_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.NOT_APPLIED)
        self.assertFalse(result.mutates_learning_state)
        self.assertEqual(a.calls, [])

    def test_blocked_decision_is_blocked_and_does_not_invoke_applier(self):
        p = proposal(blocked=True)
        d = decision(p, True)
        a = _Applier()
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Service().apply(
            d, p, application_id="application-1", applier=a
        )
        self.assertEqual(result.application_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.BLOCKED)
        self.assertEqual(a.calls, [])

    def test_accepted_requires_applier(self):
        p = proposal()
        d = decision(p, True)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Service().apply(
                d, p, application_id="application-1"
            )

    def test_applier_exception_becomes_not_applied_failure_evidence(self):
        p = proposal()
        d = decision(p, True)
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Service().apply(
            d, p, application_id="application-1", applier=_FailingApplier()
        )
        self.assertEqual(result.application_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.NOT_APPLIED)
        self.assertEqual(result.failure_reason, "applier failed")

    def test_wrong_decision_type_fails_closed(self):
        p = proposal()
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Service().apply(
                object(), p, application_id="application-1", applier=_Applier()
            )

    def test_wrong_proposal_type_fails_closed(self):
        p = proposal()
        d = decision(p, True)
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Service().apply(
                d, object(), application_id="application-1", applier=_Applier()
            )

    def test_identity_mismatch_fails_closed(self):
        p = proposal()
        d = decision(p, True)
        other = proposal({"learning_rate": 0.3})
        object.__setattr__(other, "proposal_id", "other-proposal")
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Service().apply(
                d, other, application_id="application-1", applier=_Applier()
            )

    def test_application_artifact_recursively_freezes_payload_result_reasons_and_lineage(self):
        p = proposal({"nested": {"items": [1, 2]}})
        d = decision(p, True)
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Service().apply(
            d, p, application_id="application-1", applier=_Applier(), reasons={"nested": {"x": [1]}}, lineage={"nested": {"y": [2]}}
        )
        self.assertEqual(tuple(result.applied_payload["nested"]["items"]), (1, 2))
        with self.assertRaises(TypeError):
            result.applied_payload["nested"] = {"items": ()}
        with self.assertRaises(TypeError):
            result.reasons["nested"] = {}
        with self.assertRaises(TypeError):
            result.lineage["nested"] = {}

    def test_provenance_and_fingerprints_are_preserved(self):
        p = proposal()
        d = decision(p, True)
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Service().apply(
            d, p, application_id="application-1", applier=_Applier()
        )
        self.assertEqual(result.decision_id, d.decision_id)
        for name in ("proposal_id", "source_proposal_id", "eligibility_id", "integrity_id", "signal_id", "environment_id", "expected_model_id", "observed_model_id", "signal_fingerprint", "upstream_proposal_fingerprint", "handoff_fingerprint", "result_fingerprint"):
            self.assertEqual(getattr(result, name), getattr(p, name))

    def test_application_does_not_authorize_or_execute_capabilities(self):
        p = proposal()
        d = decision(p, True)
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Service().apply(
            d, p, application_id="application-1", applier=_Applier()
        )
        self.assertTrue(result.mutates_learning_state)
        self.assertFalse(result.authorizes_adaptation)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.executes_capability)
        self.assertFalse(result.schedules_work)

    def test_constructor_rejects_applied_without_payload_or_result(self):
        p = proposal()
        d = decision(p, True)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3(
                application_id="application-1", decision_id=d.decision_id, proposal_id=p.proposal_id,
                source_proposal_id=p.source_proposal_id, eligibility_id=p.eligibility_id, integrity_id=p.integrity_id,
                signal_id=p.signal_id, evaluation_id=p.evaluation_id, feedback_id=p.feedback_id, classification_id=p.classification_id,
                execution_id=p.execution_id, handoff_id=p.handoff_id, authorization_id=p.authorization_id, validation_id=p.validation_id,
                source_signal_id=p.source_signal_id, outcome_id=p.outcome_id, preparation_id=p.preparation_id,
                source_integrity_id=p.source_integrity_id, assessment_id=p.assessment_id, environment_id=p.environment_id,
                expected_model_id=p.expected_model_id, observed_model_id=p.observed_model_id, confidence=p.confidence,
                signal_fingerprint=p.signal_fingerprint, upstream_proposal_fingerprint=p.upstream_proposal_fingerprint,
                handoff_fingerprint=p.handoff_fingerprint, result_fingerprint=p.result_fingerprint,
                authority_principal_id=p.authority_principal_id, executor_id=p.executor_id, proposal_kind=p.proposal_kind,
                proposal_status=p.proposal_status, decision_status=d.decision_status,
                application_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.APPLIED,
                applied_payload=None, application_result=None, failure_reason=None,
            )


if __name__ == "__main__":
    unittest.main()
