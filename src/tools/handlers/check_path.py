"""Read-only path existence and type checking tool confined to a shared workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult
from ..workspace import Workspace, WorkspacePathError


class CheckPathHandler:
    """Checks whether a path exists and what type it is within the workspace."""

    TOOL_NAME = "check_path"

    def __init__(self, base_dir: Union[str, Path]) -> None:
        self._workspace = Workspace(base_dir)
        self._base_dir = self._workspace.base_dir
        self._definition = ToolDefinition(
            name=self.TOOL_NAME,
            description=(
                "Checks whether a path exists and reports its type within the "
                "tool's configured workspace directory. Read-only."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {"type": "string", "description": "Path to check, relative to the workspace."},
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "exists": {"type": "boolean"},
                    "type": {"type": "string", "enum": ["file", "directory", "symlink", "other", "none"]},
                    "size_bytes": {"type": ["integer", "null"]},
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

        try:
            candidate = self._workspace.resolve_path(raw_path)
        except WorkspacePathError as exc:
            return self._failure(request, exc.code, exc.message)

        relative_path = self._workspace.relative_path(candidate)

        if not candidate.exists():
            return ToolResult(
                success=True,
                tool_name=self.TOOL_NAME,
                content={
                    "path": relative_path,
                    "exists": False,
                    "type": "none",
                    "size_bytes": None,
                },
                invocation_id=request.invocation_id,
            )

        size_bytes: int | None = None
        # Check if the original path (before resolving symlinks) was a symlink
        original_path = self._workspace.base_dir / raw_path
        if original_path.is_symlink():
            path_type = "symlink"
        elif candidate.is_dir():
            path_type = "directory"
        elif candidate.is_file():
            path_type = "file"
            try:
                size_bytes = candidate.stat().st_size
            except OSError:
                size_bytes = None
        else:
            path_type = "other"

        return ToolResult(
            success=True,
            tool_name=self.TOOL_NAME,
            content={
                "path": relative_path,
                "exists": True,
                "type": path_type,
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
