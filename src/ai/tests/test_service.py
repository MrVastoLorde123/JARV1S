import unittest

from src.ai.errors import (
    CapabilityError,
    InvalidRequestError,
)

from src.ai.model_catalog import ModelCatalog
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
        self.return_invalid_response = False
        self.return_wrong_provider = False
        self.return_empty_model = False

    def generate(
        self,
        request: AIRequest
    ) -> AIResponse:

        self.generate_count += 1
        if self.return_invalid_response:
            return "not an AIResponse"

        return AIResponse(
            content=(
                f"Fake response: "
                f"{request.task}"
            ),
            provider="wrong-provider" if self.return_wrong_provider else self._name,
            model="" if self.return_empty_model else "fake-model",
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


class InvalidCapabilitiesProvider(FakeProvider):
    def capabilities(self):
        return "invalid-capabilities"


class InvalidInventoryProvider(FakeProvider):
    def list_models(self):
        return ("valid-model", "", 123)


class ValidInventoryProvider(FakeProvider):
    def list_models(self):
        return ("valid-model", "second-model")


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

    def test_non_provider_registration_is_rejected(self):
        with self.assertRaisesRegex(TypeError, "provider must be an AIProvider"):
            self.service.register_provider(object())

    def test_identical_provider_registration_is_idempotent(self):
        self.service.register_provider(self.provider)
        self.assertEqual(self.service.list_providers(), ("fake",))

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

        self.assertIsInstance(capabilities, AICapabilities)
        self.assertTrue(
            capabilities.text_generation
        )

    def test_invalid_provider_capabilities_are_rejected(self):
        service = AIService(default_provider="invalid")
        service.register_provider(InvalidCapabilitiesProvider(name="invalid"))
        with self.assertRaisesRegex(InvalidRequestError, "must return AICapabilities"):
            service.get_capabilities()

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

    def test_invalid_required_capability_name_is_rejected(self):
        request = AIRequest(task="hello", context=None)
        with self.assertRaisesRegex(InvalidRequestError, "required_capabilities"):
            self.service.generate(request, required_capabilities=[""])

    def test_unknown_required_capability_is_rejected(self):
        request = AIRequest(task="hello", context=None)
        with self.assertRaisesRegex(InvalidRequestError, "Unknown provider capability"):
            self.service.generate(request, required_capabilities=["not_a_capability"])

    def test_provider_response_type_is_enforced(self):
        self.provider.return_invalid_response = True
        request = AIRequest(task="hello", context=None)
        with self.assertRaisesRegex(InvalidRequestError, "must return AIResponse"):
            self.service.generate(request)

    def test_provider_response_provenance_is_enforced(self):
        self.provider.return_wrong_provider = True
        request = AIRequest(task="hello", context=None)
        with self.assertRaisesRegex(InvalidRequestError, "expected 'fake'"):
            self.service.generate(request)

    def test_provider_response_requires_model_identifier(self):
        self.provider.return_empty_model = True
        request = AIRequest(task="hello", context=None)
        with self.assertRaisesRegex(InvalidRequestError, "response model cannot be empty"):
            self.service.generate(request)

    def test_provider_model_inventory_is_validated(self):
        service = AIService(
            default_provider="inventory",
            model_catalog=ModelCatalog(),
        )
        service.register_provider(ValidInventoryProvider(name="inventory"))
        self.assertEqual(
            service.observe_provider_models(),
            ("valid-model", "second-model"),
        )

    def test_invalid_provider_model_inventory_is_rejected(self):
        service = AIService(
            default_provider="inventory",
            model_catalog=ModelCatalog(),
        )
        service.register_provider(InvalidInventoryProvider(name="inventory"))
        with self.assertRaisesRegex(InvalidRequestError, "invalid model inventory"):
            service.observe_provider_models()

    def test_provider_without_model_observation_is_rejected(self):
        with self.assertRaisesRegex(InvalidRequestError, "does not expose model observation"):
            self.service.observe_provider_models()

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

    def test_non_string_task_is_rejected(self):
        request = AIRequest(task=123, context=None)
        with self.assertRaises(InvalidRequestError):
            self.service.generate(request)

    def test_invalid_request_type_is_rejected(self):

        with self.assertRaises(
            InvalidRequestError
        ):
            self.service.generate(
                "not an AIRequest"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
