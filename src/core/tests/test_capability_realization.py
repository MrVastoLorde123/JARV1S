import unittest

from src.core.capability_argument_planner import CapabilityInvocationService
from src.core.capability_catalog import CapabilityCatalog
from src.core.capability_realization import CapabilityRealizationService
from src.core.capability_selection import CapabilityCandidate
from src.core.capability_selection_service import CapabilitySelectionService
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest


class FakeGateway:
    def __init__(self, definitions):
        self._definitions = tuple(definitions)

    def list_definitions(self):
        return self._definitions


class FakeArgumentPlanner:
    def __init__(self, arguments=None):
        self.arguments = dict(arguments or {})
        self.calls = []

    def propose(self, intent, capability):
        self.calls.append((intent, capability))
        return dict(self.arguments)


def definition(name, description, schema):
    return ToolDefinition(
        name=name,
        description=description,
        version="1.0.0",
        input_schema=schema,
        output_schema={"type": "string"},
        risk_level=RiskLevel.LOW,
    )


class CapabilityRealizationTests(unittest.TestCase):
    def _service(self, definitions, arguments=None):
        catalog = CapabilityCatalog(FakeGateway(definitions))
        selector = __import__(
            "src.core.capability_selection",
            fromlist=["DeterministicCapabilitySelector"],
        ).DeterministicCapabilitySelector()
        selection_service = CapabilitySelectionService(catalog, selector)
        argument_planner = FakeArgumentPlanner(arguments)
        invocation_service = CapabilityInvocationService(argument_planner)
        return CapabilityRealizationService(selection_service, invocation_service), argument_planner

    def test_selects_best_capability(self):
        read = definition("read_file", "read a file from the workspace", {
            "type": "object",
            "required": ["path"],
            "properties": {"path": {"type": "string"}},
        })
        search = definition("search_files", "search files in the workspace", {
            "type": "object",
            "required": ["query"],
            "properties": {"query": {"type": "string"}},
        })
        service, _ = self._service([read, search], {"path": "README.md"})

        result = service.realize("read file")

        self.assertEqual(result.candidate.capability.name, "read_file")
        self.assertEqual(result.request.tool_name, "read_file")
        self.assertEqual(dict(result.request.arguments), {"path": "README.md"})

    def test_argument_planner_receives_selected_candidate_and_intent(self):
        read = definition("read_file", "read a file", {
            "type": "object",
            "required": ["path"],
            "properties": {"path": {"type": "string"}},
        })
        service, planner = self._service([read], {"path": "src/core/jarvis.py"})

        result = service.realize("inspect jarvis")

        self.assertEqual(len(planner.calls), 1)
        intent, candidate = planner.calls[0]
        self.assertEqual(intent, "inspect jarvis")
        self.assertIsInstance(candidate, CapabilityCandidate)
        self.assertEqual(result.request, ToolRequest(
            tool_name="read_file",
            arguments={"path": "src/core/jarvis.py"},
        ))

    def test_no_matching_capability_is_not_silently_realized(self):
        read = definition("read_file", "read a file", {"type": "object"})
        service, _ = self._service([read])

        with self.assertRaises(LookupError):
            service.realize("send an email")

    def test_realization_never_invokes_tool(self):
        read = definition("read_file", "read a file", {
            "type": "object",
            "required": ["path"],
            "properties": {"path": {"type": "string"}},
        })
        service, _ = self._service([read], {"path": "README.md"})

        result = service.realize("read file")

        self.assertIsInstance(result.request, ToolRequest)
        self.assertEqual(result.request.tool_name, "read_file")

    def test_empty_intent_is_rejected(self):
        read = definition("read_file", "read a file", {"type": "object"})
        service, _ = self._service([read])

        with self.assertRaises(ValueError):
            service.realize("   ")


if __name__ == "__main__":
    unittest.main()
