import os
from pathlib import Path

from src.agency.world_bootstrap import create_local_world_runtime
from src.ai.providers.local_provider import LocalProvider
from src.ai.service import AIService
from src.context.memory_context_source_provider import MemoryContextSourceProvider
from src.context.working_context_runtime import WorkingContextRuntime
from src.core.conversation_store import ConversationStore
from src.core.jarvis import JARVIS
from src.core.jarvis_runtime import JARVISRuntime
from src.database_bootstrap import bootstrap_database
from src.interface.command_host import start_command_http
from src.interface.http_command import CommandHTTPConfig
from src.interface.human_operating_layer import HumanOperatingLayer
from src.interface.session_identity import PersistentSessionIdentity
from src.interface.world_host import start_world_http
from src.personalization.end_to_end import PersonalizedWorkingContextRuntime
from src.personalization.persistence import PersonalizationStore
from src.personalization.runtime import PersonalizationRuntime


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
    enable_world_http = os.environ.get("JARVIS_WORLD_HTTP", "0").strip().lower() in {"1", "true", "yes", "on"}
    enable_command_http = os.environ.get("JARVIS_COMMAND_HTTP", "0").strip().lower() in {"1", "true", "yes", "on"}

    bootstrap_database()

    provider = LocalProvider(
        base_url=base_url,
        model=model,
        timeout=120,
    )

    ai_service = AIService(default_provider="local")
    ai_service.register_provider(provider)

    conversation_store = ConversationStore()
    personalization_store = PersonalizationStore(
        data_dir / "personalization.json",
    )
    personalization_runtime = PersonalizationRuntime()

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
        return JARVIS(
            ai_service=ai_service,
            conversation_store=conversation_store,
            conversation_id=conversation_id,
            enable_memory_formation=True,
            working_context_runtime=personalized_context_runtime,
        )

    default_processor = JARVIS(ai_service=ai_service)
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
        )
        print("JARVIS Command HTTP transport listening on http://127.0.0.1:8766")

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
        if command_host is not None:
            command_host.close()
        if world_host is not None:
            world_host.close()


if __name__ == "__main__":
    main()
