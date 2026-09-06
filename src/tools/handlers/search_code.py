"""Read-only code search tool confined to a shared workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Union

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult
from ..workspace import Workspace, WorkspacePathError

DEFAULT_MAX_RESULTS = 100
DEFAULT_MAX_FILE_SIZE_BYTES = 1_048_576


class SearchCodeHandler:
    """Searches code content in files below a fixed workspace directory."""

    TOOL_NAME = "search_code"

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
                "Searches code content in files within the tool's configured "
                "workspace directory. Supports regex patterns. Read-only."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["pattern"],
                "properties": {
                    "pattern": {"type": "string", "description": "Regex pattern to search for in file contents."},
                    "path": {"type": "string", "default": "."},
                    "recursive": {"type": "boolean", "default": True},
                    "case_sensitive": {"type": "boolean", "default": False},
                    "include_extensions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file extensions to include (e.g., ['.py', '.js']). Includes all if not provided.",
                    },
                    "exclude_extensions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file extensions to exclude.",
                    },
                    "max_results": {"type": "integer", "description": "Maximum matching lines returned by this request."},
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
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
            metadata={"category": "developer", "read_only": True},
        )

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest) -> ToolResult:
        import re

        raw_pattern = request.arguments.get("pattern")
        if not isinstance(raw_pattern, str) or not raw_pattern.strip():
            return self._failure(request, "invalid_argument", "argument 'pattern' must be a non-empty string")

        raw_path = request.arguments.get("path", ".")
        if not isinstance(raw_path, str) or not raw_path.strip():
            return self._failure(request, "invalid_argument", "argument 'path' must be a non-empty string")

        recursive = request.arguments.get("recursive", True)
        if not isinstance(recursive, bool):
            return self._failure(request, "invalid_argument", "argument 'recursive' must be a boolean")

        case_sensitive = request.arguments.get("case_sensitive", False)
        if not isinstance(case_sensitive, bool):
            return self._failure(request, "invalid_argument", "argument 'case_sensitive' must be a boolean")

        include_extensions = request.arguments.get("include_extensions")
        if include_extensions is not None:
            if not isinstance(include_extensions, list):
                return self._failure(request, "invalid_argument", "argument 'include_extensions' must be a list")
            include_extensions = [str(e).lower() if isinstance(e, str) else str(e) for e in include_extensions]
        else:
            include_extensions = None

        exclude_extensions = request.arguments.get("exclude_extensions")
        if exclude_extensions is not None:
            if not isinstance(exclude_extensions, list):
                return self._failure(request, "invalid_argument", "argument 'exclude_extensions' must be a list")
            exclude_extensions = [str(e).lower() if isinstance(e, str) else str(e) for e in exclude_extensions]
        else:
            exclude_extensions = []

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

        try:
            pattern = re.compile(raw_pattern, flags=0 if case_sensitive else re.IGNORECASE)
        except re.error as exc:
            return self._failure(request, "invalid_pattern", f"invalid regex pattern: {exc}")

        matches: List[Dict[str, object]] = []
        files_scanned = 0
        files_skipped = 0
        truncated = False

        for path in files:
            if len(matches) >= result_limit:
                truncated = True
                break

            suffix = path.suffix.lower()
            if include_extensions and suffix not in include_extensions:
                files_skipped += 1
                continue
            if suffix in exclude_extensions:
                files_skipped += 1
                continue

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
                        if pattern.search(line):
                            matches.append({
                                "path": self._workspace.relative_path(path),
                                "line": line_number,
                                "text": line.rstrip("\r\n"),
                                "language": self._detect_language(path),
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
                "pattern": raw_pattern,
                "path": self._workspace.relative_path(candidate),
                "recursive": recursive,
                "case_sensitive": case_sensitive,
                "matches": matches,
                "truncated": truncated,
                "files_scanned": files_scanned,
                "files_skipped": files_skipped,
            },
            invocation_id=request.invocation_id,
        )

    def _detect_language(self, path: Path) -> str:
        """Detect the programming language from file extension."""
        extensions = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "bash",
            ".bash": "bash",
            ".zsh": "bash",
            ".html": "html",
            ".css": "css",
            ".sql": "sql",
            ".json": "json",
            ".xml": "xml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".md": "markdown",
            ".txt": "text",
        }
        suffix = path.suffix.lower()
        return extensions.get(suffix, "unknown")

    def _failure(self, request: ToolRequest, code: str, message: str) -> ToolResult:
        return ToolResult(
            success=False,
            tool_name=self.TOOL_NAME,
            error=ToolError(code=code, message=message),
            invocation_id=request.invocation_id,
        )
