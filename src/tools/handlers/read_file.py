"""``read_file``: the first real tool implementation.

This is deliberately the *first* real tool because it is read-only and
LOW risk -- it exists to validate the full stack

    ToolDefinition -> ToolRegistry -> PolicyGate -> Policy ->
    Confirmation -> ToolService -> ToolHandler -> ToolResult

against something concrete before any tool that writes, deletes, or
executes anything is attempted.

Safety note on "LOW risk": reading a file is non-destructive, so it is
correctly classified LOW under the risk model in ``models.py``
(destructive potential is what that scale is tracking). It is not,
however, *harmless* -- an unconstrained read tool can exfiltrate
secrets or traverse outside the intended workspace. This handler
therefore enforces its own safety independent of the confirmation
boundary:

    * every request is confined to a single ``base_dir``, resolved
      once at construction time
    * the requested path is resolved and checked to still be inside
      ``base_dir`` *after* resolution, which also defends against
      symlinks that point outside it
    * absolute paths are rejected outright
    * files above ``max_file_size_bytes`` are rejected rather than
      read into memory

None of this is a substitute for the policy/confirmation layer -- it
is the handler's own responsibility for the specific capability it
grants, per "every tool must have a declared risk classification" and
the general principle that handlers execute, they don't decide *when*
they run, but they are still responsible for the safety of *what they
do* once asked to run.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult

DEFAULT_MAX_FILE_SIZE_BYTES = 1_048_576  # 1 MiB


class ReadFileHandler:
    """Reads a UTF-8 (by default) text file from within a fixed base directory."""

    TOOL_NAME = "read_file"

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
                "Reads a text file's contents from within the tool's configured "
                "workspace directory. Read-only; cannot write, delete, or execute "
                "anything."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Path to the file, relative to the tool's workspace "
                            "directory. Absolute paths and paths that resolve "
                            "outside the workspace are rejected."
                        ),
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
            return self._failure(
                request, "invalid_argument", "argument 'path' must be a non-empty string"
            )

        encoding = request.arguments.get("encoding", "utf-8")
        if not isinstance(encoding, str) or not encoding.strip():
            return self._failure(
                request, "invalid_argument", "argument 'encoding' must be a non-empty string"
            )

        requested = Path(raw_path)
        if requested.is_absolute():
            return self._failure(
                request,
                "path_outside_base_dir",
                "absolute paths are not allowed; provide a path relative to the "
                "tool's workspace directory",
            )

        candidate = (self._base_dir / requested).resolve()
        try:
            candidate.relative_to(self._base_dir)
        except ValueError:
            return self._failure(
                request,
                "path_outside_base_dir",
                f"resolved path escapes the allowed workspace directory: {raw_path}",
            )

        if not candidate.exists():
            return self._failure(request, "file_not_found", f"no such file: {raw_path}")
        if not candidate.is_file():
            return self._failure(
                request, "not_a_file", f"path is not a regular file: {raw_path}"
            )

        try:
            size_bytes = candidate.stat().st_size
        except OSError as exc:
            return self._failure(request, "io_error", str(exc))

        if size_bytes > self._max_file_size_bytes:
            return self._failure(
                request,
                "file_too_large",
                f"file is {size_bytes} bytes, exceeds the {self._max_file_size_bytes} "
                "byte limit for this tool",
            )

        try:
            content = candidate.read_text(encoding=encoding)
        except UnicodeDecodeError as exc:
            return self._failure(
                request, "decode_error", f"could not decode file as {encoding!r}: {exc}"
            )
        except OSError as exc:
            return self._failure(request, "io_error", str(exc))

        return ToolResult(
            success=True,
            tool_name=self.TOOL_NAME,
            content={
                "path": requested.as_posix(),
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
