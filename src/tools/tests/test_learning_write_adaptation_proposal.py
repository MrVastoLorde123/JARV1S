from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_decision import (
    LearningWriteAdaptationAction,
    LearningWriteAdaptationDecisionContext,
    LearningWriteAdaptationDecisionService,
)
from src.tools.learning_write_adaptation_proposal import (
    LearningWriteAdaptationProposal,
    LearningWriteAdaptationProposalContext,
    LearningWriteAdaptationProposalError,
    LearningWriteAdaptationProposalService,
)
from src.tools.learning_write_feedback_evaluation import LearningWriteFeedbackEvaluationService
from src.tools.learning_write_feedback import LearningWriteFeedbackService
from src.tools.learning_write_outcome import LearningWriteOutcome, LearningWriteOutcomeStatus


class LearningWriteAdaptationProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        outcome = self._build_outcome(LearningWriteOutcomeStatus.SUCCEEDED)
        feedback = LearningWriteFeedbackService().from_outcome(outcome)
        candidate = LearningWriteFeedbackEvaluationService().evaluate(feedback)
        decision = LearningWriteAdaptationDecisionService().decide(
            LearningWriteAdaptationDecisionContext(candidate=candidate)
        )
        self.candidate = candidate
        self.decision = decision
        self.service = LearningWriteAdaptationProposalService()
        self.adaptation = {"target": "learning_write_pipeline", "change": "reinforce_success_path"}

    @staticmethod
    def _build_outcome(status: LearningWriteOutcomeStatus) -> LearningWriteOutcome:
        common = dict(
            execution_id="exec-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            candidate_id="candidate-1",
            domain="semantic",
            status=status,
        )
        if status is LearningWriteOutcomeStatus.SUCCEEDED:
            return LearningWriteOutcome(
                **common,
                write_result={"memory_id": 42},
                result_fingerprint="fp-1",
            )
        return LearningWriteOutcome(**common, reason="writer unavailable")

    def _context(self) -> LearningWriteAdaptationProposalContext:
        return LearningWriteAdaptationProposalContext(
            decision=self.decision,
            candidate=self.candidate,
            adaptation=self.adaptation,
        )

    def test_accepted_decision_creates_proposal(self) -> None:
        proposal = self.service.propose(self._context())
        self.assertIsInstance(proposal, LearningWriteAdaptationProposal)
        self.assertEqual(proposal.decision_id, self.decision.decision_id)
        self.assertEqual(proposal.adaptation["target"], "learning_write_pipeline")

    def test_deferred_decision_creates_no_proposal(self) -> None:
        outcome = self._build_outcome(LearningWriteOutcomeStatus.FAILED)
        feedback = LearningWriteFeedbackService().from_outcome(outcome)
        candidate = LearningWriteFeedbackEvaluationService().evaluate(feedback)
        decision = LearningWriteAdaptationDecisionService().decide(
            LearningWriteAdaptationDecisionContext(candidate=candidate)
        )
        self.assertEqual(decision.action, LearningWriteAdaptationAction.DEFER)
        context = LearningWriteAdaptationProposalContext(
            decision=decision,
            candidate=candidate,
            adaptation=self.adaptation,
        )
        self.assertIsNone(self.service.propose(context))

    def test_exact_lineage_is_preserved(self) -> None:
        proposal = self.service.propose(self._context())
        assert proposal is not None
        self.assertEqual(proposal.candidate_id, self.candidate.candidate_id)
        self.assertEqual(proposal.feedback_id, self.candidate.feedback_id)
        self.assertEqual(proposal.execution_id, self.candidate.execution_id)
        self.assertEqual(proposal.admission_id, self.candidate.admission_id)
        self.assertEqual(proposal.proposal_source_candidate_id, self.candidate.source_candidate_id)
        self.assertEqual(proposal.domain, self.candidate.domain)

    def test_proposal_id_is_deterministic(self) -> None:
        first = self.service.propose(self._context())
        second = self.service.propose(self._context())
        self.assertEqual(first.proposal_id, second.proposal_id)

    def test_adaptation_is_immutable(self) -> None:
        proposal = self.service.propose(self._context())
        assert proposal is not None
        with self.assertRaises(TypeError):
            proposal.adaptation["bad"] = True  # type: ignore[index]

    def test_nested_adaptation_is_immutable(self) -> None:
        context = LearningWriteAdaptationProposalContext(
            decision=self.decision,
            candidate=self.candidate,
            adaptation={"nested": {"items": [{"x": 1}]}},
        )
        proposal = self.service.propose(context)
        assert proposal is not None
        with self.assertRaises(TypeError):
            proposal.adaptation["nested"]["items"][0]["x"] = 2

    def test_proposal_is_immutable(self) -> None:
        proposal = self.service.propose(self._context())
        assert proposal is not None
        with self.assertRaises(FrozenInstanceError):
            proposal.confidence = 1.0  # type: ignore[misc]

    def test_proposal_cannot_grant_authority(self) -> None:
        with self.assertRaises(LearningWriteAdaptationProposalError):
            LearningWriteAdaptationProposal(
                proposal_id="proposal-1",
                decision_id=self.decision.decision_id,
                candidate_id=self.candidate.candidate_id,
                feedback_id=self.candidate.feedback_id,
                execution_id=self.candidate.execution_id,
                admission_id=self.candidate.admission_id,
                proposal_source_candidate_id=self.candidate.source_candidate_id,
                domain=self.candidate.domain,
                adaptation={},
                evidence={},
                provenance={"source": "test"},
                confidence=0.5,
                reason="test",
                adaptation_write_allowed=True,
            )

    def test_proposal_is_non_writing_and_non_authorizing(self) -> None:
        proposal = self.service.propose(self._context())
        assert proposal is not None
        context = proposal.to_context()
        self.assertFalse(context["adaptation_write_allowed"])
        self.assertFalse(context["memory_mutation_allowed"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_mismatched_candidate_is_rejected(self) -> None:
        other = self.candidate.__class__(
            candidate_id="other-candidate",
            feedback_id=self.candidate.feedback_id,
            execution_id=self.candidate.execution_id,
            admission_id=self.candidate.admission_id,
            proposal_id=self.candidate.proposal_id,
            decision_id=self.candidate.decision_id,
            source_candidate_id=self.candidate.source_candidate_id,
            domain=self.candidate.domain,
            signal=self.candidate.signal,
            confidence=self.candidate.confidence,
            evidence=self.candidate.evidence,
            provenance=self.candidate.provenance,
            reason=self.candidate.reason,
        )
        with self.assertRaises(LearningWriteAdaptationProposalError):
            self.service.propose(
                LearningWriteAdaptationProposalContext(
                    decision=self.decision,
                    candidate=other,
                    adaptation=self.adaptation,
                )
            )

    def test_invalid_context_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.propose({"bad": True})  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
