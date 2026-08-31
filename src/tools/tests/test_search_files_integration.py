from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.tools.bootstrap import build_tool_stack
from src.tools.handlers.search_files import SearchFilesHandler
from src.tools.models import RiskLevel, ToolRequest


class SearchFilesIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        (self.base_dir / "jarvis.py").write_text(
            "class JARVIS:\n    pass\n", encoding="utf-8"
        )
        (self.base_dir / "notes.txt").write_text(
            "Third-Hand\nSecond-Brain\n", encoding="utf-8"
        )
        self.stack = build_tool_stack([SearchFilesHandler(self.base_dir)])

    def test_registered_search_tool_is_low_risk_and_read_only(self) -> None:
        definition = self.stack.registry.get("search_files").definition()
        self.assertEqual(definition.risk_level, RiskLevel.LOW)
        self.assertFalse(definition.requires_confirmation)
        self.assertTrue(definition.metadata["read_only"])

    def test_search_runs_through_policy_gate(self) -> None:
        result = self.stack.gate.invoke(
            ToolRequest(
                tool_name="search_files",
                arguments={"query": "Third-Hand"},
            )
        )

        self.assertTrue(result.success)
        self.assertEqual(result.content["matches"][0]["path"], "notes.txt")
        self.assertEqual(result.content["matches"][0]["line"], 1)

    def test_search_result_preserves_invocation_id(self) -> None:
        result = self.stack.gate.invoke(
            ToolRequest(
                tool_name="search_files",
                arguments={"query": "JARVIS"},
                invocation_id="search-1",
            )
        )

        self.assertTrue(result.success)
        self.assertEqual(result.invocation_id, "search-1")

    def test_unknown_path_cannot_escape_workspace(self) -> None:
        result = self.stack.gate.invoke(
            ToolRequest(
                tool_name="search_files",
                arguments={"query": "secret", "path": ".."},
            )
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "path_outside_base_dir")


if __name__ == "__main__":
    unittest.main()
