from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.tools.workspace import Workspace, WorkspacePathError


class WorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        self.workspace = Workspace(self.base_dir)

    def test_base_dir_is_resolved(self) -> None:
        self.assertEqual(self.workspace.base_dir, self.base_dir.resolve())

    def test_missing_base_dir_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Workspace(self.base_dir / "missing")

    def test_relative_path_is_resolved_inside_workspace(self) -> None:
        expected = (self.base_dir / "nested" / "file.txt").resolve()
        self.assertEqual(self.workspace.resolve_path("nested/file.txt"), expected)

    def test_dot_path_resolves_to_workspace(self) -> None:
        self.assertEqual(self.workspace.resolve_path("."), self.base_dir.resolve())

    def test_empty_path_is_rejected(self) -> None:
        with self.assertRaises(WorkspacePathError) as context:
            self.workspace.resolve_path("   ")
        self.assertEqual(context.exception.code, "invalid_argument")

    def test_absolute_path_is_rejected(self) -> None:
        with self.assertRaises(WorkspacePathError) as context:
            self.workspace.resolve_path(str(self.base_dir / "file.txt"))
        self.assertEqual(context.exception.code, "path_outside_base_dir")

    def test_parent_traversal_is_rejected(self) -> None:
        with self.assertRaises(WorkspacePathError) as context:
            self.workspace.resolve_path("../outside.txt")
        self.assertEqual(context.exception.code, "path_outside_base_dir")

    def test_symlink_to_outside_workspace_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            outside_dir = Path(outside)
            target = outside_dir / "secret.txt"
            target.write_text("secret", encoding="utf-8")
            link = self.base_dir / "secret-link.txt"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable on this platform")

            with self.assertRaises(WorkspacePathError) as context:
                self.workspace.resolve_path("secret-link.txt")
            self.assertEqual(context.exception.code, "path_outside_base_dir")

    def test_relative_path_is_reported_as_posix(self) -> None:
        path = self.base_dir / "nested" / "file.txt"
        self.assertEqual(self.workspace.relative_path(path), "nested/file.txt")

    def test_outside_path_cannot_be_converted_to_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            with self.assertRaises(ValueError):
                self.workspace.relative_path(Path(outside) / "file.txt")


if __name__ == "__main__":
    unittest.main()
