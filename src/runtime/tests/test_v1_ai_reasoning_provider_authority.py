import unittest
from unittest.mock import Mock

from src.ai.models import AIRequest, AIResponse
from src.ai.service import AIService
from src.runtime.autonomous_ai_reasoning_provider import AutonomousAIReasoningProvider
from src.runtime.autonomous_job import AutonomousJob


class V1AIReasoningProviderAuthorityTests(unittest.TestCase):
    def test_runtime_authorization_metadata_is_not_exposed_to_model(self) -> None:
        service = object.__new__(AIService)
        response = Mock(spec=AIResponse)
        response.content = {"disposition": "continue", "rationale": "ok"}
        service.generate = Mock(return_value=response)

        provider = AutonomousAIReasoningProvider(service)
        job = AutonomousJob.create(
            "keep working",
            job_id="authority-test",
            working_context={
                "task_progress": {"verdict": "PROGRESSED"},
                "_runtime_resume_authorization": {
                    "kind": "TOOL",
                    "request_fingerprint": "secret",
                },
            },
        )

        provider.reason(job)

        request = service.generate.call_args.args[0]
        self.assertIsInstance(request, AIRequest)
        self.assertNotIn("_runtime_resume_authorization", request.context["working_context"])
        self.assertIn("task_progress", request.context["working_context"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
