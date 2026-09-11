"""M28.14 minimal browser transport for the canonical M11 world response.

This module adds delivery only. World state remains owned by the backend
WorldObservation and is serialized through the existing M28.13 M11 adapter.
The server is intentionally standard-library-only so it does not introduce a
new web framework or duplicate interface semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable
from uuid import uuid4

from src.agency.world_projection import WorldObservation

from .world_observation import WorldObservationInterfaceAdapter


WorldObservationSupplier = Callable[[], WorldObservation]


@dataclass(frozen=True)
class WorldObservationHTTPConfig:
    host: str = "127.0.0.1"
    port: int = 8765
    path: str = "/api/world/observation"
    allow_origin: str = "http://localhost:5173"

    def __post_init__(self) -> None:
        if not isinstance(self.host, str) or not self.host.strip():
            raise ValueError("host must be a non-empty string")
        if not isinstance(self.port, int) or isinstance(self.port, bool) or not 1 <= self.port <= 65535:
            raise ValueError("port must be an integer from 1 to 65535")
        if not isinstance(self.path, str) or not self.path.startswith("/"):
            raise ValueError("path must start with '/'")
        if not isinstance(self.allow_origin, str) or not self.allow_origin.strip():
            raise ValueError("allow_origin must be a non-empty string")


class _WorldObservationHandler(BaseHTTPRequestHandler):
    server_version = "JARVISWorld/1.0"
    observation_supplier: WorldObservationSupplier
    adapter: WorldObservationInterfaceAdapter
    config: WorldObservationHTTPConfig

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

        request_id = self.headers.get("X-JARVIS-Request-ID") or f"world-{uuid4().hex}"
        session_id = self.headers.get("X-JARVIS-Session-ID")

        try:
            observation = self.observation_supplier()
            response = self.adapter.snapshot(
                observation,
                request_id=request_id,
                session_id=session_id,
                metadata={"transport": "HTTP", "method": "GET"},
            )
            body = response.to_json().encode("utf-8")
        except Exception as exc:  # pragma: no cover - transport safety boundary
            body = (
                '{"error":"world observation unavailable",'
                f'"detail":{_json_string(str(exc))}}'
            ).encode("utf-8")
            self.send_response(500)
            self._write_cors_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
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

    def _write_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", self.config.allow_origin)
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-JARVIS-Request-ID, X-JARVIS-Session-ID")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Vary", "Origin")


def create_world_observation_server(
    observation_supplier: WorldObservationSupplier,
    *,
    config: WorldObservationHTTPConfig | None = None,
    adapter: WorldObservationInterfaceAdapter | None = None,
) -> ThreadingHTTPServer:
    """Create the concrete browser transport around an existing world supplier."""
    if not callable(observation_supplier):
        raise TypeError("observation_supplier must be callable")

    resolved_config = config or WorldObservationHTTPConfig()
    resolved_adapter = adapter or WorldObservationInterfaceAdapter()

    handler_type = type(
        "JARVISWorldObservationHandler",
        (_WorldObservationHandler,),
        {},
    )
    handler_type.observation_supplier = observation_supplier
    handler_type.adapter = resolved_adapter
    handler_type.config = resolved_config

    return ThreadingHTTPServer(
        (resolved_config.host, resolved_config.port),
        handler_type,
    )


def serve_world_observation(
    observation_supplier: WorldObservationSupplier,
    *,
    config: WorldObservationHTTPConfig | None = None,
    adapter: WorldObservationInterfaceAdapter | None = None,
) -> None:
    """Serve world snapshots until the host process stops the server."""
    server = create_world_observation_server(
        observation_supplier,
        config=config,
        adapter=adapter,
    )
    try:
        server.serve_forever()
    finally:
        server.server_close()


def _json_string(value: str) -> str:
    import json

    return json.dumps(value)


__all__ = [
    "WorldObservationHTTPConfig",
    "WorldObservationSupplier",
    "create_world_observation_server",
    "serve_world_observation",
]
