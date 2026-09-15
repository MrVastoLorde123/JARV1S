import unittest

from src.ai.errors import InvalidRequestError
from src.ai.model_catalog import ModelCatalog
from src.ai.model_routing import ModelProfile, ModelRole
from src.ai.models import AIRequest, AIResponse, AICapabilities
from src.ai.provider import AIProvider
from src.ai.service import AIService


class CatalogProvider(AIProvider):
    def __init__(self):
        self.requests = []

    def generate(self, request: AIRequest) -> AIResponse:
        self.requests.append(request)
        return AIResponse(
            content=request.model,
            provider="local",
            model=request.model or "unknown",
            finish_reason="completed",
        )

    def capabilities(self) -> AICapabilities:
        return AICapabilities(text_generation=True)

    def provider_name(self) -> str:
        return "local"


class AIServiceModelCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = ModelCatalog(
            [
                ModelProfile(
                    "granite-8b",
                    frozenset({ModelRole.GENERAL}),
                    priority=100,
                ),
                ModelProfile(
                    "qwen3-14b",
                    frozenset({ModelRole.DIAGNOSTIC}),
                    priority=90,
                ),
            ]
        )
        self.catalog.observe_ids(["granite-8b"])
        self.service = AIService(model_catalog=self.catalog)
        self.provider = CatalogProvider()
        self.service.register_provider(self.provider)
        self.service.set_default_provider("local")

    def test_catalog_availability_controls_routing(self) -> None:
        with self.assertRaisesRegex(LookupError, "no model available for role DIAGNOSTIC"):
            self.service.route_model(ModelRole.DIAGNOSTIC)

        self.service.observe_models(["qwen3-14b"])
        decision = self.service.route_model(ModelRole.DIAGNOSTIC)
        self.assertEqual(decision.model_id, "qwen3-14b")

    def test_openai_model_observation_refreshes_routing(self) -> None:
        observed = self.service.observe_openai_models(
            {"data": [{"id": "qwen3-14b"}]}
        )
        self.assertEqual(observed, ("qwen3-14b",))
        with self.assertRaisesRegex(LookupError, "no model available for role GENERAL"):
            self.service.route_model(ModelRole.GENERAL)

        decision = self.service.route_model(ModelRole.DIAGNOSTIC)
        self.assertEqual(decision.model_id, "qwen3-14b")

    def test_catalog_observation_does_not_execute_a_provider(self) -> None:
        self.service.observe_models(["qwen3-14b"])
        self.service.route_model(ModelRole.DIAGNOSTIC)
        self.assertEqual(self.provider.requests, [])

    def test_generate_for_role_uses_current_catalog_selection(self) -> None:
        self.service.observe_models(["qwen3-14b"])
        request = AIRequest(task="Diagnose", context="test")
        response = self.service.generate_for_role(request, ModelRole.DIAGNOSTIC)
        self.assertEqual(response.model, "qwen3-14b")
        self.assertEqual(self.provider.requests[0].model, "qwen3-14b")

    def test_observation_requires_catalog(self) -> None:
        service = AIService()
        with self.assertRaisesRegex(InvalidRequestError, "No model catalog"):
            service.observe_models(["granite-8b"])


if __name__ == "__main__":
    unittest.main()
