"""Confirmation-gated file copy tool confined to a shared workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult
from ..workspace import Workspace, WorkspacePathError

DEFAULT_MAX_FILE_SIZE_BYTES = 1_048_576  # 1 MiB


class CopyFileHandler:
    """Copies a file within the tool's configured workspace directory."""

    TOOL_NAME = "copy_file"

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
                "Copies a file to a destination path within the tool's configured "
                "workspace directory. Creates parent directories if requested. "
                "This tool changes filesystem state and requires confirmation."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["source_path", "destination_path"],
                "properties": {
                    "source_path": {"type": "string", "description": "Path to the source file relative to the workspace."},
                    "destination_path": {"type": "string", "description": "Path to the destination file relative to the workspace."},
                    "overwrite": {"type": "boolean", "default": False, "description": "Whether to overwrite an existing file at the destination."},
                    "create_parents": {"type": "boolean", "default": False, "description": "Whether to create missing parent directories for the destination."},
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "source_path": {"type": "string"},
                    "destination_path": {"type": "string"},
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
        raw_source_path = request.arguments.get("source_path")
        if not isinstance(raw_source_path, str) or not raw_source_path.strip():
            return self._failure(request, "invalid_argument", "argument 'source_path' must be a non-empty string")

        raw_destination_path = request.arguments.get("destination_path")
        if not isinstance(raw_destination_path, str) or not raw_destination_path.strip():
            return self._failure(request, "invalid_argument", "argument 'destination_path' must be a non-empty string")

        overwrite = request.arguments.get("overwrite", False)
        if not isinstance(overwrite, bool):
            return self._failure(request, "invalid_argument", "argument 'overwrite' must be a boolean")

        create_parents = request.arguments.get("create_parents", False)
        if not isinstance(create_parents, bool):
            return self._failure(request, "invalid_argument", "argument 'create_parents' must be a boolean")

        try:
            source = self._workspace.resolve_path(raw_source_path)
        except WorkspacePathError as exc:
            return self._failure(request, exc.code, exc.message)

        if not source.exists():
            return self._failure(request, "source_not_found", f"source file not found: {raw_source_path}")
        if not source.is_file():
            return self._failure(request, "not_a_file", f"source path is not a regular file: {raw_source_path}")

        try:
            size_bytes = source.stat().st_size
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
            destination = self._workspace.resolve_path(raw_destination_path)
        except WorkspacePathError as exc:
            return self._failure(request, exc.code, exc.message)

        destination_existed = destination.exists()
        if destination_existed and not destination.is_file():
            return self._failure(request, "not_a_file", f"destination path is not a regular file: {raw_destination_path}")

        if destination_existed and not overwrite:
            return self._failure(request, "file_exists", f"file already exists at destination and overwrite is false: {raw_destination_path}")

        parent = destination.parent
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
            self._workspace.ensure_within(parent, display_path=raw_destination_path)
        except WorkspacePathError as exc:
            return self._failure(request, exc.code, exc.message)

        try:
            with source.open("rb") as src_file:
                destination.write_bytes(src_file.read())
        except OSError as exc:
            code, message = self._workspace.runtime_error(exc)
            return self._failure(request, code, message)

        return ToolResult(
            success=True,
            tool_name=self.TOOL_NAME,
            content={
                "source_path": self._workspace.relative_path(source),
                "destination_path": self._workspace.relative_path(destination),
                "size_bytes": size_bytes,
                "overwritten": destination_existed,
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
