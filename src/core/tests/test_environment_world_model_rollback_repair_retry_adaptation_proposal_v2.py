import unittest

from src.core.environment_world_model_rollback_repair_retry_learning_eligibility_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2,
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Service,
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_signal_integrity_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_signal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status,
)


class M23_61AdaptationProposalV2Tests(unittest.TestCase):
    def _make_eligibility(self, *, eligible: bool = True):
        return EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2(
            eligibility_id="eligibility-1",
            integrity_id="integrity-1",
            signal_id="signal-1",
            evaluation_id="evaluation-1",
            feedback_id="feedback-1",
            outcome_id="outcome-1",
            execution_id="execution-1",
            preparation_id="preparation-1",
            decision_id="decision-1",
            proposal_id="upstream-proposal-1",
            assessment_id="assessment-1",
            environment_id="env-1",
            expected_model_id="model-expected",
            observed_model_id="model-observed",
            signal_integrity_status=(
                EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status.VALID
                if eligible
                else EnvironmentWorldModelRollbackRepairRetryLearningSignalIntegrityV2Status.INVALID
            ),
            signal_status=EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.POSITIVE_SIGNAL,
            confidence=0.8,
            signal_fingerprint="a" * 64,
            eligibility_status=(
                EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE
                if eligible
                else EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.INELIGIBLE
            ),
            reasons={"origin": "test"},
            lineage={"chain": {"signal": "signal-1"}},
        )

    def test_eligible_evidence_becomes_proposed(self):
        payload = {"candidate": "adjust future learning weight", "magnitude": 0.1}
        proposal = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Service().propose(
            self._make_eligibility(), proposal_id="proposal-1", proposal_payload=payload
        )
        self.assertEqual(
            proposal.proposal_status,
            EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED,
        )
        self.assertEqual(proposal.proposal_kind, "ADAPTATION_CANDIDATE")
        self.assertEqual(proposal.proposal_payload["candidate"], "adjust future learning weight")

    def test_ineligible_evidence_is_blocked(self):
        proposal = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Service().propose(
            self._make_eligibility(eligible=False),
            proposal_id="proposal-1",
            proposal_payload={"candidate": "must be discarded"},
        )
        self.assertEqual(
            proposal.proposal_status,
            EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.BLOCKED,
        )
        self.assertIsNone(proposal.proposal_payload)

    def test_provenance_and_signal_fields_are_preserved(self):
        proposal = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Service().propose(
            self._make_eligibility(), proposal_id="proposal-1", proposal_payload={"candidate": "x"}
        )
        self.assertEqual(proposal.eligibility_id, "eligibility-1")
        self.assertEqual(proposal.integrity_id, "integrity-1")
        self.assertEqual(proposal.signal_id, "signal-1")
        self.assertEqual(proposal.evaluation_id, "evaluation-1")
        self.assertEqual(proposal.feedback_id, "feedback-1")
        self.assertEqual(proposal.outcome_id, "outcome-1")
        self.assertEqual(proposal.decision_id, "decision-1")
        self.assertEqual(proposal.environment_id, "env-1")
        self.assertEqual(proposal.expected_model_id, "model-expected")
        self.assertEqual(proposal.observed_model_id, "model-observed")
        self.assertEqual(proposal.confidence, 0.8)
        self.assertEqual(proposal.signal_fingerprint, "a" * 64)

    def test_proposal_payload_rejects_missing_or_non_mapping_payload(self):
        service = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Service()
        with self.assertRaises(ValueError):
            service.propose(self._make_eligibility(), proposal_id="proposal-1")
        with self.assertRaises(ValueError):
            service.propose(self._make_eligibility(), proposal_id="proposal-1", proposal_payload=[])

    def test_nested_payload_reasons_and_lineage_are_frozen(self):
        payload = {"nested": {"items": ["a", "b"]}}
        proposal = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Service().propose(
            self._make_eligibility(),
            proposal_id="proposal-1",
            proposal_payload=payload,
            reasons={"nested": {"reason": "candidate"}},
            lineage={"nested": [{"id": "eligibility-1"}]},
        )
        with self.assertRaises(TypeError):
            proposal.proposal_payload["nested"] = {}
        with self.assertRaises(TypeError):
            proposal.reasons["nested"] = {}
        with self.assertRaises(TypeError):
            proposal.lineage["nested"] = []

    def test_proposal_is_immutable_and_has_no_authority(self):
        proposal = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Service().propose(
            self._make_eligibility(), proposal_id="proposal-1", proposal_payload={"candidate": "x"}
        )
        with self.assertRaises((AttributeError, TypeError)):
            proposal.proposal_status = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.BLOCKED
        self.assertTrue(proposal.is_advisory_only)
        self.assertFalse(proposal.authorizes_adaptation)
        self.assertFalse(proposal.requests_adaptation_execution)
        self.assertFalse(proposal.grants_authority)
        self.assertFalse(proposal.updates_model)
        self.assertFalse(proposal.mutates_memory)
        self.assertFalse(proposal.mutates_policy)
        self.assertFalse(proposal.mutates_persistence)
        self.assertFalse(proposal.schedules_work)
        self.assertFalse(proposal.executes)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Service().propose(
                object(), proposal_id="proposal-1", proposal_payload={"candidate": "x"}
            )

    def test_proposal_id_is_required(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Service().propose(
                self._make_eligibility(), proposal_id=" ", proposal_payload={"candidate": "x"}
            )

    def test_constructor_rejects_inconsistent_status(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2(
                proposal_id="proposal-1",
                eligibility_id="eligibility-1",
                integrity_id="integrity-1",
                signal_id="signal-1",
                evaluation_id="evaluation-1",
                feedback_id="feedback-1",
                outcome_id="outcome-1",
                execution_id="execution-1",
                preparation_id="preparation-1",
                decision_id="decision-1",
                source_proposal_id="proposal-1",
                assessment_id="assessment-1",
                environment_id="env-1",
                expected_model_id="expected",
                observed_model_id="observed",
                eligibility_status=EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.INELIGIBLE,
                signal_status=EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status.POSITIVE_SIGNAL,
                confidence=1.0,
                signal_fingerprint="a" * 64,
                proposal_kind="ADAPTATION_CANDIDATE",
                proposal_status=EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED,
                proposal_payload={"candidate": "x"},
            )

    def test_source_eligibility_remains_unchanged(self):
        eligibility = self._make_eligibility()
        before = dict(eligibility.__dict__)
        EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Service().propose(
            eligibility, proposal_id="proposal-1", proposal_payload={"candidate": "x"}
        )
        self.assertEqual(dict(eligibility.__dict__), before)


if __name__ == "__main__":
    unittest.main()
