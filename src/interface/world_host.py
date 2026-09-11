"""M28.16 host-process bootstrap for the canonical JARVIS world transport.

This module owns only process wiring. It does not create world state, workers,
authority, execution, or persistence. A configured JARVISRuntime supplies the
read-only WorldObservation; this helper starts/stops the existing M28.14 HTTP
transport around that runtime-owned supplier.
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import Thread

from src.core.jarvis_runtime import JARVISRuntime

from .http_world import WorldObservationHTTPConfig, create_world_observation_server


@dataclass
class WorldHostHandle:
    """Running world HTTP host owned by the application process."""

    server: object
    thread: Thread

    def close(self) -> None:
        """Stop the HTTP server and wait briefly for the daemon thread."""
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2.0)


def start_world_http(
    runtime: JARVISRuntime,
    *,
    config: WorldObservationHTTPConfig | None = None,
) -> WorldHostHandle:
    """Start browser delivery for a runtime that has real world agency configured."""
    if not isinstance(runtime, JARVISRuntime):
        raise TypeError("runtime must be a JARVISRuntime")
    if runtime.world_runtime is None:
        raise RuntimeError(
            "JARVISRuntime has no AgentWorldRuntime configured; refusing to start "
            "the world transport without a real runtime-owned world producer."
        )

    server = create_world_observation_server(
        runtime.observe_world,
        config=config,
    )
    thread = Thread(
        target=server.serve_forever,
        name="jarvis-world-http",
        daemon=True,
    )
    thread.start()
    return WorldHostHandle(server=server, thread=thread)


__all__ = ["WorldHostHandle", "start_world_http"]
