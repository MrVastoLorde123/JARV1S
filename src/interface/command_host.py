"""Process bootstrap for the M28 browser command transport."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Thread

from src.core.jarvis_runtime import JARVISRuntime

from .http_command import CommandHTTPConfig, create_command_server


@dataclass
class CommandHostHandle:
    server: object
    thread: Thread

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2.0)


def start_command_http(
    runtime: JARVISRuntime,
    *,
    config: CommandHTTPConfig | None = None,
) -> CommandHostHandle:
    if not isinstance(runtime, JARVISRuntime):
        raise TypeError("runtime must be a JARVISRuntime")
    server = create_command_server(runtime, config=config)
    thread = Thread(
        target=server.serve_forever,
        name="jarvis-command-http",
        daemon=True,
    )
    thread.start()
    return CommandHostHandle(server=server, thread=thread)


__all__ = ["CommandHostHandle", "start_command_http"]
