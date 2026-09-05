from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.feedback_evaluation import LearningCandidate, LearningSignalKind
from src.tools.learning_decision import LearningAction, LearningDecision
from src.tools.learning_write_proposal import (
    LearningWriteDomain,
    LearningWriteProposal,
    LearningWriteProposalContext,
    LearningWriteProposalError,
    LearningWriteProposalService,
)


class LearningWriteProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = LearningWriteProposalService()

    @staticmethod
    def _candidate(candidate_id: str = "candidate-1") -> LearningCandidate:
        return LearningCandidate(
            candidate_id=candidate_id,
            feedback_id="feedback-1",
            execution_id="exec-1",
            handoff_id="handoff-1",
            tool_name="echo",
            signal=LearningSignalKind.SUCCESS_SIGNAL,
            confidence=0.8,
            evidence={"observed": True, "nested": {"value": 1}},
            provenance={
                "source": "execution_feedback",
                "feedback_id": "feedback-1",
                "execution_id": "exec-1",
                "handoff_id": "handoff-1",
            },
            reason="successful execution provides an observed positive signal",
        )

    @staticmethod
    def _decision(candidate: LearningCandidate, action: LearningAction = LearningAction.ACCEPT):
        return LearningDecision(
            decision_id="decision-1",
            candidate_id=candidate.candidate_id,
            action=action,
            reason="candidate may proceed",
            confidence=0.7,
        )

    def _context(self, action: LearningAction = LearningAction.ACCEPT, payload=None):
        candidate = self._candidate()
        return LearningWriteProposalContext(
            decision=self._decision(candidate, action),
            candidate=candidate,
            domain=LearningWriteDomain.SEMANTIC,
            payload=payload if payload is not None else {"content": "observed success"},
        )

    def test_accepted_decision_creates_proposal(self) -> None:
        proposal = self.service.propose(self._context())
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.decision_id, "decision-1")
        self.assertEqual(proposal.domain, LearningWriteDomain.SEMANTIC)

    def test_deferred_decision_creates_no_proposal(self) -> None:
        self.assertIsNone(self.service.propose(self._context(LearningAction.DEFER)))

    def test_rejected_decision_creates_no_proposal(self) -> None:
        self.assertIsNone(self.service.propose(self._context(LearningAction.REJECT)))

    def test_exact_candidate_identity_is_required(self) -> None:
        source = self._candidate("candidate-1")
        other = self._candidate("candidate-2")
        context = LearningWriteProposalContext(
            decision=self._decision(source),
            candidate=other,
            domain=LearningWriteDomain.SEMANTIC,
            payload={"content": "mismatch"},
        )
        with self.assertRaises(LearningWriteProposalError):
            self.service.propose(context)

    def test_proposal_preserves_identity_and_provenance(self) -> None:
        candidate = self._candidate()
        proposal = self.service.propose(
            LearningWriteProposalContext(
                decision=self._decision(candidate),
                candidate=candidate,
                domain=LearningWriteDomain.PROCEDURAL,
                payload={"rule": "validate before execution"},
            )
        )
        self.assertEqual(proposal.candidate_id, candidate.candidate_id)
        self.assertEqual(proposal.feedback_id, candidate.feedback_id)
        self.assertEqual(proposal.execution_id, candidate.execution_id)
        self.assertEqual(proposal.handoff_id, candidate.handoff_id)
        self.assertEqual(dict(proposal.provenance), dict(candidate.provenance))
        self.assertEqual(proposal.domain, LearningWriteDomain.PROCEDURAL)

    def test_proposal_confidence_is_bounded_by_source_confidence(self) -> None:
        candidate = self._candidate()
        proposal = self.service.propose(self._context())
        self.assertEqual(proposal.confidence, 0.7)
        self.assertLessEqual(proposal.confidence, candidate.confidence)

    def test_proposal_id_is_deterministic(self) -> None:
        context = self._context(payload={"content": "same"})
        first = self.service.propose(context)
        second = self.service.propose(context)
        self.assertEqual(first.proposal_id, second.proposal_id)

    def test_nested_payload_is_immutable(self) -> None:
        payload = {"items": [{"value": 1}]}
        proposal = self.service.propose(self._context(payload=payload))
        with self.assertRaises(TypeError):
            proposal.payload["items"][0]["value"] = 2

    def test_proposal_is_immutable(self) -> None:
        proposal = self.service.propose(self._context())
        with self.assertRaises(FrozenInstanceError):
            proposal.domain = LearningWriteDomain.META  # type: ignore[misc]

    def test_proposal_is_non_authorizing_and_non_writing(self) -> None:
        proposal = self.service.propose(self._context())
        context = proposal.to_context()
        self.assertFalse(context["learning_write_allowed"])
        self.assertFalse(context["learning_written"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_invalid_context_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.propose({"bad": True})  # type: ignore[arg-type]

    def test_write_proposal_cannot_grant_authority(self) -> None:
        candidate = self._candidate()
        with self.assertRaises(LearningWriteProposalError):
            LearningWriteProposal(
                proposal_id="proposal-1",
                decision_id="decision-1",
                candidate_id=candidate.candidate_id,
                feedback_id=candidate.feedback_id,
                execution_id=candidate.execution_id,
                handoff_id=candidate.handoff_id,
                tool_name=candidate.tool_name,
                domain=LearningWriteDomain.SEMANTIC,
                payload={"content": "bad"},
                evidence=candidate.evidence,
                provenance=candidate.provenance,
                confidence=0.5,
                reason="bad authority",
                learning_write_allowed=True,
            )

    def test_invalid_decision_type_is_rejected(self) -> None:
        candidate = self._candidate()
        context = LearningWriteProposalContext(
            decision="bad",  # type: ignore[arg-type]
            candidate=candidate,
            domain=LearningWriteDomain.SEMANTIC,
            payload={"x": 1},
        )
        with self.assertRaises(TypeError):
            self.service.propose(context)


if __name__ == "__main__":
    unittest.main()
