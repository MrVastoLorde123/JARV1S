import unittest

from src.context.execution_semantics import ExecutionRequest
from src.core.plugin_boundary import (
    CapabilityPluginRegistry,
    PluginDefinition,
)
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest, ToolResult


class ExamplePlugin:
    def definition(self):
        return PluginDefinition("filesystem", "1.0.0")

    def capabilities(self):
        return (
            ToolDefinition(
                name="read_file",
                description="Read a file",
                version="1.0.0",
                input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
                output_schema={"type": "string"},
                risk_level=RiskLevel.LOW,
            ),
        )

    def execute(self, request: ToolRequest):
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content={"path": request.arguments["path"]},
            invocation_id=request.invocation_id,
        )


def execution_request(operation="read_workspace_file"):
    return ExecutionRequest(
        execution_id="exec-1",
        request={"path": "README.md"},
        proposal_id="proposal-1",
        validation_id="validation-1",
        policy_decision_id="policy-1",
        confirmation_id=None,
        authorization_id="authorization-1",
        operation=operation,
        arguments={"path": "README.md"},
        metadata={"source": "test"},
    )


class CapabilityPluginBoundaryTests(unittest.TestCase):
    def test_register_and_resolve_without_execution(self):
        registry = CapabilityPluginRegistry()
        registry.register(ExamplePlugin())
        registry.bind("read_workspace_file", "read_file")

        binding = registry.resolve("READ_WORKSPACE_FILE")

        self.assertEqual(binding.plugin_id, "filesystem")
        self.assertEqual(binding.capability.name, "read_file")

    def test_duplicate_plugin_is_rejected(self):
        registry = CapabilityPluginRegistry()
        registry.register(ExamplePlugin())

        with self.assertRaises(ValueError):
            registry.register(ExamplePlugin())

    def test_duplicate_capability_across_plugins_is_rejected(self):
        class OtherPlugin(ExamplePlugin):
            def definition(self):
                return PluginDefinition("other", "1.0.0")

        registry = CapabilityPluginRegistry()
        registry.register(ExamplePlugin())
        with self.assertRaises(ValueError):
            registry.register(OtherPlugin())

    def test_operation_must_bind_to_registered_capability(self):
        registry = CapabilityPluginRegistry()
        registry.register(ExamplePlugin())

        with self.assertRaises(KeyError):
            registry.bind("read_workspace_file", "missing")

    def test_resolve_is_case_and_whitespace_insensitive(self):
        registry = CapabilityPluginRegistry()
        registry.register(ExamplePlugin())
        registry.bind("read_workspace_file", "read_file")

        binding = registry.resolve("  Read_Workspace_File  ")
        self.assertEqual(binding.capability.name, "read_file")

    def test_unbound_operation_is_rejected(self):
        registry = CapabilityPluginRegistry()
        registry.register(ExamplePlugin())

        with self.assertRaises(KeyError):
            registry.resolve("write_workspace_file")

    def test_execute_preserves_execution_identity(self):
        registry = CapabilityPluginRegistry()
        registry.register(ExamplePlugin())
        registry.bind("read_workspace_file", "read_file")

        result = registry.execute(execution_request())

        self.assertTrue(result.success)
        self.assertEqual(result.tool_name, "read_file")
        self.assertEqual(result.invocation_id, "exec-1")
        self.assertEqual(result.content, {"path": "README.md"})

    def test_plugin_result_for_wrong_capability_is_rejected(self):
        class BadPlugin(ExamplePlugin):
            def definition(self):
                return PluginDefinition("bad", "1.0.0")

            def execute(self, request):
                return ToolResult(
                    success=True,
                    tool_name="wrong_tool",
                    content=None,
                    invocation_id=request.invocation_id,
                )

        registry = CapabilityPluginRegistry()
        registry.register(BadPlugin())
        registry.bind("read_workspace_file", "read_file")

        with self.assertRaises(ValueError):
            registry.execute(execution_request())


if __name__ == "__main__":
    unittest.main()
