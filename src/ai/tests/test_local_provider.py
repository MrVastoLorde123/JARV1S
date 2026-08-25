import json
import threading
import unittest
from src.context.models import (
    ContextItem,
    ContextPackage,
    MEMORY,
    PRIVATE,
)


from http.server import (
    BaseHTTPRequestHandler,
    HTTPServer,
)

from src.ai.models import (
    AIRequest,
    AIResponse,
)

from src.ai.providers.local_provider import (
    LocalProvider,
)


class FakeLLMHandler(
    BaseHTTPRequestHandler
):

    response_payload = {
        "model": "qwen3-4b-local",
        "choices": [
            {
                "message": {
                    "content":
                        "Fake local response."
                },
                "finish_reason":
                    "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 20,
            "completion_tokens": 10,
            "total_tokens": 30,
        },
    }

    last_request = None

    def do_POST(self):

        length = int(
            self.headers.get(
                "Content-Length",
                0
            )
        )

        body = self.rfile.read(
            length
        )

        FakeLLMHandler.last_request = (
            json.loads(
                body.decode("utf-8")
            )
        )

        response = json.dumps(
            self.response_payload
        ).encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Content-Length",
            str(len(response))
        )

        self.end_headers()

        self.wfile.write(
            response
        )

    def log_message(
        self,
        format,
        *args
    ):
        pass


class LocalProviderTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.server = HTTPServer(
            ("127.0.0.1", 0),
            FakeLLMHandler
        )

        cls.port = (
            cls.server.server_address[1]
        )

        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True,
        )

        cls.thread.start()

    @classmethod
    def tearDownClass(cls):

        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):

        FakeLLMHandler.last_request = None

        self.provider = LocalProvider(
            base_url=(
                f"http://127.0.0.1:"
                f"{self.port}"
            ),
            model="qwen3-4b-local",
        )

    def test_provider_name(self):

        self.assertEqual(
            self.provider.provider_name(),
            "local"
        )

    def test_capabilities(self):

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
            capabilities.tool_calling
        )

    def test_generate_returns_ai_response(self):

        ai_request = AIRequest(
            task="Explain JARVIS.",
            context=None,
        )

        response = (
            self.provider.generate(
                ai_request
            )
        )

        self.assertIsInstance(
            response,
            AIResponse
        )

        self.assertEqual(
            response.provider,
            "local"
        )

        self.assertEqual(
            response.model,
            "qwen3-4b-local"
        )

        self.assertEqual(
            response.content,
            "Fake local response."
        )

    def test_usage_is_parsed(self):

        ai_request = AIRequest(
            task="Test usage.",
            context=None,
        )

        response = (
            self.provider.generate(
                ai_request
            )
        )

        self.assertIsNotNone(
            response.usage
        )

        self.assertEqual(
            response.usage.total_tokens,
            30
        )

    def test_request_is_sent_to_server(self):

        ai_request = AIRequest(
            task="Explain Modbus.",
            context=None,
        )

        self.provider.generate(
            ai_request
        )

        sent = (
            FakeLLMHandler.last_request
        )

        self.assertEqual(
            sent["model"],
            "qwen3-4b-local"
        )

        self.assertEqual(
            sent["stream"],
            False
        )

        self.assertEqual(
            sent["messages"][-1]["content"],
            "Explain Modbus."
        )

    def test_generation_options_are_translated(self):

        ai_request = AIRequest(
            task="Test options.",
            context=None,
            generation_options={
                "temperature": 0.2,
                "top_p": 0.8,
                "max_output_tokens": 100,
                "seed": 42,
            },
        )

        self.provider.generate(
            ai_request
        )

        sent = (
            FakeLLMHandler.last_request
        )

        self.assertEqual(
            sent["temperature"],
            0.2
        )

        self.assertEqual(
            sent["top_p"],
            0.8
        )

        self.assertEqual(
            sent["max_tokens"],
            100
        )

        self.assertEqual(
            sent["seed"],
            42
        )

    def test_context_is_translated_into_system_context(self):
        context = ContextPackage(
            request="What do you know?",
            items=(
                ContextItem(
                    source_type=MEMORY,
                    content="User is learning PCVUE.",
                    relevance_score=1.0,
                    confidence=0.95,
                    importance=0.90,
                    privacy_level=PRIVATE,
                    provenance={
                        "memory_key": "pcvue_skill",
                    },
                ),
            ),
            instructions=(
                "Treat memory as evidence.",
            ),
            metadata={
                "builder_version": "1.0",
            },
        )

        ai_request = AIRequest(
            task="What do you know?",
            context=context,
        )

        self.provider.generate(
            ai_request
        )

        sent = FakeLLMHandler.last_request

        system_message = (
            sent["messages"][0]["content"]
        )

        self.assertIn(
            "JARVIS INSTRUCTIONS",
            system_message
        )

        self.assertIn(
            "Treat memory as evidence.",
            system_message
        )

        self.assertIn(
            "User is learning PCVUE.",
            system_message
        )

    def test_provider_does_not_require_openai_sdk(self):

        self.assertFalse(
            hasattr(
                self.provider,
                "openai"
            )
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )