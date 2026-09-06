from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from src.tools.handlers.copy_file import DEFAULT_MAX_FILE_SIZE_BYTES, CopyFileHandler
from src.tools.models import RiskLevel, ToolRequest


class CopyFileHandlerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        self.handler = CopyFileHandler(self.base_dir)

    def write(self, relative_path: str, content: str, encoding: str = "utf-8") -> Path:
        path = self.base_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)
        return path


class TestDefinition(CopyFileHandlerTestCase):
    def test_definition_is_high_risk_and_requires_confirmation(self) -> None:
        definition = self.handler.definition()
        self.assertEqual(definition.name, "copy_file")
        self.assertEqual(definition.risk_level, RiskLevel.HIGH)
        self.assertTrue(definition.requires_confirmation)
        self.assertFalse(definition.metadata.get("read_only"))

    def test_constructor_rejects_missing_base_dir(self) -> None:
        with self.assertRaises(ValueError):
            CopyFileHandler(self.base_dir / "does-not-exist")

    def test_constructor_rejects_invalid_max_file_size(self) -> None:
        with self.assertRaises(ValueError):
            CopyFileHandler(self.base_dir, max_file_size_bytes=0)


class TestSuccessfulCopy(CopyFileHandlerTestCase):
    def test_copies_file_within_workspace(self) -> None:
        self.write("source.txt", "hello world")
        request = ToolRequest(
            tool_name="copy_file",
            arguments={"source_path": "source.txt", "destination_path": "dest.txt"},
        )

        result = self.handler.execute(request)

        self.assertTrue(result.success)
        self.assertEqual(result.content["source_path"], "source.txt")
        self.assertEqual(result.content["destination_path"], "dest.txt")
        self.assertEqual(result.content["size_bytes"], len("hello world".encode("utf-8")))
        self.assertFalse(result.content["overwritten"])

        dest_path = self.base_dir / "dest.txt"
        self.assertTrue(dest_path.exists())
        self.assertEqual(dest_path.read_text(), "hello world")

    def test_copies_file_to_nested_directory(self) -> None:
        self.write("source.txt", "nested content")
        request = ToolRequest(
            tool_name="copy_file",
            arguments={
                "source_path": "source.txt",
                "destination_path": "subdir/deep/dest.txt",
                "create_parents": True,
            },
        )

        result = self.handler.execute(request)

        self.assertTrue(result.success)
        self.assertEqual(result.content["destination_path"], "subdir/deep/dest.txt")

        dest_path = self.base_dir / "subdir" / "deep" / "dest.txt"
        self.assertTrue(dest_path.exists())
        self.assertEqual(dest_path.read_text(), "nested content")

    def test_overwrites_existing_file_when_allowed(self) -> None:
        self.write("source.txt", "original")
        self.write("dest.txt", "will be overwritten")
        request = ToolRequest(
            tool_name="copy_file",
            arguments={
                "source_path": "source.txt",
                "destination_path": "dest.txt",
                "overwrite": True,
            },
        )

        result = self.handler.execute(request)

        self.assertTrue(result.success)
        self.assertTrue(result.content["overwritten"])

        dest_path = self.base_dir / "dest.txt"
        self.assertEqual(dest_path.read_text(), "original")

    def test_invocation_id_is_propagated(self) -> None:
        self.write("source.txt", "hi")
        request = ToolRequest(
            tool_name="copy_file",
            arguments={"source_path": "source.txt", "destination_path": "dest.txt"},
            invocation_id="req-1",
        )

        result = self.handler.execute(request)

        self.assertEqual(result.invocation_id, "req-1")


class TestInvalidArguments(CopyFileHandlerTestCase):
    def test_missing_source_path_argument(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="copy_file", arguments={"destination_path": "dest.txt"})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_empty_source_path_argument(self) -> None:
        result = self.handler.execute(
            ToolRequest(
                tool_name="copy_file",
                arguments={"source_path": "   ", "destination_path": "dest.txt"},
            )
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_missing_destination_path_argument(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="copy_file", arguments={"source_path": "source.txt"})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_non_string_source_path_argument(self) -> None:
        result = self.handler.execute(
            ToolRequest(
                tool_name="copy_file",
                arguments={"source_path": 123, "destination_path": "dest.txt"},
            )
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_non_boolean_overwrite_argument(self) -> None:
        result = self.handler.execute(
            ToolRequest(
                tool_name="copy_file",
                arguments={
                    "source_path": "source.txt",
                    "destination_path": "dest.txt",
                    "overwrite": "yes",
                },
            )
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")


class TestFileNotFound(CopyFileHandlerTestCase):
    def test_source_not_found(self) -> None:
        request = ToolRequest(
            tool_name="copy_file",
            arguments={"source_path": "nonexistent.txt", "destination_path": "dest.txt"},
        )

        result = self.handler.execute(request)

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "source_not_found")


class TestFileTooLarge(CopyFileHandlerTestCase):
    def test_file_too_large(self) -> None:
        large_content = "x" * (DEFAULT_MAX_FILE_SIZE_BYTES + 1)
        self.write("large.txt", large_content)
        request = ToolRequest(
            tool_name="copy_file",
            arguments={"source_path": "large.txt", "destination_path": "dest.txt"},
        )

        result = self.handler.execute(request)

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "file_too_large")


class TestDestinationExists(CopyFileHandlerTestCase):
    def test_destination_exists_without_overwrite(self) -> None:
        self.write("source.txt", "content")
        self.write("dest.txt", "existing")
        request = ToolRequest(
            tool_name="copy_file",
            arguments={"source_path": "source.txt", "destination_path": "dest.txt"},
        )

        result = self.handler.execute(request)

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "file_exists")


class TestParentNotFound(CopyFileHandlerTestCase):
    def test_parent_not_found_without_create_parents(self) -> None:
        self.write("source.txt", "content")
        request = ToolRequest(
            tool_name="copy_file",
            arguments={
                "source_path": "source.txt",
                "destination_path": "nonexistent_dir/dest.txt",
            },
        )

        result = self.handler.execute(request)

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "parent_not_found")


class TestNotAFile(CopyFileHandlerTestCase):
    def test_source_is_directory(self) -> None:
        (self.base_dir / "dir").mkdir()
        request = ToolRequest(
            tool_name="copy_file",
            arguments={"source_path": "dir", "destination_path": "dest.txt"},
        )

        result = self.handler.execute(request)

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "not_a_file")


class TestWorkspaceBoundary(CopyFileHandlerTestCase):
    def test_absolute_path_rejected(self) -> None:
        outside_path = Path(tempfile.gettempdir()) / "outside.txt"
        outside_path.write_text("outside content")
        request = ToolRequest(
            tool_name="copy_file",
            arguments={"source_path": str(outside_path), "destination_path": "dest.txt"},
        )

        result = self.handler.execute(request)

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "path_outside_base_dir")

    def test_escape_attempt_rejected(self) -> None:
        request = ToolRequest(
            tool_name="copy_file",
            arguments={"source_path": "../etc/passwd", "destination_path": "dest.txt"},
        )

        result = self.handler.execute(request)

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "path_outside_base_dir")


if __name__ == "__main__":
    unittest.main()
