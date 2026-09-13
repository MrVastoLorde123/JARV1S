from __future__ import annotations

import unittest

from src.ai.models import AIRequest
from src.ai.providers.ollama_provider import OllamaProvider


class OllamaProviderTests(unittest.TestCase):
    def test_default_endpoint_and_model_are_isolated_from_llama_cpp_defaults(self) -> None:
        provider = OllamaProvider()
        self.assertEqual(provider.provider_name(), "ollama")
        self.assertEqual(provider.base_url, "http://127.0.0.1:11434")
        self.assertEqual(provider.model, "qwen3:4b")
        self.assertEqual(provider.api_key, "ollama")

    def test_provider_keeps_existing_provider_neutral_payload_contract(self) -> None:
        provider = OllamaProvider()
        payload = provider._build_payload(
            AIRequest(
                task="hello",
                context=None,
                model="qwen3:4b",
                generation_options={"temperature": 0.2, "max_output_tokens": 128},
            )
        )
        self.assertEqual(payload["model"], "qwen3:4b")
        self.assertEqual(payload["temperature"], 0.2)
        self.assertEqual(payload["max_tokens"], 128)
        self.assertEqual(payload["stream"], False)
        self.assertEqual(
            payload["messages"][1],
            {"role": "user", "content": "hello"},
        )


if __name__ == "__main__":
    unittest.main()
