"""Process bootstrap for the M28 capability catalog transport."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Thread

from .http_capabilities import CapabilityHTTPConfig, create_capability_server


@dataclass
class CapabilityHostHandle:
    server: object
    thread: Thread

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2.0)


def start_capability_http(
    source,
    *,
    config: CapabilityHTTPConfig | None = None,
) -> CapabilityHostHandle:
    server = create_capability_server(source, config=config)
    thread = Thread(
        target=server.serve_forever,
        name="jarvis-capability-http",
        daemon=True,
    )
    thread.start()
    return CapabilityHostHandle(server=server, thread=thread)


__all__ = ["CapabilityHostHandle", "start_capability_http"]
