import unittest

from src.ai.models import AIRequest
from src.ai.providers.local_provider import LocalProvider
from src.context.models import ContextItem, ContextPackage
from src.context.working_context import WorkingContext


class LocalProviderWorkingContextTests(unittest.TestCase):
    def test_accepts_provider_neutral_working_context(self):
        working_context = WorkingContext(
            request="What do you know about my PCVUE skills?",
            context_package=ContextPackage(
                request="What do you know about my PCVUE skills?",
                items=(
                    ContextItem(
                        source_type="MEMORY",
                        content="User is learning PCVUE.",
                        relevance_score=1.0,
                        confidence=0.95,
                        importance=0.9,
                        provenance={"source_id": "memory-pcvue"},
                    ),
                ),
                instructions=(
                    "Treat stored memories as claims, not automatic truth.",
                ),
            ),
        )

        request = AIRequest(
            task=working_context.request,
            context=working_context.to_context(),
        )

        messages = LocalProvider()._build_messages(request)
        system_message = messages[0]["content"]

        self.assertIn("JARVIS INSTRUCTIONS", system_message)
        self.assertIn(
            "Treat stored memories as claims, not automatic truth.",
            system_message,
        )
        self.assertIn("User is learning PCVUE.", system_message)
        self.assertIn("memory-pcvue", system_message)

    def test_rejects_malformed_provider_neutral_context(self):
        request = AIRequest(
            task="Test context.",
            context={"not_context": {}},
        )

        with self.assertRaises(Exception):
            LocalProvider()._build_messages(request)


if __name__ == "__main__":
    unittest.main(verbosity=2)
