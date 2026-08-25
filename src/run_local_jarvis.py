from src.ai.providers.local_provider import LocalProvider
from src.ai.service import AIService
from src.core.jarvis import JARVIS


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

    response = jarvis.ask(
        "What do you know about my PCVUE skills?"
    )

    print("=" * 60)
    print("JARVIS")
    print("=" * 60)

    print(response.content)

    print()
    print("Provider:", response.ai_response.provider)
    print("Model:", response.ai_response.model)
    print(
        "Context items:",
        len(response.context.items)
    )

if __name__ == "__main__":
    main()