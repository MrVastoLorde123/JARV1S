"""Shared workspace boundary and traversal policy for filesystem-backed tools.

The workspace owns only common filesystem safety behavior: one resolved base
directory, safe resolution of request-relative paths, and bounded traversal
that never follows symlinks outside the workspace. Individual handlers remain
responsible for capability semantics, limits, and result schemas.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Iterator, Union


class WorkspacePathError(ValueError):
    """Raised when a requested path is invalid or escapes the workspace."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class Workspace:
    """A fixed, resolved directory that bounds filesystem tool access."""

    def __init__(self, base_dir: Union[str, Path]) -> None:
        resolved_base = Path(base_dir).resolve()
        if not resolved_base.is_dir():
            raise ValueError(f"base_dir must be an existing directory, got: {base_dir!r}")
        self._base_dir = resolved_base

    @property
    def base_dir(self) -> Path:
        """Return the resolved workspace root."""
        return self._base_dir

    def resolve_path(self, raw_path: str) -> Path:
        """Resolve a request-relative path and enforce the workspace boundary."""
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise WorkspacePathError(
                "invalid_argument",
                "path must be a non-empty string",
            )

        requested = Path(raw_path)
        if requested.is_absolute():
            raise WorkspacePathError(
                "path_outside_base_dir",
                "absolute paths are not allowed; provide a path relative to the tool's workspace directory",
            )

        candidate = (self._base_dir / requested).resolve()
        try:
            candidate.relative_to(self._base_dir)
        except ValueError as exc:
            raise WorkspacePathError(
                "path_outside_base_dir",
                f"resolved path escapes the allowed workspace directory: {raw_path}",
            ) from exc

        return candidate

    def relative_path(self, path: Path) -> str:
        """Return a workspace-relative POSIX path."""
        return path.relative_to(self._base_dir).as_posix()

    def iter_paths(
        self,
        directory: Path,
        *,
        recursive: bool,
        include_hidden: bool = False,
        follow_symlinks: bool = False,
        on_error: Callable[[OSError], None] | None = None,
    ) -> Iterator[Path]:
        """Yield paths below an already-resolved workspace directory.

        Traversal is deterministic and workspace-confined. Symlinked entries
        are yielded but are not descended into by default. When traversal
        encounters an inaccessible path, ``on_error`` receives the ``OSError``
        when supplied; otherwise the branch is skipped.
        """
        try:
            directory.relative_to(self._base_dir)
        except ValueError as exc:
            raise WorkspacePathError(
                "path_outside_base_dir",
                f"resolved path escapes the allowed workspace directory: {directory}",
            ) from exc

        if not recursive:
            for child in sorted(directory.iterdir(), key=lambda p: p.name):
                if not include_hidden and child.name.startswith("."):
                    continue
                yield child
            return

        def handle_error(exc: OSError) -> None:
            if on_error is not None:
                on_error(exc)

        for root, dirnames, filenames in os.walk(
            directory,
            onerror=handle_error,
            followlinks=follow_symlinks,
        ):
            root_path = Path(root)
            dirnames.sort()
            filenames.sort()

            if not include_hidden:
                dirnames[:] = [name for name in dirnames if not name.startswith(".")]
                filenames[:] = [name for name in filenames if not name.startswith(".")]

            safe_dirnames = []
            for name in dirnames:
                candidate = root_path / name
                if candidate.is_symlink() and not follow_symlinks:
                    yield candidate
                    continue
                try:
                    candidate.resolve().relative_to(self._base_dir)
                except ValueError:
                    continue
                safe_dirnames.append(name)
                yield candidate
            dirnames[:] = safe_dirnames

            for name in filenames:
                candidate = root_path / name
                if candidate.is_symlink() and not follow_symlinks:
                    yield candidate
                    continue
                try:
                    candidate.resolve().relative_to(self._base_dir)
                except ValueError:
                    continue
                yield candidate
