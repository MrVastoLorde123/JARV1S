import unittest

from src.ai.models import (
    AIRequest,
    AIResponse,
    AIUsage,
    AICapabilities,
)


class AIModelsTests(unittest.TestCase):

    def test_ai_request_defaults(self):

        request = AIRequest(
            task="Answer the user's question.",
            context="test context"
        )

        self.assertEqual(
            request.task,
            "Answer the user's question."
        )

        self.assertEqual(
            request.context,
            "test context"
        )

        self.assertIsNone(
            request.model
        )

        self.assertEqual(
            request.generation_options,
            {}
        )

    def test_ai_request_preserves_options(self):

        request = AIRequest(
            task="Test task",
            context="test context",
            model="test-model",
            generation_options={
                "temperature": 0.2,
                "max_output_tokens": 500,
            },
        )

        self.assertEqual(
            request.model,
            "test-model"
        )

        self.assertEqual(
            request.generation_options[
                "temperature"
            ],
            0.2
        )

    def test_ai_usage_defaults_to_unknown(self):

        usage = AIUsage()

        self.assertIsNone(
            usage.input_tokens
        )

        self.assertIsNone(
            usage.output_tokens
        )

        self.assertIsNone(
            usage.total_tokens
        )

    def test_ai_response_can_store_text(self):

        response = AIResponse(
            content="Hello from JARVIS.",
            provider="test",
            model="test-model",
            finish_reason="completed",
        )

        self.assertEqual(
            response.content,
            "Hello from JARVIS."
        )

        self.assertEqual(
            response.provider,
            "test"
        )

        self.assertEqual(
            response.model,
            "test-model"
        )

        self.assertEqual(
            response.finish_reason,
            "completed"
        )

    def test_ai_response_can_store_usage(self):

        usage = AIUsage(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        )

        response = AIResponse(
            content="Test",
            provider="test",
            model="test-model",
            usage=usage,
        )

        self.assertEqual(
            response.usage.total_tokens,
            150
        )

    def test_capabilities_default_to_false(self):

        capabilities = AICapabilities()

        self.assertFalse(
            capabilities.text_generation
        )

        self.assertFalse(
            capabilities.streaming
        )

        self.assertFalse(
            capabilities.structured_output
        )

        self.assertFalse(
            capabilities.tool_calling
        )

        self.assertFalse(
            capabilities.vision
        )

        self.assertFalse(
            capabilities.embeddings
        )

    def test_capabilities_can_be_declared(self):

        capabilities = AICapabilities(
            text_generation=True,
            streaming=True,
            structured_output=True,
            tool_calling=False,
            vision=True,
            embeddings=False,
        )

        self.assertTrue(
            capabilities.text_generation
        )

        self.assertTrue(
            capabilities.streaming
        )

        self.assertTrue(
            capabilities.structured_output
        )

        self.assertFalse(
            capabilities.tool_calling
        )

        self.assertTrue(
            capabilities.vision
        )

        self.assertFalse(
            capabilities.embeddings
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)