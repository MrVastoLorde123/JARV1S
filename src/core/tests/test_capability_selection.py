import math
import unittest

from src.core.capability_selection import (
    CapabilityCandidate,
    CapabilitySelection,
    CapabilitySelector,
    DeterministicCapabilitySelector,
)
from src.tools.models import RiskLevel, ToolDefinition


class CapabilitySelectionTests(unittest.TestCase):
    def setUp(self):
        self.capabilities = (
            ToolDefinition(
                name="read_file",
                description="Read the contents of a file in the workspace.",
                version="1.0.0",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                risk_level=RiskLevel.LOW,
            ),
            ToolDefinition(
                name="list_directory",
                description="List files and directories in the workspace.",
                version="1.0.0",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                risk_level=RiskLevel.LOW,
            ),
            ToolDefinition(
                name="write_file",
                description="Write or modify a file in the workspace.",
                version="1.0.0",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                risk_level=RiskLevel.HIGH,
                requires_confirmation=True,
            ),
        )
        self.selector = DeterministicCapabilitySelector()

    def test_selector_implements_contract(self):
        self.assertIsInstance(self.selector, CapabilitySelector)

    def test_best_match_is_ranked_first(self):
        result = self.selector.select("read a file", self.capabilities)

        self.assertIsInstance(result, CapabilitySelection)
        self.assertIsNotNone(result.best)
        self.assertEqual("read_file", result.best.capability.name)

    def test_name_matches_have_more_weight_than_description_matches(self):
        result = self.selector.select("write file", self.capabilities)

        self.assertEqual("write_file", result.best.capability.name)

    def test_results_are_deterministic(self):
        first = self.selector.select("workspace file", self.capabilities)
        second = self.selector.select("workspace file", self.capabilities)

        self.assertEqual(first, second)

    def test_unmatched_query_returns_no_candidates(self):
        result = self.selector.select("send an email", self.capabilities)

        self.assertEqual((), result.candidates)
        self.assertIsNone(result.best)

    def test_generic_stopwords_do_not_create_false_capability_match(self):
        capabilities = (
            ToolDefinition(
                name="report_status",
                description="Report the current runtime status.",
                version="1.0.0",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                risk_level=RiskLevel.LOW,
            ),
        )

        result = self.selector.select(
            "Deploy the production database.",
            capabilities,
        )

        self.assertEqual((), result.candidates)
        self.assertIsNone(result.best)

    def test_empty_query_is_rejected(self):
        with self.assertRaises(ValueError):
            self.selector.select(" ", self.capabilities)

    def test_non_string_query_is_rejected(self):
        with self.assertRaises(TypeError):
            self.selector.select(None, self.capabilities)

    def test_invalid_capability_entries_are_rejected(self):
        with self.assertRaises(TypeError):
            self.selector.select("read file", (object(),))

    def test_selection_does_not_modify_capabilities(self):
        before = self.capabilities
        self.selector.select("read file", self.capabilities)
        self.assertEqual(before, self.capabilities)

    def test_candidate_requires_tool_definition(self):
        with self.assertRaises(TypeError):
            CapabilityCandidate(capability=object(), score=1, reason="match")  # type: ignore[arg-type]

    def test_candidate_requires_finite_non_negative_score(self):
        with self.assertRaises(ValueError):
            CapabilityCandidate(self.capabilities[0], math.inf, "match")
        with self.assertRaises(ValueError):
            CapabilityCandidate(self.capabilities[0], -0.1, "match")

    def test_candidate_rejects_empty_reason(self):
        with self.assertRaises(ValueError):
            CapabilityCandidate(self.capabilities[0], 1.0, " ")

    def test_selection_rejects_invalid_candidate_entries(self):
        with self.assertRaises(TypeError):
            CapabilitySelection("read file", (object(),))  # type: ignore[arg-type]

    def test_selection_requires_non_empty_query(self):
        with self.assertRaises(ValueError):
            CapabilitySelection(" ", ())

    def test_candidate_score_normalizes_to_float(self):
        candidate = CapabilityCandidate(self.capabilities[0], 2, "  matched  ")

        self.assertEqual(2.0, candidate.score)
        self.assertEqual("matched", candidate.reason)


if __name__ == "__main__":
    unittest.main(verbosity=2)
