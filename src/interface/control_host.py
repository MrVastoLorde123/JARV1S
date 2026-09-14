"""Process bootstrap for the runtime-owned control-plane transport."""
from __future__ import annotations

from dataclasses import dataclass
from threading import Thread

from src.core.jarvis_runtime import JARVISRuntime
from src.core.runtime_activity_stream import RuntimeActivityStream

from .control_plane import ControlPlaneSnapshotBuilder
from .http_control_plane import ControlPlaneHTTPConfig, create_control_plane_server


@dataclass
class ControlPlaneHostHandle:
    server: object
    thread: Thread

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2.0)


def start_control_plane_http(
    runtime: JARVISRuntime,
    *,
    activity_stream: RuntimeActivityStream,
    config: ControlPlaneHTTPConfig | None = None,
) -> ControlPlaneHostHandle:
    if not isinstance(runtime, JARVISRuntime):
        raise TypeError("runtime must be a JARVISRuntime")
    if type(activity_stream) is not RuntimeActivityStream:
        raise TypeError("activity_stream must be a RuntimeActivityStream")

    def world_supplier():
        if runtime.world_runtime is None:
            return {"available": False}
        return runtime.observe_world().to_context()

    builder = ControlPlaneSnapshotBuilder(
        world_supplier=world_supplier,
        activity_stream=activity_stream,
        task_supplier=lambda: {"state": "UNKNOWN", "source": "runtime_boundary_pending"},
        agents_supplier=lambda: (),
        approvals_supplier=lambda: (),
        tools_supplier=lambda: (),
        model_supplier=lambda: {"provider": "local", "state": "AVAILABLE"},
        blockers_supplier=lambda: (),
        verification_supplier=lambda: {"state": "NOT_REPORTED", "evidence": []},
    )
    server = create_control_plane_server(
        builder,
        config=config or ControlPlaneHTTPConfig(port=8768),
    )
    thread = Thread(
        target=server.serve_forever,
        name="jarvis-control-plane-http",
        daemon=True,
    )
    thread.start()
    return ControlPlaneHostHandle(server=server, thread=thread)


__all__ = ["ControlPlaneHostHandle", "start_control_plane_http"]
