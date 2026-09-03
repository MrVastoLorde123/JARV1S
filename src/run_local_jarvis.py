from src.ai.providers.local_provider import LocalProvider
from src.ai.service import AIService
from src.core.jarvis import JARVIS
from src.core.jarvis_runtime import JARVISRuntime
from src.interface.boundary import InterfaceChannel


def main():

    provider = LocalProvider(
        base_url="http://127.0.0.1:8080",
        model="qwen3-4b-local",
        timeout=120,
    )

    ai_service = AIService(
        default_provider="local"
    )

    ai_service.register_provider(
        provider
    )

    jarvis = JARVIS(
        ai_service=ai_service
    )

    runtime = JARVISRuntime.from_processor(
        jarvis
    )

    result = runtime.receive(
        request_id="local-cli-1",
        channel=InterfaceChannel.TEXT,
        content="What do you know about my PCVUE skills?",
    )

    response = runtime.respond(result)

    print("=" * 60)
    print("JARVIS")
    print("=" * 60)

    print(response.content)

    print()
    print(
        "Request ID:",
        response.request_id
    )


if __name__ == "__main__":
    main()
