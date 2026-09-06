import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_eligibility_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_signal_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_signal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_proposal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Service,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status,
)


class M23_73AdaptationProposalV3Tests(unittest.TestCase):
    def _make_eligibility(self, eligible=True):
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3(
            eligibility_id="eligibility-73",
            integrity_id="integrity-73",
            signal_id="signal-73",
            evaluation_id="evaluation-73",
            feedback_id="feedback-73",
            classification_id="classification-73",
            execution_id="execution-73",
            handoff_id="handoff-73",
            authorization_id="authorization-73",
            validation_id="validation-73",
            proposal_id="upstream-proposal-73",
            source_signal_id="source-signal-73",
            outcome_id="outcome-73",
            preparation_id="preparation-73",
            decision_id="decision-73",
            source_proposal_id="source-proposal-72",
            source_integrity_id="source-integrity-73",
            assessment_id="assessment-73",
            environment_id="env-73",
            expected_model_id="expected-73",
            observed_model_id="observed-73",
            execution_status="SUCCESS",
            feedback_status="SUCCESS_SIGNAL",
            evaluation_status="SUCCESS_EVALUATION",
            signal_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status.POSITIVE_SIGNAL,
            confidence=0.86,
            signal_fingerprint="a" * 64,
            proposal_fingerprint="b" * 64,
            handoff_fingerprint="c" * 64,
            result_fingerprint="d" * 64,
            authority_principal_id="user:test",
            executor_id="executor:test",
            failure_reason=None,
            integrity_status=(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.VALID if eligible else EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status.INVALID),
            status=(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.ELIGIBLE if eligible else EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.INELIGIBLE),
            reasons={"origin": "test"},
            lineage={"chain": {"signal": "signal-73"}},
        )

    def test_eligible_evidence_becomes_proposed(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Service().propose(
            self._make_eligibility(),
            proposal_id="proposal-73",
            proposal_payload={"candidate": "adjust future learning weight", "magnitude": 0.1},
        )
        self.assertEqual(result.proposal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.PROPOSED)
        self.assertEqual(result.proposal_kind, "ADAPTATION_CANDIDATE")
        self.assertEqual(result.proposal_payload["candidate"], "adjust future learning weight")

    def test_ineligible_evidence_is_blocked(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Service().propose(
            self._make_eligibility(False),
            proposal_id="proposal-73",
            proposal_payload={"candidate": "must not pass"},
        )
        self.assertEqual(result.proposal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.BLOCKED)
        self.assertEqual(result.proposal_kind, "BLOCKED_ADAPTATION_CANDIDATE")
        self.assertIsNone(result.proposal_payload)

    def test_provenance_and_fingerprints_are_preserved(self):
        source = self._make_eligibility()
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Service().propose(
            source, proposal_id="proposal-73", proposal_payload={"candidate": "x"}
        )
        for name in ("eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id", "classification_id", "execution_id", "handoff_id", "authorization_id", "validation_id", "source_signal_id", "outcome_id", "preparation_id", "decision_id", "source_proposal_id", "source_integrity_id", "environment_id", "expected_model_id", "observed_model_id"):
            if name == "source_proposal_id":
                self.assertEqual(result.source_proposal_id, source.proposal_id)
            else:
                self.assertEqual(getattr(result, name), getattr(source, name))
        self.assertEqual(result.proposal_id, "proposal-73")
        self.assertEqual(result.upstream_proposal_fingerprint, source.proposal_fingerprint)
        self.assertEqual(result.signal_fingerprint, source.signal_fingerprint)
        self.assertEqual(result.result_fingerprint, source.result_fingerprint)
        self.assertEqual(result.confidence, source.confidence)

    def test_eligible_requires_mapping_payload(self):
        service = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Service()
        with self.assertRaises(ValueError):
            service.propose(self._make_eligibility(), proposal_id="proposal-73")
        with self.assertRaises(ValueError):
            service.propose(self._make_eligibility(), proposal_id="proposal-73", proposal_payload=[])

    def test_nested_payload_reasons_and_lineage_are_frozen(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Service().propose(
            self._make_eligibility(),
            proposal_id="proposal-73",
            proposal_payload={"nested": {"items": [1, 2]}},
            reasons={"nested": {"reason": "candidate"}},
            lineage={"nested": [{"id": "eligibility-73"}]},
        )
        self.assertIsInstance(result.proposal_payload, MappingProxyType)
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.proposal_payload["new"] = "blocked"
        with self.assertRaises(TypeError):
            result.proposal_payload["nested"]["items"] = ()
        with self.assertRaises(TypeError):
            result.reasons["new"] = "blocked"
        with self.assertRaises(TypeError):
            result.lineage["new"] = "blocked"

    def test_proposal_is_immutable_and_has_no_authority(self):
        result = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Service().propose(
            self._make_eligibility(), proposal_id="proposal-73", proposal_payload={"candidate": "x"}
        )
        with self.assertRaises((AttributeError, TypeError)):
            result.proposal_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.BLOCKED
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.authorizes_adaptation)
        self.assertFalse(result.requests_adaptation_execution)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Service().propose(
                object(), proposal_id="proposal-73", proposal_payload={"candidate": "x"}
            )

    def test_blank_proposal_id_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Service().propose(
                self._make_eligibility(), proposal_id=" ", proposal_payload={"candidate": "x"}
            )

    def test_constructor_rejects_inconsistent_status(self):
        proposal = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Service().propose(
            self._make_eligibility(), proposal_id="proposal-73", proposal_payload={"candidate": "x"}
        )
        values = dict(proposal.__dict__)
        values["proposal_status"] = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.BLOCKED
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3(**values)

    def test_source_eligibility_remains_unchanged(self):
        source = self._make_eligibility()
        before = dict(source.__dict__)
        EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Service().propose(
            source, proposal_id="proposal-73", proposal_payload={"candidate": "x"}
        )
        self.assertEqual(dict(source.__dict__), before)
        self.assertEqual(source.status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.ELIGIBLE)


if __name__ == "__main__":
    unittest.main()
