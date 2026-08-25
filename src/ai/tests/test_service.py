import unittest

from src.ai.errors import (
    CapabilityError,
    InvalidRequestError,
)

from src.ai.models import (
    AIRequest,
    AIResponse,
    AICapabilities,
)

from src.ai.provider import AIProvider
from src.ai.service import AIService


class FakeProvider(AIProvider):

    def __init__(
        self,
        name="fake",
        structured_output=True
    ):
        self._name = name
        self._structured_output = (
            structured_output
        )

        self.generate_count = 0

    def generate(
        self,
        request: AIRequest
    ) -> AIResponse:

        self.generate_count += 1

        return AIResponse(
            content=(
                f"Fake response: "
                f"{request.task}"
            ),
            provider=self._name,
            model="fake-model",
            finish_reason="completed",
        )

    def capabilities(self):

        return AICapabilities(
            text_generation=True,
            structured_output=(
                self._structured_output
            ),
        )

    def provider_name(self):

        return self._name


class AIServiceTests(unittest.TestCase):

    def setUp(self):

        self.provider = FakeProvider()

        self.service = AIService()

        self.service.register_provider(
            self.provider
        )

        self.service.set_default_provider(
            "fake"
        )

    def test_provider_can_be_registered(self):

        self.assertEqual(
            self.service.list_providers(),
            ("fake",)
        )

    def test_default_provider_is_selected(self):

        provider = self.service.get_provider()

        self.assertIs(
            provider,
            self.provider
        )

    def test_specific_provider_can_be_selected(self):

        second_provider = FakeProvider(
            name="second"
        )

        self.service.register_provider(
            second_provider
        )

        selected = self.service.get_provider(
            "second"
        )

        self.assertIs(
            selected,
            second_provider
        )

    def test_generate_uses_selected_provider(self):

        request = AIRequest(
            task="Explain JARVIS.",
            context="test context"
        )

        response = self.service.generate(
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
            self.provider.generate_count,
            1
        )

    def test_provider_capabilities_are_available(self):

        capabilities = (
            self.service.get_capabilities()
        )

        self.assertTrue(
            capabilities.text_generation
        )

    def test_required_capability_is_checked(self):

        request = AIRequest(
            task="Return structured data.",
            context="test context"
        )

        response = self.service.generate(
            request,
            required_capabilities=[
                "structured_output"
            ]
        )

        self.assertIsInstance(
            response,
            AIResponse
        )

    def test_missing_capability_is_rejected(self):

        provider = FakeProvider(
            name="limited",
            structured_output=False
        )

        service = AIService(
            default_provider="limited"
        )

        service.register_provider(
            provider
        )

        request = AIRequest(
            task="Return structured data.",
            context="test context"
        )

        with self.assertRaises(
            CapabilityError
        ):
            service.generate(
                request,
                required_capabilities=[
                    "structured_output"
                ]
            )

    def test_unknown_provider_is_rejected(self):

        with self.assertRaises(
            InvalidRequestError
        ):
            self.service.get_provider(
                "does_not_exist"
            )

    def test_no_default_provider_is_rejected(self):

        service = AIService()

        with self.assertRaises(
            InvalidRequestError
        ):
            service.get_provider()

    def test_empty_task_is_rejected(self):

        request = AIRequest(
            task="",
            context="test context"
        )

        with self.assertRaises(
            InvalidRequestError
        ):
            self.service.generate(
                request
            )

    def test_invalid_request_type_is_rejected(self):

        with self.assertRaises(
            InvalidRequestError
        ):
            self.service.generate(
                "not an AIRequest"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)