import os
from pathlib import Path

from src.agency.world_bootstrap import create_local_world_runtime
from src.agents.coding_confirmation import CodingAgentConfirmationService
from src.agents.coding_confirmation_provider import CodingAgentConfirmationProvider
from src.agents.coding_confirmation_store import CodingConfirmationStore
from src.agents.coding_service import CodingAgentService
from src.ai.local_model_policy import build_local_model_role_policy
from src.ai.model_routing_runtime import ModelRoutingRuntime
from src.ai.providers.local_provider import LocalProvider
from src.ai.service import AIService
from src.context.memory_context_source_provider import MemoryContextSourceProvider
from src.context.working_context_runtime import WorkingContextRuntime
from src.core.coding_agent_jarvis import CodingAgentJARVIS
from src.core.conversation_store import ConversationStore
from src.core.jarvis_runtime import JARVISRuntime
from src.core.runtime_activity_stream import RuntimeActivityStream
from src.core.tool_authorization_evidence_recording import ToolAuthorizationEvidenceRecorder
from src.core.tool_authorization_evidence_store import ToolAuthorizationEvidenceStore
from src.database_bootstrap import bootstrap_database
from src.interface.capability_host import start_capability_http
from src.interface.coding_execution_activity import CodingExecutionActivityRecorder, ObservingToolInvoker
from src.interface.command_host import start_command_http
from src.interface.control_host import start_control_plane_http
from src.interface.control_plane import ControlPlaneActivityRecorder
from src.interface.control_plane_store import ControlPlaneActivityStore
from src.interface.http_capabilities import CapabilityHTTPConfig
from src.interface.http_command import CommandHTTPConfig
from src.interface.human_operating_layer import HumanOperatingLayer
from src.interface.session_identity import PersistentSessionIdentity
from src.interface.world_host import start_world_http
from src.personalization.end_to_end import PersonalizedWorkingContextRuntime
from src.personalization.persistence import PersonalizationStore
from src.personalization.runtime import PersonalizationRuntime
from src.tools.bootstrap import build_local_development_tool_stack


