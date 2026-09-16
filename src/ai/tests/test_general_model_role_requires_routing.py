import unittest

from src.ai.model_routing import ModelProfile, ModelRole, ModelRouter
from src.ai.models import AICapabilities, AIRequest, AIResponse
from src.ai.provider import AIProvider
from src.ai.service import AIService


class RoutingProvider(AIProvider):
    def __init__(self):
        self.requests = []

    def generate(self, request):
        self.requests.append(request)
        return AIResponse(
            content="routed-general-response",
            provider="routing",
            model=request.model,
        )

    def capabilities(self):
        return AICapabilities(text_generation=True)

    def provider_name(self):
        return "routing"


class GeneralModelRoleRoutingRequirementTests(unittest.TestCase):
    def test_unconfigured_service_requires_general_routing(self):
        provider = RoutingProvider()
        service = AIService(default_provider="routing")
        service.register_provider(provider)

        with self.assertRaises(LookupError):
            service.generate_for_role(
                AIRequest(task="hello", context=None),
                role=ModelRole.GENERAL,
            )

        self.assertEqual(provider.requests, [])

    def test_explicit_empty_router_remains_strict(self):
        provider = RoutingProvider()
        service = AIService(
            default_provider="routing",
            model_router=ModelRouter(),
        )
        service.register_provider(provider)

        with self.assertRaises(LookupError):
            service.generate_for_role(
                AIRequest(task="hello", context=None),
                role=ModelRole.GENERAL,
            )
        self.assertEqual(provider.requests, [])

    def test_general_role_routes_before_provider_execution(self):
        provider = RoutingProvider()
        service = AIService(default_provider="routing")
        service.register_provider(provider)
        service.register_model(
            ModelProfile(
                model_id="general-model",
                roles=frozenset({ModelRole.GENERAL}),
                priority=100,
            )
        )

        response = service.generate_for_role(
            AIRequest(task="hello", context=None),
            role=ModelRole.GENERAL,
        )

        self.assertEqual(response.content, "routed-general-response")
        self.assertEqual(len(provider.requests), 1)
        self.assertEqual(provider.requests[0].model, "general-model")


if __name__ == "__main__":
    unittest.main(verbosity=2)
