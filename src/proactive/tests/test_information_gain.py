import unittest

from src.proactive.information_gain import (
    InformationGainAssessment,
    InformationGainError,
    InformationGainFactors,
    assess_information_gain,
    rank_information_gain,
)


class InformationGainTests(unittest.TestCase):
    def test_score_is_deterministic(self) -> None:
        factors = InformationGainFactors(0.8, 0.5, 0.9, 1.0)
        first = assess_information_gain("p1", factors)
        second = assess_information_gain("p1", factors)
        self.assertEqual(first, second)
        self.assertAlmostEqual(first.score, 0.36)

    def test_score_is_bounded(self) -> None:
        assessment = assess_information_gain("p1", InformationGainFactors(1, 1, 1, 1))
        self.assertEqual(assessment.score, 1.0)

    def test_factors_reject_out_of_range(self) -> None:
        with self.assertRaises(ValueError):
            InformationGainFactors(1.01, 0.5, 0.5, 0.5)

    def test_assessment_rejects_authority(self) -> None:
        factors = InformationGainFactors(0.5, 0.5, 0.5, 0.5)
        with self.assertRaises(InformationGainError):
            InformationGainAssessment("p1", 0.1, factors, authorization_granted=True)

    def test_context_contains_no_authority(self) -> None:
        assessment = assess_information_gain(
            "p1", InformationGainFactors(0.5, 0.5, 0.5, 0.5)
        )
        context = assessment.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])

    def test_ranking_is_score_descending_then_id(self) -> None:
        factors = InformationGainFactors(1, 1, 1, 1)
        low = assess_information_gain("a", InformationGainFactors(0.5, 1, 1, 1))
        high_b = assess_information_gain("b", factors)
        high_a = assess_information_gain("a-high", factors)
        ranked = rank_information_gain(
            {"a": low, "b": high_b, "a-high": high_a}
        )
        self.assertEqual([item.proposal_id for item in ranked], ["a-high", "b", "a"])

    def test_mapping_identity_is_required(self) -> None:
        assessment = assess_information_gain(
            "p1", InformationGainFactors(0.5, 0.5, 0.5, 0.5)
        )
        with self.assertRaises(ValueError):
            rank_information_gain({"other": assessment})


if __name__ == "__main__":
    unittest.main()
