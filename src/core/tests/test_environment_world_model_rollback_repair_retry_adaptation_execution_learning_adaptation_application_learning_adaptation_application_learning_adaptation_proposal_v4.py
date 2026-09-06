"""Focused tests for M23.93 application learning adaptation proposal v4."""
from __future__ import annotations

import unittest
from dataclasses import replace
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_proposal_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4 as Proposal,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Service as ProposalService,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status as ProposalStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_eligibility_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4 as Eligibility,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4Status as EligibilityStatus,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4Error,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_signal_integrity_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4Status as IntegrityStatus,
)


SHA = "a" * 64


def eligibility(status: EligibilityStatus = EligibilityStatus.ELIGIBLE) -> Eligibility:
    integrity_status = (
        IntegrityStatus.VALID if status is EligibilityStatus.ELIGIBLE else IntegrityStatus.INVALID
    )
    return Eligibility(
        eligibility_id="eligibility-93",
        integrity_id="integrity-92",
        signal_id="signal-90",
        evaluation_id="evaluation-89",
        feedback_id="feedback-88",
        feedback_source_id="feedback-source-88",
        classification_id="classification-87",
        source_integrity_id="integrity-91",
        application_id="application-86",
        decision_id="decision-85",
        proposal_id="source-proposal-84",
        outcome_id="outcome-83",
        outcome_status="SUCCESS",
        feedback_status="SUCCESS_FEEDBACK",
        confidence=0.91,
        signal_fingerprint=SHA,
        source_signal_fingerprint=SHA,
        result_fingerprint=SHA,
        application_fingerprint=SHA,
        failure_reason=None if status is EligibilityStatus.ELIGIBLE else "upstream invalid integrity",
        evaluation_status="VALID",
        signal_status="VALID",
        integrity_status=integrity_status,
        status=status,
        reasons={"nested": {"items": ["reason"]}},
        lineage={"parents": ["integrity-91", "signal-90"]},
    )


