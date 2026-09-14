"""Process bootstrap for the runtime-owned control-plane transport."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from threading import Thread
from urllib import error, request

from src.agency.agent_entity import AgentStatus
from src.agents.coding_confirmation import CodingAgentConfirmationService
from src.core.jarvis_runtime import JARVISRuntime
from src.core.runtime_activity_stream import RuntimeActivityStream
from src.tools.registry import ToolRegistry

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


def local_model_projection(
    *,
    base_url: str,
    model_id: str,
    opener=request.urlopen,
) -> dict[str, object]:
    """Return an evidence-backed local model/provider observation."""
    normalized_base = base_url.rstrip("/")
    normalized_model = model_id.strip() or "unknown"
    try:
        response_request = request.Request(
            f"{normalized_base}/v1/models",
            headers={"Accept": "application/json"},
            method="GET",
        )
        with opener(response_request, timeout=1) as response:
            payload = json.loads(response.read().decode("utf-8"))
        model_ids = tuple(
            str(item.get("id"))
            for item in payload.get("data", ())
            if isinstance(item, dict) and item.get("id")
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError, error.URLError):
        return {
            "provider": "local",
            "model": normalized_model,
            "state": "UNAVAILABLE",
            "observed_model_ids": (),
            "evidence": "local_server_models_unreachable",
        }

    if normalized_model in model_ids:
        state = "AVAILABLE"
    elif len(model_ids) == 1:
        state = "MODEL_MISMATCH"
    else:
        state = "UNAVAILABLE"

    return {
        "provider": "local",
        "model": normalized_model,
        "state": state,
        "observed_model_ids": model_ids,
        "evidence": "local_server_models_observed",
    }


def start_control_plane_http(
    runtime: JARVISRuntime,
    *,
    activity_stream: RuntimeActivityStream,
    tool_registry: ToolRegistry | None = None,
    confirmation_service: CodingAgentConfirmationService | None = None,
    config: ControlPlaneHTTPConfig | None = None,
) -> ControlPlaneHostHandle:
    if not isinstance(runtime, JARVISRuntime):
        raise TypeError("runtime must be a JARVISRuntime")
    if type(activity_stream) is not RuntimeActivityStream:
        raise TypeError("activity_stream must be a RuntimeActivityStream")
    if tool_registry is not None and type(tool_registry) is not ToolRegistry:
        raise TypeError("tool_registry must be a ToolRegistry or None")
    if confirmation_service is not None and type(confirmation_service) is not CodingAgentConfirmationService:
        raise TypeError("confirmation_service must be a CodingAgentConfirmationService or None")

    def world_supplier():
        if runtime.world_runtime is None:
            return {"available": False}
        return runtime.observe_world().to_context()

    def agents_supplier():
        if runtime.world_runtime is None:
            return ()
        return tuple(
            agent.to_context()
            for agent in runtime.world_runtime.agents
            if agent.status is not AgentStatus.RETIRED
        )

    def tools_supplier():
        if tool_registry is None:
            return ()
        return tuple(
            {
                "name": definition.name,
                "description": definition.description,
                "version": definition.version,
                "risk_level": definition.risk_level.value,
                "requires_confirmation": definition.requires_confirmation,
                "metadata": dict(definition.metadata),
            }
            for definition in tool_registry.list_definitions()
        )

    def approvals_supplier():
        if confirmation_service is None:
            return ()
        operation = confirmation_service.get_pending()
        if operation is None:
            return ()
        metadata = dict(operation.metadata)
        return (
            {
                "operation_id": operation.operation_id,
                "status": operation.status.value,
                "task_id": operation.task.task_id,
                "objective": operation.task.objective,
                "created_at": operation.created_at,
                "plan_fingerprint": metadata.get("plan_fingerprint"),
                "edit_count": len(operation.plan.edits),
                "verification_runner": operation.plan.verification.runner,
            },
        )

    def model_supplier():
        return local_model_projection(
            base_url=os.environ.get("JARVIS_LOCAL_BASE_URL", "http://127.0.0.1:8080"),
            model_id=os.environ.get("JARVIS_LOCAL_MODEL", "unknown"),
        )

    builder = ControlPlaneSnapshotBuilder(
        world_supplier=world_supplier,
        activity_stream=activity_stream,
        task_supplier=lambda: {"state": "NOT_REPORTED", "source": "task_projection_not_wired"},
        agents_supplier=agents_supplier,
        approvals_supplier=approvals_supplier,
        tools_supplier=tools_supplier,
        model_supplier=model_supplier,
        blockers_supplier=lambda: (),
        verification_supplier=lambda: {"state": "NOT_REPORTED", "evidence": []},
    )
    server = create_control_plane_server(
        builder,
        config=config or ControlPlaneHTTPConfig(),
    )
    thread = Thread(
        target=server.serve_forever,
        name="jarvis-control-plane-http",
        daemon=True,
    )
    thread.start()
    return ControlPlaneHostHandle(server=server, thread=thread)


__all__ = ["ControlPlaneHostHandle", "local_model_projection", "start_control_plane_http"]
