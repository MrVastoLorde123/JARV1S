from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.tools.bootstrap import build_workspace_tool_stack
from src.tools.confirmation import AutoApproveConfirmationProvider
from src.tools.models import ToolRequest


class WorkspacePathReportingTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        (self.base_dir / "nested").mkdir()
        (self.base_dir / "nested" / "file.txt").write_text("hello", encoding="utf-8")
        self.stack = build_workspace_tool_stack(
            self.base_dir,
            confirmation_provider=AutoApproveConfirmationProvider(),
        )

    def test_all_workspace_success_paths_use_posix_relative_paths(self) -> None:
        cases = (
            ("read_file", {"path": "nested\\file.txt"}),
            ("list_directory", {"path": "nested"}),
            ("search_files", {"path": "nested", "query": "hello"}),
            ("write_file", {"path": "nested\\created.txt", "content": "hello"}),
        )

        for tool_name, arguments in cases:
            with self.subTest(tool_name=tool_name):
                result = self.stack.gate.invoke(
                    ToolRequest(tool_name=tool_name, arguments=arguments)
                )
                self.assertTrue(result.success)
                if tool_name == "read_file":
                    self.assertEqual(result.content["path"], "nested/file.txt")
                elif tool_name == "list_directory":
                    self.assertEqual(result.content["path"], "nested")
                elif tool_name == "search_files":
                    self.assertEqual(result.content["path"], "nested")
                    self.assertEqual(result.content["matches"][0]["path"], "nested/file.txt")
                else:
                    self.assertEqual(result.content["path"], "nested/created.txt")


if __name__ == "__main__":
    unittest.main()