class M23_93ApplicationLearningAdaptationProposalV4Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ProposalService()

    def test_eligible_becomes_proposed_adaptation_candidate(self) -> None:
        result = self.service.propose(
            eligibility(),
            proposal_id="proposal-93",
            proposal_payload={"target": "bounded-learning-state", "change": "adjust"},
        )
        self.assertEqual(result.proposal_status, ProposalStatus.PROPOSED)
        self.assertEqual(result.proposal_kind, "ADAPTATION_CANDIDATE")
        self.assertIsNotNone(result.proposal_payload)

    def test_ineligible_becomes_blocked_candidate(self) -> None:
        result = self.service.propose(
            eligibility(EligibilityStatus.INELIGIBLE),
            proposal_id="proposal-93-blocked",
            proposal_payload={"target": "must-not-appear"},
        )
        self.assertEqual(result.proposal_status, ProposalStatus.BLOCKED)
        self.assertEqual(result.proposal_kind, "BLOCKED_ADAPTATION_CANDIDATE")
        self.assertIsNone(result.proposal_payload)

    def test_eligible_requires_mapping_payload(self) -> None:
        with self.assertRaises(ValueError):
            self.service.propose(eligibility(), proposal_id="proposal-93", proposal_payload=None)

    def test_non_mapping_payload_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.service.propose(eligibility(), proposal_id="proposal-93", proposal_payload=["bad"])

    def test_blocked_candidate_never_carries_payload(self) -> None:
        result = self.service.propose(
            eligibility(EligibilityStatus.INELIGIBLE),
            proposal_id="proposal-93-blocked",
            proposal_payload={"secret": "payload"},
        )
        self.assertIsNone(result.proposal_payload)

    def test_blank_proposal_id_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            self.service.propose(eligibility(), proposal_id=" ", proposal_payload={"x": 1})

    def test_wrong_source_type_fails_closed(self) -> None:
        with self.assertRaises(TypeError):
            self.service.propose(object(), proposal_id="proposal-93", proposal_payload={"x": 1})

    def test_new_identity_and_source_provenance_are_preserved(self) -> None:
        source = eligibility()
        result = self.service.propose(
            source,
            proposal_id="proposal-93",
            proposal_payload={"x": 1},
        )
        self.assertEqual(result.proposal_id, "proposal-93")
        self.assertNotEqual(result.proposal_id, source.proposal_id)
        for field_name in (
            "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id",
            "feedback_source_id", "classification_id", "source_integrity_id", "application_id",
            "source_decision_id", "source_proposal_id", "outcome_id", "outcome_status",
            "feedback_status", "confidence", "signal_fingerprint", "source_signal_fingerprint",
            "result_fingerprint", "application_fingerprint", "failure_reason", "evaluation_status",
            "signal_status",
        ):
            source_name = "decision_id" if field_name == "source_decision_id" else "proposal_id" if field_name == "source_proposal_id" else field_name
            self.assertEqual(getattr(result, field_name), getattr(source, source_name))
        self.assertEqual(result.eligibility_status, EligibilityStatus.ELIGIBLE)

    def test_failure_evidence_is_preserved(self) -> None:
        source = eligibility(EligibilityStatus.INELIGIBLE)
        result = self.service.propose(source, proposal_id="proposal-93-blocked")
        self.assertEqual(result.failure_reason, "upstream invalid integrity")

    def test_payload_reasons_and_lineage_are_recursively_immutable(self) -> None:
        result = self.service.propose(
            eligibility(),
            proposal_id="proposal-93",
            proposal_payload={"outer": {"items": [1, 2]}},
            reasons={"reason": {"values": ["a", "b"]}},
            lineage={"chain": ["eligibility-93"]},
        )
        self.assertIsInstance(result.proposal_payload, MappingProxyType)
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertEqual(result.proposal_payload["outer"]["items"], (1, 2))
        with self.assertRaises(TypeError):
            result.proposal_payload["new"] = "blocked"
        with self.assertRaises(TypeError):
            result.reasons["new"] = "blocked"
        with self.assertRaises(TypeError):
            result.lineage["new"] = "blocked"

    def test_source_is_not_mutated(self) -> None:
        source = eligibility()
        original = (
            source.eligibility_id,
            source.proposal_id,
            source.status,
            source.reasons,
            source.lineage,
        )
        result = self.service.propose(source, proposal_id="proposal-93", proposal_payload={"x": 1})
        self.assertEqual(
            (
                source.eligibility_id,
                source.proposal_id,
                source.status,
                source.reasons,
                source.lineage,
            ),
            original,
        )
        self.assertEqual(result.eligibility_id, "eligibility-93")

    def test_status_and_kind_contract_is_enforced(self) -> None:
        result = self.service.propose(eligibility(), proposal_id="proposal-93", proposal_payload={"x": 1})
        with self.assertRaises(ValueError):
            replace(result, proposal_kind="BLOCKED_ADAPTATION_CANDIDATE")

    def test_blocked_status_rejects_payload(self) -> None:
        result = self.service.propose(
            eligibility(EligibilityStatus.INELIGIBLE),
            proposal_id="proposal-93-blocked",
        )
        with self.assertRaises(ValueError):
            replace(
                result,
                proposal_status=ProposalStatus.BLOCKED,
                proposal_kind="BLOCKED_ADAPTATION_CANDIDATE",
                proposal_payload={"x": 1},
            )

    def test_fingerprint_contract_is_preserved(self) -> None:
        with self.assertRaises(ValueError):
            Eligibility(
                eligibility_id="eligibility-93",
                integrity_id="integrity-92",
                signal_id="signal-90",
                evaluation_id="evaluation-89",
                feedback_id="feedback-88",
                feedback_source_id="feedback-source-88",
                classification_id="classification-87",
                source_integrity_id="integrity-91",
                application_id="application-86",
                decision_id="decision-85",
                proposal_id="source-proposal-84",
                outcome_id="outcome-83",
                outcome_status="SUCCESS",
                feedback_status="SUCCESS_FEEDBACK",
                confidence=0.91,
                signal_fingerprint="short",
                source_signal_fingerprint=SHA,
                result_fingerprint=SHA,
                application_fingerprint=SHA,
                failure_reason=None,
                evaluation_status="VALID",
                signal_status="VALID",
                integrity_status=IntegrityStatus.VALID,
                status=EligibilityStatus.ELIGIBLE,
            )

    def test_authority_and_mutation_walls_are_false(self) -> None:
        result = self.service.propose(
            eligibility(),
            proposal_id="proposal-93",
            proposal_payload={"x": 1},
        )
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.authorizes_adaptation)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.is_learning)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_memory)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.mutates_persistence)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)


if __name__ == "__main__":
    unittest.main()
