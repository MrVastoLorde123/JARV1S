"""Safe-by-default local verification capability.

This handler deliberately does not expose an arbitrary shell. It supports only
repository verification operations that map to known executable forms:

* Python unittest: ``python -m unittest <arguments...>`` from repository root
* npm build: ``npm run build`` from the repository's ``ui`` directory

JARVIS still reaches this handler through the normal tool policy, authorization,
sandbox, handoff, and execution-attempt layers.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from shutil import which
from typing import Union

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult


MAX_OUTPUT_CHARS = 64_000
DEFAULT_TIMEOUT_SECONDS = 120
MAX_TIMEOUT_SECONDS = 600


class TestRunnerHandler:
    """Run approved repository verification operations inside one workspace."""

    TOOL_NAME = "run_test"

    def __init__(
        self,
        base_dir: Union[str, Path],
        *,
        default_timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._base_dir = Path(base_dir).resolve()
        if not self._base_dir.is_dir():
            raise ValueError("base_dir must point to an existing directory")
        if not isinstance(default_timeout_seconds, int) or isinstance(default_timeout_seconds, bool):
            raise TypeError("default_timeout_seconds must be an integer")
        if not 1 <= default_timeout_seconds <= MAX_TIMEOUT_SECONDS:
            raise ValueError(
                f"default_timeout_seconds must be between 1 and {MAX_TIMEOUT_SECONDS}"
            )

        self._default_timeout_seconds = default_timeout_seconds
        self._definition = ToolDefinition(
            name=self.TOOL_NAME,
            description=(
                "Runs a constrained repository verification operation. Supported operations are "
                "Python unittest or npm build. Arbitrary shell commands are not accepted."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["runner"],
                "properties": {
                    "runner": {
                        "type": "string",
                        "enum": ["python_unittest", "npm_build"],
                    },
                    "arguments": {
                        "type": "array",
                    },
                    "timeout_seconds": {
                        "type": "integer",
                    },
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "runner": {"type": "string"},
                    "command": {"type": "array"},
                    "cwd": {"type": "string"},
                    "exit_code": {"type": "integer"},
                    "stdout": {"type": "string"},
                    "stderr": {"type": "string"},
                    "timed_out": {"type": "boolean"},
                    "duration_seconds": {"type": "number"},
                },
            },
            risk_level=RiskLevel.MEDIUM,
            requires_confirmation=False,
            metadata={
                "category": "verification",
                "read_only": False,
                "workspace_scoped": True,
            },
        )

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest) -> ToolResult:
        runner = request.arguments.get("runner")
        if runner not in {"python_unittest", "npm_build"}:
            return self._failure(
                request,
                "invalid_runner",
                "runner must be 'python_unittest' or 'npm_build'",
            )

        arguments = request.arguments.get("arguments", [])
        if not isinstance(arguments, (list, tuple)) or any(not isinstance(item, str) for item in arguments):
            return self._failure(
                request,
                "invalid_arguments",
                "arguments must be an array of strings",
            )

        timeout_value = request.arguments.get(
            "timeout_seconds",
            self._default_timeout_seconds,
        )
        if not isinstance(timeout_value, int) or isinstance(timeout_value, bool):
            return self._failure(
                request,
                "invalid_timeout",
                "timeout_seconds must be an integer",
            )
        if not 1 <= timeout_value <= MAX_TIMEOUT_SECONDS:
            return self._failure(
                request,
                "invalid_timeout",
                f"timeout_seconds must be between 1 and {MAX_TIMEOUT_SECONDS}",
            )

        command = self._build_command(runner, tuple(arguments))
        if isinstance(command, str):
            return self._failure(request, "invalid_arguments", command)

        cwd = self._working_directory(runner)
        if isinstance(cwd, str):
            return self._failure(request, "workspace_error", cwd)

        started = time.monotonic()
        timed_out = False
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=False,
                timeout=timeout_value,
                check=False,
            )
            exit_code = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            exit_code = None
            stdout = self._coerce_output(exc.stdout)
            stderr = self._coerce_output(exc.stderr)
        except OSError as exc:
            return self._failure(
                request,
                "process_start_error",
                str(exc) or exc.__class__.__name__,
            )

        duration = round(time.monotonic() - started, 3)
        content = {
            "runner": runner,
            "command": list(command),
            "cwd": str(cwd),
            "exit_code": exit_code,
            "stdout": self._truncate(stdout),
            "stderr": self._truncate(stderr),
            "timed_out": timed_out,
            "duration_seconds": duration,
        }

        if timed_out:
            return ToolResult(
                success=False,
                tool_name=self.TOOL_NAME,
                content=content,
                error=ToolError(
                    code="timeout",
                    message=f"verification command exceeded {timeout_value} second(s)",
                    details=content,
                ),
                invocation_id=request.invocation_id,
            )

        if exit_code != 0:
            return ToolResult(
                success=False,
                tool_name=self.TOOL_NAME,
                content=content,
                error=ToolError(
                    code="verification_failed",
                    message=f"verification command exited with code {exit_code}",
                    details=content,
                ),
                invocation_id=request.invocation_id,
            )

        return ToolResult(
            success=True,
            tool_name=self.TOOL_NAME,
            content=content,
            invocation_id=request.invocation_id,
        )

    def _working_directory(self, runner: str) -> Path | str:
        if runner == "python_unittest":
            return self._base_dir

        ui_dir = self._base_dir / "ui"
        if not ui_dir.is_dir():
            return f"UI workspace does not exist: {ui_dir}"
        return ui_dir

    @staticmethod
    def _build_command(runner: str, arguments: tuple[str, ...]) -> list[str] | str:
        if runner == "python_unittest":
            if len(arguments) < 2 or arguments[0] != "-m" or arguments[1] != "unittest":
                return "python_unittest requires arguments beginning with '-m', 'unittest'"
            return [sys.executable, *arguments]

        if runner == "npm_build":
            if arguments:
                return "npm_build does not accept arguments; it always runs 'npm run build'"
            executable = "npm.cmd" if os.name == "nt" else "npm"
            if which(executable) is None:
                return f"could not locate executable: {executable}"
            return [executable, "run", "build"]

        return f"unsupported runner: {runner}"

    @staticmethod
    def _truncate(value: str) -> str:
        if len(value) <= MAX_OUTPUT_CHARS:
            return value
        return value[:MAX_OUTPUT_CHARS] + "\n...[output truncated]"

    @staticmethod
    def _coerce_output(value: object) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return str(value)

    def _failure(self, request: ToolRequest, code: str, message: str) -> ToolResult:
        return ToolResult(
            success=False,
            tool_name=self.TOOL_NAME,
            error=ToolError(code=code, message=message),
            invocation_id=request.invocation_id,
        )


__all__ = ["TestRunnerHandler"]
