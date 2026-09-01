import unittest

from src.core.capability_catalog import CapabilityCatalog
from src.core.capability_selection import (
    CapabilitySelection,
    DeterministicCapabilitySelector,
)
from src.core.capability_selection_service import CapabilitySelectionService
from src.core.tool_execution import ToolCapabilityGateway
from src.tools.models import RiskLevel, ToolDefinition


class Gateway(ToolCapabilityGateway):
    def __init__(self, definitions):
        self._definitions = tuple(definitions)

    def list_definitions(self):
        return self._definitions

    def invoke(self, request):
        raise AssertionError("selection service must never invoke a tool")


class CapabilitySelectionServiceTests(unittest.TestCase):
    def setUp(self):
        definitions = (
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
        gateway = Gateway(definitions)
        self.service = CapabilitySelectionService(
            CapabilityCatalog(gateway),
            DeterministicCapabilitySelector(),
        )

    def test_returns_selection(self):
        result = self.service.select("read file")
        self.assertIsInstance(result, CapabilitySelection)
        self.assertEqual("read_file", result.best.capability.name)

    def test_service_does_not_invoke_tools(self):
        result = self.service.select("write file")
        self.assertEqual("write_file", result.best.capability.name)

    def test_empty_query_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.select(" ")


if __name__ == "__main__":
    unittest.main(verbosity=2)
