"""Process bootstrap for the M28 browser command transport."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Thread

from src.core.jarvis_runtime import JARVISRuntime
from src.core.runtime_activity_stream import InterfaceRuntimeActivityRecorder

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
    activity_recorder: InterfaceRuntimeActivityRecorder | None = None,
) -> CommandHostHandle:
    if not isinstance(runtime, JARVISRuntime):
        raise TypeError("runtime must be a JARVISRuntime")
    if activity_recorder is not None and type(activity_recorder) is not InterfaceRuntimeActivityRecorder:
        raise TypeError("activity_recorder must be an InterfaceRuntimeActivityRecorder or None")
    server = create_command_server(runtime, config=config, activity_recorder=activity_recorder)
    thread = Thread(
        target=server.serve_forever,
        name="jarvis-command-http",
        daemon=True,
    )
    thread.start()
    return CommandHostHandle(server=server, thread=thread)


__all__ = ["CommandHostHandle", "start_command_http"]
