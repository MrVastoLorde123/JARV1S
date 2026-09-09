from __future__ import annotations

import unittest
from types import MappingProxyType

from src.core.capability_registry import CapabilityDefinition, CapabilityRegistry
from src.core.tool_capability_integration import (
    ToolCapabilityIntegrationBoundary,
    ToolCapabilitySnapshot,
)
from src.tools.models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult


class FakeGateway:
    def __init__(self, definitions):
        self.definitions = definitions
        self.requests = []
        self.result = None

    def list_definitions(self):
        return list(self.definitions)

    def invoke(self, request):
        self.requests.append(request)
        return self.result


class M26_4ToolCapabilityIntegrationBoundaryTests(unittest.TestCase):
    def make_definition(self):
        return ToolDefinition(
            name=" Read_File ",
            description="Read a file",
            version="1.2.3",
            input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
            output_schema={"type": "string"},
            risk_level=RiskLevel.MEDIUM,
            requires_confirmation=True,
            metadata={"nested": {"tags": ["filesystem", "read"]}},
        )

    def test_requires_exact_gateway_and_registry(self):
        with self.assertRaises(TypeError):
            ToolCapabilityIntegrationBoundary(object(), CapabilityRegistry())
        gateway = FakeGateway([])
        with self.assertRaises(TypeError):
            ToolCapabilityIntegrationBoundary(gateway, object())

    def test_snapshot_is_distinct_and_recursively_immutable(self):
        definition = self.make_definition()
        gateway = FakeGateway([definition])
        boundary = ToolCapabilityIntegrationBoundary(gateway, CapabilityRegistry())

        snapshot = boundary.snapshot()
        self.assertIsInstance(snapshot, ToolCapabilitySnapshot)
        self.assertIsNot(snapshot.definitions[0], definition)
        self.assertIsInstance(snapshot.definitions[0].input_schema, MappingProxyType)
        self.assertIsInstance(snapshot.definitions[0].metadata, MappingProxyType)
        self.assertIsInstance(snapshot.definitions[0].metadata["nested"]["tags"], tuple)
        with self.assertRaises(TypeError):
            snapshot.definitions[0].metadata["nested"] = {}

    def test_snapshot_rejects_non_tool_definition(self):
        gateway = FakeGateway([object()])
        boundary = ToolCapabilityIntegrationBoundary(gateway, CapabilityRegistry())
        with self.assertRaises(TypeError):
            boundary.snapshot()

    def test_registers_tool_as_provider_neutral_capability(self):
        registry = CapabilityRegistry()
        gateway = FakeGateway([self.make_definition()])
        boundary = ToolCapabilityIntegrationBoundary(gateway, registry)

        registered = boundary.register_capabilities()
        self.assertEqual(len(registered), 1)
        capability = registered[0]
        self.assertIsInstance(capability, CapabilityDefinition)
        self.assertEqual(capability.capability_id, "tool:read_file")
        self.assertEqual(capability.name, " Read_File ")
        self.assertEqual(capability.category, "tool")
        self.assertEqual(capability.metadata["tool_version"], "1.2.3")
        self.assertEqual(capability.metadata["risk_level"], "medium")
        self.assertTrue(capability.metadata["requires_confirmation"])
        self.assertIs(registry.get(capability.capability_id), capability)

    def test_duplicate_registration_is_rejected_by_existing_registry(self):
        registry = CapabilityRegistry()
        gateway = FakeGateway([self.make_definition()])
        boundary = ToolCapabilityIntegrationBoundary(gateway, registry)
        boundary.register_capabilities()
        with self.assertRaises(RuntimeError):
            boundary.register_capabilities()

    def test_invocation_requires_exact_tool_request(self):
        gateway = FakeGateway([])
        boundary = ToolCapabilityIntegrationBoundary(gateway, CapabilityRegistry())
        with self.assertRaises(TypeError):
            boundary.invoke(object())

    def test_invocation_forwards_exact_request_and_preserves_exact_result(self):
        gateway = FakeGateway([])
        result = ToolResult(
            success=True,
            tool_name="read_file",
            content={"line": "hello"},
            metadata={"source": "local"},
            invocation_id="inv-1",
        )
        gateway.result = result
        boundary = ToolCapabilityIntegrationBoundary(gateway, CapabilityRegistry())
        request = ToolRequest(
            tool_name="read_file",
            arguments={"path": "x.txt"},
            metadata={"trace": "t1"},
            invocation_id="inv-1",
        )

        returned = boundary.invoke(request)
        self.assertIs(returned, result)
        self.assertEqual(gateway.requests, [request])
        self.assertIs(gateway.requests[0], request)

    def test_rejects_non_tool_result_from_gateway(self):
        gateway = FakeGateway([])
        gateway.result = object()
        boundary = ToolCapabilityIntegrationBoundary(gateway, CapabilityRegistry())
        request = ToolRequest(tool_name="read_file")
        with self.assertRaises(TypeError):
            boundary.invoke(request)

    def test_failed_tool_result_remains_data(self):
        gateway = FakeGateway([])
        result = ToolResult(
            success=False,
            tool_name="read_file",
            error=ToolError(code="not_found", message="missing"),
            invocation_id="inv-2",
        )
        gateway.result = result
        boundary = ToolCapabilityIntegrationBoundary(gateway, CapabilityRegistry())
        returned = boundary.invoke(ToolRequest(tool_name="read_file", invocation_id="inv-2"))
        self.assertIs(returned, result)
        self.assertFalse(returned.success)
        self.assertEqual(returned.error.code, "not_found")

    def test_does_not_select_authorize_or_establish_truth(self):
        boundary = ToolCapabilityIntegrationBoundary(FakeGateway([]), CapabilityRegistry())
        self.assertFalse(boundary.selects_tool)
        self.assertFalse(boundary.authorizes_execution)
        self.assertFalse(boundary.mutates_state)
        self.assertFalse(boundary.persists_state)
        self.assertFalse(boundary.establishes_truth)
        self.assertFalse(boundary.establishes_certainty)


if __name__ == "__main__":
    unittest.main()
