from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.tools.handlers.write_file import (
    DEFAULT_MAX_FILE_SIZE_BYTES,
    WriteFileHandler,
)
from src.tools.models import RiskLevel, ToolRequest


class WriteFileHandlerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        self.handler = WriteFileHandler(self.base_dir)

    def write(self, relative_path: str, content: str) -> Path:
        path = self.base_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path


class TestDefinition(WriteFileHandlerTestCase):
    def test_definition_is_high_risk_and_confirmation_gated(self) -> None:
        definition = self.handler.definition()
        self.assertEqual(definition.name, "write_file")
        self.assertEqual(definition.risk_level, RiskLevel.HIGH)
        self.assertTrue(definition.requires_confirmation)
        self.assertFalse(definition.metadata.get("read_only"))

    def test_default_max_file_size(self) -> None:
        self.assertEqual(DEFAULT_MAX_FILE_SIZE_BYTES, 1_048_576)

    def test_constructor_rejects_missing_base_dir(self) -> None:
        with self.assertRaises(ValueError):
            WriteFileHandler(self.base_dir / "does-not-exist")

    def test_constructor_rejects_invalid_max_file_size(self) -> None:
        with self.assertRaises(ValueError):
            WriteFileHandler(self.base_dir, max_file_size_bytes=0)


class TestWrite(WriteFileHandlerTestCase):
    def test_creates_new_file(self) -> None:
        result = self.handler.execute(
            ToolRequest(
                tool_name="write_file",
                arguments={"path": "notes.txt", "content": "hello"},
                invocation_id="inv-1",
            )
        )

        self.assertTrue(result.success)
        self.assertEqual((self.base_dir / "notes.txt").read_text(encoding="utf-8"), "hello")
        self.assertEqual(result.content["path"], "notes.txt")
        self.assertEqual(result.content["size_bytes"], 5)
        self.assertFalse(result.content["overwritten"])
        self.assertEqual(result.invocation_id, "inv-1")

    def test_existing_file_requires_overwrite(self) -> None:
        self.write("notes.txt", "old")

        result = self.handler.execute(
            ToolRequest(
                tool_name="write_file",
                arguments={"path": "notes.txt", "content": "new"},
            )
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "file_exists")
        self.assertEqual((self.base_dir / "notes.txt").read_text(encoding="utf-8"), "old")

    def test_existing_file_can_be_overwritten_explicitly(self) -> None:
        self.write("notes.txt", "old")

        result = self.handler.execute(
            ToolRequest(
                tool_name="write_file",
                arguments={
                    "path": "notes.txt",
                    "content": "new",
                    "overwrite": True,
                },
            )
        )

        self.assertTrue(result.success)
        self.assertEqual((self.base_dir / "notes.txt").read_text(encoding="utf-8"), "new")
        self.assertTrue(result.content["overwritten"])

    def test_new_file_with_overwrite_true_is_not_reported_as_overwrite(self) -> None:
        result = self.handler.execute(
            ToolRequest(
                tool_name="write_file",
                arguments={
                    "path": "new.txt",
                    "content": "created",
                    "overwrite": True,
                },
            )
        )

        self.assertTrue(result.success)
        self.assertFalse(result.content["overwritten"])

    def test_missing_parent_requires_create_parents(self) -> None:
        result = self.handler.execute(
            ToolRequest(
                tool_name="write_file",
                arguments={"path": "nested/notes.txt", "content": "hello"},
            )
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "parent_not_found")

    def test_create_parents_is_explicit(self) -> None:
        result = self.handler.execute(
            ToolRequest(
                tool_name="write_file",
                arguments={
                    "path": "nested/notes.txt",
                    "content": "hello",
                    "create_parents": True,
                },
            )
        )

        self.assertTrue(result.success)
        self.assertEqual(
            (self.base_dir / "nested/notes.txt").read_text(encoding="utf-8"),
            "hello",
        )

    def test_content_size_limit_is_enforced_before_write(self) -> None:
        handler = WriteFileHandler(self.base_dir, max_file_size_bytes=5)
        result = handler.execute(
            ToolRequest(
                tool_name="write_file",
                arguments={"path": "large.txt", "content": "123456"},
            )
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "content_too_large")
        self.assertFalse((self.base_dir / "large.txt").exists())


class TestArgumentsAndSafety(WriteFileHandlerTestCase):
    def test_missing_path_is_rejected(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="write_file", arguments={"content": "hello"})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_missing_content_is_rejected(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="write_file", arguments={"path": "notes.txt"})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_non_string_content_is_rejected(self) -> None:
        result = self.handler.execute(
            ToolRequest(
                tool_name="write_file",
                arguments={"path": "notes.txt", "content": 123},
            )
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_invalid_overwrite_is_rejected(self) -> None:
        result = self.handler.execute(
            ToolRequest(
                tool_name="write_file",
                arguments={"path": "notes.txt", "content": "hello", "overwrite": "yes"},
            )
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_invalid_create_parents_is_rejected(self) -> None:
        result = self.handler.execute(
            ToolRequest(
                tool_name="write_file",
                arguments={
                    "path": "notes.txt",
                    "content": "hello",
                    "create_parents": "yes",
                },
            )
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_absolute_path_is_rejected(self) -> None:
        result = self.handler.execute(
            ToolRequest(
                tool_name="write_file",
                arguments={
                    "path": str(self.base_dir / "escape.txt"),
                    "content": "blocked",
                },
            )
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "path_outside_base_dir")

    def test_parent_traversal_is_rejected(self) -> None:
        result = self.handler.execute(
            ToolRequest(
                tool_name="write_file",
                arguments={"path": "../escape.txt", "content": "blocked"},
            )
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "path_outside_base_dir")

    def test_existing_directory_is_not_a_file_target(self) -> None:
        (self.base_dir / "folder").mkdir()
        result = self.handler.execute(
            ToolRequest(
                tool_name="write_file",
                arguments={"path": "folder", "content": "blocked"},
            )
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "not_a_file")
