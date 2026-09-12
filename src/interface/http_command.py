"""M28 command transport for the canonical JARVIS runtime.

The browser sends plain interface content into JARVISRuntime.receive(). This
module owns transport only; interpretation, authority, authorization, and any
future execution remain backend-owned.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from uuid import uuid4

from src.core.jarvis_runtime import JARVISRuntime
from src.interface.boundary import InterfaceChannel


@dataclass(frozen=True)
class CommandHTTPConfig:
    host: str = "127.0.0.1"
    port: int = 8766
    path: str = "/api/command"
    allow_origin: str = "http://localhost:5173"
    max_body_bytes: int = 16_384

    def __post_init__(self) -> None:
        if not isinstance(self.host, str) or not self.host.strip():
            raise ValueError("host must be a non-empty string")
        if not isinstance(self.port, int) or isinstance(self.port, bool) or not 1 <= self.port <= 65535:
            raise ValueError("port must be an integer from 1 to 65535")
        if not isinstance(self.path, str) or not self.path.startswith("/"):
            raise ValueError("path must start with '/'")
        if not isinstance(self.allow_origin, str) or not self.allow_origin.strip():
            raise ValueError("allow_origin must be a non-empty string")
        if not isinstance(self.max_body_bytes, int) or isinstance(self.max_body_bytes, bool) or self.max_body_bytes < 1:
            raise ValueError("max_body_bytes must be a positive integer")


class _CommandHandler(BaseHTTPRequestHandler):
    server_version = "JARVISCommand/1.0"
    runtime: JARVISRuntime
    config: CommandHTTPConfig

    def do_OPTIONS(self) -> None:  # noqa: N802
        if self.path != self.config.path:
            self.send_error(404)
            return
        self.send_response(204)
        self._write_cors_headers()
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        if self.path != self.config.path:
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json_error(400, "Content-Length must be an integer")
            return

        if length < 1 or length > self.config.max_body_bytes:
            self._json_error(413, "request body is missing or too large")
            return

        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json_error(400, "request body must be valid UTF-8 JSON")
            return

        if not isinstance(payload, dict):
            self._json_error(400, "request body must be a JSON object")
            return

        content = payload.get("content")
        if not isinstance(content, str) or not content.strip():
            self._json_error(400, "content must be a non-empty string")
            return

        session_id = self.headers.get("X-JARVIS-Session-ID")
        request_id = self.headers.get("X-JARVIS-Request-ID") or f"command-{uuid4().hex}"

        try:
            result = self.runtime.receive(
                request_id=request_id,
                channel=InterfaceChannel.UI,
                content=content,
                session_id=session_id,
                metadata={"transport": "HTTP", "method": "POST"},
            )
            response = self.runtime.respond(result)
            body = response.to_json().encode("utf-8")
        except Exception as exc:  # pragma: no cover - transport safety boundary
            self._json_error(500, "JARVIS command processing failed", detail=str(exc))
            return

        self.send_response(200)
        self._write_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _json_error(self, status: int, message: str, *, detail: str | None = None) -> None:
        payload: dict[str, Any] = {"error": message}
        if detail is not None:
            payload["detail"] = detail
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self._write_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", self.config.allow_origin)
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-JARVIS-Request-ID, X-JARVIS-Session-ID")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Vary", "Origin")


def create_command_server(
    runtime: JARVISRuntime,
    *,
    config: CommandHTTPConfig | None = None,
) -> ThreadingHTTPServer:
    if not isinstance(runtime, JARVISRuntime):
        raise TypeError("runtime must be a JARVISRuntime")

    resolved_config = config or CommandHTTPConfig()
    handler_type = type("JARVISCommandHandler", (_CommandHandler,), {})
    handler_type.runtime = runtime
    handler_type.config = resolved_config
    return ThreadingHTTPServer((resolved_config.host, resolved_config.port), handler_type)


__all__ = ["CommandHTTPConfig", "create_command_server"]
