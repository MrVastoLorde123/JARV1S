from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from src.tools.handlers.list_directory import DEFAULT_MAX_ENTRIES, ListDirectoryHandler
from src.tools.models import RiskLevel, ToolRequest


class ListDirectoryHandlerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        self.handler = ListDirectoryHandler(self.base_dir)

    def make_file(self, relative_path: str, content: str = "x") -> Path:
        path = self.base_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def make_dir(self, relative_path: str) -> Path:
        path = self.base_dir / relative_path
        path.mkdir(parents=True, exist_ok=True)
        return path

    def entry_names(self, result) -> list:
        return [e["name"] for e in result.content["entries"]]


class TestDefinition(ListDirectoryHandlerTestCase):
    def test_definition_is_low_risk_and_read_only(self) -> None:
        definition = self.handler.definition()
        self.assertEqual(definition.name, "list_directory")
        self.assertEqual(definition.risk_level, RiskLevel.LOW)
        self.assertFalse(definition.requires_confirmation)
        self.assertTrue(definition.metadata.get("read_only"))

    def test_constructor_rejects_missing_base_dir(self) -> None:
        with self.assertRaises(ValueError):
            ListDirectoryHandler(self.base_dir / "does-not-exist")

    def test_constructor_rejects_invalid_max_entries(self) -> None:
        with self.assertRaises(ValueError):
            ListDirectoryHandler(self.base_dir, max_entries=0)


class TestNonRecursiveListing(ListDirectoryHandlerTestCase):
    def test_lists_default_path_as_workspace_root(self) -> None:
        self.make_file("a.txt")
        self.make_dir("subdir")

        result = self.handler.execute(ToolRequest(tool_name="list_directory"))

        self.assertTrue(result.success)
        self.assertEqual(result.content["path"], ".")
        self.assertFalse(result.content["recursive"])
        self.assertEqual(sorted(self.entry_names(result)), ["a.txt", "subdir"])

    def test_does_not_descend_into_subdirectories(self) -> None:
        self.make_file("a.txt")
        self.make_file("subdir/nested.txt")

        result = self.handler.execute(ToolRequest(tool_name="list_directory"))

        self.assertEqual(sorted(self.entry_names(result)), ["a.txt", "subdir"])

    def test_lists_a_specific_subdirectory(self) -> None:
        self.make_file("subdir/nested.txt")

        result = self.handler.execute(
            ToolRequest(tool_name="list_directory", arguments={"path": "subdir"})
        )

        self.assertTrue(result.success)
        self.assertEqual(self.entry_names(result), ["nested.txt"])

    def test_entry_shape_for_a_file(self) -> None:
        self.make_file("a.txt", content="hello")

        result = self.handler.execute(ToolRequest(tool_name="list_directory"))

        entry = result.content["entries"][0]
        self.assertEqual(entry["name"], "a.txt")
        self.assertEqual(entry["path"], "a.txt")
        self.assertEqual(entry["type"], "file")
        self.assertEqual(entry["size_bytes"], 5)

    def test_entry_shape_for_a_directory(self) -> None:
        self.make_dir("subdir")

        result = self.handler.execute(ToolRequest(tool_name="list_directory"))

        entry = result.content["entries"][0]
        self.assertEqual(entry["type"], "directory")
        self.assertIsNone(entry["size_bytes"])

    def test_hidden_entries_excluded_by_default(self) -> None:
        self.make_file(".hidden")
        self.make_file("visible.txt")

        result = self.handler.execute(ToolRequest(tool_name="list_directory"))

        self.assertEqual(self.entry_names(result), ["visible.txt"])

    def test_hidden_entries_included_when_requested(self) -> None:
        self.make_file(".hidden")
        self.make_file("visible.txt")

        result = self.handler.execute(
            ToolRequest(tool_name="list_directory", arguments={"include_hidden": True})
        )

        self.assertEqual(sorted(self.entry_names(result)), [".hidden", "visible.txt"])

    def test_entries_sorted_deterministically(self) -> None:
        self.make_file("zebra.txt")
        self.make_file("apple.txt")
        self.make_dir("mango")

        result = self.handler.execute(ToolRequest(tool_name="list_directory"))

        self.assertEqual(self.entry_names(result), ["apple.txt", "mango", "zebra.txt"])

    def test_empty_directory(self) -> None:
        result = self.handler.execute(ToolRequest(tool_name="list_directory"))
        self.assertTrue(result.success)
        self.assertEqual(result.content["entries"], [])
        self.assertFalse(result.content["truncated"])


