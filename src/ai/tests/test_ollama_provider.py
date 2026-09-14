from __future__ import annotations

import builtins
import unittest
from unittest.mock import patch

from src.ai.errors import TimeoutError as JARVISTimeoutError
from src.ai.models import AIRequest
from src.ai.providers.local_provider import LocalProvider
from src.ai.providers.ollama_provider import OllamaProvider


class OllamaProviderTests(unittest.TestCase):
    def test_default_endpoint_model_and_timeout_are_isolated_from_llama_cpp_defaults(self) -> None:
        provider = OllamaProvider()
        self.assertEqual(provider.provider_name(), "ollama")
        self.assertEqual(provider.base_url, "http://127.0.0.1:11434")
        self.assertEqual(provider.model, "qwen3:4b")
        self.assertEqual(provider.timeout, 300)
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

    def test_builtin_timeout_is_preserved_as_jarvis_timeout(self) -> None:
        provider = LocalProvider(
            base_url="http://127.0.0.1:1",
            model="qwen3:4b",
            timeout=1,
        )
        request = AIRequest(task="hello", context=None)

        with patch(
            "src.ai.providers.local_provider.request.urlopen",
            side_effect=builtins.TimeoutError(),
        ):
            with self.assertRaises(JARVISTimeoutError):
                provider.generate(request)


if __name__ == "__main__":
    unittest.main()
