import json
import unittest

from src.ai.models import AIResponse
from src.ai.service import AIService
from src.core.capability_argument_planner import (
    AIRequestArgumentPlanner,
    CapabilityInvocationService,
)
from src.core.capability_selection import CapabilityCandidate
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest, ToolResult


class FakeAIProvider:
    def __init__(self, content):
        self._content = content

    def provider_name(self):
        return "fake"

    def capabilities(self):
        from src.ai.models import AICapabilities
        return AICapabilities(text_generation=True, structured_output=False)

    def generate(self, request):
        return AIResponse(content=self._content, provider="fake", model="fake-model")


def capability():
    return ToolDefinition(
        name="read_file",
        description="Read a text file from the workspace.",
        version="1.0.0",
        input_schema={
            "type": "object",
            "required": ["path"],
            "properties": {"path": {"type": "string"}},
        },
        output_schema={"type": "object"},
        risk_level=RiskLevel.LOW,
    )


class CapabilityArgumentPlannerTests(unittest.TestCase):
    def test_ai_proposal_is_parsed_as_arguments(self):
        ai = AIService(default_provider="fake")
        ai.register_provider(FakeAIProvider(json.dumps({"path": "README.md"})))
        planner = AIRequestArgumentPlanner(ai)
        candidate = CapabilityCandidate(capability(), 3.0, "match")
        self.assertEqual(planner.propose("open the README", candidate), {"path": "README.md"})

    def test_invalid_json_is_rejected(self):
        ai = AIService(default_provider="fake")
        ai.register_provider(FakeAIProvider("not json"))
        planner = AIRequestArgumentPlanner(ai)
        candidate = CapabilityCandidate(capability(), 3.0, "match")
        with self.assertRaises(ValueError):
            planner.propose("open the README", candidate)

    def test_json_array_is_rejected(self):
        ai = AIService(default_provider="fake")
        ai.register_provider(FakeAIProvider("[]"))
        planner = AIRequestArgumentPlanner(ai)
        candidate = CapabilityCandidate(capability(), 3.0, "match")
        with self.assertRaises(ValueError):
            planner.propose("open the README", candidate)

    def test_empty_intent_is_rejected(self):
        ai = AIService(default_provider="fake")
        ai.register_provider(FakeAIProvider("{}"))
        planner = AIRequestArgumentPlanner(ai)
        candidate = CapabilityCandidate(capability(), 3.0, "match")
        with self.assertRaises(ValueError):
            planner.propose(" ", candidate)

    def test_invocation_service_validates_model_output(self):
        ai = AIService(default_provider="fake")
        ai.register_provider(FakeAIProvider(json.dumps({"path": "README.md"})))
        service = CapabilityInvocationService(
            AIRequestArgumentPlanner(ai)
        )
        request = service.build_request(
            "open the README",
            CapabilityCandidate(capability(), 3.0, "match"),
        )
        self.assertIsInstance(request, ToolRequest)
        self.assertEqual(request.arguments, {"path": "README.md"})

    def test_invocation_service_rejects_bad_model_arguments(self):
        ai = AIService(default_provider="fake")
        ai.register_provider(FakeAIProvider(json.dumps({"path": 123})))
        service = CapabilityInvocationService(AIRequestArgumentPlanner(ai))
        with self.assertRaises(ValueError):
            service.build_request(
                "open the README",
                CapabilityCandidate(capability(), 3.0, "match"),
            )

    def test_invocation_service_never_invokes_tool(self):
        ai = AIService(default_provider="fake")
        ai.register_provider(FakeAIProvider(json.dumps({"path": "README.md"})))
        service = CapabilityInvocationService(AIRequestArgumentPlanner(ai))
        request = service.build_request(
            "open the README",
            CapabilityCandidate(capability(), 3.0, "match"),
        )
        self.assertEqual(request.tool_name, "read_file")
