from __future__ import annotations

import builtins

from src.ai.providers.local_provider import LocalProvider


class OllamaProvider(LocalProvider):
    """JARVIS provider for Ollama's local OpenAI-compatible API.

    Ollama exposes the same `/v1/chat/completions` shape consumed by the
    existing local provider, so model evaluation can switch runtimes without
    changing the provider-neutral AI contract.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "qwen3:4b",
        timeout: int = 300,
        api_key: str = "ollama",
    ) -> None:
        super().__init__(
            base_url=base_url,
            model=model,
            timeout=timeout,
            api_key=api_key,
        )

    def provider_name(self) -> str:
        return "ollama"
