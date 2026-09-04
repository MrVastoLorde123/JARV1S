import unittest

from src.context.cross_domain import DomainReference
from src.context.relevance import (
    ContextRelevance,
    ContextRelevanceRanking,
    ContextRelevanceValidationError,
    rank_relevance,
)


class TestContextRelevance(unittest.TestCase):
    def setUp(self):
        self.a = DomainReference("project", "p-1", "JARVIS")
        self.b = DomainReference("person", "person-1", "User")
        self.c = DomainReference("system", "sys-1", "Runtime")

    def test_valid_relevance(self):
        item = ContextRelevance(self.a, 0.8, ("active project",))
        self.assertEqual(item.score, 0.8)
        self.assertEqual(item.reference_key, ("project", "p-1"))

    def test_score_bounds(self):
        for score in (-0.1, 1.1):
            with self.assertRaises(ContextRelevanceValidationError):
                ContextRelevance(self.a, score)

    def test_score_finite(self):
        for score in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ContextRelevanceValidationError):
                ContextRelevance(self.a, score)

    def test_score_rejects_bool(self):
        with self.assertRaises(ContextRelevanceValidationError):
            ContextRelevance(self.a, True)

    def test_reference_required(self):
        with self.assertRaises(ContextRelevanceValidationError):
            ContextRelevance("p-1", 0.5)

    def test_reasons_must_be_tuple(self):
        with self.assertRaises(ContextRelevanceValidationError):
            ContextRelevance(self.a, 0.5, ["reason"])

    def test_duplicate_reasons_rejected(self):
        with self.assertRaises(ContextRelevanceValidationError):
            ContextRelevance(self.a, 0.5, ("same", "same"))

    def test_ranking_is_deterministic(self):
        ranking = rank_relevance(
            [ContextRelevance(self.c, 0.4), ContextRelevance(self.a, 0.9), ContextRelevance(self.b, 0.7)]
        )
        self.assertEqual([item.reference.reference_id for item in ranking.items], ["p-1", "person-1", "sys-1"])

    def test_ties_use_domain_then_id(self):
        ranking = rank_relevance([ContextRelevance(self.b, 0.5), ContextRelevance(self.a, 0.5)])
        self.assertEqual([item.reference.domain for item in ranking.items], ["person", "project"])

    def test_duplicate_references_rejected(self):
        item = ContextRelevance(self.a, 0.5)
        with self.assertRaises(ContextRelevanceValidationError):
            ContextRelevanceRanking((item, item))

    def test_unsorted_ranking_rejected(self):
        high = ContextRelevance(self.a, 0.9)
        low = ContextRelevance(self.b, 0.1)
        with self.assertRaises(ContextRelevanceValidationError):
            ContextRelevanceRanking((low, high))

    def test_top(self):
        ranking = rank_relevance([ContextRelevance(self.a, 0.9), ContextRelevance(self.b, 0.2)])
        self.assertEqual(ranking.top.reference.reference_id, "p-1")

    def test_empty_top(self):
        self.assertIsNone(ContextRelevanceRanking().top)

    def test_for_domain(self):
        ranking = rank_relevance([ContextRelevance(self.a, 0.8), ContextRelevance(self.b, 0.7)])
        self.assertEqual(len(ranking.for_domain("PROJECT")), 1)

    def test_above_threshold(self):
        ranking = rank_relevance([ContextRelevance(self.a, 0.8), ContextRelevance(self.b, 0.2)])
        self.assertEqual(len(ranking.above(0.5)), 1)

    def test_threshold_bounds(self):
        ranking = ContextRelevanceRanking()
        for threshold in (-0.1, 1.1):
            with self.assertRaises(ContextRelevanceValidationError):
                ranking.above(threshold)

    def test_serialization_preserves_boundary_flags(self):
        payload = ContextRelevance(self.a, 0.75, ("current",)).to_dict()
        self.assertEqual(payload["score"], 0.75)
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["importance_guaranteed"])
        self.assertFalse(payload["authorization_granted"])

    def test_json_is_serializable(self):
        ranking = rank_relevance([ContextRelevance(self.a, 0.5)])
        self.assertIn("\"items\"", ranking.to_json())


if __name__ == "__main__":
    unittest.main()
