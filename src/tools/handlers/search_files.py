"""Bounded, read-only text search within a fixed workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Union

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult
from ..workspace import Workspace, WorkspacePathError

DEFAULT_MAX_RESULTS = 100
DEFAULT_MAX_FILE_SIZE_BYTES = 1_048_576


class SearchFilesHandler:
    """Search text content in files below a fixed workspace directory."""

    TOOL_NAME = "search_files"

    def __init__(
        self,
        base_dir: Union[str, Path],
        *,
        max_results: int = DEFAULT_MAX_RESULTS,
        max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
    ) -> None:
        self._workspace = Workspace(base_dir)
        self._base_dir = self._workspace.base_dir
        if not isinstance(max_results, int) or max_results <= 0:
            raise ValueError("max_results must be a positive integer")
        if not isinstance(max_file_size_bytes, int) or max_file_size_bytes <= 0:
            raise ValueError("max_file_size_bytes must be a positive integer")

        self._max_results = max_results
        self._max_file_size_bytes = max_file_size_bytes
        self._definition = ToolDefinition(
            name=self.TOOL_NAME,
            description=(
                "Searches text content in files within the tool's configured "
                "workspace directory. Read-only; bounded and workspace-confined."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {"type": "string", "description": "Text to search for in file contents."},
                    "path": {"type": "string", "default": "."},
                    "recursive": {"type": "boolean", "default": True},
                    "case_sensitive": {"type": "boolean", "default": False},
                    "max_results": {"type": "integer", "description": "Maximum matching lines returned by this request."},
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "path": {"type": "string"},
                    "recursive": {"type": "boolean"},
                    "case_sensitive": {"type": "boolean"},
                    "matches": {"type": "array"},
                    "truncated": {"type": "boolean"},
                    "files_scanned": {"type": "integer"},
                    "files_skipped": {"type": "integer"},
                },
            },
            risk_level=RiskLevel.LOW,
            requires_confirmation=False,
            metadata={"category": "filesystem", "read_only": True},
        )

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest) -> ToolResult:
        raw_query = request.arguments.get("query")
        if not isinstance(raw_query, str) or not raw_query.strip():
            return self._failure(request, "invalid_argument", "argument 'query' must be a non-empty string")

        raw_path = request.arguments.get("path", ".")
        if not isinstance(raw_path, str) or not raw_path.strip():
            return self._failure(request, "invalid_argument", "argument 'path' must be a non-empty string")

        recursive = request.arguments.get("recursive", True)
        if not isinstance(recursive, bool):
            return self._failure(request, "invalid_argument", "argument 'recursive' must be a boolean")

        case_sensitive = request.arguments.get("case_sensitive", False)
        if not isinstance(case_sensitive, bool):
            return self._failure(request, "invalid_argument", "argument 'case_sensitive' must be a boolean")

        request_max_results = request.arguments.get("max_results", self._max_results)
        if not isinstance(request_max_results, int) or isinstance(request_max_results, bool) or request_max_results <= 0:
            return self._failure(request, "invalid_argument", "argument 'max_results' must be a positive integer")
        result_limit = min(request_max_results, self._max_results)

        try:
            candidate = self._workspace.resolve_path(raw_path)
        except WorkspacePathError as exc:
            return self._failure(request, exc.code, exc.message)

        if not candidate.exists():
            return self._failure(request, "path_not_found", f"no such path: {raw_path}")

        if candidate.is_file():
            files = iter((candidate,))
        elif candidate.is_dir():
            files = (
                path
                for path in self._workspace.iter_paths(
                    candidate,
                    recursive=recursive,
                    include_hidden=False,
                    follow_symlinks=False,
                )
                if path.is_file() and not path.is_symlink()
            )
        else:
            return self._failure(request, "unsupported_path", f"path is not a regular file or directory: {raw_path}")

        needle = raw_query if case_sensitive else raw_query.casefold()
        matches: List[Dict[str, object]] = []
        files_scanned = 0
        files_skipped = 0
        truncated = False

        for path in files:
            if len(matches) >= result_limit:
                truncated = True
                break
            try:
                size_bytes = path.stat().st_size
            except OSError:
                files_skipped += 1
                continue
            if size_bytes > self._max_file_size_bytes:
                files_skipped += 1
                continue

            files_scanned += 1
            try:
                with path.open("r", encoding="utf-8") as handle:
                    for line_number, line in enumerate(handle, start=1):
                        haystack = line if case_sensitive else line.casefold()
                        if needle in haystack:
                            matches.append({
                                "path": self._workspace.relative_path(path),
                                "line": line_number,
                                "text": line.rstrip("\r\n"),
                            })
                            if len(matches) >= result_limit:
                                truncated = True
                                break
            except (UnicodeDecodeError, OSError):
                files_skipped += 1

        return ToolResult(
            success=True,
            tool_name=self.TOOL_NAME,
            content={
                "query": raw_query,
                "path": Path(raw_path).as_posix(),
                "recursive": recursive,
                "case_sensitive": case_sensitive,
                "matches": matches,
                "truncated": truncated,
                "files_scanned": files_scanned,
                "files_skipped": files_skipped,
            },
            invocation_id=request.invocation_id,
        )

    def _failure(self, request: ToolRequest, code: str, message: str) -> ToolResult:
        return ToolResult(
            success=False,
            tool_name=self.TOOL_NAME,
            error=ToolError(code=code, message=message),
            invocation_id=request.invocation_id,
        )
