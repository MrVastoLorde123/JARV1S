import unittest

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_proposal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_decision_v3 import (
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


def application(decision_accept=True, blocked=False, failing=False):
    p = proposal(blocked=blocked)
    d = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service().decide(
        p, decision_id="decision-1", accept=decision_accept
    )
    status = (
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.BLOCKED
        if blocked else
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.NOT_APPLIED
        if (not decision_accept or failing) else
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.APPLIED
    )
    return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3(
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
        proposal_status=p.proposal_status, decision_status=d.decision_status, application_status=status,
        applied_payload=None if status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.APPLIED else p.proposal_payload,
        application_result=None if status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.APPLIED else {"applied": True},
        failure_reason="applier failed" if failing else None,
    )


class M23_76AdaptationApplicationIntegrityV3Tests(unittest.TestCase):
    def test_applied_application_is_valid_and_fingerprinted(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service().verify(
            application(), integrity_id="application-integrity-1"
        )
        self.assertEqual(result.integrity_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status.VALID)
        self.assertEqual(len(result.application_fingerprint), 64)
        self.assertTrue(result.application_integrity)

    def test_rejected_application_is_valid(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service().verify(
            application(decision_accept=False), integrity_id="application-integrity-1"
        )
        self.assertEqual(result.integrity_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status.VALID)

    def test_failed_application_is_valid_failure_evidence(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service().verify(
            application(failing=True), integrity_id="application-integrity-1"
        )
        self.assertEqual(result.integrity_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status.VALID)
        self.assertEqual(result.failure_reason, "applier failed")

    def test_blocked_application_is_valid(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service().verify(
            application(blocked=True), integrity_id="application-integrity-1"
        )
        self.assertEqual(result.integrity_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status.VALID)

    def test_tampered_application_becomes_invalid(self):
        source = application()
        object.__setattr__(source, "application_result", {"tampered": True})
        object.__setattr__(source, "failure_reason", "unexpected")
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service().verify(
            source, integrity_id="application-integrity-1"
        )
        self.assertEqual(result.integrity_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status.INVALID)
        self.assertIsNotNone(result.failure_reason)

    def test_wrong_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service().verify(
                object(), integrity_id="application-integrity-1"
            )

    def test_blank_integrity_id_fails_closed(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service().verify(
                application(), integrity_id=""
            )

    def test_application_fingerprint_is_deterministic(self):
        service = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service()
        first = service.verify(application({}), integrity_id="application-integrity-1")
        second = service.verify(application({}), integrity_id="application-integrity-2")
        self.assertEqual(first.application_fingerprint, second.application_fingerprint)

    def test_integrity_artifact_recursively_freezes_evidence(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service().verify(
            application(), integrity_id="application-integrity-1", reasons={"nested": {"x": [1]}}, lineage={"nested": {"y": [2]}}
        )
        with self.assertRaises(TypeError):
            result.reasons["nested"] = {}
        with self.assertRaises(TypeError):
            result.lineage["nested"] = {}
        with self.assertRaises(TypeError):
            result.applied_payload["learning_rate"] = 0.4

    def test_integrity_is_advisory_and_does_not_authorize(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service().verify(
            application(), integrity_id="application-integrity-1"
        )
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.authorizes_adaptation)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.mutates_policy)

    def test_source_application_remains_unchanged(self):
        source = application()
        before = source.applied_payload
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service().verify(
            source, integrity_id="application-integrity-1"
        )
        self.assertEqual(source.applied_payload, before)


if __name__ == "__main__":
    unittest.main()
