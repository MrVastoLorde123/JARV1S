import unittest

from src.proactive.value import (
    ProposalValueAssessment,
    ProposalValueFactors,
    ValueAssessmentError,
    assess_proposal_value,
    rank_assessments,
)


class ProposalValueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.factors = ProposalValueFactors(
            importance=0.8,
            urgency=0.6,
            expected_benefit=0.9,
            confidence=0.7,
            effort_cost=0.2,
            risk=0.1,
        )

    def test_score_is_deterministic(self) -> None:
        first = assess_proposal_value("p1", self.factors)
        second = assess_proposal_value("p1", self.factors)
        self.assertEqual(first, second)

    def test_score_is_bounded(self) -> None:
        assessment = assess_proposal_value("p1", self.factors)
        self.assertGreaterEqual(assessment.score, 0.0)
        self.assertLessEqual(assessment.score, 1.0)

    def test_factors_reject_out_of_range_values(self) -> None:
        with self.assertRaises(ValueAssessmentError):
            ProposalValueFactors(
                importance=1.1,
                urgency=0.0,
                expected_benefit=0.0,
                confidence=0.0,
                effort_cost=0.0,
                risk=0.0,
            )

    def test_assessment_rejects_authority(self) -> None:
        with self.assertRaises(ValueAssessmentError):
            ProposalValueAssessment(
                proposal_id="p1",
                score=0.5,
                factors=self.factors,
                authorization_granted=True,
            )

    def test_context_contains_no_authority(self) -> None:
        context = assess_proposal_value("p1", self.factors).to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])

    def test_ranking_is_score_descending_then_id(self) -> None:
        low = assess_proposal_value(
            "b",
            ProposalValueFactors(0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
        )
        high = assess_proposal_value(
            "a",
            ProposalValueFactors(1.0, 1.0, 1.0, 1.0, 0.0, 0.0),
        )
        tied_a = ProposalValueAssessment(
            proposal_id="a2",
            score=0.5,
            factors=self.factors,
        )
        tied_b = ProposalValueAssessment(
            proposal_id="a1",
            score=0.5,
            factors=self.factors,
        )
        ranked = rank_assessments(
            {item.proposal_id: item for item in (low, high, tied_a, tied_b)}
        )
        self.assertEqual([item.proposal_id for item in ranked], ["a", "a1", "a2", "b"])

    def test_mapping_identity_is_required(self) -> None:
        assessment = assess_proposal_value("p1", self.factors)
        with self.assertRaises(ValueAssessmentError):
            rank_assessments({"different": assessment})


if __name__ == "__main__":
    unittest.main()