class TestRecursiveListing(ListDirectoryHandlerTestCase):
    def test_recursive_lists_nested_files(self) -> None:
        self.make_file("a.txt")
        self.make_file("subdir/nested.txt")
        self.make_file("subdir/deep/deeper.txt")

        result = self.handler.execute(
            ToolRequest(tool_name="list_directory", arguments={"recursive": True})
        )

        self.assertTrue(result.success)
        self.assertTrue(result.content["recursive"])
        paths = sorted(e["path"] for e in result.content["entries"])
        self.assertEqual(
            paths,
            ["a.txt", "subdir", "subdir/deep", "subdir/deep/deeper.txt", "subdir/nested.txt"],
        )

    def test_recursive_respects_hidden_filter(self) -> None:
        self.make_file("subdir/.hidden")
        self.make_file("subdir/visible.txt")

        result = self.handler.execute(
            ToolRequest(tool_name="list_directory", arguments={"recursive": True})
        )

        paths = [e["path"] for e in result.content["entries"]]
        self.assertNotIn("subdir/.hidden", paths)
        self.assertIn("subdir/visible.txt", paths)


class TestInvalidArguments(ListDirectoryHandlerTestCase):
    def test_non_string_path(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="list_directory", arguments={"path": 5})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_non_bool_recursive(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="list_directory", arguments={"recursive": "yes"})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_non_bool_include_hidden(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="list_directory", arguments={"include_hidden": 1})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")


class TestPathSafety(ListDirectoryHandlerTestCase):
    def test_rejects_absolute_path(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="list_directory", arguments={"path": "/etc"})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "path_outside_base_dir")

    def test_rejects_parent_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as outside_parent:
            base_dir = Path(outside_parent) / "workspace"
            base_dir.mkdir()
            (Path(outside_parent) / "secret_dir").mkdir()

            handler = ListDirectoryHandler(base_dir)
            result = handler.execute(
                ToolRequest(tool_name="list_directory", arguments={"path": "../secret_dir"})
            )

            self.assertFalse(result.success)
            self.assertEqual(result.error.code, "path_outside_base_dir")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks not supported on this platform")
    def test_does_not_descend_into_symlinked_directory_that_escapes_base_dir(self) -> None:
        with tempfile.TemporaryDirectory() as outside_parent:
            base_dir = Path(outside_parent) / "workspace"
            base_dir.mkdir()
            secret_dir = Path(outside_parent) / "secret_dir"
            secret_dir.mkdir()
            (secret_dir / "secret.txt").write_text("top secret")

            link = base_dir / "link"
            try:
                os.symlink(secret_dir, link, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation not permitted in this environment")

            handler = ListDirectoryHandler(base_dir)
            result = handler.execute(
                ToolRequest(tool_name="list_directory", arguments={"recursive": True})
            )

            self.assertTrue(result.success)
            entries_by_path = {e["path"]: e for e in result.content["entries"]}
            self.assertEqual(entries_by_path["link"]["type"], "symlink")
            # The symlinked directory's contents must never appear -- os.walk
            # was never allowed to descend into it.
            self.assertNotIn("link/secret.txt", entries_by_path)


class TestDirectoryStateErrors(ListDirectoryHandlerTestCase):
    def test_missing_directory(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="list_directory", arguments={"path": "does-not-exist"})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "directory_not_found")

    def test_path_is_a_file_not_a_directory(self) -> None:
        self.make_file("a.txt")
        result = self.handler.execute(
            ToolRequest(tool_name="list_directory", arguments={"path": "a.txt"})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "not_a_directory")


class TestTruncation(ListDirectoryHandlerTestCase):
    def test_truncates_when_over_max_entries(self) -> None:
        for i in range(5):
            self.make_file(f"file_{i}.txt")

        handler = ListDirectoryHandler(self.base_dir, max_entries=3)
        result = handler.execute(ToolRequest(tool_name="list_directory"))

        self.assertTrue(result.success)
        self.assertEqual(len(result.content["entries"]), 3)
        self.assertTrue(result.content["truncated"])

    def test_not_truncated_when_under_max_entries(self) -> None:
        self.make_file("a.txt")
        result = self.handler.execute(ToolRequest(tool_name="list_directory"))
        self.assertFalse(result.content["truncated"])

    def test_default_max_entries(self) -> None:
        self.assertEqual(DEFAULT_MAX_ENTRIES, 1000)


if __name__ == "__main__":
    unittest.main()
