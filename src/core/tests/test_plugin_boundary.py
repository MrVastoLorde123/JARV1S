import unittest

from src.agency.execution_runtime import ExecutionRuntime, ExecutionStatus
from src.context.execution_semantics import (
    ExecutionPreparation,
    ExecutionPreparationStatus,
    ExecutionRequest,
)
from src.core.plugin_boundary import (
    CapabilityExecutionAdapter,
    CapabilityPluginRegistry,
    PluginDefinition,
)
from src.tools.models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult


class ExamplePlugin:
    def definition(self):
        return PluginDefinition("filesystem", "1.0.0")

    def capabilities(self):
        return (
            ToolDefinition(
                name="read_file",
                description="Read a file",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "required": ["path"],
                    "properties": {"path": {"type": "string"}},
                },
                output_schema={"type": "object"},
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


def execution_request(operation="read_workspace_file", arguments=None):
    return ExecutionRequest(
        execution_id="exec-1",
        request="read README.md",
        proposal_id="proposal-1",
        validation_id="validation-1",
        policy_decision_id="policy-1",
        confirmation_id=None,
        authorization_id="authorization-1",
        operation=operation,
        arguments={"path": "README.md"} if arguments is None else arguments,
        metadata={"source": "test"},
    )


def ready_preparation(request: ExecutionRequest | None = None) -> ExecutionPreparation:
    request = request or execution_request()
    return ExecutionPreparation(
        request=request.request,
        execution_id=request.execution_id,
        status=ExecutionPreparationStatus.READY,
        execution_request=request,
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

    def test_capability_arguments_are_validated_before_plugin_execution(self):
        class RecordingPlugin(ExamplePlugin):
            def __init__(self):
                self.called = False

            def execute(self, request):
                self.called = True
                return super().execute(request)

        plugin = RecordingPlugin()
        registry = CapabilityPluginRegistry()
        registry.register(plugin)
        registry.bind("read_workspace_file", "read_file")

        with self.assertRaises(ValueError):
            registry.execute(execution_request(arguments={"path": 42}))

        self.assertFalse(plugin.called)

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

    def test_execution_adapter_translates_success_to_m8_1_outcome(self):
        registry = CapabilityPluginRegistry()
        registry.register(ExamplePlugin())
        registry.bind("read_workspace_file", "read_file")

        outcome = CapabilityExecutionAdapter(registry).execute(execution_request())

        self.assertTrue(outcome.success)
        self.assertEqual(outcome.content, {"path": "README.md"})
        self.assertEqual(outcome.metadata["capability_plugin_boundary"], "m8.2")

    def test_execution_adapter_integrates_with_m8_1_runtime(self):
        registry = CapabilityPluginRegistry()
        registry.register(ExamplePlugin())
        registry.bind("read_workspace_file", "read_file")

        observation = ExecutionRuntime(CapabilityExecutionAdapter(registry)).execute(
            ready_preparation()
        )

        self.assertIs(observation.status, ExecutionStatus.SUCCEEDED)
        self.assertEqual(observation.execution_id, "exec-1")
        self.assertEqual(observation.operation, "read_workspace_file")
        self.assertEqual(observation.outcome.content, {"path": "README.md"})

    def test_execution_adapter_translates_plugin_failure(self):
        class FailingPlugin(ExamplePlugin):
            def execute(self, request):
                return ToolResult(
                    success=False,
                    tool_name=request.tool_name,
                    error=ToolError(
                        code="file_unavailable",
                        message="README.md is missing",
                    ),
                    invocation_id=request.invocation_id,
                )

        registry = CapabilityPluginRegistry()
        registry.register(FailingPlugin())
        registry.bind("read_workspace_file", "read_file")

        outcome = CapabilityExecutionAdapter(registry).execute(execution_request())

        self.assertFalse(outcome.success)
        self.assertEqual(outcome.error["code"], "file_unavailable")
        self.assertEqual(outcome.error["message"], "README.md is missing")


if __name__ == "__main__":
    unittest.main()
