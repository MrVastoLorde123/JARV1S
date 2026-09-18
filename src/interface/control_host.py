"""Process bootstrap for the runtime-owned control-plane transport."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from threading import Thread
from typing import Mapping
from urllib import error, request

from src.agency.agent_entity import AgentStatus
from src.agents.coding_confirmation import CodingAgentConfirmationService
from src.ai.errors import InvalidRequestError
from src.ai.model_routing import ModelRole
from src.ai.service import AIService
from src.core.jarvis_runtime import JARVISRuntime
from src.core.runtime_activity_stream import RuntimeActivityKind, RuntimeActivityStream
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


def local_model_projection(*, base_url: str, model_id: str, opener=request.urlopen) -> dict[str, object]:
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
        model_ids = tuple(str(item.get("id")) for item in payload["data"] if isinstance(item, dict) and item.get("id"))
    except (OSError, ValueError, TypeError, error.URLError):
        return {"provider": "local", "model": normalized_model, "state": "UNAVAILABLE", "observed_model_ids": (), "evidence": "local_server_models_unreachable"}

    if normalized_model in model_ids:
        state = "AVAILABLE"
    elif len(model_ids) == 1:
        state = "MODEL_MISMATCH"
    else:
        state = "UNAVAILABLE"

    return {"provider": "local", "model": normalized_model, "state": state, "observed_model_ids": model_ids, "evidence": "local_server_models_observed"}


def _model_routing_projection(*, ai_service: AIService, observation: Mapping[str, object]) -> dict[str, object]:
    """Project observed model inventory and deterministic role selection without execution."""
    observed_ids = tuple(item for item in observation.get("observed_model_ids", ()) if isinstance(item, str))
    if observed_ids:
        ai_service.observe_models(observed_ids)

    profiles = []
    for profile in ai_service.list_models():
        profiles.append(
            {
                "model_id": profile.model_id,
                "roles": tuple(role.value for role in profile.roles),
                "priority": profile.priority,
                "available": profile.available,
                "notes": profile.notes,
            }
        )

    selections: dict[str, object] = {}
    for role in ModelRole:
        try:
            decision = ai_service.route_model(role)
        except LookupError:
            selections[role.value] = {"state": "NO_AVAILABLE_MODEL"}
            continue
        selections[role.value] = {
            "state": "SELECTED",
            "model_id": decision.model_id,
            "reason": decision.reason,
            "candidates_considered": decision.candidates_considered,
        }

    return {
        "observed_model_ids": ai_service.observed_model_ids(),
        "profiles": tuple(profiles),
        "role_selections": selections,
        "routing_read_only": True,
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
    for key in ("task_id", "operation_id", "plan_fingerprint", "edit_count", "coding_status", "edits_attempted", "edits_applied", "blocked_tool"):
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
        evidence: dict[str, object] = {"tool_name": verification.tool_name, "success": verification.success}
        if verification.error is not None:
            evidence["error_code"] = verification.error.code
            evidence["error"] = verification.error.message
        return {"state": state, "evidence": [evidence]}

    if not isinstance(verification, Mapping):
        return {"state": "REPORTED", "evidence": []}

    state = verification.get("state") or verification.get("status")
    if state is None and "passed" in verification:
        state = "PASSED" if verification.get("passed") is True else "FAILED"
    if state is None and "success" in verification:
        state = "PASSED" if verification.get("success") is True else "FAILED"
    evidence = {key: verification[key] for key in ("runner", "exit_code", "passed", "error") if key in verification}
    return {"state": str(state or "REPORTED"), "evidence": [evidence] if evidence else []}


def _blockers_projection(activity_stream: RuntimeActivityStream) -> tuple[Mapping[str, object], ...]:
    """Project only explicitly observed execution blockers; never infer authority."""
    observation = _latest_coding_observation(activity_stream)
    if observation is None:
        return ()

    task_id = observation.get("task_id")
    operation_id = observation.get("operation_id")
    stage = str(observation.get("stage", "UNKNOWN"))
    blocked_tool = observation.get("blocked_tool")

    if blocked_tool:
        blocker: dict[str, object] = {"type": "TOOL_BLOCKED", "severity": "HIGH", "tool": blocked_tool, "source": "coding_agent_response"}
    elif stage == "CONFIRMATION":
        blocker = {"type": "AWAITING_APPROVAL", "severity": "MEDIUM", "source": "coding_agent_response"}
    elif stage == "EXECUTION" and observation.get("success") is False:
        blocker = {"type": "EXECUTION_FAILED", "severity": "HIGH", "source": "coding_agent_response"}
    else:
        verification = observation.get("verification")
        if isinstance(verification, Mapping):
            verification_failed = verification.get("passed") is False or verification.get("success") is False or verification.get("state") == "FAILED" or verification.get("status") == "FAILED"
            if not verification_failed:
                return ()
            blocker = {"type": "VERIFICATION_FAILED", "severity": "HIGH", "source": "coding_agent_response"}
            if verification.get("error"):
                blocker["error"] = verification["error"]
        elif isinstance(verification, ToolResult) and not verification.success:
            blocker = {"type": "VERIFICATION_FAILED", "severity": "HIGH", "source": "coding_agent_response"}
            if verification.error is not None:
                blocker["error"] = verification.error.message
        else:
            return ()

    if task_id is not None:
        blocker["task_id"] = task_id
    if operation_id is not None:
        blocker["operation_id"] = operation_id
    return (blocker,)


def start_control_plane_http(runtime: JARVISRuntime, *, ai_service: AIService | None = None, activity_stream: RuntimeActivityStream, tool_registry: ToolRegistry | None = None, confirmation_service: CodingAgentConfirmationService | None = None, config: ControlPlaneHTTPConfig | None = None) -> ControlPlaneHostHandle:
    if not isinstance(runtime, JARVISRuntime):
        raise TypeError("runtime must be a JARVISRuntime")
    if ai_service is not None and not isinstance(ai_service, AIService):
        raise TypeError("ai_service must be an AIService or None")
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
        return tuple(agent.to_context() for agent in runtime.world_runtime.agents if agent.status is not AgentStatus.RETIRED)

    def tools_supplier():
        if tool_registry is None:
            return ()
        return tuple({"name": definition.name, "description": definition.description, "version": definition.version, "risk_level": definition.risk_level.value, "requires_confirmation": definition.requires_confirmation, "metadata": dict(definition.metadata)} for definition in tool_registry.list_definitions())

    def approvals_supplier():
        if confirmation_service is None:
            return ()
        operation = confirmation_service.get_pending()
        if operation is None:
            return ()
        metadata = dict(operation.metadata)
        return ({"operation_id": operation.operation_id, "status": operation.status.value, "task_id": operation.task.task_id, "objective": operation.task.objective, "created_at": operation.created_at, "plan_fingerprint": metadata.get("plan_fingerprint"), "edit_count": len(operation.plan.edits), "verification_runner": operation.plan.verification.runner},)

    def autonomous_supplier():
        if runtime.operational_runtime is None:
            return ()
        records = []
        for job in runtime.operational_runtime.list_jobs(limit=100):
            records.append(
                {
                    "job_id": job.job_id,
                    "goal": job.goal,
                    "status": job.status.value,
                    "step_count": job.step_count,
                    "max_steps": job.max_steps,
                    "waiting_reason": job.waiting_reason,
                    "result": job.result,
                    "failure_reason": job.failure_reason,
                    "resumable": job.resumable,
                    "terminal": job.terminal,
                    "authority_granted": False,
                    "authorization_granted": False,
                    "execution_requested": False,
                }
            )
        return tuple(records)

    def model_supplier():
        base_projection = local_model_projection(
            base_url=os.environ.get("JARVIS_LOCAL_BASE_URL", "http://127.0.0.1:8080"),
            model_id=os.environ.get("JARVIS_LOCAL_MODEL", "unknown"),
        )
        if ai_service is None:
            return base_projection
        try:
            return {**base_projection, **_model_routing_projection(ai_service=ai_service, observation=base_projection)}
        except InvalidRequestError:
            return {**base_projection, "routing_state": "UNCONFIGURED"}

    builder = ControlPlaneSnapshotBuilder(
        world_supplier=world_supplier,
        activity_stream=activity_stream,
        task_supplier=lambda: _task_projection(activity_stream),
        agents_supplier=agents_supplier,
        approvals_supplier=approvals_supplier,
        tools_supplier=tools_supplier,
        model_supplier=model_supplier,
        blockers_supplier=lambda: _blockers_projection(activity_stream),
        verification_supplier=lambda: _verification_projection(activity_stream),
        autonomous_supplier=autonomous_supplier,
    )
    server = create_control_plane_server(builder, config=config or ControlPlaneHTTPConfig())
    thread = Thread(target=server.serve_forever, name="jarvis-control-plane-http", daemon=True)
    thread.start()
    return ControlPlaneHostHandle(server=server, thread=thread)


__all__ = ["ControlPlaneHostHandle", "local_model_projection", "start_control_plane_http"]
