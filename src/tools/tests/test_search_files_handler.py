from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.tools.handlers.search_files import (
    DEFAULT_MAX_FILE_SIZE_BYTES,
    DEFAULT_MAX_RESULTS,
    SearchFilesHandler,
)
from src.tools.models import RiskLevel, ToolRequest


class SearchFilesHandlerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        self.handler = SearchFilesHandler(self.base_dir)

    def write(self, relative_path: str, content: str) -> Path:
        path = self.base_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path


class TestDefinition(SearchFilesHandlerTestCase):
    def test_definition_is_low_risk_and_read_only(self) -> None:
        definition = self.handler.definition()
        self.assertEqual(definition.name, "search_files")
        self.assertEqual(definition.risk_level, RiskLevel.LOW)
        self.assertFalse(definition.requires_confirmation)
        self.assertTrue(definition.metadata.get("read_only"))

    def test_constructor_rejects_missing_base_dir(self) -> None:
        with self.assertRaises(ValueError):
            SearchFilesHandler(self.base_dir / "does-not-exist")

    def test_constructor_rejects_invalid_max_results(self) -> None:
        with self.assertRaises(ValueError):
            SearchFilesHandler(self.base_dir, max_results=0)

    def test_constructor_rejects_invalid_max_file_size(self) -> None:
        with self.assertRaises(ValueError):
            SearchFilesHandler(self.base_dir, max_file_size_bytes=0)


class TestSearch(SearchFilesHandlerTestCase):
    def test_finds_matching_lines_recursively(self) -> None:
        self.write("one.py", "alpha\nTARGET here\n")
        self.write("nested/two.py", "nothing\nsecond TARGET match\n")

        result = self.handler.execute(
            ToolRequest(tool_name="search_files", arguments={"query": "target"})
        )

        self.assertTrue(result.success)
        self.assertEqual(
            [(m["path"], m["line"]) for m in result.content["matches"]],
            [("nested/two.py", 2), ("one.py", 2)],
        )
        self.assertFalse(result.content["truncated"])

    def test_search_is_case_insensitive_by_default(self) -> None:
        self.write("notes.txt", "JARVIS\n")

        result = self.handler.execute(
            ToolRequest(tool_name="search_files", arguments={"query": "jarvis"})
        )

        self.assertTrue(result.success)
        self.assertEqual(len(result.content["matches"]), 1)

    def test_case_sensitive_search(self) -> None:
        self.write("notes.txt", "JARVIS\njarvis\n")

        result = self.handler.execute(
            ToolRequest(
                tool_name="search_files",
                arguments={"query": "jarvis", "case_sensitive": True},
            )
        )

        self.assertTrue(result.success)
        self.assertEqual(len(result.content["matches"]), 1)
        self.assertEqual(result.content["matches"][0]["line"], 2)

    def test_specific_file_can_be_searched(self) -> None:
        self.write("one.txt", "needle\n")
        self.write("two.txt", "needle\n")

        result = self.handler.execute(
            ToolRequest(
                tool_name="search_files",
                arguments={"query": "needle", "path": "one.txt"},
            )
        )

        self.assertTrue(result.success)
        self.assertEqual([m["path"] for m in result.content["matches"]], ["one.txt"])

    def test_non_recursive_search_ignores_nested_files(self) -> None:
        self.write("root.txt", "needle\n")
        self.write("nested/child.txt", "needle\n")

        result = self.handler.execute(
            ToolRequest(
                tool_name="search_files",
                arguments={"query": "needle", "recursive": False},
            )
        )

        self.assertTrue(result.success)
        self.assertEqual([m["path"] for m in result.content["matches"]], ["root.txt"])

    def test_result_limit_is_bounded(self) -> None:
        self.write("matches.txt", "needle\nneedle\nneedle\n")
        handler = SearchFilesHandler(self.base_dir, max_results=10)

        result = handler.execute(
            ToolRequest(
                tool_name="search_files",
                arguments={"query": "needle", "max_results": 2},
            )
        )

        print("DEBUG RESULT:", result.content)

        self.assertTrue(result.success)
        self.assertEqual(len(result.content["matches"]), 2)
        self.assertTrue(result.content["truncated"])


    def test_tool_level_limit_cannot_be_exceeded_by_request(self) -> None:
        self.write("matches.txt", "needle\nneedle\nneedle\n")
        handler = SearchFilesHandler(self.base_dir, max_results=2)

        result = handler.execute(
            ToolRequest(
                tool_name="search_files",
                arguments={"query": "needle", "max_results": 100},
            )
        )

        self.assertEqual(len(result.content["matches"]), 2)
        self.assertTrue(result.content["truncated"])

    def test_oversized_file_is_skipped(self) -> None:
        handler = SearchFilesHandler(self.base_dir, max_file_size_bytes=6)
        self.write("small.txt", "needle")
        self.write("large.txt", "x" * 100)

        result = handler.execute(
            ToolRequest(tool_name="search_files", arguments={"query": "needle"})
        )

        self.assertTrue(result.success)
        self.assertEqual(
            [m["path"] for m in result.content["matches"]],
            ["small.txt"],
        )
        self.assertEqual(result.content["files_skipped"], 1)

class TestArgumentsAndSafety(SearchFilesHandlerTestCase):
    def test_missing_query_is_rejected(self) -> None:
        result = self.handler.execute(ToolRequest(tool_name="search_files"))
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_empty_query_is_rejected(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="search_files", arguments={"query": "   "})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_invalid_recursive_is_rejected(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="search_files", arguments={"query": "x", "recursive": "yes"})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_invalid_case_sensitive_is_rejected(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="search_files", arguments={"query": "x", "case_sensitive": 1})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_invalid_max_results_is_rejected(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="search_files", arguments={"query": "x", "max_results": True})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_absolute_path_is_rejected(self) -> None:
        result = self.handler.execute(
            ToolRequest(
                tool_name="search_files",
                arguments={"query": "x", "path": str(self.base_dir)},
            )
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "path_outside_base_dir")

    def test_parent_traversal_is_rejected(self) -> None:
        outside = self.base_dir.parent / "secret.txt"
        outside.write_text("needle", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))

        result = self.handler.execute(
            ToolRequest(
                tool_name="search_files",
                arguments={"query": "needle", "path": "../secret.txt"},
            )
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "path_outside_base_dir")

    def test_missing_path_is_reported(self) -> None:
        result = self.handler.execute(
            ToolRequest(
                tool_name="search_files",
                arguments={"query": "needle", "path": "missing"},
            )
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "path_not_found")


class TestDefaults(SearchFilesHandlerTestCase):
    def test_default_max_results(self) -> None:
        self.assertEqual(DEFAULT_MAX_RESULTS, 100)

    def test_default_max_file_size(self) -> None:
        self.assertEqual(DEFAULT_MAX_FILE_SIZE_BYTES, 1_048_576)


if __name__ == "__main__":
    unittest.main()
