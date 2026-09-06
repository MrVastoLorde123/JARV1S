import unittest

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_proposal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_signal_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_signal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_eligibility_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status,
)


class M23_74AdaptationDecisionV3Tests(unittest.TestCase):
    def make_proposal(self, status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.PROPOSED):
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3(
            proposal_id="proposal-73",
            eligibility_id="eligibility-72",
            integrity_id="integrity-71",
            signal_id="signal-70",
            evaluation_id="evaluation-69",
            feedback_id="feedback-68",
            classification_id="classification-67",
            execution_id="execution-66",
            handoff_id="handoff-65",
            authorization_id="authorization-64",
            validation_id="validation-63",
            source_signal_id="source-signal-70",
            outcome_id="outcome-61",
            preparation_id="preparation-60",
            decision_id="decision-59",
            source_proposal_id="eligibility-proposal-72",
            source_integrity_id="source-integrity-71",
            assessment_id="assessment-58",
            environment_id="environment-57",
            expected_model_id="expected-model-56",
            observed_model_id="observed-model-55",
            execution_status="EXECUTION_SUCCEEDED",
            feedback_status="FEEDBACK_AVAILABLE",
            evaluation_status="SUCCESS_EVALUATION",
            integrity_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID,
            eligibility_status=(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.ELIGIBLE if status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.PROPOSED else EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.INELIGIBLE),
            signal_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL,
            confidence=0.91,
            signal_fingerprint="signal-fp",
            upstream_proposal_fingerprint="proposal-fp",
            handoff_fingerprint="handoff-fp",
            result_fingerprint="result-fp",
            authority_principal_id="principal-1",
            executor_id="executor-1",
            failure_reason=None,
            proposal_kind="ADAPTATION_CANDIDATE" if status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.PROPOSED else "BLOCKED_ADAPTATION_CANDIDATE",
            proposal_status=status,
            proposal_payload={"target": "policy-x", "change": {"limit": 4}} if status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.PROPOSED else None,
            reasons={"why": "test"},
            lineage={"upstream": "eligibility-72"},
        )

    def test_proposed_accepts(self):
        decision = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service().decide(
            self.make_proposal(), decision_id="decision-74", accept=True
        )
        self.assertEqual(decision.decision_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.ACCEPTED)
        self.assertEqual(decision.proposal_id, "proposal-73")

    def test_proposed_rejects(self):
        decision = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service().decide(
            self.make_proposal(), decision_id="decision-74", accept=False
        )
        self.assertEqual(decision.decision_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.REJECTED)

    def test_blocked_stays_blocked_even_when_accept_requested(self):
        decision = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service().decide(
            self.make_proposal(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.BLOCKED),
            decision_id="decision-74", accept=True
        )
        self.assertEqual(decision.decision_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.BLOCKED)

    def test_provenance_and_fingerprints_are_preserved(self):
        source = self.make_proposal()
        decision = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service().decide(source, decision_id="decision-74", accept=True)
        for name in ("proposal_id", "source_proposal_id", "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id", "classification_id", "execution_id", "handoff_id", "authorization_id", "validation_id", "source_signal_id", "outcome_id", "preparation_id", "source_integrity_id", "assessment_id", "environment_id", "expected_model_id", "observed_model_id", "signal_fingerprint", "upstream_proposal_fingerprint", "handoff_fingerprint", "result_fingerprint", "authority_principal_id", "executor_id", "failure_reason", "proposal_kind", "confidence"):
            self.assertEqual(getattr(decision, name), getattr(source, name))

    def test_decision_basis_is_recursively_immutable(self):
        decision = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service().decide(
            self.make_proposal(), decision_id="decision-74", accept=True,
            decision_basis={"nested": {"list": [1, 2]}}
        )
        with self.assertRaises(TypeError):
            decision.decision_basis["nested"] = {}
        with self.assertRaises(TypeError):
            decision.decision_basis["nested"]["list"] = ()
        self.assertEqual(decision.decision_basis["nested"]["list"], (1, 2))

    def test_advisory_walls(self):
        decision = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service().decide(
            self.make_proposal(), decision_id="decision-74", accept=True
        )
        self.assertTrue(decision.is_advisory_only)
        self.assertFalse(decision.authorizes_adaptation)
        self.assertFalse(decision.requests_adaptation_execution)
        self.assertFalse(decision.grants_authority)
        self.assertFalse(decision.executes)
        self.assertFalse(decision.updates_model)
        self.assertFalse(decision.mutates_memory)
        self.assertFalse(decision.mutates_policy)
        self.assertFalse(decision.mutates_persistence)
        self.assertFalse(decision.schedules_work)

    def test_wrong_source_type_is_rejected(self):
        service = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service()
        with self.assertRaises(TypeError):
            service.decide(object(), decision_id="decision-74")

    def test_blank_decision_id_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service().decide(self.make_proposal(), decision_id="  ")

    def test_constructor_rejects_status_mismatch(self):
        source = self.make_proposal()
        values = {k: v for k, v in source.__dict__.items() if k != "proposal_payload"}
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3(
                **{
                    **values,
                    "decision_id": "decision-74",
                    "decision_status": EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.BLOCKED,
                    "decision_basis": {},
                }
            )

    def test_blocked_constructor_rejects_non_blocked_decision(self):
        source = self.make_proposal(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.BLOCKED)
        values = {k: v for k, v in source.__dict__.items() if k != "proposal_payload"}
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3(
                **{
                    **values,
                    "decision_id": "decision-74",
                    "decision_status": EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.REJECTED,
                    "decision_basis": {},
                }
            )

    def test_source_proposal_is_unchanged(self):
        source = self.make_proposal()
        before = source.__dict__.copy()
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service().decide(
            source, decision_id="decision-74", accept=True,
            decision_basis={"reason": "bounded"}, reasons={"source": "unchanged"}, lineage={"source": source.proposal_id}
        )
        self.assertEqual(source.__dict__, before)


if __name__ == "__main__":
    unittest.main()
