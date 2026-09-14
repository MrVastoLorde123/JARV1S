"""HTTP transport for the runtime-owned control-plane snapshot."""
from __future__ import annotations

import json
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from uuid import uuid4

from .control_plane import ControlPlaneSnapshotBuilder


@dataclass(frozen=True)
class ControlPlaneHTTPConfig:
    host: str = "127.0.0.1"
    port: int = 8768
    path: str = "/api/control-plane"
    allow_origin: str = "http://localhost:5173"

    def __post_init__(self) -> None:
        if not isinstance(self.host, str) or not self.host.strip():
            raise ValueError("host must be a non-empty string")
        # Port 0 is intentionally supported for OS-assigned ephemeral test servers.
        # The production/default transport remains pinned to 8768.
        if type(self.port) is not int or not 0 <= self.port <= 65535:
            raise ValueError("port must be an integer from 0 to 65535")
        if not isinstance(self.path, str) or not self.path.startswith("/"):
            raise ValueError("path must start with '/'")
        if not isinstance(self.allow_origin, str) or not self.allow_origin.strip():
            raise ValueError("allow_origin must be a non-empty string")


class _ControlPlaneHandler(BaseHTTPRequestHandler):
    server_version = "JARVISControlPlane/1.0"
    builder: ControlPlaneSnapshotBuilder
    config: ControlPlaneHTTPConfig

    def do_OPTIONS(self) -> None:  # noqa: N802
        if self.path.split("?", 1)[0] != self.config.path:
            self.send_error(404)
            return
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path, _, query = self.path.partition("?")
        if path != self.config.path:
            self.send_error(404)
            return
        params = _parse_query(query)
        try:
            after_cursor = int(params.get("after_cursor", "0"))
            limit = int(params.get("limit", "50"))
            snapshot = self.builder.build(after_cursor=after_cursor, limit=limit)
            body = snapshot.to_json().encode("utf-8")
        except Exception as exc:  # pragma: no cover - transport boundary
            body = json.dumps(
                {"error": "control-plane unavailable", "detail": str(exc)}
            ).encode("utf-8")
            self.send_response(500)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-JARVIS-Request-ID", self.headers.get("X-JARVIS-Request-ID") or f"control-{uuid4().hex}")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", self.config.allow_origin)
        self.send_header("Access-Control-Allow-Headers", "Accept, X-JARVIS-Request-ID, X-JARVIS-Session-ID")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Vary", "Origin")


def create_control_plane_server(
    builder: ControlPlaneSnapshotBuilder,
    *,
    config: ControlPlaneHTTPConfig | None = None,
) -> ThreadingHTTPServer:
    if type(builder) is not ControlPlaneSnapshotBuilder:
        raise TypeError("builder must be a ControlPlaneSnapshotBuilder")
    resolved = config or ControlPlaneHTTPConfig()
    handler_type = type("JARVISControlPlaneHandler", (_ControlPlaneHandler,), {})
    handler_type.builder = builder
    handler_type.config = resolved
    return ThreadingHTTPServer((resolved.host, resolved.port), handler_type)


def serve_control_plane(
    builder: ControlPlaneSnapshotBuilder,
    *,
    config: ControlPlaneHTTPConfig | None = None,
) -> None:
    server = create_control_plane_server(builder, config=config)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def _parse_query(query: str) -> dict[str, str]:
    from urllib.parse import parse_qs

    parsed = parse_qs(query, keep_blank_values=False)
    return {key: values[-1] for key, values in parsed.items() if values}


__all__ = ["ControlPlaneHTTPConfig", "create_control_plane_server", "serve_control_plane"]
