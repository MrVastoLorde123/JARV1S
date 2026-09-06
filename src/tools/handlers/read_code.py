"""Read-only code file reading tool with syntax highlighting support."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult
from ..workspace import Workspace, WorkspacePathError

DEFAULT_MAX_FILE_SIZE_BYTES = 1_048_576  # 1 MiB


class ReadCodeHandler:
    """Reads a code file's contents with optional syntax information."""

    TOOL_NAME = "read_code"

    def __init__(
        self,
        base_dir: Union[str, Path],
        *,
        max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
    ) -> None:
        self._workspace = Workspace(base_dir)
        self._base_dir = self._workspace.base_dir
        if not isinstance(max_file_size_bytes, int) or max_file_size_bytes <= 0:
            raise ValueError("max_file_size_bytes must be a positive integer")

        self._max_file_size_bytes = max_file_size_bytes
        self._definition = ToolDefinition(
            name=self.TOOL_NAME,
            description=(
                "Reads a code file's contents from within the tool's configured "
                "workspace directory. Returns content with line numbers and "
                "detected language information. Read-only."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {"type": "string", "description": "Path to the code file relative to the workspace."},
                    "encoding": {"type": "string", "default": "utf-8", "description": "Text encoding to decode the file with."},
                    "with_line_numbers": {"type": "boolean", "default": True, "description": "Whether to include line numbers in the output."},
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                    "size_bytes": {"type": "integer"},
                    "language": {"type": "string"},
                    "num_lines": {"type": "integer"},
                    "encoding": {"type": "string"},
                },
            },
            risk_level=RiskLevel.LOW,
            requires_confirmation=False,
            metadata={"category": "developer", "read_only": True},
        )

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest) -> ToolResult:
        raw_path = request.arguments.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            return self._failure(request, "invalid_argument", "argument 'path' must be a non-empty string")

        encoding = request.arguments.get("encoding", "utf-8")
        if not isinstance(encoding, str) or not encoding.strip():
            return self._failure(request, "invalid_argument", "argument 'encoding' must be a non-empty string")

        with_line_numbers = request.arguments.get("with_line_numbers", True)
        if not isinstance(with_line_numbers, bool):
            return self._failure(request, "invalid_argument", "argument 'with_line_numbers' must be a boolean")

        try:
            candidate = self._workspace.resolve_path(raw_path)
        except WorkspacePathError as exc:
            return self._failure(request, exc.code, exc.message)

        if not candidate.exists():
            return self._failure(request, "file_not_found", f"no such file: {raw_path}")
        if not candidate.is_file():
            return self._failure(request, "not_a_file", f"path is not a regular file: {raw_path}")

        try:
            size_bytes = candidate.stat().st_size
        except OSError as exc:
            code, message = self._workspace.runtime_error(exc)
            return self._failure(request, code, message)

        if size_bytes > self._max_file_size_bytes:
            return self._failure(
                request,
                "file_too_large",
                f"file is {size_bytes} bytes, exceeds the {self._max_file_size_bytes} byte limit for this tool",
            )

        try:
            content = candidate.read_text(encoding=encoding)
        except UnicodeDecodeError as exc:
            return self._failure(request, "decode_error", f"could not decode file as {encoding!r}: {exc}")
        except OSError as exc:
            code, message = self._workspace.runtime_error(exc)
            return self._failure(request, code, message)

        language = self._detect_language(candidate)
        num_lines = len(content.splitlines())

        if with_line_numbers:
            lines = content.splitlines()
            content_with_numbers = "\n".join(f"{i+1:4d} | {line}" for i, line in enumerate(lines))
            formatted_content = content_with_numbers
        else:
            formatted_content = content

        return ToolResult(
            success=True,
            tool_name=self.TOOL_NAME,
            content={
                "path": self._workspace.relative_path(candidate),
                "content": formatted_content,
                "size_bytes": size_bytes,
                "language": language,
                "num_lines": num_lines,
                "encoding": encoding,
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
