import unittest

from src.core.capability_selection import (
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
