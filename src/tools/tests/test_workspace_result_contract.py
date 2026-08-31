from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.tools.bootstrap import build_workspace_tool_stack
from src.tools.confirmation import AutoApproveConfirmationProvider
from src.tools.models import ToolRequest


class WorkspaceResultContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        (self.base_dir / "notes.txt").write_text("needle\n", encoding="utf-8")
        self.stack = build_workspace_tool_stack(
            self.base_dir,
            confirmation_provider=AutoApproveConfirmationProvider(),
        )

    def test_runtime_failures_are_tool_results(self) -> None:
        requests = [
            ToolRequest(tool_name="read_file", arguments={"path": "missing.txt"}),
            ToolRequest(tool_name="list_directory", arguments={"path": "missing"}),
            ToolRequest(tool_name="search_files", arguments={"query": "needle", "path": "missing"}),
            ToolRequest(tool_name="write_file", arguments={"path": "notes.txt", "content": "blocked"}),
        ]

        expected_codes = {
            "read_file": "file_not_found",
            "list_directory": "directory_not_found",
            "search_files": "path_not_found",
            "write_file": "file_exists",
        }

        for request in requests:
            with self.subTest(tool_name=request.tool_name):
                result = self.stack.gate.invoke(request)
                self.assertFalse(result.success)
                self.assertEqual(result.tool_name, request.tool_name)
                self.assertEqual(result.error.code, expected_codes[request.tool_name])
                self.assertIsInstance(result.error.message, str)
                self.assertEqual(result.invocation_id, request.invocation_id)

    def test_workspace_boundary_is_the_only_shared_failure_code(self) -> None:
        for request in (
            ToolRequest(tool_name="read_file", arguments={"path": "../outside.txt"}),
            ToolRequest(tool_name="list_directory", arguments={"path": "../outside"}),
            ToolRequest(tool_name="search_files", arguments={"query": "needle", "path": "../outside"}),
            ToolRequest(tool_name="write_file", arguments={"path": "../outside.txt", "content": "blocked"}),
        ):
            with self.subTest(tool_name=request.tool_name):
                result = self.stack.gate.invoke(request)
                self.assertFalse(result.success)
                self.assertEqual(result.error.code, "path_outside_base_dir")
