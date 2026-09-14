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
from src.core.runtime_activity_stream import RuntimeActivityEvent, RuntimeActivityKind, RuntimeActivityStream
from src.tools.models import ToolResult
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
        if not isinstance(payload, dict) or not isinstance(payload.get("data", ()), list):
            raise ValueError("/v1/models response must contain a list-valued data field")
        model_ids = tuple(
            str(item.get("id"))
            for item in payload["data"]
            if isinstance(item, dict) and item.get("id")
        )
    except (OSError, ValueError, TypeError, error.URLError):
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


def _latest_coding_observation(activity_stream: RuntimeActivityStream) -> dict[str, object] | None:
    """Return only the latest sanitized coding-agent response metadata."""
    for event in reversed(activity_stream.snapshot()):
        if event.kind is not RuntimeActivityKind.RESPONSE_EMITTED:
            continue
        metadata = dict(event.metadata)
        if metadata.get("route") == "CODING_AGENT":
            return metadata
    return None


def _task_projection(activity_stream: RuntimeActivityStream) -> dict[str, object]:
    observation = _latest_coding_observation(activity_stream)
    if observation is None:
        return {"state": "NOT_REPORTED", "source": "coding_agent_response_not_observed"}

    stage = str(observation.get("stage", "UNKNOWN"))
    success = observation.get("success")
    if stage == "PLANNING":
        state = "PLANNING"
    elif stage == "CONFIRMATION":
        state = "WAITING_APPROVAL"
    elif stage == "EXECUTION":
        state = "COMPLETED" if success is True else "FAILED"
    else:
        state = "REPORTED"

    projection: dict[str, object] = {"state": state, "source": "coding_agent_response"}
    for key in (
        "task_id",
        "operation_id",
        "plan_fingerprint",
        "edit_count",
        "coding_status",
        "edits_attempted",
        "edits_applied",
        "blocked_tool",
    ):
        if key in observation:
            projection[key] = observation[key]
    if "success" in observation:
        projection["success"] = observation["success"]
    return projection


def _verification_projection(activity_stream: RuntimeActivityStream) -> dict[str, object]:
    """Expose bounded verification outcome/evidence, never raw verification logs."""
    observation = _latest_coding_observation(activity_stream)
    if observation is None or "verification" not in observation:
        return {"state": "NOT_REPORTED", "evidence": []}

    verification = observation.get("verification")
    if isinstance(verification, ToolResult):
        state = "PASSED" if verification.success else "FAILED"
        evidence: dict[str, object] = {
            "tool_name": verification.tool_name,
            "success": verification.success,
        }
        if verification.error is not None:
            evidence["error_code"] = verification.error.code
            evidence["error"] = verification.error.message
        return {"state": state, "evidence": [evidence]}

    if not isinstance(verification, dict):
        return {"state": "REPORTED", "evidence": []}

    state = verification.get("state") or verification.get("status")
    if state is None and "passed" in verification:
        state = "PASSED" if verification.get("passed") is True else "FAILED"
    if state is None and "success" in verification:
        state = "PASSED" if verification.get("success") is True else "FAILED"
    evidence = {
        key: verification[key]
        for key in ("runner", "exit_code", "passed", "error")
        if key in verification
    }
    return {"state": str(state or "REPORTED"), "evidence": [evidence] if evidence else []}


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
        task_supplier=lambda: _task_projection(activity_stream),
        agents_supplier=agents_supplier,
        approvals_supplier=approvals_supplier,
        tools_supplier=tools_supplier,
        model_supplier=model_supplier,
        blockers_supplier=lambda: (),
        verification_supplier=lambda: _verification_projection(activity_stream),
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
