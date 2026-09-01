import unittest

from src.core.capability_invocation import (
    CapabilityInvocationBuilder,
    CapabilityInvocationError,
)
from src.tools.models import RiskLevel, ToolDefinition


class CapabilityInvocationTests(unittest.TestCase):
    def setUp(self):
        self.builder = CapabilityInvocationBuilder()
        self.capability = ToolDefinition(
            name="read_file",
            description="Read a text file from the workspace.",
            version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {"type": "string"},
                    "encoding": {"type": "string"},
                },
            },
            output_schema={"type": "object"},
            risk_level=RiskLevel.LOW,
            metadata={"category": "filesystem"},
        )

    def test_builds_tool_request(self):
        request = self.builder.build(
            self.capability,
            {"path": "README.md"},
            invocation_id="inv-1",
        )
        self.assertEqual(request.tool_name, "read_file")
        self.assertEqual(request.arguments, {"path": "README.md"})
        self.assertEqual(request.invocation_id, "inv-1")

    def test_missing_required_argument_is_rejected(self):
        with self.assertRaisesRegex(CapabilityInvocationError, "path"):
            self.builder.build(self.capability, {})

    def test_wrong_argument_type_is_rejected(self):
        with self.assertRaisesRegex(CapabilityInvocationError, "path.*string"):
            self.builder.build(self.capability, {"path": 123})

    def test_unknown_arguments_are_preserved(self):
        request = self.builder.build(
            self.capability,
            {"path": "README.md", "future_flag": True},
        )
        self.assertEqual(request.arguments["future_flag"], True)

    def test_metadata_is_request_scoped(self):
        request = self.builder.build(
            self.capability,
            {"path": "README.md"},
            metadata={"conversation_id": "conv-1"},
        )
        self.assertEqual(request.metadata["conversation_id"], "conv-1")

    def test_builder_does_not_invoke_capability(self):
        request = self.builder.build(self.capability, {"path": "README.md"})
        self.assertEqual(request.tool_name, "read_file")

    def test_non_mapping_arguments_are_rejected(self):
        with self.assertRaises(CapabilityInvocationError):
            self.builder.build(self.capability, None)

    def test_invalid_capability_type_is_rejected(self):
        with self.assertRaises(TypeError):
            self.builder.build(object(), {})
