from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from src.tools.handlers.check_path import CheckPathHandler
from src.tools.models import RiskLevel, ToolRequest


class CheckPathHandlerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        self.handler = CheckPathHandler(self.base_dir)

    def write(self, relative_path: str, content: str, encoding: str = "utf-8") -> Path:
        path = self.base_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)
        return path


class TestDefinition(CheckPathHandlerTestCase):
    def test_definition_is_low_risk_and_read_only(self) -> None:
        definition = self.handler.definition()
        self.assertEqual(definition.name, "check_path")
        self.assertEqual(definition.risk_level, RiskLevel.LOW)
        self.assertFalse(definition.requires_confirmation)
        self.assertTrue(definition.metadata.get("read_only"))

    def test_constructor_rejects_missing_base_dir(self) -> None:
        with self.assertRaises(ValueError):
            CheckPathHandler(self.base_dir / "does-not-exist")


class TestExistingFile(CheckPathHandlerTestCase):
    def test_file_exists(self) -> None:
        self.write("test.txt", "content")
        request = ToolRequest(tool_name="check_path", arguments={"path": "test.txt"})

        result = self.handler.execute(request)

        self.assertTrue(result.success)
        self.assertEqual(result.content["path"], "test.txt")
        self.assertTrue(result.content["exists"])
        self.assertEqual(result.content["type"], "file")
        self.assertEqual(result.content["size_bytes"], len("content".encode("utf-8")))

    def test_invocation_id_is_propagated(self) -> None:
        self.write("test.txt", "content")
        request = ToolRequest(
            tool_name="check_path", arguments={"path": "test.txt"}, invocation_id="req-1"
        )

        result = self.handler.execute(request)

        self.assertEqual(result.invocation_id, "req-1")


class TestExistingDirectory(CheckPathHandlerTestCase):
    def test_directory_exists(self) -> None:
        (self.base_dir / "dir").mkdir()
        request = ToolRequest(tool_name="check_path", arguments={"path": "dir"})

        result = self.handler.execute(request)

        self.assertTrue(result.success)
        self.assertEqual(result.content["path"], "dir")
        self.assertTrue(result.content["exists"])
        self.assertEqual(result.content["type"], "directory")
        self.assertIsNone(result.content["size_bytes"])


class TestExistingSymlink(CheckPathHandlerTestCase):
    def test_symlink_exists(self) -> None:
        self.write("target.txt", "content")
        link_path = self.base_dir / "link.txt"
        link_path.symlink_to("target.txt")
        request = ToolRequest(tool_name="check_path", arguments={"path": "link.txt"})

        result = self.handler.execute(request)

        self.assertTrue(result.success)
        self.assertTrue(result.content["exists"])
        self.assertEqual(result.content["type"], "symlink")


class TestNonExistentPath(CheckPathHandlerTestCase):
    def test_path_not_exists(self) -> None:
        request = ToolRequest(
            tool_name="check_path", arguments={"path": "nonexistent.txt"}
        )

        result = self.handler.execute(request)

        self.assertTrue(result.success)
        self.assertEqual(result.content["path"], "nonexistent.txt")
        self.assertFalse(result.content["exists"])
        self.assertEqual(result.content["type"], "none")
        self.assertIsNone(result.content["size_bytes"])


class TestInvalidArguments(CheckPathHandlerTestCase):
    def test_missing_path_argument(self) -> None:
        result = self.handler.execute(ToolRequest(tool_name="check_path"))
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_empty_path_argument(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="check_path", arguments={"path": "   "})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_non_string_path_argument(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="check_path", arguments={"path": 123})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")


class TestWorkspaceBoundary(CheckPathHandlerTestCase):
    def test_absolute_path_rejected(self) -> None:
        outside_path = Path(tempfile.gettempdir()) / "outside.txt"
        outside_path.write_text("outside content")
        request = ToolRequest(
            tool_name="check_path", arguments={"path": str(outside_path)}
        )

        result = self.handler.execute(request)

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "path_outside_base_dir")

    def test_escape_attempt_rejected(self) -> None:
        request = ToolRequest(
            tool_name="check_path", arguments={"path": "../etc/passwd"}
        )

        result = self.handler.execute(request)

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "path_outside_base_dir")


if __name__ == "__main__":
    unittest.main()
