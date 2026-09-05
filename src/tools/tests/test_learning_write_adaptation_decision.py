from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_adaptation_decision import (
    DeterministicLearningWriteAdaptationDecisionProvider,
    LearningWriteAdaptationAction,
    LearningWriteAdaptationDecision,
    LearningWriteAdaptationDecisionContext,
    LearningWriteAdaptationDecisionError,
    LearningWriteAdaptationDecisionService,
)
from src.tools.learning_write_feedback_evaluation import LearningWriteFeedbackEvaluationService
from src.tools.learning_write_feedback import LearningWriteFeedbackService
from src.tools.learning_write_outcome import LearningWriteOutcome, LearningWriteOutcomeStatus


class LearningWriteAdaptationDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        outcome = self._build_outcome(LearningWriteOutcomeStatus.SUCCEEDED)
        feedback = LearningWriteFeedbackService().from_outcome(outcome)
        self.candidate = LearningWriteFeedbackEvaluationService().evaluate(feedback)
        self.service = LearningWriteAdaptationDecisionService()
        self.context = LearningWriteAdaptationDecisionContext(candidate=self.candidate)

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

    def test_success_candidate_is_accepted(self) -> None:
        decision = self.service.decide(self.context)
        self.assertEqual(decision.action, LearningWriteAdaptationAction.ACCEPT)
        self.assertEqual(decision.confidence, 0.5)

    def test_failure_candidate_is_deferred(self) -> None:
        outcome = self._build_outcome(LearningWriteOutcomeStatus.FAILED)
        feedback = LearningWriteFeedbackService().from_outcome(outcome)
        candidate = LearningWriteFeedbackEvaluationService().evaluate(feedback)
        decision = self.service.decide(LearningWriteAdaptationDecisionContext(candidate=candidate))
        self.assertEqual(decision.action, LearningWriteAdaptationAction.DEFER)

    def test_decision_is_deterministic(self) -> None:
        first = self.service.decide(self.context)
        second = self.service.decide(self.context)
        self.assertEqual(first.decision_id, second.decision_id)

    def test_exact_lineage_is_preserved(self) -> None:
        decision = self.service.decide(self.context)
        self.assertEqual(decision.candidate_id, self.candidate.candidate_id)
        self.assertEqual(decision.feedback_id, self.candidate.feedback_id)
        self.assertEqual(decision.execution_id, self.candidate.execution_id)
        self.assertEqual(decision.admission_id, self.candidate.admission_id)
        self.assertEqual(decision.proposal_id, self.candidate.proposal_id)
        self.assertEqual(decision.source_candidate_id, self.candidate.source_candidate_id)
        self.assertEqual(decision.domain, self.candidate.domain)

    def test_decision_is_immutable(self) -> None:
        decision = self.service.decide(self.context)
        with self.assertRaises(FrozenInstanceError):
            decision.action = LearningWriteAdaptationAction.REJECT  # type: ignore[misc]

    def test_metadata_is_immutable(self) -> None:
        decision = self.service.decide(self.context)
        with self.assertRaises(TypeError):
            decision.metadata["bad"] = True  # type: ignore[index]

    def test_decision_is_non_authorizing_and_non_writing(self) -> None:
        decision = self.service.decide(self.context)
        context = decision.to_context()
        self.assertFalse(context["adaptation_write_allowed"])
        self.assertFalse(context["memory_mutation_allowed"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_provider_is_replaceable(self) -> None:
        provider = DeterministicLearningWriteAdaptationDecisionProvider()
        service = LearningWriteAdaptationDecisionService(provider=provider)
        decision = service.decide(self.context)
        self.assertEqual(decision.action, LearningWriteAdaptationAction.ACCEPT)

    def test_invalid_context_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.decide({"bad": True})  # type: ignore[arg-type]

    def test_provider_identity_mismatch_is_rejected(self) -> None:
        class BadProvider:
            def decide(self, context):
                candidate = context.candidate
                return LearningWriteAdaptationDecision(
                    decision_id="bad-decision",
                    candidate_id="wrong-candidate",
                    feedback_id=candidate.feedback_id,
                    execution_id=candidate.execution_id,
                    admission_id=candidate.admission_id,
                    proposal_id=candidate.proposal_id,
                    source_candidate_id=candidate.source_candidate_id,
                    domain=candidate.domain,
                    action=LearningWriteAdaptationAction.ACCEPT,
                    reason="bad",
                    confidence=0.5,
                )

        with self.assertRaises(LearningWriteAdaptationDecisionError):
            LearningWriteAdaptationDecisionService(provider=BadProvider()).decide(self.context)

    def test_authority_flags_cannot_be_enabled(self) -> None:
        with self.assertRaises(LearningWriteAdaptationDecisionError):
            LearningWriteAdaptationDecision(
                decision_id="decision-1",
                candidate_id="candidate-1",
                feedback_id="feedback-1",
                execution_id="exec-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                source_candidate_id="source-1",
                domain="semantic",
                action=LearningWriteAdaptationAction.ACCEPT,
                reason="bad",
                confidence=0.5,
                authority_granted=True,
            )


if __name__ == "__main__":
    unittest.main()
