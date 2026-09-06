import unittest

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_outcome_classification_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Service,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_proposal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_feedback_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status,
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
    feedback_id="feedback-source-1", classification_id="classification-source-1", execution_id="execution-1", handoff_id="handoff-1",
    authorization_id="authorization-1", validation_id="validation-1", source_signal_id="source-signal-1", outcome_id="outcome-1",
    preparation_id="preparation-1", source_proposal_id="source-proposal-1", source_integrity_id="source-integrity-1",
    assessment_id=None, environment_id="environment-1", expected_model_id="expected-1", observed_model_id="observed-1",
    confidence=0.9, signal_fingerprint="signal-fp", upstream_proposal_fingerprint="proposal-fp",
    handoff_fingerprint="handoff-fp", result_fingerprint="result-fp", authority_principal_id=None, executor_id=None,
    proposal_kind="ADAPTATION_CANDIDATE", decision_id="decision-source-1", failure_reason=None,
    execution_status="SUCCESS", feedback_status="SUCCESS", evaluation_status="SUCCESS",
    integrity_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID,
    eligibility_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.ELIGIBLE,
    signal_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL,
    proposal_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.PROPOSED,
)


def source_application(*, mode="applied"):
    values = dict(BASE)
    payload = {"learning_rate": 0.2}
    if mode == "blocked":
        values.update(
            eligibility_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.INELIGIBLE,
            proposal_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.BLOCKED,
            proposal_kind="BLOCKED_ADAPTATION_CANDIDATE",
        )
        payload = None
    proposal = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3(
        proposal_id="proposal-1", proposal_payload=payload, reasons={"source": "test"}, lineage={"root": "test"}, **values
    )
    decision = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service().decide(
        proposal, decision_id="decision-1", accept=(mode not in {"rejected", "blocked"})
    )
    status = {
        "applied": EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.APPLIED,
        "failure": EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.NOT_APPLIED,
        "rejected": EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.NOT_APPLIED,
        "blocked": EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.BLOCKED,
    }[mode]
    return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3(
        application_id="application-1", decision_id=decision.decision_id, proposal_id=proposal.proposal_id,
        source_proposal_id=proposal.source_proposal_id, eligibility_id=proposal.eligibility_id,
        integrity_id=proposal.integrity_id, signal_id=proposal.signal_id, evaluation_id=proposal.evaluation_id,
        feedback_id=proposal.feedback_id, classification_id=proposal.classification_id, execution_id=proposal.execution_id,
        handoff_id=proposal.handoff_id, authorization_id=proposal.authorization_id, validation_id=proposal.validation_id,
        source_signal_id=proposal.source_signal_id, outcome_id=proposal.outcome_id, preparation_id=proposal.preparation_id,
        source_integrity_id=proposal.source_integrity_id, assessment_id=proposal.assessment_id, environment_id=proposal.environment_id,
        expected_model_id=proposal.expected_model_id, observed_model_id=proposal.observed_model_id, confidence=proposal.confidence,
        signal_fingerprint=proposal.signal_fingerprint, upstream_proposal_fingerprint=proposal.upstream_proposal_fingerprint,
        handoff_fingerprint=proposal.handoff_fingerprint, result_fingerprint=proposal.result_fingerprint,
        authority_principal_id=proposal.authority_principal_id, executor_id=proposal.executor_id, proposal_kind=proposal.proposal_kind,
        proposal_status=proposal.proposal_status, decision_status=decision.decision_status, application_status=status,
        applied_payload=None if status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.APPLIED else proposal.proposal_payload,
        application_result=None if status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.APPLIED else {"applied": True},
        failure_reason="applier failed" if mode == "failure" else None,
    )


def classification_of(mode="applied"):
    from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_integrity_v3 import (
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service,
    )
    integrity = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service().verify(
        source_application(mode=mode), integrity_id="application-integrity-1"
    )
    return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Service().classify(
        integrity, classification_id="outcome-classification-1"
    )


class M23_78AdaptationApplicationFeedbackV3Tests(unittest.TestCase):
    def test_applied_outcome_becomes_success_signal(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Service().record(
            classification_of(), feedback_id="feedback-1"
        )
        self.assertEqual(result.feedback_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.SUCCESS_SIGNAL)

    def test_failed_outcome_becomes_failure_signal(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Service().record(
            classification_of("failure"), feedback_id="feedback-1"
        )
        self.assertEqual(result.feedback_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.FAILURE_SIGNAL)
        self.assertEqual(result.failure_reason, "applier failed")

    def test_rejected_outcome_becomes_rejection_signal(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Service().record(
            classification_of("rejected"), feedback_id="feedback-1"
        )
        self.assertEqual(result.feedback_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.REJECTION_SIGNAL)

    def test_blocked_outcome_becomes_rejection_signal(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Service().record(
            classification_of("blocked"), feedback_id="feedback-1"
        )
        self.assertEqual(result.feedback_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Status.REJECTION_SIGNAL)

    def test_invalid_integrity_cannot_become_feedback(self):
        from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_integrity_v3 import (
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service,
        )
        source = source_application()
        object.__setattr__(source, "failure_reason", "unexpected")
        integrity = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service().verify(
            source, integrity_id="application-integrity-1"
        )
        self.assertEqual(integrity.integrity_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status.INVALID)
        with self.assertRaises(Exception):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationOutcomeClassificationV3Service().classify(
                integrity, classification_id="outcome-classification-1"
            )

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Service().record(
                object(), feedback_id="feedback-1"
            )

    def test_blank_feedback_id_fails_closed(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Service().record(
                classification_of(), feedback_id=""
            )

    def test_provenance_and_fingerprints_are_preserved(self):
        classification = classification_of()
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Service().record(
            classification, feedback_id="feedback-1"
        )
        for name in (
            "classification_id", "integrity_id", "application_id", "decision_id", "proposal_id", "source_proposal_id",
            "eligibility_id", "source_integrity_id", "signal_id", "evaluation_id", "execution_id", "handoff_id",
            "authorization_id", "validation_id", "source_signal_id", "outcome_id", "preparation_id", "environment_id",
            "signal_fingerprint", "upstream_proposal_fingerprint", "handoff_fingerprint", "result_fingerprint",
            "application_fingerprint", "proposal_kind",
        ):
            self.assertEqual(getattr(result, name), getattr(classification, name))

    def test_feedback_is_recursively_immutable(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Service().record(
            classification_of(), feedback_id="feedback-1", reasons={"nested": {"x": [1]}}, lineage={"nested": {"y": [2]}}
        )
        with self.assertRaises(TypeError):
            result.reasons["nested"] = {}
        with self.assertRaises(TypeError):
            result.lineage["nested"] = {}

    def test_feedback_is_advisory_only(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Service().record(
            classification_of(), feedback_id="feedback-1"
        )
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.creates_learning_signal)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_memory)

    def test_source_classification_remains_unchanged(self):
        classification = classification_of()
        before = classification
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationFeedbackV3Service().record(
            classification, feedback_id="feedback-1"
        )
        self.assertEqual(classification, before)


if __name__ == "__main__":
    unittest.main()
