"""M26.3 focused tests for the bounded model-provider boundary."""
from __future__ import annotations

import unittest

from src.ai.models import AICapabilities, AIResponse, AIUsage
from src.ai.provider import AIProvider
from src.core.model_provider_boundary import ModelProviderBoundary, ModelProviderBoundaryError


class _Provider(AIProvider):
    def __init__(self) -> None:
        self.requests = []

    def generate(self, request):
        self.requests.append(request)
        return AIResponse(
            content={"answer": "model suggestion"},
            provider="test-provider",
            model="test-model",
            finish_reason="stop",
            usage=AIUsage(input_tokens=3, output_tokens=4, total_tokens=7),
            metadata={"nested": {"safe": True}, "tags": ["suggestion"]},
        )

    def capabilities(self):
        return AICapabilities(text_generation=True)

    def provider_name(self):
        return "test-provider"


class _BadProvider(_Provider):
    def generate(self, request):
        return object()


class M26_3ModelProviderBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = _Provider()
        self.boundary = ModelProviderBoundary(self.provider)

    def test_provider_is_required(self) -> None:
        with self.assertRaises(TypeError):
            ModelProviderBoundary(object())

    def test_suggest_builds_provider_request(self) -> None:
        suggestion = self.boundary.suggest(
            "  explain this  ",
            {"topic": "runtime"},
            model="test-model",
            generation_options={"temperature": 0},
            metadata={"source": "interface"},
        )
        request = self.provider.requests[0]
        self.assertEqual(request.task, "explain this")
        self.assertEqual(request.context, {"topic": "runtime"})
        self.assertEqual(request.model, "test-model")
        self.assertEqual(request.generation_options, {"temperature": 0})
        self.assertEqual(request.metadata, {"source": "interface"})
        self.assertEqual(suggestion.content["answer"], "model suggestion")

    def test_suggestion_preserves_provider_model_finish_and_usage(self) -> None:
        suggestion = self.boundary.suggest("task", {})
        self.assertEqual(suggestion.provider, "test-provider")
        self.assertEqual(suggestion.model, "test-model")
        self.assertEqual(suggestion.finish_reason, "stop")
        self.assertEqual(suggestion.usage.total_tokens, 7)

    def test_suggestion_metadata_is_recursively_immutable(self) -> None:
        suggestion = self.boundary.suggest("task", {})
        with self.assertRaises(TypeError):
            suggestion.metadata["x"] = 1
        with self.assertRaises(TypeError):
            suggestion.metadata["nested"]["safe"] = False
        with self.assertRaises(TypeError):
            suggestion.metadata["tags"] += ("x",)

    def test_empty_task_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.boundary.suggest("   ", {})

    def test_generation_options_and_metadata_require_mappings(self) -> None:
        with self.assertRaises(TypeError):
            self.boundary.suggest("task", {}, generation_options=[])
        with self.assertRaises(TypeError):
            self.boundary.suggest("task", {}, metadata=[])

    def test_provider_response_type_is_validated(self) -> None:
        with self.assertRaises(ModelProviderBoundaryError):
            ModelProviderBoundary(_BadProvider()).suggest("task", {})

    def test_provider_name_is_exposed_without_provider_semantics(self) -> None:
        self.assertEqual(self.boundary.provider_name, "test-provider")
        self.assertFalse(self.boundary.is_ai_provider)

    def test_suggestion_is_not_an_authority_surface(self) -> None:
        suggestion = self.boundary.suggest("task", {})
        self.assertFalse(suggestion.authorizes_execution)
        self.assertFalse(suggestion.executes_capability)
        self.assertFalse(suggestion.mutates_state)
        self.assertFalse(suggestion.persists_state)
        self.assertFalse(suggestion.establishes_truth)
        self.assertFalse(suggestion.establishes_certainty)

    def test_boundary_is_not_an_authority_surface(self) -> None:
        self.assertFalse(self.boundary.authorizes_execution)
        self.assertFalse(self.boundary.executes_capability)
        self.assertFalse(self.boundary.mutates_state)
        self.assertFalse(self.boundary.persists_state)
        self.assertFalse(self.boundary.establishes_truth)
        self.assertFalse(self.boundary.establishes_certainty)

    def test_provider_is_the_only_component_invoked(self) -> None:
        self.boundary.suggest("task", {})
        self.assertEqual(len(self.provider.requests), 1)

    def test_suggestion_identity_is_distinct_from_provider_response(self) -> None:
        suggestion = self.boundary.suggest("task", {})
        self.assertIsNot(self.provider.requests[0], suggestion)


if __name__ == "__main__":
    unittest.main()
