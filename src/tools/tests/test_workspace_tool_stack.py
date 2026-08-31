"""Cohesion tests for the standard workspace capability set."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.tools.bootstrap import build_workspace_tool_stack
from src.tools.confirmation import AutoApproveConfirmationProvider
from src.tools.models import RiskLevel, ToolRequest


class WorkspaceToolStackTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        (self.base_dir / "notes.txt").write_text("needle\nhello\n", encoding="utf-8")
        (self.base_dir / "nested").mkdir()
        (self.base_dir / "nested" / "code.py").write_text("needle = True\n", encoding="utf-8")

        self.stack = build_workspace_tool_stack(
            self.base_dir,
            confirmation_provider=AutoApproveConfirmationProvider(),
        )

    def test_standard_workspace_stack_registers_all_four_capabilities(self) -> None:
        self.assertEqual(
            [definition.name for definition in self.stack.registry.list_definitions()],
            ["list_directory", "read_file", "search_files", "write_file"],
        )

    def test_all_workspace_tools_share_filesystem_category(self) -> None:
        definitions = {
            definition.name: definition
            for definition in self.stack.registry.list_definitions()
        }
        for name in ("list_directory", "read_file", "search_files", "write_file"):
            self.assertEqual(definitions[name].metadata["category"], "filesystem")

    def test_read_list_and_search_observe_the_same_workspace(self) -> None:
        listed = self.stack.gate.invoke(
            ToolRequest(tool_name="list_directory", arguments={"recursive": True})
        )
        searched = self.stack.gate.invoke(
            ToolRequest(tool_name="search_files", arguments={"query": "needle"})
        )
        read = self.stack.gate.invoke(
            ToolRequest(tool_name="read_file", arguments={"path": "nested/code.py"})
        )

        self.assertTrue(listed.success)
        self.assertTrue(searched.success)
        self.assertTrue(read.success)
        self.assertIn("nested/code.py", [entry["path"] for entry in listed.content["entries"]])
        self.assertIn("nested/code.py", [match["path"] for match in searched.content["matches"]])
        self.assertEqual(read.content["content"], "needle = True\n")

    def test_write_requires_confirmation_but_joins_the_same_workspace_capability_set(self) -> None:
        definition = self.stack.registry.get("write_file").definition()
        self.assertEqual(definition.risk_level, RiskLevel.HIGH)
        self.assertTrue(definition.requires_confirmation)

        result = self.stack.gate.invoke(
            ToolRequest(
                tool_name="write_file",
                arguments={"path": "created.txt", "content": "created"},
            )
        )

        self.assertTrue(result.success)
        self.assertEqual(
            (self.base_dir / "created.txt").read_text(encoding="utf-8"),
            "created",
        )

    def test_workspace_boundary_is_consistent_across_capabilities(self) -> None:
        for tool_name, arguments in (
            ("read_file", {"path": "../outside.txt"}),
            ("list_directory", {"path": "../outside"}),
            ("search_files", {"query": "needle", "path": "../outside"}),
            ("write_file", {"path": "../outside.txt", "content": "blocked"}),
        ):
            result = self.stack.gate.invoke(
                ToolRequest(tool_name=tool_name, arguments=arguments)
            )
            self.assertFalse(result.success, tool_name)
            self.assertEqual(result.error.code, "path_outside_base_dir", tool_name)


if __name__ == "__main__":
    unittest.main()
