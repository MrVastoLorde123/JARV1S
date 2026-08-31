"""Shared workspace boundary for filesystem-backed tools.

The workspace owns only the common filesystem safety boundary: one resolved
base directory and safe resolution of request-relative paths. Individual
handlers remain responsible for their own capability semantics, limits,
and result schemas.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union


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
