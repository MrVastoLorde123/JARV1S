import unittest

from src.ai.model_routing import ModelProfile, ModelRole, ModelRouter
from src.ai.models import AIRequest, AIResponse, AICapabilities
from src.ai.provider import AIProvider
from src.ai.service import AIService


class RoutingProvider(AIProvider):
    def __init__(self, name="local"):
        self._name = name
        self.requests = []

    def generate(self, request: AIRequest) -> AIResponse:
        self.requests.append(request)
        return AIResponse(
            content=f"model={request.model}",
            provider=self._name,
            model=request.model or "provider-default",
            finish_reason="completed",
        )

    def capabilities(self) -> AICapabilities:
        return AICapabilities(text_generation=True)

    def provider_name(self) -> str:
        return self._name


class AIServiceModelRoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = RoutingProvider()
        router = ModelRouter(
            [
                ModelProfile(
                    "granite-8b",
                    frozenset({ModelRole.GENERAL, ModelRole.VERIFICATION}),
                    priority=100,
                ),
                ModelProfile(
                    "qwen3-14b",
                    frozenset({ModelRole.DIAGNOSTIC}),
                    priority=90,
                ),
            ]
        )
        self.service = AIService(model_router=router)
        self.service.register_provider(self.provider)
        self.service.set_default_provider("local")

    def test_route_model_is_available_without_provider_execution(self) -> None:
        decision = self.service.route_model(ModelRole.DIAGNOSTIC)
        self.assertEqual(decision.model_id, "qwen3-14b")
        self.assertEqual(self.provider.requests, [])

    def test_generate_for_role_sets_selected_model_on_request(self) -> None:
        request = AIRequest(task="Diagnose this.", context="test")
        response = self.service.generate_for_role(request, ModelRole.DIAGNOSTIC)
        self.assertEqual(response.content, "model=qwen3-14b")
        self.assertEqual(len(self.provider.requests), 1)
        self.assertEqual(self.provider.requests[0].model, "qwen3-14b")

    def test_request_model_can_be_used_as_explicit_preference(self) -> None:
        request = AIRequest(
            task="Explain this.",
            context="test",
            model="granite-8b",
        )
        response = self.service.generate_for_role(request, ModelRole.GENERAL)
        self.assertEqual(response.model, "granite-8b")

    def test_role_routing_does_not_create_authority_or_permission_fields(self) -> None:
        decision = self.service.route_model(ModelRole.GENERAL)
        self.assertFalse(hasattr(decision, "authority"))
        self.assertFalse(hasattr(decision, "permissions"))
        self.assertFalse(hasattr(decision, "tools"))
        self.assertFalse(hasattr(decision, "execution"))

    def test_invalid_model_preference_remains_a_routing_failure(self) -> None:
        request = AIRequest(
            task="Explain this.",
            context="test",
            model="qwen3-14b",
        )
        with self.assertRaisesRegex(ValueError, "does not serve role GENERAL"):
            self.service.generate_for_role(request, ModelRole.GENERAL)


if __name__ == "__main__":
    unittest.main()
