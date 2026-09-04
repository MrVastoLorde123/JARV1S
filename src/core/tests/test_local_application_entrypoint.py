import io
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch

from src import run_local_jarvis


class LocalApplicationEntrypointTests(unittest.TestCase):

    @patch("src.run_local_jarvis.HumanOperatingLayer")
    @patch("src.run_local_jarvis.JARVISRuntime")
    @patch("src.run_local_jarvis.JARVIS")
    @patch("src.run_local_jarvis.AIService")
    @patch("src.run_local_jarvis.LocalProvider")
    def test_main_uses_canonical_runtime_and_operator(
        self,
        local_provider_cls,
        ai_service_cls,
        jarvis_cls,
        runtime_cls,
        operator_cls,
    ):
        provider = local_provider_cls.return_value
        ai_service = ai_service_cls.return_value
        processor = jarvis_cls.return_value
        runtime = runtime_cls.from_processor.return_value
        operator = operator_cls.return_value

        output = io.StringIO()
        with patch.dict(
            os.environ,
            {
                "JARVIS_LOCAL_BASE_URL": "http://127.0.0.1:8080",
                "JARVIS_LOCAL_MODEL": "qwen3-4b-local",
                "JARVIS_SESSION_ID": "test-session",
            },
            clear=False,
        ), redirect_stdout(output):
            run_local_jarvis.main()

        local_provider_cls.assert_called_once_with(
            base_url="http://127.0.0.1:8080",
            model="qwen3-4b-local",
            timeout=120,
        )
        ai_service_cls.assert_called_once_with(default_provider="local")
        ai_service.register_provider.assert_called_once_with(provider)
        jarvis_cls.assert_called_once_with(ai_service=ai_service)
        runtime_cls.from_processor.assert_called_once_with(processor)
        operator_cls.assert_called_once_with(
            runtime,
            session_id="test-session",
        )
        operator.run.assert_called_once_with()

    @patch("src.run_local_jarvis.HumanOperatingLayer")
    @patch("src.run_local_jarvis.JARVISRuntime")
    @patch("src.run_local_jarvis.JARVIS")
    @patch("src.run_local_jarvis.AIService")
    @patch("src.run_local_jarvis.LocalProvider")
    def test_main_does_not_call_processor_or_runtime_directly(
        self,
        local_provider_cls,
        ai_service_cls,
        jarvis_cls,
        runtime_cls,
        operator_cls,
    ):
        with redirect_stdout(io.StringIO()):
            run_local_jarvis.main()

        jarvis_cls.return_value.ask.assert_not_called()
        runtime_cls.from_processor.return_value.receive.assert_not_called()
        runtime_cls.from_processor.return_value.respond.assert_not_called()
        operator_cls.return_value.run.assert_called_once_with()


if __name__ == "__main__":
    unittest.main(verbosity=2)
