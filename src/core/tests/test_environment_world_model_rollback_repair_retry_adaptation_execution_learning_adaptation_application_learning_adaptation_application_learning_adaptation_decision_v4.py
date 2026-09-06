import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_proposal_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status as P,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_decision_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4 as D,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Service as DS,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status as S,
)


class M23_94DecisionV4Tests(unittest.TestCase):
    def _proposal(self, *, status=P.PROPOSED, payload=None):
        if payload is None and status is P.PROPOSED:
            payload = {"change": {"field": "threshold", "value": 0.9}}
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4(
            proposal_id="proposal-94",
            eligibility_id="eligibility-92",
            integrity_id="integrity-91",
            signal_id="signal-90",
            evaluation_id="evaluation-89",
            feedback_id="feedback-88",
            feedback_source_id="feedback-source-88",
            classification_id="classification-87",
            source_integrity_id="source-integrity-91",
            application_id="application-86",
            source_decision_id="decision-85",
            source_proposal_id="proposal-84",
            outcome_id="outcome-83",
            outcome_status="SUCCESS",
            feedback_status="VALID",
            confidence=0.91,
            signal_fingerprint="a" * 64,
            source_signal_fingerprint="b" * 64,
            result_fingerprint="c" * 64,
            application_fingerprint="d" * 64,
            failure_reason=None if status is P.PROPOSED else "eligibility blocked",
            evaluation_status="EVALUATED",
            signal_status="VALID",
            integrity_status="VALID",
            eligibility_status=__import__(
                "src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_eligibility_v4",
                fromlist=["EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4Status"],
            ).EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4Status.ELIGIBLE
            if status is P.PROPOSED else __import__(
                "src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_eligibility_v4",
                fromlist=["EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4Status"],
            ).EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4Status.INELIGIBLE,
            proposal_status=status,
            proposal_kind="ADAPTATION_CANDIDATE" if status is P.PROPOSED else "BLOCKED_ADAPTATION_CANDIDATE",
            proposal_payload=payload,
            reasons={"nested": {"reason": "bounded"}},
            lineage={"path": ["eligibility-92", "proposal-94"]},
        )

    def test_proposed_acceptance_becomes_accepted(self):
        result = DS().decide(self._proposal(), decision_id="decision-94", accept=True)
        self.assertEqual(result.decision_status, S.ACCEPTED)

    def test_proposed_rejection_becomes_rejected(self):
        result = DS().decide(self._proposal(), decision_id="decision-94", accept=False)
        self.assertEqual(result.decision_status, S.REJECTED)

    def test_blocked_proposal_remains_blocked(self):
        result = DS().decide(self._proposal(status=P.BLOCKED), decision_id="decision-94", accept=True)
        self.assertEqual(result.decision_status, S.BLOCKED)

    def test_acceptance_input_cannot_override_blocked_status(self):
        result = DS().decide(self._proposal(status=P.BLOCKED), decision_id="decision-94", accept=False)
        self.assertEqual(result.decision_status, S.BLOCKED)

    def test_new_identity_and_proposal_identity_are_preserved(self):
        result = DS().decide(self._proposal(), decision_id="decision-new", accept=True)
        self.assertEqual(result.decision_id, "decision-new")
        self.assertEqual(result.proposal_id, "proposal-94")
        self.assertNotEqual(result.decision_id, result.proposal_id)

    def test_provenance_and_fingerprints_are_preserved(self):
        source = self._proposal()
        result = DS().decide(source, decision_id="decision-94", accept=True)
        for name in ("eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id", "feedback_source_id", "classification_id", "source_integrity_id", "application_id", "source_decision_id", "source_proposal_id", "outcome_id"):
            self.assertEqual(getattr(result, name), getattr(source, name))
        for name in ("signal_fingerprint", "source_signal_fingerprint", "result_fingerprint", "application_fingerprint"):
            self.assertEqual(getattr(result, name), getattr(source, name))
        self.assertEqual(result.confidence, source.confidence)
        self.assertEqual(result.failure_reason, source.failure_reason)

    def test_proposal_payload_is_not_executable_decision_authority(self):
        result = DS().decide(self._proposal(), decision_id="decision-94", accept=True)
        self.assertNotIn("proposal_payload", result.__dataclass_fields__)
        self.assertEqual(result.decision_basis["decision"], "ACCEPTED")
        self.assertTrue(result.is_advisory_only)

    def test_decision_basis_reasons_and_lineage_are_recursively_immutable(self):
        result = DS().decide(
            self._proposal(),
            decision_id="decision-94",
            accept=True,
            decision_basis={"outer": {"inner": ["x"]}},
            reasons={"reason": {"code": "R1"}},
            lineage={"chain": ["proposal-94", {"next": "decision-94"}]},
        )
        self.assertIsInstance(result.decision_basis, MappingProxyType)
        self.assertIsInstance(result.decision_basis["outer"], MappingProxyType)
        self.assertEqual(result.decision_basis["outer"]["inner"], ("x",))
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.decision_basis["x"] = 1

    def test_source_is_not_mutated(self):
        source = self._proposal()
        before = source.proposal_payload
        result = DS().decide(source, decision_id="decision-94", accept=True)
        self.assertEqual(source.proposal_payload, before)
        self.assertEqual(result.proposal_id, source.proposal_id)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            DS().decide(object(), decision_id="decision-94", accept=True)

    def test_blank_decision_id_fails_closed(self):
        with self.assertRaises(ValueError):
            DS().decide(self._proposal(), decision_id="   ", accept=True)

    def test_blocked_decision_contract_rejects_mismatched_direct_construction(self):
        source = self._proposal(status=P.BLOCKED)
        with self.assertRaises(ValueError):
            D(
                decision_id="decision-94",
                proposal_id=source.proposal_id,
                eligibility_id=source.eligibility_id,
                integrity_id=source.integrity_id,
                signal_id=source.signal_id,
                evaluation_id=source.evaluation_id,
                feedback_id=source.feedback_id,
                feedback_source_id=source.feedback_source_id,
                classification_id=source.classification_id,
                source_integrity_id=source.source_integrity_id,
                application_id=source.application_id,
                source_decision_id=source.source_decision_id,
                source_proposal_id=source.source_proposal_id,
                outcome_id=source.outcome_id,
                outcome_status=source.outcome_status,
                feedback_status=source.feedback_status,
                confidence=source.confidence,
                signal_fingerprint=source.signal_fingerprint,
                source_signal_fingerprint=source.source_signal_fingerprint,
                result_fingerprint=source.result_fingerprint,
                application_fingerprint=source.application_fingerprint,
                failure_reason=source.failure_reason,
                evaluation_status=source.evaluation_status,
                signal_status=source.signal_status,
                integrity_status=source.integrity_status,
                eligibility_status=source.eligibility_status,
                proposal_status=source.proposal_status,
                proposal_kind=source.proposal_kind,
                decision_status=S.ACCEPTED,
                decision_basis={},
            )

    def test_authority_and_mutation_walls_are_false(self):
        result = DS().decide(self._proposal(), decision_id="decision-94", accept=True)
        for name in ("authorizes_adaptation", "grants_authority", "updates_model", "mutates_memory", "mutates_policy", "mutates_persistence", "schedules_work", "executes_action"):
            self.assertFalse(getattr(result, name))
        self.assertTrue(result.is_advisory_only)

    def test_fingerprint_contract_is_enforced(self):
        source = self._proposal()
        with self.assertRaises(ValueError):
            D(
                decision_id="decision-94",
                proposal_id=source.proposal_id,
                eligibility_id=source.eligibility_id,
                integrity_id=source.integrity_id,
                signal_id=source.signal_id,
                evaluation_id=source.evaluation_id,
                feedback_id=source.feedback_id,
                feedback_source_id=source.feedback_source_id,
                classification_id=source.classification_id,
                source_integrity_id=source.source_integrity_id,
                application_id=source.application_id,
                source_decision_id=source.source_decision_id,
                source_proposal_id=source.source_proposal_id,
                outcome_id=source.outcome_id,
                outcome_status=source.outcome_status,
                feedback_status=source.feedback_status,
                confidence=source.confidence,
                signal_fingerprint="bad",
                source_signal_fingerprint=source.source_signal_fingerprint,
                result_fingerprint=source.result_fingerprint,
                application_fingerprint=source.application_fingerprint,
                failure_reason=source.failure_reason,
                evaluation_status=source.evaluation_status,
                signal_status=source.signal_status,
                integrity_status=source.integrity_status,
                eligibility_status=source.eligibility_status,
                proposal_status=source.proposal_status,
                proposal_kind=source.proposal_kind,
                decision_status=S.ACCEPTED,
                decision_basis={},
            )


if __name__ == "__main__":
    unittest.main()