def main():
    base_url = os.environ.get(
        "JARVIS_LOCAL_BASE_URL",
        "http://127.0.0.1:8080",
    )
    model = os.environ.get(
        "JARVIS_LOCAL_MODEL",
        "qwen3-4b-local",
    )
    requested_session_id = os.environ.get("JARVIS_SESSION_ID")
    data_dir = Path(os.environ.get("JARVIS_DATA_DIR", "data"))
    workspace_dir = Path(os.environ.get("JARVIS_WORKSPACE_DIR", Path.cwd())).resolve()
    enable_world_http = os.environ.get("JARVIS_WORLD_HTTP", "0").strip().lower() in {"1", "true", "yes", "on"}
    enable_command_http = os.environ.get(
        "JARVIS_COMMAND_HTTP",
        "1" if enable_world_http else "0",
    ).strip().lower() in {"1", "true", "yes", "on"}
    enable_capability_http = os.environ.get(
        "JARVIS_CAPABILITY_HTTP",
        "1" if enable_world_http else "0",
    ).strip().lower() in {"1", "true", "yes", "on"}
    enable_control_plane_http = os.environ.get(
        "JARVIS_CONTROL_PLANE_HTTP",
        "1" if enable_world_http else "0",
    ).strip().lower() in {"1", "true", "yes", "on"}

    bootstrap_database()

    provider = LocalProvider(
        base_url=base_url,
        model=model,
        timeout=120,
    )

    model_routing_runtime = ModelRoutingRuntime(build_local_model_role_policy())
    ai_service = AIService(
        default_provider="local",
        model_routing_runtime=model_routing_runtime,
    )
    ai_service.register_provider(provider)

    conversation_store = ConversationStore()
    personalization_store = PersonalizationStore(
        data_dir / "personalization.json",
    )
    personalization_runtime = PersonalizationRuntime()

    database_path = data_dir / "processed" / "jarvis.db"
    control_plane_store = ControlPlaneActivityStore(database_path)
    authorization_evidence_store = ToolAuthorizationEvidenceStore(database_path)
    authorization_evidence_recorder = ToolAuthorizationEvidenceRecorder(
        authorization_evidence_store,
    )
    activity_stream = RuntimeActivityStream()
    activity_recorder = ControlPlaneActivityRecorder(
        activity_stream,
        durable_store=control_plane_store,
    )

    coding_confirmation_store = CodingConfirmationStore(database_path)
    coding_confirmation_service = CodingAgentConfirmationService()
    coding_confirmation_service.bind_store(coding_confirmation_store)
    coding_confirmation_provider = CodingAgentConfirmationProvider(
        coding_confirmation_service,
    )
    tool_stack = build_local_development_tool_stack(
        workspace_dir,
        confirmation_provider=coding_confirmation_provider,
        authorization_recorder=authorization_evidence_recorder,
    )
    coding_execution_recorder = CodingExecutionActivityRecorder(
        activity_stream,
        durable_store=control_plane_store,
    )
    coding_tool_invoker = ObservingToolInvoker(
        tool_stack.gate,
        coding_execution_recorder,
    )
    coding_agent_service = CodingAgentService.from_ai_service(
        ai_service,
        tool_stack.gate,
    )
    coding_agent_service.bind_tool_invoker(coding_tool_invoker)

    def processor_factory(session_id, conversation_id):
        base_context_runtime = WorkingContextRuntime(
            MemoryContextSourceProvider(
                include_memories=True,
                include_evidence=True,
            )
        )
        personalized_context_runtime = PersonalizedWorkingContextRuntime(
            base_context_runtime,
            personalization_runtime=personalization_runtime,
            persistence_store=personalization_store,
        )
        return CodingAgentJARVIS(
            ai_service=ai_service,
            conversation_store=conversation_store,
            conversation_id=conversation_id,
            enable_memory_formation=True,
            working_context_runtime=personalized_context_runtime,
            tool_invoker=coding_tool_invoker,
            coding_agent_service=coding_agent_service,
            coding_confirmation_service=coding_confirmation_service,
        )

    default_processor = CodingAgentJARVIS(
        ai_service=ai_service,
        tool_invoker=coding_tool_invoker,
        coding_agent_service=coding_agent_service,
        coding_confirmation_service=coding_confirmation_service,
    )
    world_runtime = create_local_world_runtime() if enable_world_http else None
    runtime = JARVISRuntime.from_processor(
        default_processor,
        conversation_store=conversation_store,
        durable_processor_factory=processor_factory,
        world_runtime=world_runtime,
    )

    world_host = None
    if enable_world_http:
        world_host = start_world_http(runtime)
        print("JARVIS World HTTP transport listening on http://127.0.0.1:8765")

    command_host = None
    if enable_command_http:
        command_host = start_command_http(
            runtime,
            config=CommandHTTPConfig(port=8766),
            activity_recorder=activity_recorder,
        )
        print("JARVIS Command HTTP transport listening on http://127.0.0.1:8766")

    capability_host = None
    if enable_capability_http:
        capability_host = start_capability_http(
            tool_stack.gate,
            config=CapabilityHTTPConfig(port=8767),
        )
        print("JARVIS Capability HTTP transport listening on http://127.0.0.1:8767")

    control_plane_host = None
    if enable_control_plane_http:
        if not enable_world_http:
            print("JARVIS Control Plane requires the world runtime; enable JARVIS_WORLD_HTTP=1.")
        else:
            control_plane_host = start_control_plane_http(
                runtime,
                ai_service=ai_service,
                activity_stream=activity_stream,
                tool_registry=tool_stack.registry,
                confirmation_service=coding_confirmation_service,
            )
            print("JARVIS Control Plane HTTP transport listening on http://127.0.0.1:8768")

    session_identity = PersistentSessionIdentity(
        data_dir / "active_session.json",
    )
    session_id = session_identity.get_or_create(requested_session_id)

    operator = HumanOperatingLayer(
        runtime,
        session_id=session_id,
        session_identity=session_identity,
    )

    try:
        operator.run()
    finally:
        if control_plane_host is not None:
            control_plane_host.close()
        if capability_host is not None:
            capability_host.close()
        if command_host is not None:
            command_host.close()
        if world_host is not None:
            world_host.close()


if __name__ == "__main__":
    main()
