"""``write_file``: a confirmation-gated workspace write tool.

Unlike the read-only filesystem tools, writing changes user data, so this
handler declares HIGH risk and requires confirmation. The handler itself
only implements the write operation; the Policy/Confirmation/Executor
layers decide whether and when the operation may run.

Safety properties:
    * requests are confined to a fixed workspace directory
    * absolute paths are rejected
    * resolved paths must remain inside the workspace, including symlink
      resolution for existing targets/parents
    * overwriting is disabled by default
    * parent directory creation is disabled by default
    * writes are UTF-8 and text-only
    * file size is bounded before the write
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult

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
        resolved_base = Path(base_dir).resolve()
        if not resolved_base.is_dir():
            raise ValueError(f"base_dir must be an existing directory, got: {base_dir!r}")
        if not isinstance(max_file_size_bytes, int) or max_file_size_bytes <= 0:
            raise ValueError("max_file_size_bytes must be a positive integer")

        self._base_dir = resolved_base
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
                    "path": {
                        "type": "string",
                        "description": "Path to the target file, relative to the workspace.",
                    },
                    "content": {
                        "type": "string",
                        "description": "UTF-8 text to write to the target file.",
                    },
                    "overwrite": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether an existing file may be replaced.",
                    },
                    "create_parents": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether missing parent directories may be created.",
                    },
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
            return self._failure(
                request, "invalid_argument", "argument 'path' must be a non-empty string"
            )

        content = request.arguments.get("content")
        if not isinstance(content, str):
            return self._failure(
                request, "invalid_argument", "argument 'content' must be a string"
            )

        overwrite = request.arguments.get("overwrite", False)
        if not isinstance(overwrite, bool):
            return self._failure(
                request, "invalid_argument", "argument 'overwrite' must be a boolean"
            )

        create_parents = request.arguments.get("create_parents", False)
        if not isinstance(create_parents, bool):
            return self._failure(
                request,
                "invalid_argument",
                "argument 'create_parents' must be a boolean",
            )

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

        requested = Path(raw_path)
        if requested.is_absolute():
            return self._failure(
                request,
                "path_outside_base_dir",
                "absolute paths are not allowed; provide a path relative to the tool's workspace directory",
            )

        candidate = (self._base_dir / requested).resolve()
        try:
            candidate.relative_to(self._base_dir)
        except ValueError:
            return self._failure(
                request,
                "path_outside_base_dir",
                f"resolved path escapes the allowed workspace: {raw_path}",
            )

        target_existed = candidate.exists()
        if target_existed and not candidate.is_file():
            return self._failure(
                request, "not_a_file", f"target path is not a regular file: {raw_path}"
            )

        if target_existed and not overwrite:
            return self._failure(
                request,
                "file_exists",
                f"file already exists and overwrite is false: {raw_path}",
            )

        parent = candidate.parent
        if not parent.exists():
            if not create_parents:
                return self._failure(
                    request,
                    "parent_not_found",
                    f"parent directory does not exist: {parent.relative_to(self._base_dir).as_posix()}",
                )
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                return self._failure(request, "io_error", str(exc))

        try:
            parent.resolve().relative_to(self._base_dir)
        except ValueError:
            return self._failure(
                request,
                "path_outside_base_dir",
                f"resolved parent directory escapes the allowed workspace: {raw_path}",
            )

        try:
            candidate.write_text(content, encoding="utf-8", newline="")
        except OSError as exc:
            return self._failure(request, "io_error", str(exc))

        return ToolResult(
            success=True,
            tool_name=self.TOOL_NAME,
            content={
                "path": requested.as_posix(),
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
