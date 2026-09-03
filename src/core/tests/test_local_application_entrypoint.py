import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch

from src.core.models import JARVISResponse
from src.interface.boundary import InterfaceResponse
from src import run_local_jarvis


class LocalApplicationEntrypointTests(unittest.TestCase):

    @patch("src.run_local_jarvis.JARVISRuntime")
    @patch("src.run_local_jarvis.JARVIS")
    @patch("src.run_local_jarvis.AIService")
    @patch("src.run_local_jarvis.LocalProvider")
    def test_main_uses_canonical_runtime_entrypoint(
        self,
        local_provider_cls,
        ai_service_cls,
        jarvis_cls,
        runtime_cls,
    ):
        provider = local_provider_cls.return_value
        ai_service = ai_service_cls.return_value
        processor = jarvis_cls.return_value
        runtime = runtime_cls.from_processor.return_value

        runtime.receive.return_value = MagicMock()
        runtime.respond.return_value = InterfaceResponse(
            request_id="local-cli-1",
            content="test response",
        )

        output = io.StringIO()
        with redirect_stdout(output):
            run_local_jarvis.main()

        local_provider_cls.assert_called_once_with(
            base_url="http://127.0.0.1:8080",
            model="qwen3-4b-local",
            timeout=120,
        )
        ai_service_cls.assert_called_once_with(
            default_provider="local"
        )
        ai_service.register_provider.assert_called_once_with(
            provider
        )
        jarvis_cls.assert_called_once_with(
            ai_service=ai_service
        )
        runtime_cls.from_processor.assert_called_once_with(
            processor
        )
        runtime.receive.assert_called_once_with(
            request_id="local-cli-1",
            channel=run_local_jarvis.InterfaceChannel.TEXT,
            content="What do you know about my PCVUE skills?",
        )
        runtime.respond.assert_called_once_with(
            runtime.receive.return_value
        )
        self.assertIn(
            "test response",
            output.getvalue(),
        )
        self.assertIn(
            "Request ID: local-cli-1",
            output.getvalue(),
        )

    @patch("src.run_local_jarvis.JARVISRuntime")
    @patch("src.run_local_jarvis.JARVIS")
    @patch("src.run_local_jarvis.AIService")
    @patch("src.run_local_jarvis.LocalProvider")
    def test_main_does_not_call_processor_directly(
        self,
        local_provider_cls,
        ai_service_cls,
        jarvis_cls,
        runtime_cls,
    ):
        runtime = runtime_cls.from_processor.return_value
        runtime.receive.return_value = MagicMock()
        runtime.respond.return_value = InterfaceResponse(
            request_id="local-cli-1",
            content="test response",
        )

        with redirect_stdout(io.StringIO()):
            run_local_jarvis.main()

        jarvis_cls.return_value.ask.assert_not_called()
        runtime.receive.assert_called_once()
        runtime.respond.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
