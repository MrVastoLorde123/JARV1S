import unittest

from src.ai.models import AIResponse
from src.ai.model_routing import ModelRole
from src.core.jarvis import JARVIS


class FakeConversationAIService:
    def __init__(self):
        self.role_calls = []
        self.legacy_generate_calls = []

    def generate_for_role(self, request, *, role, provider_name=None):
        self.role_calls.append((request, role, provider_name))
        return AIResponse(
            content="general-response",
            provider=provider_name or "fake",
            model="fake-general-model",
        )

    def generate(self, request, provider_name=None):
        self.legacy_generate_calls.append((request, provider_name))
        raise AssertionError("conversation path must prefer explicit GENERAL routing")


class ConversationGeneralModelRoleTests(unittest.TestCase):
    def test_conversation_requests_general_model_role(self):
        ai = FakeConversationAIService()
        jarvis = JARVIS(ai)

        response = jarvis.ask("hello there")

        self.assertEqual(response.content, "general-response")
        self.assertEqual(len(ai.role_calls), 1)
        request, role, provider_name = ai.role_calls[0]
        self.assertEqual(role, ModelRole.GENERAL)
        self.assertIsNone(provider_name)
        self.assertEqual(request.task, "hello there")
        self.assertEqual(ai.legacy_generate_calls, [])

    def test_conversation_forwards_provider_to_general_routing(self):
        ai = FakeConversationAIService()
        jarvis = JARVIS(ai)

        jarvis.ask("hello there", provider_name="local")

        self.assertEqual(len(ai.role_calls), 1)
        _, role, provider_name = ai.role_calls[0]
        self.assertEqual(role, ModelRole.GENERAL)
        self.assertEqual(provider_name, "local")


if __name__ == "__main__":
    unittest.main(verbosity=2)
