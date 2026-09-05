import json
import unittest

from src.ai.models import AIResponse, AICapabilities
from src.ai.service import AIService
from src.core.capability_argument_planner import AIRequestArgumentPlanner
from src.core.capability_catalog import CapabilityCatalog
from src.core.capability_request_service import (
    CapabilityRequestProposal,
    CapabilityRequestProposalService,
)
from src.core.capability_selection import DeterministicCapabilitySelector
from src.core.capability_selection_service import CapabilitySelectionService
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest


class FakeAIProvider:
    def __init__(self, content):
        self._content = content

    def provider_name(self):
        return "fake"

    def capabilities(self):
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


def snapshot():
    definition = capability()

    class Gateway:
        def list_definitions(self):
            return (definition,)

        def invoke(self, request):
            raise AssertionError("request proposal must never execute")

    service = CapabilitySelectionService(
        CapabilityCatalog(Gateway()),
        DeterministicCapabilitySelector(),
    )
    return service.discover_and_select("read file")


class CapabilityRequestProposalTests(unittest.TestCase):
    def setUp(self):
        self.ai = AIService(default_provider="fake")
        self.ai.register_provider(FakeAIProvider(json.dumps({"path": "README.md"})))
        self.planner = AIRequestArgumentPlanner(self.ai)
        self.service = CapabilityRequestProposalService(self.planner)

    def test_propose_returns_validated_tool_request(self):
        result = self.service.propose(snapshot(), invocation_id="inv-1")

        self.assertIsInstance(result, CapabilityRequestProposal)
        self.assertIsInstance(result.request, ToolRequest)
        self.assertEqual(result.request.tool_name, "read_file")
        self.assertEqual(result.request.arguments, {"path": "README.md"})
        self.assertEqual(result.request.invocation_id, "inv-1")

    def test_proposal_is_bound_to_discovery_snapshot(self):
        result = self.service.propose(snapshot())
        self.assertIs(
            result.candidate,
            result.snapshot.selection.best,
        )
        self.assertTrue(
            any(candidate is result.candidate for candidate in result.snapshot.selection.candidates)
        )

    def test_proposal_is_non_authorizing(self):
        result = self.service.propose(snapshot())
        context = result.to_context()

        self.assertTrue(context["validated_request"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["permission_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["confirmation_interpreted"])
        self.assertFalse(context["execution_requested"])

    def test_candidate_outside_snapshot_is_rejected(self):
        discovered = snapshot()
        foreign = type(discovered.best)(capability(), 999.0, "foreign")

        with self.assertRaises(ValueError):
            self.service.propose(discovered, candidate=foreign)

    def test_no_selected_capability_is_rejected(self):
        discovered = snapshot()
        empty = type(discovered.selection)(query=discovered.query, candidates=())
        empty_snapshot = type(discovered)(
            query=discovered.query,
            discovered=discovered.discovered,
            selection=empty,
        )

        with self.assertRaises(ValueError):
            self.service.propose(empty_snapshot)

    def test_bad_arguments_are_rejected_before_request_materialization(self):
        bad_ai = AIService(default_provider="fake")
        bad_ai.register_provider(FakeAIProvider(json.dumps({"path": 123})))
        service = CapabilityRequestProposalService(AIRequestArgumentPlanner(bad_ai))

        with self.assertRaises(ValueError):
            service.propose(snapshot())

    def test_proposal_does_not_execute_or_authorize(self):
        result = self.service.propose(
            snapshot(),
            metadata={"source": "m22.7"},
        )

        self.assertEqual(result.request.metadata["source"], "m22.7")
        self.assertFalse(result.to_context()["execution_requested"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
