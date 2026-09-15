import unittest

from src.ai.model_routing import ModelProfile, ModelRole
from src.ai.models import AIResponse, AICapabilities
from src.ai.provider import AIProvider
from src.ai.service import AIService
from src.runtime.autonomous_job import AutonomousJob
from src.runtime.autonomous_ai_reasoning_provider import AutonomousAIReasoningProvider


class P(AIProvider):
    def provider_name(self):
        return "p"

    def capabilities(self):
        return AICapabilities(structured_output=True)

    def generate(self, request):
        self.request = request
        return AIResponse('{"disposition":"continue","rationale":"ok"}', "p", request.model or "legacy")


class T(unittest.TestCase):
    def _service(self):
        provider = P()
        service = AIService()
        service.register_provider(provider)
        service.set_default_provider("p")
        service.register_model(
            ModelProfile(
                model_id="reasoning-model",
                roles=frozenset({ModelRole.GENERAL}),
                priority=100,
            )
        )
        return service, provider

    def test_reason_uses_general_model_role(self):
        service, provider = self._service()
        out = AutonomousAIReasoningProvider(service).reason(
            AutonomousJob("j", "inspect ATS")
        )
        self.assertIn("disposition", out)
        self.assertEqual(provider.request.model, "reasoning-model")
        self.assertEqual(provider.request.context["job_id"], "j")

    def test_reason_forwards_provider_and_structured_capability(self):
        service, provider = self._service()
        out = AutonomousAIReasoningProvider(service, provider_name="p").reason(
            AutonomousJob("j", "inspect ATS")
        )
        self.assertIn("disposition", out)
        self.assertEqual(provider.request.model, "reasoning-model")
        self.assertEqual(provider.request.metadata["runtime"], "autonomous_reasoning")

    def test_bad_job(self):
        with self.assertRaises(TypeError):
            AutonomousAIReasoningProvider(AIService()).reason("x")
