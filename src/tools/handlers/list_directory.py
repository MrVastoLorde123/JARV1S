"""Read-only directory listing tool confined to a shared workspace."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Union

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult
from ..workspace import Workspace, WorkspacePathError

DEFAULT_MAX_ENTRIES = 1000


class ListDirectoryHandler:
    """Lists the contents of a directory within a fixed workspace."""

    TOOL_NAME = "list_directory"

    def __init__(
        self,
        base_dir: Union[str, Path],
        *,
        max_entries: int = DEFAULT_MAX_ENTRIES,
    ) -> None:
        self._workspace = Workspace(base_dir)
        self._base_dir = self._workspace.base_dir
        if not isinstance(max_entries, int) or max_entries <= 0:
            raise ValueError("max_entries must be a positive integer")

        self._max_entries = max_entries
        self._definition = ToolDefinition(
            name=self.TOOL_NAME,
            description=(
                "Lists files and directories within the tool's configured workspace "
                "directory. Read-only; never follows symlinks out of the workspace."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": "."},
                    "recursive": {"type": "boolean", "default": False},
                    "include_hidden": {"type": "boolean", "default": False},
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "recursive": {"type": "boolean"},
                    "entries": {"type": "array"},
                    "truncated": {"type": "boolean"},
                    "errors": {"type": "array"},
                },
            },
            risk_level=RiskLevel.LOW,
            requires_confirmation=False,
            metadata={"category": "filesystem", "read_only": True},
        )

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest) -> ToolResult:
        raw_path = request.arguments.get("path", ".")
        if not isinstance(raw_path, str) or not raw_path.strip():
            return self._failure(request, "invalid_argument", "argument 'path' must be a non-empty string")

        recursive = request.arguments.get("recursive", False)
        if not isinstance(recursive, bool):
            return self._failure(request, "invalid_argument", "argument 'recursive' must be a boolean")

        include_hidden = request.arguments.get("include_hidden", False)
        if not isinstance(include_hidden, bool):
            return self._failure(request, "invalid_argument", "argument 'include_hidden' must be a boolean")

        try:
            candidate = self._workspace.resolve_path(raw_path)
        except WorkspacePathError as exc:
            return self._failure(request, exc.code, exc.message)

        if not candidate.exists():
            return self._failure(request, "directory_not_found", f"no such directory: {raw_path}")
        if not candidate.is_dir():
            return self._failure(request, "not_a_directory", f"path is not a directory: {raw_path}")

        try:
            entries, truncated, walk_errors = self._collect_entries(
                candidate, recursive=recursive, include_hidden=include_hidden
            )
        except OSError as exc:
            return self._failure(request, "io_error", str(exc))

        return ToolResult(
            success=True,
            tool_name=self.TOOL_NAME,
            content={
                "path": Path(raw_path).as_posix(),
                "recursive": recursive,
                "entries": entries,
                "truncated": truncated,
                "errors": walk_errors,
            },
            invocation_id=request.invocation_id,
        )

    def _collect_entries(
        self, target_dir: Path, *, recursive: bool, include_hidden: bool
    ) -> "tuple[List[Dict[str, object]], bool, List[Dict[str, str]]]":
        entries: List[Dict[str, object]] = []
        errors: List[Dict[str, str]] = []
        truncated = False

        for path in self._iter_paths(target_dir, recursive, include_hidden, errors):
            if len(entries) >= self._max_entries:
                truncated = True
                break
            entries.append(self._make_entry(path))

        entries.sort(key=lambda entry: entry["path"])
        return entries, truncated, errors

    def _iter_paths(
        self,
        target_dir: Path,
        recursive: bool,
        include_hidden: bool,
        errors: List[Dict[str, str]],
    ) -> Iterator[Path]:
        if not recursive:
            for child in sorted(target_dir.iterdir(), key=lambda p: p.name):
                if not include_hidden and child.name.startswith("."):
                    continue
                yield child
            return

        def on_walk_error(exc: OSError) -> None:
            errors.append({"path": getattr(exc, "filename", "") or "", "message": str(exc)})

        for root, dirnames, filenames in os.walk(
            target_dir, onerror=on_walk_error, followlinks=False
        ):
            root_path = Path(root)
            dirnames.sort()
            filenames.sort()
            if not include_hidden:
                dirnames[:] = [d for d in dirnames if not d.startswith(".")]
                filenames[:] = [f for f in filenames if not f.startswith(".")]
            for name in dirnames:
                yield root_path / name
            for name in filenames:
                yield root_path / name

    def _make_entry(self, path: Path) -> Dict[str, object]:
        relative_path = self._workspace.relative_path(path)
        size_bytes: Optional[int] = None

        if path.is_symlink():
            entry_type = "symlink"
        elif path.is_dir():
            entry_type = "directory"
        elif path.is_file():
            entry_type = "file"
            try:
                size_bytes = path.stat().st_size
            except OSError:
                size_bytes = None
        else:
            entry_type = "other"

        return {"name": path.name, "path": relative_path, "type": entry_type, "size_bytes": size_bytes}

    def _failure(self, request: ToolRequest, code: str, message: str) -> ToolResult:
        return ToolResult(
            success=False,
            tool_name=self.TOOL_NAME,
            error=ToolError(code=code, message=message),
            invocation_id=request.invocation_id,
        )
