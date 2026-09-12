"""Read-only HTTP delivery for the active JARVIS tool capability catalog."""

from __future__ import annotations

import json
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Protocol

from src.tools.models import ToolDefinition


class CapabilitySource(Protocol):
    def list_definitions(self) -> tuple[ToolDefinition, ...]:
        ...


@dataclass(frozen=True)
class CapabilityHTTPConfig:
    host: str = "127.0.0.1"
    port: int = 8767
    path: str = "/api/capabilities"
    allow_origin: str = "http://localhost:5173"


class _CapabilityHandler(BaseHTTPRequestHandler):
    server_version = "JARVISCapabilities/1.0"
    source: CapabilitySource
    config: CapabilityHTTPConfig

    def do_OPTIONS(self) -> None:  # noqa: N802
        if self.path != self.config.path:
            self.send_error(404)
            return
        self.send_response(204)
        self._write_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path != self.config.path:
            self.send_error(404)
            return

        capabilities = []
        for definition in self.source.list_definitions():
            capabilities.append(
                {
                    "name": definition.name,
                    "description": definition.description,
                    "version": definition.version,
                    "risk_level": definition.risk_level.value,
                    "requires_confirmation": definition.requires_confirmation,
                    "metadata": dict(definition.metadata),
                    "authority_granted": False,
                    "execution_requested": False,
                }
            )

        body = json.dumps(
            {
                "schema": "m28.capabilities.v1",
                "capabilities": capabilities,
                "read_only": True,
                "authority_granted": False,
                "authorization_granted": False,
                "execution_requested": False,
            },
            sort_keys=True,
        ).encode("utf-8")

        self.send_response(200)
        self._write_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _write_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", self.config.allow_origin)
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-JARVIS-Request-ID, X-JARVIS-Session-ID")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Vary", "Origin")


def create_capability_server(
    source: CapabilitySource,
    *,
    config: CapabilityHTTPConfig | None = None,
) -> ThreadingHTTPServer:
    if not hasattr(source, "list_definitions") or not callable(source.list_definitions):
        raise TypeError("source must expose list_definitions()")

    resolved_config = config or CapabilityHTTPConfig()
    handler_type = type("JARVISCapabilityHandler", (_CapabilityHandler,), {})
    handler_type.source = source
    handler_type.config = resolved_config
    return ThreadingHTTPServer((resolved_config.host, resolved_config.port), handler_type)


__all__ = ["CapabilityHTTPConfig", "CapabilitySource", "create_capability_server"]
