from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from src.tools.handlers.read_file import DEFAULT_MAX_FILE_SIZE_BYTES, ReadFileHandler
from src.tools.models import RiskLevel, ToolRequest


class ReadFileHandlerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        self.handler = ReadFileHandler(self.base_dir)

    def write(self, relative_path: str, content: str, encoding: str = "utf-8") -> Path:
        path = self.base_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)
        return path


class TestDefinition(ReadFileHandlerTestCase):
    def test_definition_is_low_risk_and_read_only(self) -> None:
        definition = self.handler.definition()
        self.assertEqual(definition.name, "read_file")
        self.assertEqual(definition.risk_level, RiskLevel.LOW)
        self.assertFalse(definition.requires_confirmation)
        self.assertTrue(definition.metadata.get("read_only"))

    def test_constructor_rejects_missing_base_dir(self) -> None:
        with self.assertRaises(ValueError):
            ReadFileHandler(self.base_dir / "does-not-exist")

    def test_constructor_rejects_invalid_max_file_size(self) -> None:
        with self.assertRaises(ValueError):
            ReadFileHandler(self.base_dir, max_file_size_bytes=0)


class TestSuccessfulRead(ReadFileHandlerTestCase):
    def test_reads_file_contents(self) -> None:
        self.write("notes.txt", "hello world")
        request = ToolRequest(tool_name="read_file", arguments={"path": "notes.txt"})

        result = self.handler.execute(request)

        self.assertTrue(result.success)
        self.assertEqual(result.content["content"], "hello world")
        self.assertEqual(result.content["path"], "notes.txt")
        self.assertEqual(result.content["size_bytes"], len("hello world".encode("utf-8")))

    def test_reads_file_in_nested_directory(self) -> None:
        self.write("subdir/deep/notes.txt", "nested")
        request = ToolRequest(tool_name="read_file", arguments={"path": "subdir/deep/notes.txt"})

        result = self.handler.execute(request)

        self.assertTrue(result.success)
        self.assertEqual(result.content["content"], "nested")

    def test_invocation_id_is_propagated(self) -> None:
        self.write("notes.txt", "hi")
        request = ToolRequest(
            tool_name="read_file", arguments={"path": "notes.txt"}, invocation_id="req-1"
        )

        result = self.handler.execute(request)

        self.assertEqual(result.invocation_id, "req-1")

    def test_custom_encoding(self) -> None:
        self.write("latin1.txt", "café", encoding="latin-1")
        request = ToolRequest(
            tool_name="read_file",
            arguments={"path": "latin1.txt", "encoding": "latin-1"},
        )

        result = self.handler.execute(request)

        self.assertTrue(result.success)
        self.assertEqual(result.content["content"], "café")


class TestInvalidArguments(ReadFileHandlerTestCase):
    def test_missing_path_argument(self) -> None:
        result = self.handler.execute(ToolRequest(tool_name="read_file"))
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_empty_path_argument(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="read_file", arguments={"path": "   "})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_non_string_path_argument(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="read_file", arguments={"path": 123})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")

    def test_non_string_encoding_argument(self) -> None:
        self.write("notes.txt", "hi")
        result = self.handler.execute(
            ToolRequest(
                tool_name="read_file", arguments={"path": "notes.txt", "encoding": 5}
            )
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")


class TestPathSafety(ReadFileHandlerTestCase):
    def test_rejects_absolute_path(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="read_file", arguments={"path": "/etc/passwd"})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "path_outside_base_dir")

    def test_rejects_parent_directory_traversal(self) -> None:
        # Create a file just outside base_dir and try to reach it with '..'.
        with tempfile.TemporaryDirectory() as outside_parent:
            base_dir = Path(outside_parent) / "workspace"
            base_dir.mkdir()
            secret = Path(outside_parent) / "secret.txt"
            secret.write_text("top secret")

            handler = ReadFileHandler(base_dir)
            result = handler.execute(
                ToolRequest(tool_name="read_file", arguments={"path": "../secret.txt"})
            )

            self.assertFalse(result.success)
            self.assertEqual(result.error.code, "path_outside_base_dir")

    def test_traversal_that_stays_inside_base_dir_is_allowed(self) -> None:
        self.write("a/b/notes.txt", "inside")
        result = self.handler.execute(
            ToolRequest(tool_name="read_file", arguments={"path": "a/b/../b/notes.txt"})
        )
        self.assertTrue(result.success)
        self.assertEqual(result.content["content"], "inside")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks not supported on this platform")
    def test_rejects_symlink_that_escapes_base_dir(self) -> None:
        with tempfile.TemporaryDirectory() as outside_parent:
            base_dir = Path(outside_parent) / "workspace"
            base_dir.mkdir()
            secret = Path(outside_parent) / "secret.txt"
            secret.write_text("top secret")

            link = base_dir / "link.txt"
            try:
                os.symlink(secret, link)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation not permitted in this environment")

            handler = ReadFileHandler(base_dir)
            result = handler.execute(
                ToolRequest(tool_name="read_file", arguments={"path": "link.txt"})
            )

            self.assertFalse(result.success)
            self.assertEqual(result.error.code, "path_outside_base_dir")


class TestFileStateErrors(ReadFileHandlerTestCase):
    def test_missing_file(self) -> None:
        result = self.handler.execute(
            ToolRequest(tool_name="read_file", arguments={"path": "does-not-exist.txt"})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "file_not_found")

    def test_path_is_a_directory(self) -> None:
        (self.base_dir / "adir").mkdir()
        result = self.handler.execute(
            ToolRequest(tool_name="read_file", arguments={"path": "adir"})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "not_a_file")

    def test_file_too_large_is_rejected(self) -> None:
        handler = ReadFileHandler(self.base_dir, max_file_size_bytes=10)
        self.write("big.txt", "x" * 100)

        result = handler.execute(
            ToolRequest(tool_name="read_file", arguments={"path": "big.txt"})
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "file_too_large")

    def test_default_max_file_size_is_one_mebibyte(self) -> None:
        self.assertEqual(DEFAULT_MAX_FILE_SIZE_BYTES, 1_048_576)

    def test_decode_error(self) -> None:
        path = self.base_dir / "binary.dat"
        path.write_bytes(b"\xff\xfe\x00\x01not-valid-utf8\x80\x81")

        result = self.handler.execute(
            ToolRequest(tool_name="read_file", arguments={"path": "binary.dat"})
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "decode_error")


if __name__ == "__main__":
    unittest.main()
