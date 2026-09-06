"""Read-only web content fetching tool."""

from __future__ import annotations

from typing import Union
from pathlib import Path

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult
from ..workspace import Workspace, WorkspacePathError

DEFAULT_MAX_RESPONSE_BYTES = 1_048_576  # 1 MiB
DEFAULT_TIMEOUT_SECONDS = 30


class FetchWebHandler:
    """Fetches web content from a URL."""

    TOOL_NAME = "fetch_web"

    def __init__(
        self,
        base_dir: Union[str, Path],
        *,
        max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._workspace = Workspace(base_dir)
        self._base_dir = self._workspace.base_dir
        if not isinstance(max_response_bytes, int) or max_response_bytes <= 0:
            raise ValueError("max_response_bytes must be a positive integer")
        if not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive integer")

        self._max_response_bytes = max_response_bytes
        self._timeout_seconds = timeout_seconds
        self._definition = ToolDefinition(
            name=self.TOOL_NAME,
            description=(
                "Fetches content from a web URL. Returns text content and metadata. "
                "Read-only. Respects robots.txt and standard HTTP headers."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {"type": "string", "description": "The URL to fetch."},
                    "headers": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                        "description": "Optional HTTP headers to include in the request.",
                    },
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "status_code": {"type": "integer"},
                    "content": {"type": "string"},
                    "content_type": {"type": "string"},
                    "size_bytes": {"type": "integer"},
                    "encoding": {"type": "string"},
                },
            },
            risk_level=RiskLevel.LOW,
            requires_confirmation=False,
            metadata={"category": "web", "read_only": True},
        )

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest) -> ToolResult:
        import urllib.request
        import urllib.error
        from urllib.parse import urlparse

        raw_url = request.arguments.get("url")
        if not isinstance(raw_url, str) or not raw_url.strip():
            return self._failure(request, "invalid_argument", "argument 'url' must be a non-empty string")

        parsed = urlparse(raw_url)
        if not parsed.scheme or not parsed.netloc:
            return self._failure(request, "invalid_argument", "argument 'url' must be a valid absolute URL")

        if parsed.scheme not in ("http", "https"):
            return self._failure(request, "invalid_argument", "only http and https URLs are supported")

        headers = request.arguments.get("headers", {})
        if not isinstance(headers, dict):
            return self._failure(request, "invalid_argument", "argument 'headers' must be an object")

        try:
            req = urllib.request.Request(raw_url, headers=headers)
            with urllib.request.urlopen(req, timeout=self._timeout_seconds) as response:
                content = response.read(self._max_response_bytes + 1)

                if len(content) > self._max_response_bytes:
                    return self._failure(
                        request,
                        "response_too_large",
                        f"response is {len(content)} bytes, exceeds the {self._max_response_bytes} byte limit for this tool",
                    )

                content_type = response.getheader("Content-Type", "") or ""
                encoding = self._extract_encoding(content_type)

                try:
                    text_content = content.decode(encoding)
                except (UnicodeDecodeError, LookupError):
                    try:
                        text_content = content.decode("utf-8")
                    except UnicodeDecodeError:
                        try:
                            text_content = content.decode("latin-1")
                        except Exception:
                            text_content = str(content)

                return ToolResult(
                    success=True,
                    tool_name=self.TOOL_NAME,
                    content={
                        "url": raw_url,
                        "status_code": response.status,
                        "content": text_content,
                        "content_type": content_type,
                        "size_bytes": len(content),
                        "encoding": encoding,
                    },
                    invocation_id=request.invocation_id,
                )

        except urllib.error.HTTPError as exc:
            return self._failure(request, "http_error", f"HTTP {exc.code}: {exc.reason}")
        except urllib.error.URLError as exc:
            return self._failure(request, "url_error", f"URL error: {exc.reason}")
        except TimeoutError:
            return self._failure(request, "timeout", f"request timed out after {self._timeout_seconds} seconds")
        except Exception as exc:
            return self._failure(request, "fetch_error", f"failed to fetch URL: {exc}")

    def _extract_encoding(self, content_type: str) -> str:
        """Extract encoding from Content-Type header."""
        if "charset=" in content_type.lower():
            parts = content_type.split("charset=")
            if len(parts) > 1:
                encoding = parts[1].strip().split(";")[0].strip()
                return encoding
        return "utf-8"

    def _failure(self, request: ToolRequest, code: str, message: str) -> ToolResult:
        return ToolResult(
            success=False,
            tool_name=self.TOOL_NAME,
            error=ToolError(code=code, message=message),
            invocation_id=request.invocation_id,
        )
