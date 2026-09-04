import os
from pathlib import Path

from src.ai.providers.local_provider import LocalProvider
from src.ai.service import AIService
from src.core.conversation_store import ConversationStore
from src.core.jarvis import JARVIS
from src.core.jarvis_runtime import JARVISRuntime
from src.database_bootstrap import bootstrap_database
from src.interface.human_operating_layer import HumanOperatingLayer
from src.interface.session_identity import PersistentSessionIdentity


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

    bootstrap_database()

    provider = LocalProvider(
        base_url=base_url,
        model=model,
        timeout=120,
    )

    ai_service = AIService(default_provider="local")
    ai_service.register_provider(provider)

    conversation_store = ConversationStore()

    def processor_factory(session_id, conversation_id):
        return JARVIS(
            ai_service=ai_service,
            conversation_store=conversation_store,
            conversation_id=conversation_id,
            enable_memory_formation=True,
        )

    default_processor = JARVIS(ai_service=ai_service)
    runtime = JARVISRuntime.from_processor(
        default_processor,
        conversation_store=conversation_store,
        durable_processor_factory=processor_factory,
    )

    session_identity = PersistentSessionIdentity(
        data_dir / "active_session.json",
    )
    session_id = session_identity.get_or_create(requested_session_id)

    operator = HumanOperatingLayer(
        runtime,
        session_id=session_id,
        session_identity=session_identity,
    )

    operator.run()


if __name__ == "__main__":
    main()
