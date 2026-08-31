"""Confirmation-gated text-file write tool confined to a shared workspace."""

from __future__ import annotations

from typing import Union
from pathlib import Path

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult
from ..workspace import Workspace, WorkspacePathError

DEFAULT_MAX_FILE_SIZE_BYTES = 1_048_576  # 1 MiB


class WriteFileHandler:
    """Write UTF-8 text into a fixed workspace directory."""

    TOOL_NAME = "write_file"

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
                "Writes UTF-8 text to a file within the tool's configured workspace. "
                "Overwriting existing files and creating missing parent directories "
                "are opt-in. This tool changes filesystem state and requires confirmation."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["path", "content"],
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                    "overwrite": {"type": "boolean", "default": False},
                    "create_parents": {"type": "boolean", "default": False},
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "size_bytes": {"type": "integer"},
                    "overwritten": {"type": "boolean"},
                },
            },
            risk_level=RiskLevel.HIGH,
            requires_confirmation=True,
            metadata={"category": "filesystem", "read_only": False},
        )

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest) -> ToolResult:
        raw_path = request.arguments.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            return self._failure(request, "invalid_argument", "argument 'path' must be a non-empty string")

        content = request.arguments.get("content")
        if not isinstance(content, str):
            return self._failure(request, "invalid_argument", "argument 'content' must be a string")

        overwrite = request.arguments.get("overwrite", False)
        if not isinstance(overwrite, bool):
            return self._failure(request, "invalid_argument", "argument 'overwrite' must be a boolean")

        create_parents = request.arguments.get("create_parents", False)
        if not isinstance(create_parents, bool):
            return self._failure(request, "invalid_argument", "argument 'create_parents' must be a boolean")

        try:
            size_bytes = len(content.encode("utf-8"))
        except UnicodeEncodeError as exc:
            return self._failure(request, "encode_error", str(exc))

        if size_bytes > self._max_file_size_bytes:
            return self._failure(
                request,
                "content_too_large",
                f"content is {size_bytes} bytes, exceeds the {self._max_file_size_bytes} byte limit for this tool",
            )

        try:
            candidate = self._workspace.resolve_path(raw_path)
        except WorkspacePathError as exc:
            return self._failure(request, exc.code, exc.message)

        target_existed = candidate.exists()
        if target_existed and not candidate.is_file():
            return self._failure(request, "not_a_file", f"target path is not a regular file: {raw_path}")

        if target_existed and not overwrite:
            return self._failure(request, "file_exists", f"file already exists and overwrite is false: {raw_path}")

        parent = candidate.parent
        if not parent.exists():
            if not create_parents:
                return self._failure(
                    request,
                    "parent_not_found",
                    f"parent directory does not exist: {self._workspace.relative_path(parent)}",
                )
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                code, message = self._workspace.runtime_error(exc)
                return self._failure(request, code, message)

        try:
            self._workspace.ensure_within(parent, display_path=raw_path)
        except WorkspacePathError as exc:
            return self._failure(request, exc.code, exc.message)

        try:
            candidate.write_text(content, encoding="utf-8", newline="")
        except OSError as exc:
            code, message = self._workspace.runtime_error(exc)
            return self._failure(request, code, message)

        return ToolResult(
            success=True,
            tool_name=self.TOOL_NAME,
            content={
                "path": self._workspace.relative_path(candidate),
                "size_bytes": size_bytes,
                "overwritten": target_existed,
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
