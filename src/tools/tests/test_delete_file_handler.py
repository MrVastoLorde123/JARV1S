from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from src.tools.handlers.delete_file import DeleteFileHandler
from src.tools.models import RiskLevel, ToolRequest


class DeleteFileHandlerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        self.handler = DeleteFileHandler(self.base_dir)

    def write(self, relative_path: str, content: str, encoding: str = "utf-8") -> Path:
        path = self.base_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)
        return path


class TestDefinition(DeleteFileHandlerTestCase):
    def test_definition_is_critical_risk_and_requires_confirmation(self) -> None:
        definition = self.handler.definition()
        self.assertEqual(definition.name, "delete_file")
        self.assertEqual(definition.risk_level, RiskLevel.CRITICAL)
        self.assertTrue(definition.requires_confirmation)
        self.assertFalse(definition.metadata.get("read_only"))

    def test_constructor_rejects_missing_base_dir(self) -> None:
        with self.assertRaises(ValueError):
            DeleteFileHandler(self.base_dir / "does-not-exist")


class TestSuccessfulDelete(DeleteFileHandlerTestCase):
    def test_deletes_file(self) -> None:
        self.write("test.txt", "content")
        request = ToolRequest(tool_name="delete_file", arguments={"path": "test.txt"})

        result = self.handler.execute(request)

        self.assertTrue(result.success)
        self.assertEqual(result.content["path"], "test.txt")
        self.assertTrue(result.content["deleted"])

        file_path = self.base_dir / "test.txt"
        self.assertFalse(file_path.exists())

    def test_invocation_id_is_propagated(self) -> None:
        self.write("test.txt", "content")
        request = ToolRequest(
            tool_name="delete_file", arguments={"path": "test.txt"}, invocation_id="req-1"
        )

        result = self.handler.execute(request)

        self.assertEqual(result.invocation_id, "req-1")


class TestInvalidArguments(DeleteFileHandlerTestCase):
    def test_missing_path_argument(self) -> None:
        result = self.handler.execute(ToolRequest(tool_name="delete_file"))
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_empty_path_argument(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="delete_file", arguments={"path": "   "})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_non_string_path_argument(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="delete_file", arguments={"path": 123})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")


class TestFileNotFound(DeleteFileHandlerTestCase):
    def test_file_not_found(self) -> None:
        request = ToolRequest(
            tool_name="delete_file", arguments={"path": "nonexistent.txt"}
        )

        result = self.handler.execute(request)

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "file_not_found")


class TestNotAFile(DeleteFileHandlerTestCase):
    def test_path_is_directory(self) -> None:
        (self.base_dir / "dir").mkdir()
        request = ToolRequest(tool_name="delete_file", arguments={"path": "dir"})

        result = self.handler.execute(request)

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "not_a_file")


class TestWorkspaceBoundary(DeleteFileHandlerTestCase):
    def test_absolute_path_rejected(self) -> None:
        outside_path = Path(tempfile.gettempdir()) / "outside.txt"
        outside_path.write_text("outside content")
        request = ToolRequest(
            tool_name="delete_file", arguments={"path": str(outside_path)}
        )

        result = self.handler.execute(request)

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "path_outside_base_dir")

    def test_escape_attempt_rejected(self) -> None:
        request = ToolRequest(
            tool_name="delete_file", arguments={"path": "../etc/passwd"}
        )

        result = self.handler.execute(request)

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "path_outside_base_dir")


if __name__ == "__main__":
    unittest.main()
