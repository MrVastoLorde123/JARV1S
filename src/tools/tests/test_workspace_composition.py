from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.tools.bootstrap import build_workspace_tool_stack
from src.tools.confirmation import AutoApproveConfirmationProvider, AutoDenyConfirmationProvider
from src.tools.models import ToolRequest


class WorkspaceCompositionTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        (self.base_dir / "project").mkdir()
        (self.base_dir / "project" / "config.txt").write_text(
            "environment=dev\nneedle=true\n",
            encoding="utf-8",
        )
        self.stack = build_workspace_tool_stack(
            self.base_dir,
            confirmation_provider=AutoApproveConfirmationProvider(),
        )

    def test_discover_inspect_search_modify(self) -> None:
        """Exercise the workspace as one coherent capability surface."""
        discovered = self.stack.gate.invoke(
            ToolRequest(tool_name="list_directory", arguments={"path": "project"})
        )
        self.assertTrue(discovered.success)
        self.assertIn(
            "project/config.txt",
            [entry["path"] for entry in discovered.content["entries"]],
        )

        inspected = self.stack.gate.invoke(
            ToolRequest(tool_name="read_file", arguments={"path": "project/config.txt"})
        )
        self.assertTrue(inspected.success)
        self.assertIn("environment=dev", inspected.content["content"])

        searched = self.stack.gate.invoke(
            ToolRequest(
                tool_name="search_files",
                arguments={"path": "project", "query": "needle=true"},
            )
        )
        self.assertTrue(searched.success)
        self.assertEqual(searched.content["matches"][0]["path"], "project/config.txt")

        modified = self.stack.gate.invoke(
            ToolRequest(
                tool_name="write_file",
                arguments={
                    "path": "project/config.txt",
                    "content": "environment=prod\nneedle=true\n",
                    "overwrite": True,
                },
            )
        )
        self.assertTrue(modified.success)

        verified = self.stack.gate.invoke(
            ToolRequest(tool_name="read_file", arguments={"path": "project/config.txt"})
        )
        self.assertTrue(verified.success)
        self.assertIn("environment=prod", verified.content["content"])
        self.assertNotIn("environment=dev", verified.content["content"])

    def test_modify_step_is_still_confirmation_gated(self) -> None:
        denying_stack = build_workspace_tool_stack(
            self.base_dir,
            confirmation_provider=AutoDenyConfirmationProvider(),
        )

        result = denying_stack.gate.invoke(
            ToolRequest(
                tool_name="write_file",
                arguments={
                    "path": "project/config.txt",
                    "content": "environment=prod\nneedle=true\n",
                    "overwrite": True,
                },
            )
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "confirmation_denied")
        self.assertIn(
            "environment=dev",
            (self.base_dir / "project" / "config.txt").read_text(encoding="utf-8"),
        )

    def test_capability_results_remain_tool_specific(self) -> None:
        listed = self.stack.gate.invoke(ToolRequest(tool_name="list_directory"))
        searched = self.stack.gate.invoke(
            ToolRequest(tool_name="search_files", arguments={"query": "needle"})
        )

        self.assertEqual(
            set(listed.content),
            {"path", "recursive", "entries", "truncated", "errors"},
        )
        self.assertEqual(
            set(searched.content),
            {
                "query",
                "path",
                "recursive",
                "case_sensitive",
                "matches",
                "truncated",
                "files_scanned",
                "files_skipped",
            },
        )


if __name__ == "__main__":
    unittest.main()
