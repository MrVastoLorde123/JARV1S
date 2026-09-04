from datetime import datetime, timezone
import unittest

from src.proactive import (
    InitiativeCandidate,
    InitiativeDisposition,
    InitiativeEvaluation,
    ProactiveTrigger,
    ProactiveTriggerSource,
    evaluate_initiative,
)
from src.proactive.proposal import (
    InitiativeProposal,
    ProposalEvaluation,
    ProposalStatus,
    build_proposal,
)


class ProposalBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 9, 4, 12, 0, tzinfo=timezone.utc)
        self.trigger = ProactiveTrigger(
            trigger_id="trigger-1",
            source=ProactiveTriggerSource.OBSERVATION,
            reference_id="obs-1",
            signal="task may need attention",
            observed_at=self.now,
            evidence_ids=("e1", "e2"),
        )
        self.candidate = InitiativeCandidate(
            candidate_id="candidate-1",
            trigger_id="trigger-1",
            title="Review stalled task",
            rationale="Current evidence suggests attention may be useful.",
            evidence_ids=("e1", "e2"),
            expires_at=datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc),
        )
        self.eligible = evaluate_initiative(self.trigger, self.candidate, now=self.now)

    def test_eligible_candidate_forms_proposal(self) -> None:
        result = build_proposal(
            self.candidate,
            self.eligible,
            proposal_id="proposal-1",
            recommendation="Review the task status and identify the blocking condition.",
            created_at=self.now,
            confidence=0.8,
        )
        self.assertIsInstance(result, ProposalEvaluation)
        self.assertEqual(result.status, ProposalStatus.PROPOSED)
        self.assertIsNotNone(result.proposal)

    def test_proposal_preserves_identity_and_evidence(self) -> None:
        result = build_proposal(
            self.candidate,
            self.eligible,
            proposal_id="proposal-1",
            recommendation="Review the task.",
            created_at=self.now,
        )
        proposal = result.proposal
        assert proposal is not None
        self.assertEqual(proposal.candidate_id, self.candidate.candidate_id)
        self.assertEqual(proposal.trigger_id, self.trigger.trigger_id)
        self.assertEqual(proposal.evidence_ids, self.candidate.evidence_ids)

    def test_non_eligible_candidate_requires_review(self) -> None:
        suppressed = evaluate_initiative(
            self.trigger,
            self.candidate,
            now=self.now,
            suppressed=True,
        )
        result = build_proposal(
            self.candidate,
            suppressed,
            proposal_id="proposal-1",
            recommendation="Review the task.",
            created_at=self.now,
        )
        self.assertEqual(result.status, ProposalStatus.NEEDS_REVIEW)
        self.assertIsNone(result.proposal)

    def test_evaluation_identity_mismatch_is_rejected(self) -> None:
        mismatched = InitiativeEvaluation(
            candidate_id="other-candidate",
            trigger_id=self.trigger.trigger_id,
            disposition=InitiativeDisposition.ELIGIBLE,
            reason="test",
        )
        with self.assertRaises(ValueError):
            build_proposal(
                self.candidate,
                mismatched,
                proposal_id="proposal-1",
                recommendation="Review the task.",
                created_at=self.now,
            )

    def test_proposal_rejects_authorization(self) -> None:
        with self.assertRaises(ValueError):
            InitiativeProposal(
                proposal_id="p",
                candidate_id="c",
                trigger_id="t",
                title="title",
                recommendation="recommendation",
                rationale="rationale",
                authorization_granted=True,
            )

    def test_proposal_rejects_execution(self) -> None:
        with self.assertRaises(ValueError):
            InitiativeProposal(
                proposal_id="p",
                candidate_id="c",
                trigger_id="t",
                title="title",
                recommendation="recommendation",
                rationale="rationale",
                execution_requested=True,
            )

    def test_confidence_is_bounded(self) -> None:
        with self.assertRaises(ValueError):
            InitiativeProposal(
                proposal_id="p",
                candidate_id="c",
                trigger_id="t",
                title="title",
                recommendation="recommendation",
                rationale="rationale",
                confidence=1.1,
            )

    def test_context_exposes_no_authority(self) -> None:
        result = build_proposal(
            self.candidate,
            self.eligible,
            proposal_id="proposal-1",
            recommendation="Review the task.",
            created_at=self.now,
        )
        context = result.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["proposal"]["authorization_granted"])
        self.assertFalse(context["proposal"]["execution_requested"])


if __name__ == "__main__":
    unittest.main()
