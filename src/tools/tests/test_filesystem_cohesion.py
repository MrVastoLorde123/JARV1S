from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.tools.bootstrap import build_tool_stack
from src.tools.confirmation import AutoApproveConfirmationProvider
from src.tools.handlers.list_directory import ListDirectoryHandler
from src.tools.handlers.read_file import ReadFileHandler
from src.tools.handlers.search_files import SearchFilesHandler
from src.tools.handlers.write_file import WriteFileHandler
from src.tools.models import ToolRequest


class FilesystemCapabilityCohesionTests(unittest.TestCase):
    """Guard the shared behavioral contract of the four workspace tools.

    These tests intentionally verify only behavior that should be common
    across capabilities. Capability-specific errors remain distinct where
    the operation semantics differ.

    The stack uses an approving confirmation provider because these tests
    are validating filesystem behavior, not the policy boundary itself.
    Write-tool confirmation behavior is covered by the dedicated
    write-file integration tests.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        (self.base_dir / "notes.txt").write_text("needle\n", encoding="utf-8")
        (self.base_dir / "nested").mkdir()
        (self.base_dir / "nested" / "code.py").write_text(
            "needle\n", encoding="utf-8"
        )

        self.handlers = {
            "read_file": ReadFileHandler(self.base_dir),
            "search_files": SearchFilesHandler(self.base_dir),
            "list_directory": ListDirectoryHandler(self.base_dir),
            "write_file": WriteFileHandler(self.base_dir),
        }
        self.stack = build_tool_stack(
            self.handlers.values(),
            confirmation_provider=AutoApproveConfirmationProvider(),
        )

    def request(self, tool_name: str, **arguments: object) -> ToolRequest:
        return ToolRequest(
            tool_name=tool_name,
            arguments=arguments,
            invocation_id=f"cohesion-{tool_name}",
        )

    def test_all_filesystem_tools_share_the_same_workspace_boundary(self) -> None:
        absolute = str(self.base_dir / "escape.txt")
        for tool_name, arguments in [
            ("read_file", {"path": absolute}),
            ("search_files", {"query": "secret", "path": absolute}),
            ("list_directory", {"path": absolute}),
            ("write_file", {"path": absolute, "content": "blocked"}),
        ]:
            with self.subTest(tool_name=tool_name):
                result = self.stack.gate.invoke(self.request(tool_name, **arguments))
                self.assertFalse(result.success)
                self.assertEqual(result.error.code, "path_outside_base_dir")
                self.assertEqual(result.invocation_id, f"cohesion-{tool_name}")

    def test_all_filesystem_tools_reject_parent_traversal(self) -> None:
        for tool_name, arguments in [
            ("read_file", {"path": "../escape.txt"}),
            ("search_files", {"query": "secret", "path": "../"}),
            ("list_directory", {"path": "../"}),
            ("write_file", {"path": "../escape.txt", "content": "blocked"}),
        ]:
            with self.subTest(tool_name=tool_name):
                result = self.stack.gate.invoke(self.request(tool_name, **arguments))
                self.assertFalse(result.success)
                self.assertEqual(result.error.code, "path_outside_base_dir")

    def test_all_filesystem_tools_report_empty_path_as_invalid_argument(self) -> None:
        for tool_name, arguments in [
            ("read_file", {"path": "   "}),
            ("search_files", {"query": "needle", "path": "   "}),
            ("list_directory", {"path": "   "}),
            ("write_file", {"path": "   ", "content": "blocked"}),
        ]:
            with self.subTest(tool_name=tool_name):
                result = self.stack.gate.invoke(self.request(tool_name, **arguments))
                self.assertFalse(result.success)
                self.assertEqual(result.error.code, "invalid_argument")

    def test_capability_specific_not_found_errors_remain_meaningful(self) -> None:
        cases = [
            (
                "read_file",
                {"path": "missing.txt"},
                "file_not_found",
            ),
            (
                "search_files",
                {"query": "needle", "path": "missing"},
                "path_not_found",
            ),
            (
                "list_directory",
                {"path": "missing"},
                "directory_not_found",
            ),
        ]

        for tool_name, arguments, expected_code in cases:
            with self.subTest(tool_name=tool_name):
                result = self.stack.gate.invoke(self.request(tool_name, **arguments))
                self.assertFalse(result.success)
                self.assertEqual(result.error.code, expected_code)

    def test_shared_read_tools_are_low_risk_and_read_only(self) -> None:
        for tool_name in ("read_file", "search_files", "list_directory"):
            with self.subTest(tool_name=tool_name):
                definition = self.stack.registry.get(tool_name).definition()
                self.assertEqual(definition.risk_level.value, "low")
                self.assertFalse(definition.requires_confirmation)
                self.assertTrue(definition.metadata["read_only"])

    def test_write_tool_is_the_only_filesystem_tool_requiring_confirmation(self) -> None:
        definition = self.stack.registry.get("write_file").definition()
        self.assertEqual(definition.risk_level.value, "high")
        self.assertTrue(definition.requires_confirmation)
        self.assertFalse(definition.metadata["read_only"])

    def test_list_then_search_then_read_then_write_compose_through_one_stack(self) -> None:
        listing = self.stack.gate.invoke(
            self.request("list_directory", recursive=True)
        )
        self.assertTrue(listing.success)
        discovered = [
            entry["path"]
            for entry in listing.content["entries"]
            if entry["type"] == "file"
        ]
        self.assertEqual(discovered, ["nested/code.py", "notes.txt"])

        search = self.stack.gate.invoke(
            self.request("search_files", query="needle", path=".")
        )
        self.assertTrue(search.success)
        self.assertEqual(
            [(m["path"], m["line"]) for m in search.content["matches"]],
            [("nested/code.py", 1), ("notes.txt", 1)],
        )

        read = self.stack.gate.invoke(
            self.request("read_file", path=search.content["matches"][0]["path"])
        )
        self.assertTrue(read.success)
        self.assertEqual(read.content["content"], "needle\n")

        write = self.stack.gate.invoke(
            self.request("write_file", path="result.txt", content="done")
        )
        self.assertTrue(write.success)
        self.assertEqual(write.content["path"], "result.txt")
        self.assertEqual(
            (self.base_dir / "result.txt").read_text(encoding="utf-8"),
            "done",
        )


if __name__ == "__main__":
    unittest.main()
