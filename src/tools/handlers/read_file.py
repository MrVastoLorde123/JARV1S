"""Read-only text-file tool confined to a shared workspace boundary."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult
from ..workspace import Workspace, WorkspacePathError

DEFAULT_MAX_FILE_SIZE_BYTES = 1_048_576  # 1 MiB


class ReadFileHandler:
    """Reads a UTF-8 (by default) text file from within a fixed workspace."""

    TOOL_NAME = "read_file"

    def __init__(
        self,
        base_dir: Union[str, Path],
        *,
        max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
    ) -> None:
        self._workspace = Workspace(base_dir)
        self._base_dir = self._workspace.base_dir  # compatibility for existing callers/tests
        if not isinstance(max_file_size_bytes, int) or max_file_size_bytes <= 0:
            raise ValueError("max_file_size_bytes must be a positive integer")

        self._max_file_size_bytes = max_file_size_bytes
        self._definition = ToolDefinition(
            name=self.TOOL_NAME,
            description=(
                "Reads a text file's contents from within the tool's configured "
                "workspace directory. Read-only; cannot write, delete, or execute anything."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file relative to the workspace.",
                    },
                    "encoding": {
                        "type": "string",
                        "description": "Text encoding to decode the file with.",
                        "default": "utf-8",
                    },
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                    "size_bytes": {"type": "integer"},
                },
            },
            risk_level=RiskLevel.LOW,
            requires_confirmation=False,
            metadata={"category": "filesystem", "read_only": True},
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
            return self._failure(request, "io_error", str(exc))

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
            return self._failure(request, "io_error", str(exc))

        return ToolResult(
            success=True,
            tool_name=self.TOOL_NAME,
            content={
                "path": Path(raw_path).as_posix(),
                "content": content,
                "size_bytes": size_bytes,
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
