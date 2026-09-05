import unittest

from src.core.capability_catalog import CapabilityCatalog
from src.core.capability_selection import DeterministicCapabilitySelector
from src.core.capability_selection_service import (
    CapabilityDiscoverySelection,
    CapabilitySelectionService,
)
from src.core.tool_execution import ToolCapabilityGateway
from src.tools.models import RiskLevel, ToolDefinition


class NonInvokingGateway(ToolCapabilityGateway):
    def __init__(self, definitions):
        self._definitions = tuple(definitions)
        self.invocations = 0

    def list_definitions(self):
        return self._definitions

    def invoke(self, request):
        self.invocations += 1
        raise AssertionError("discovery/selection must never invoke a tool")


class CapabilityDiscoverySelectionIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.definitions = (
            ToolDefinition(
                name="read_file",
                description="Read file contents from the workspace.",
                version="1.0.0",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                risk_level=RiskLevel.LOW,
            ),
            ToolDefinition(
                name="write_file",
                description="Write file contents in the workspace.",
                version="1.0.0",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                risk_level=RiskLevel.HIGH,
                requires_confirmation=True,
            ),
        )
        self.gateway = NonInvokingGateway(self.definitions)
        self.service = CapabilitySelectionService(
            CapabilityCatalog(self.gateway),
            DeterministicCapabilitySelector(),
        )

    def test_discover_returns_gateway_snapshot_without_execution(self):
        discovered = self.service.discover()
        self.assertEqual(discovered, self.definitions)
        self.assertEqual(self.gateway.invocations, 0)

    def test_discover_and_select_returns_integrated_snapshot(self):
        result = self.service.discover_and_select("read file")

        self.assertIsInstance(result, CapabilityDiscoverySelection)
        self.assertEqual(result.query, "read file")
        self.assertEqual(result.discovered, self.definitions)
        self.assertEqual(result.best.capability.name, "read_file")
        self.assertEqual(self.gateway.invocations, 0)

    def test_selected_capabilities_must_come_from_discovered_snapshot(self):
        result = self.service.discover_and_select("write file")
        discovered_names = {
            capability.name.strip().lower() for capability in result.discovered
        }

        self.assertTrue(
            all(
                candidate.capability.name.strip().lower() in discovered_names
                for candidate in result.selection.candidates
            )
        )

    def test_snapshot_is_deterministic(self):
        first = self.service.discover_and_select("workspace file")
        second = self.service.discover_and_select("workspace file")

        self.assertEqual(first, second)

    def test_snapshot_is_non_authorizing(self):
        result = self.service.discover_and_select("write file")
        context = result.to_context()

        self.assertTrue(context["selected"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["permission_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])

    def test_selection_integration_does_not_change_discovery_state(self):
        before = self.service.discover()
        self.service.discover_and_select("write file")
        after = self.service.discover()

        self.assertEqual(before, after)
        self.assertEqual(self.gateway.invocations, 0)

    def test_snapshot_rejects_mismatched_selection_query(self):
        selection = DeterministicCapabilitySelector().select("read file", self.definitions)

        with self.assertRaises(ValueError):
            CapabilityDiscoverySelection(
                query="write file",
                discovered=self.definitions,
                selection=selection,
            )

    def test_service_keeps_selection_provider_replaceable(self):
        class FixedSelector:
            def select(self, query, capabilities):
                return DeterministicCapabilitySelector().select(query, capabilities)

        alternate = CapabilitySelectionService(
            CapabilityCatalog(self.gateway),
            FixedSelector(),
        )
        result = alternate.discover_and_select("read file")

        self.assertEqual(result.best.capability.name, "read_file")
        self.assertEqual(self.gateway.invocations, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
