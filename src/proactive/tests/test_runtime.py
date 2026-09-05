from datetime import datetime, timedelta, timezone
import unittest

from src.proactive import (
    InitiativeCandidate,
    InitiativeDisposition,
    InitiativeEvaluation,
    InformationGainFactors,
    ProposalValueFactors,
    ProactiveTrigger,
    ProactiveTriggerSource,
    assess_information_gain,
    assess_proposal_value,
    evaluate_initiative,
)
from src.proactive.proposal import build_proposal
from src.proactive.runtime import (
    FeedbackOutcome,
    ProactiveFeedback,
    ProactiveRuntimeResult,
    RuntimeStatus,
    compose_proactive_runtime,
    rank_runtime_results,
)
from src.proactive.scheduling import propose_schedule


class RuntimeBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc)
        self.trigger = ProactiveTrigger(
            trigger_id="trigger-1",
            source=ProactiveTriggerSource.OBSERVATION,
            reference_id="obs-1",
            signal="task may need attention",
            observed_at=self.now,
            evidence_ids=("e1",),
        )
        self.candidate = InitiativeCandidate(
            candidate_id="candidate-1",
            trigger_id="trigger-1",
            title="Review stalled task",
            rationale="Current evidence suggests attention may be useful.",
            evidence_ids=("e1",),
            expires_at=self.now + timedelta(days=1),
        )
        self.initiative = evaluate_initiative(self.trigger, self.candidate, now=self.now)
        self.proposal = build_proposal(
            self.candidate,
            self.initiative,
            proposal_id="proposal-1",
            recommendation="Review the stalled task.",
            created_at=self.now,
            confidence=0.8,
        )
        self.value = assess_proposal_value(
            "proposal-1",
            ProposalValueFactors(
                importance=0.8,
                urgency=0.6,
                expected_benefit=0.9,
                confidence=0.8,
                effort_cost=0.2,
                risk=0.1,
            ),
        )
        self.information_gain = assess_information_gain(
            "proposal-1",
            InformationGainFactors(
                current_uncertainty=0.9,
                expected_reduction=0.7,
                evidence_quality=0.8,
                relevance=0.9,
            ),
        )
        self.scheduling = propose_schedule(
            "proposal-1",
            scheduled_for=self.now + timedelta(hours=2),
            reason="Review during the next work window.",
        )

    def test_runtime_composes_all_bounded_stages(self) -> None:
        result = compose_proactive_runtime(
            proposal_id="proposal-1",
            initiative=self.candidate,
            initiative_evaluation=self.initiative,
            proposal_evaluation=self.proposal,
            value_assessment=self.value,
            information_gain=self.information_gain,
            scheduling=self.scheduling,
        )
        self.assertIsInstance(result, ProactiveRuntimeResult)
        self.assertEqual(result.status, RuntimeStatus.READY)
        self.assertEqual(result.feedback.outcome, FeedbackOutcome.NOT_OBSERVED)
        context = result.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["executed"])

    def test_runtime_preserves_feedback(self) -> None:
        feedback = ProactiveFeedback(
            proposal_id="proposal-1",
            outcome=FeedbackOutcome.DECLINED,
            notes="Operator intentionally skipped the recommendation.",
        )
        result = compose_proactive_runtime(
            proposal_id="proposal-1",
            initiative=self.candidate,
            initiative_evaluation=self.initiative,
            proposal_evaluation=self.proposal,
            value_assessment=self.value,
            information_gain=self.information_gain,
            scheduling=self.scheduling,
            feedback=feedback,
        )
        self.assertEqual(result.feedback, feedback)

    def test_non_proposed_source_requires_review(self) -> None:
        not_eligible = InitiativeEvaluation(
            candidate_id="candidate-1",
            trigger_id="trigger-1",
            disposition=InitiativeDisposition.SUPPRESSED,
            reason="suppressed",
        )
        review_proposal = build_proposal(
            self.candidate,
            not_eligible,
            proposal_id="proposal-1",
            recommendation="Review the task.",
            created_at=self.now,
        )
        result = compose_proactive_runtime(
            proposal_id="proposal-1",
            initiative=self.candidate,
            initiative_evaluation=not_eligible,
            proposal_evaluation=review_proposal,
            value_assessment=self.value,
            information_gain=self.information_gain,
            scheduling=self.scheduling,
        )
        self.assertEqual(result.status, RuntimeStatus.NEEDS_REVIEW)

    def test_identity_mismatch_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            compose_proactive_runtime(
                proposal_id="other-proposal",
                initiative=self.candidate,
                initiative_evaluation=self.initiative,
                proposal_evaluation=self.proposal,
                value_assessment=self.value,
                information_gain=self.information_gain,
                scheduling=self.scheduling,
            )

    def test_feedback_identity_mismatch_is_rejected(self) -> None:
        feedback = ProactiveFeedback(
            proposal_id="other-proposal",
            outcome=FeedbackOutcome.ACCEPTED,
        )
        with self.assertRaises(ValueError):
            compose_proactive_runtime(
                proposal_id="proposal-1",
                initiative=self.candidate,
                initiative_evaluation=self.initiative,
                proposal_evaluation=self.proposal,
                value_assessment=self.value,
                information_gain=self.information_gain,
                scheduling=self.scheduling,
                feedback=feedback,
            )

    def test_feedback_cannot_grant_authority(self) -> None:
        with self.assertRaises(ValueError):
            ProactiveFeedback(
                proposal_id="proposal-1",
                outcome=FeedbackOutcome.ACCEPTED,
                authority_granted=True,
            )

    def test_feedback_cannot_change_policy(self) -> None:
        with self.assertRaises(ValueError):
            ProactiveFeedback(
                proposal_id="proposal-1",
                outcome=FeedbackOutcome.ACCEPTED,
                policy_changed=True,
            )

    def test_not_observed_feedback_is_consistent(self) -> None:
        feedback = ProactiveFeedback(
            proposal_id="proposal-1",
            outcome=FeedbackOutcome.NOT_OBSERVED,
            observed=False,
        )
        self.assertFalse(feedback.observed)
        with self.assertRaises(ValueError):
            ProactiveFeedback(
                proposal_id="proposal-1",
                outcome=FeedbackOutcome.NOT_OBSERVED,
                observed=True,
            )

    def test_runtime_identity_is_immutable_and_consistent(self) -> None:
        result = compose_proactive_runtime(
            proposal_id="proposal-1",
            initiative=self.candidate,
            initiative_evaluation=self.initiative,
            proposal_evaluation=self.proposal,
            value_assessment=self.value,
            information_gain=self.information_gain,
            scheduling=self.scheduling,
        )
        with self.assertRaises(Exception):
            result.proposal_id = "other"

    def test_ranking_is_deterministic(self) -> None:
        second_value = assess_proposal_value(
            "proposal-2",
            ProposalValueFactors(
                importance=0.7,
                urgency=0.7,
                expected_benefit=0.8,
                confidence=0.8,
                effort_cost=0.2,
                risk=0.1,
            ),
        )
        second_info = assess_information_gain(
            "proposal-2",
            InformationGainFactors(
                current_uncertainty=0.8,
                expected_reduction=0.7,
                evidence_quality=0.8,
                relevance=0.9,
            ),
        )
        second_schedule = propose_schedule(
            "proposal-2",
            scheduled_for=self.now + timedelta(hours=1),
            reason="Review earlier.",
        )
        second_proposal = build_proposal(
            self.candidate,
            self.initiative,
            proposal_id="proposal-2",
            recommendation="Review the task earlier.",
            created_at=self.now,
            confidence=0.8,
        )
        second = compose_proactive_runtime(
            proposal_id="proposal-2",
            initiative=self.candidate,
            initiative_evaluation=self.initiative,
            proposal_evaluation=second_proposal,
            value_assessment=second_value,
            information_gain=second_info,
            scheduling=second_schedule,
        )
        first = compose_proactive_runtime(
            proposal_id="proposal-1",
            initiative=self.candidate,
            initiative_evaluation=self.initiative,
            proposal_evaluation=self.proposal,
            value_assessment=self.value,
            information_gain=self.information_gain,
            scheduling=self.scheduling,
        )
        ranked = rank_runtime_results({"proposal-2": second, "proposal-1": first})
        self.assertEqual(tuple(item.proposal_id for item in ranked), ("proposal-1", "proposal-2"))


if __name__ == "__main__":
    unittest.main()
