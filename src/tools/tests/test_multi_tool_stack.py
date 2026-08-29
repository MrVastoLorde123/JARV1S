"""Proves the read_file pattern generalizes to a second tool.

This is the actual point of milestone 4: register two independently-
written LOW-risk handlers into one registry and confirm ``PolicyGate``
routes to the right one, they don't interfere with each other, and
nothing tool-specific had to be added anywhere outside the handler
itself (registry, service, policy, gate all stayed untouched).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.tools.bootstrap import build_tool_stack
from src.tools.handlers.list_directory import ListDirectoryHandler
from src.tools.handlers.read_file import ReadFileHandler
from src.tools.models import ToolRequest


class TwoToolStackTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        (self.base_dir / "notes.txt").write_text("hello workspace")
        (self.base_dir / "subdir").mkdir()
        (self.base_dir / "subdir" / "nested.txt").write_text("nested")

        self.stack = build_tool_stack(
            [ReadFileHandler(self.base_dir), ListDirectoryHandler(self.base_dir)]
        )

    def test_both_tools_are_registered_and_enumerable(self) -> None:
        names = sorted(d.name for d in self.stack.registry.list_definitions())
        self.assertEqual(names, ["list_directory", "read_file"])

    def test_gate_routes_to_the_correct_handler_by_name(self) -> None:
        read_result = self.stack.gate.invoke(
            ToolRequest(tool_name="read_file", arguments={"path": "notes.txt"})
        )
        list_result = self.stack.gate.invoke(ToolRequest(tool_name="list_directory"))

        self.assertTrue(read_result.success)
        self.assertEqual(read_result.content["content"], "hello workspace")

        self.assertTrue(list_result.success)
        names = [e["name"] for e in list_result.content["entries"]]
        self.assertEqual(sorted(names), ["notes.txt", "subdir"])

    def test_a_workflow_lists_then_reads(self) -> None:
        # Simulates the shape of a real usage: enumerate a directory,
        # then read one of the files it reported.
        listing = self.stack.gate.invoke(ToolRequest(tool_name="list_directory"))
        self.assertTrue(listing.success)

        file_entries = [e for e in listing.content["entries"] if e["type"] == "file"]
        self.assertEqual(len(file_entries), 1)
        discovered_path = file_entries[0]["path"]

        read = self.stack.gate.invoke(
            ToolRequest(tool_name="read_file", arguments={"path": discovered_path})
        )
        self.assertTrue(read.success)
        self.assertEqual(read.content["content"], "hello workspace")

    def test_both_tools_share_the_low_risk_allow_path_without_confirmation(self) -> None:
        # Neither tool needed a confirmation provider configured at
        # all -- both are LOW risk under DefaultPolicy, same as
        # read_file alone in milestone 3. This is the "generalizes"
        # claim, made concrete.
        for request in [
            ToolRequest(tool_name="read_file", arguments={"path": "notes.txt"}),
            ToolRequest(tool_name="list_directory"),
        ]:
            with self.subTest(tool_name=request.tool_name):
                result = self.stack.gate.invoke(request)
                self.assertTrue(result.success)

    def test_one_tool_failing_does_not_affect_the_other(self) -> None:
        missing = self.stack.gate.invoke(
            ToolRequest(tool_name="read_file", arguments={"path": "missing.txt"})
        )
        self.assertFalse(missing.success)

        listing = self.stack.gate.invoke(ToolRequest(tool_name="list_directory"))
        self.assertTrue(listing.success)

    def test_recursive_listing_and_read_across_nested_directory(self) -> None:
        listing = self.stack.gate.invoke(
            ToolRequest(tool_name="list_directory", arguments={"recursive": True})
        )
        self.assertTrue(listing.success)
        nested_path = next(
            e["path"] for e in listing.content["entries"] if e["name"] == "nested.txt"
        )

        read = self.stack.gate.invoke(
            ToolRequest(tool_name="read_file", arguments={"path": nested_path})
        )
        self.assertTrue(read.success)
        self.assertEqual(read.content["content"], "nested")


if __name__ == "__main__":
    unittest.main()
