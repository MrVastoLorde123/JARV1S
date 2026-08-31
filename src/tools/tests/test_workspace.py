from __future__ import annotations

import os
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

    def make_file(self, relative_path: str, content: str = "x") -> Path:
        path = self.base_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

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


class WorkspaceTraversalTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        self.workspace = Workspace(self.base_dir)

    def make_file(self, relative_path: str, content: str = "x") -> Path:
        path = self.base_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_non_recursive_traversal_is_deterministic(self) -> None:
        self.make_file("z.txt")
        self.make_file("a.txt")
        (self.base_dir / "middle").mkdir()

        paths = list(self.workspace.iter_paths(self.base_dir, recursive=False))
        self.assertEqual([path.name for path in paths], ["a.txt", "middle", "z.txt"])

    def test_recursive_traversal_is_deterministic_and_confined(self) -> None:
        self.make_file("z.txt")
        self.make_file("nested/a.txt")
        self.make_file("nested/deep/b.txt")

        paths = list(self.workspace.iter_paths(self.base_dir, recursive=True))
        self.assertEqual(
            [self.workspace.relative_path(path) for path in paths],
            ["nested", "nested/a.txt", "nested/deep", "nested/deep/b.txt", "z.txt"],
        )

    def test_hidden_entries_are_excluded_by_default(self) -> None:
        self.make_file(".hidden.txt")
        self.make_file("visible.txt")
        self.make_file("nested/.hidden-child.txt")
        self.make_file("nested/visible-child.txt")

        paths = list(self.workspace.iter_paths(self.base_dir, recursive=True))
        relative = [self.workspace.relative_path(path) for path in paths]
        self.assertEqual(
            relative,
            ["nested", "nested/visible-child.txt", "visible.txt"],
        )

    def test_hidden_entries_can_be_included(self) -> None:
        self.make_file(".hidden.txt")
        self.make_file("nested/.hidden-child.txt")

        paths = list(
            self.workspace.iter_paths(self.base_dir, recursive=True, include_hidden=True)
        )
        relative = [self.workspace.relative_path(path) for path in paths]
        self.assertIn(".hidden.txt", relative)
        self.assertIn("nested/.hidden-child.txt", relative)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks not supported on this platform")
    def test_symlinked_directory_is_reported_but_not_descended_into(self) -> None:
        with tempfile.TemporaryDirectory() as outside_parent:
            outside_dir = Path(outside_parent) / "secret"
            outside_dir.mkdir()
            (outside_dir / "secret.txt").write_text("secret", encoding="utf-8")

            link = self.base_dir / "link"
            try:
                os.symlink(outside_dir, link, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation not permitted in this environment")

            paths = list(self.workspace.iter_paths(self.base_dir, recursive=True))
            relative = [self.workspace.relative_path(path) for path in paths]
            self.assertIn("link", relative)
            self.assertNotIn("link/secret.txt", relative)

    def test_outside_directory_cannot_be_traversed(self) -> None:
        outside = self.base_dir.parent / f"{self.base_dir.name}-outside"
        outside.mkdir()
        self.addCleanup(lambda: outside.rmdir())
        with self.assertRaises(WorkspacePathError):
            list(self.workspace.iter_paths(outside, recursive=True))


if __name__ == "__main__":
    unittest.main()
