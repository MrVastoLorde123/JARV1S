from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.tools.workspace import Workspace, WorkspacePathError


class WorkspaceContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        self.workspace = Workspace(self.base_dir)

    def test_shared_error_codes_are_stable(self) -> None:
        self.assertEqual(Workspace.INVALID_ARGUMENT, "invalid_argument")
        self.assertEqual(Workspace.PATH_OUTSIDE_BASE_DIR, "path_outside_base_dir")
        self.assertEqual(Workspace.IO_ERROR, "io_error")

    def test_runtime_filesystem_errors_map_to_shared_io_error(self) -> None:
        code, message = self.workspace.runtime_error(OSError("permission denied"))
        self.assertEqual(code, Workspace.IO_ERROR)
        self.assertEqual(message, "permission denied")

    def test_ensure_within_returns_safe_path_unchanged(self) -> None:
        path = self.base_dir / "nested" / "file.txt"
        self.assertEqual(self.workspace.ensure_within(path), path)

    def test_ensure_within_rejects_outside_path(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            outside_path = Path(outside) / "file.txt"
            with self.assertRaises(WorkspacePathError) as context:
                self.workspace.ensure_within(
                    outside_path,
                    display_path="../outside/file.txt",
                )
            self.assertEqual(context.exception.code, Workspace.PATH_OUTSIDE_BASE_DIR)
            self.assertIn("../outside/file.txt", context.exception.message)


if __name__ == "__main__":
    unittest.main()
