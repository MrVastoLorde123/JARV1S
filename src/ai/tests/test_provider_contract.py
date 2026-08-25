import unittest

from src.ai.models import (
    AIRequest,
    AIResponse,
    AICapabilities,
)

from src.ai.provider import AIProvider


class FakeProvider(AIProvider):
    """
    Minimal fake provider used only for testing the interface.
    """

    def generate(
        self,
        request: AIRequest
    ) -> AIResponse:

        return AIResponse(
            content=f"Fake response to: {request.task}",
            provider=self.provider_name(),
            model="fake-model",
            finish_reason="completed",
        )

    def capabilities(self):
        return AICapabilities(
            text_generation=True,
            structured_output=True,
        )

    def provider_name(self):
        return "fake"


class AIProviderContractTests(unittest.TestCase):

    def setUp(self):

        self.provider = FakeProvider()

    def test_provider_name(self):

        self.assertEqual(
            self.provider.provider_name(),
            "fake"
        )

    def test_capabilities_are_available(self):

        capabilities = (
            self.provider.capabilities()
        )

        self.assertTrue(
            capabilities.text_generation
        )

        self.assertTrue(
            capabilities.structured_output
        )

        self.assertFalse(
            capabilities.vision
        )

    def test_generate_returns_ai_response(self):

        request = AIRequest(
            task="Explain JARVIS.",
            context="test context",
        )

        response = self.provider.generate(
            request
        )

        self.assertIsInstance(
            response,
            AIResponse
        )

        self.assertEqual(
            response.provider,
            "fake"
        )

        self.assertEqual(
            response.model,
            "fake-model"
        )

    def test_provider_receives_request_without_database_access(self):

        request = AIRequest(
            task="Test task",
            context={
                "source": "context_builder"
            },
        )

        response = self.provider.generate(
            request
        )

        self.assertIn(
            "Test task",
            response.content
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)