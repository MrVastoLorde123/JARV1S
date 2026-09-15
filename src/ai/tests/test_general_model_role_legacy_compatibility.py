import unittest

from src.ai.model_routing import ModelProfile, ModelRole, ModelRouter
from src.ai.models import AICapabilities, AIRequest, AIResponse
from src.ai.provider import AIProvider
from src.ai.service import AIService


class CompatibilityProvider(AIProvider):
    def __init__(self):
        self.requests = []

    def generate(self, request):
        self.requests.append(request)
        return AIResponse(
            content="legacy-general-response",
            provider="compatibility",
            model="legacy-model",
        )

    def capabilities(self):
        return AICapabilities(text_generation=True)

    def provider_name(self):
        return "compatibility"


class GeneralModelRoleLegacyCompatibilityTests(unittest.TestCase):
    def test_unconfigured_service_preserves_legacy_general_generation(self):
        provider = CompatibilityProvider()
        service = AIService(default_provider="compatibility")
        service.register_provider(provider)

        response = service.generate_for_role(
            AIRequest(task="hello", context=None),
            role=ModelRole.GENERAL,
        )

        self.assertEqual(response.content, "legacy-general-response")
        self.assertEqual(len(provider.requests), 1)
        self.assertIsNone(provider.requests[0].model)

    def test_explicit_empty_router_does_not_bypass_general_routing(self):
        provider = CompatibilityProvider()
        service = AIService(
            default_provider="compatibility",
            model_router=ModelRouter(),
        )
        service.register_provider(provider)

        with self.assertRaises(LookupError):
            service.generate_for_role(
                AIRequest(task="hello", context=None),
                role=ModelRole.GENERAL,
            )
        self.assertEqual(provider.requests, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
