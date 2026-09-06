"""Confirmation-gated file deletion tool confined to a shared workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult
from ..workspace import Workspace, WorkspacePathError


class DeleteFileHandler:
    """Deletes a file within the tool's configured workspace directory."""

    TOOL_NAME = "delete_file"

    def __init__(self, base_dir: Union[str, Path]) -> None:
        self._workspace = Workspace(base_dir)
        self._base_dir = self._workspace.base_dir
        self._definition = ToolDefinition(
            name=self.TOOL_NAME,
            description=(
                "Deletes a file from the tool's configured workspace directory. "
                "This is a destructive operation and requires confirmation."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {"type": "string", "description": "Path to the file to delete, relative to the workspace."},
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "deleted": {"type": "boolean"},
                },
            },
            risk_level=RiskLevel.CRITICAL,
            requires_confirmation=True,
            metadata={"category": "filesystem", "read_only": False},
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

        if not candidate.exists():
            return self._failure(request, "file_not_found", f"no such file: {raw_path}")
        if not candidate.is_file():
            return self._failure(request, "not_a_file", f"path is not a regular file: {raw_path}")

        try:
            self._workspace.ensure_within(candidate.parent, display_path=raw_path)
        except WorkspacePathError as exc:
            return self._failure(request, exc.code, exc.message)

        try:
            candidate.unlink()
        except OSError as exc:
            code, message = self._workspace.runtime_error(exc)
            return self._failure(request, code, message)

        return ToolResult(
            success=True,
            tool_name=self.TOOL_NAME,
            content={
                "path": self._workspace.relative_path(candidate),
                "deleted": True,
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
