from __future__ import annotations

import unittest

from src.tools.errors import ToolLayerError
from src.tools.models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult


class TestToolDefinition(unittest.TestCase):
    def test_valid_definition_defaults(self) -> None:
        definition = ToolDefinition(
            name="read_file",
            description="Reads a file from disk.",
            version="1.0.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )
        self.assertEqual(definition.name, "read_file")
        self.assertEqual(definition.risk_level, RiskLevel.LOW)
        self.assertFalse(definition.requires_confirmation)
        self.assertEqual(definition.metadata, {})
        self.assertEqual(definition.admissible_verification_sources, ())

    def test_can_set_all_fields(self) -> None:
        definition = ToolDefinition(
            name="delete_file",
            description="Deletes a file from disk.",
            version="2.1.0",
            input_schema={"type": "object", "required": ["path"]},
            output_schema={"type": "object"},
            risk_level=RiskLevel.HIGH,
            requires_confirmation=True,
            metadata={"author": "jarvis-team"},
        )
        self.assertEqual(definition.risk_level, RiskLevel.HIGH)
        self.assertTrue(definition.requires_confirmation)
        self.assertEqual(definition.metadata, {"author": "jarvis-team"})

    def test_normalizes_admissible_verification_sources(self) -> None:
        definition = ToolDefinition(
            name="read_status",
            description="Reads status.",
            version="1.0.0",
            input_schema={},
            output_schema={},
            admissible_verification_sources=(
                " status-check ",
                "status-check",
                "independent-reader",
            ),
        )
        self.assertEqual(
            definition.admissible_verification_sources,
            ("status-check", "independent-reader"),
        )

    def test_rejects_invalid_admissible_verification_sources(self) -> None:
        with self.assertRaises(ToolLayerError):
            ToolDefinition(
                name="read_status",
                description="Reads status.",
                version="1.0.0",
                input_schema={},
                output_schema={},
                admissible_verification_sources=["status-check"],  # type: ignore[arg-type]
            )

    def test_rejects_invalid_name(self) -> None:
        for bad_name in ["", "   ", None, 123]:
            with self.subTest(bad_name=bad_name):
                with self.assertRaises(ToolLayerError):
                    ToolDefinition(
                        name=bad_name,
                        description="desc",
                        version="1.0.0",
                        input_schema={},
                        output_schema={},
                    )

    def test_rejects_non_mapping_schema(self) -> None:
        with self.assertRaises(ToolLayerError):
            ToolDefinition(
                name="tool",
                description="desc",
                version="1.0.0",
                input_schema="not-a-mapping",  # type: ignore[arg-type]
                output_schema={},
            )

    def test_rejects_non_risk_level(self) -> None:
        with self.assertRaises(ToolLayerError):
            ToolDefinition(
                name="tool",
                description="desc",
                version="1.0.0",
                input_schema={},
                output_schema={},
                risk_level="high",  # type: ignore[arg-type]
            )

    def test_is_frozen(self) -> None:
        definition = ToolDefinition(
            name="tool",
            description="desc",
            version="1.0.0",
            input_schema={},
            output_schema={},
        )
        with self.assertRaises(Exception):
            definition.name = "renamed"  # type: ignore[misc]

    def test_nested_contract_data_is_immutable(self) -> None:
        schema = {"type": "object", "properties": {"path": {"type": "string"}}}
        metadata = {"tags": ["filesystem", "read"], "nested": {"safe": True}}
        definition = ToolDefinition(
            name="read_file",
            description="Reads a file.",
            version="1.0.0",
            input_schema=schema,
            output_schema={"type": "object"},
            metadata=metadata,
        )
        with self.assertRaises(TypeError):
            definition.input_schema["new"] = True  # type: ignore[index]
        with self.assertRaises(TypeError):
            definition.input_schema["properties"]["path"]["type"] = "integer"  # type: ignore[index]
        with self.assertRaises(TypeError):
            definition.metadata["nested"]["safe"] = False  # type: ignore[index]
        with self.assertRaises(TypeError):
            definition.metadata["tags"] += ("write",)  # type: ignore[index]


class TestToolRequest(unittest.TestCase):
    def test_valid_request_defaults(self) -> None:
        request = ToolRequest(tool_name="echo")
        self.assertEqual(request.arguments, {})
        self.assertEqual(request.metadata, {})
        self.assertIsNone(request.invocation_id)

    def test_valid_request_with_all_fields(self) -> None:
        request = ToolRequest(
            tool_name="echo",
            arguments={"text": "hi"},
            metadata={"source": "test"},
            invocation_id="abc-123",
        )
        self.assertEqual(request.arguments, {"text": "hi"})
        self.assertEqual(request.invocation_id, "abc-123")

    def test_rejects_invalid_tool_name(self) -> None:
        for bad_name in ["", "   ", None, 42]:
            with self.subTest(bad_name=bad_name):
                with self.assertRaises(ToolLayerError):
                    ToolRequest(tool_name=bad_name)

    def test_rejects_non_mapping_arguments(self) -> None:
        with self.assertRaises(ToolLayerError):
            ToolRequest(tool_name="echo", arguments="not-a-mapping")  # type: ignore[arg-type]

    def test_rejects_non_string_invocation_id(self) -> None:
        with self.assertRaises(ToolLayerError):
            ToolRequest(tool_name="echo", invocation_id=123)  # type: ignore[arg-type]

    def test_nested_request_data_is_immutable(self) -> None:
        request = ToolRequest(
            tool_name="echo",
            arguments={"payload": {"items": [1, 2]}},
            metadata={"trace": {"source": "test"}},
        )
        with self.assertRaises(TypeError):
            request.arguments["payload"]["items"] = (3,)  # type: ignore[index]
        with self.assertRaises(TypeError):
            request.metadata["trace"]["source"] = "mutated"  # type: ignore[index]


class TestToolResult(unittest.TestCase):
    def test_valid_success_result(self) -> None:
        result = ToolResult(success=True, tool_name="echo", content={"ok": True})
        self.assertIsNone(result.error)

    def test_valid_failure_result(self) -> None:
        error = ToolError(code="not_found", message="File not found")
        result = ToolResult(success=False, tool_name="echo", error=error)
        self.assertIs(result.error, error)

    def test_failure_without_error_is_rejected(self) -> None:
        with self.assertRaises(ToolLayerError):
            ToolResult(success=False, tool_name="echo")

    def test_success_with_error_is_rejected(self) -> None:
        error = ToolError(code="not_found", message="File not found")
        with self.assertRaises(ToolLayerError):
            ToolResult(success=True, tool_name="echo", error=error)

    def test_rejects_invalid_tool_name(self) -> None:
        for bad_name in ["", "   ", None]:
            with self.subTest(bad_name=bad_name):
                with self.assertRaises(ToolLayerError):
                    ToolResult(success=True, tool_name=bad_name)

    def test_nested_result_data_is_immutable(self) -> None:
        result = ToolResult(
            success=True,
            tool_name="echo",
            content={"payload": {"items": [1, 2]}},
            metadata={"trace": {"source": "test"}},
        )
        with self.assertRaises(TypeError):
            result.content["payload"]["items"] = (3,)  # type: ignore[index]
        with self.assertRaises(TypeError):
            result.metadata["trace"]["source"] = "mutated"  # type: ignore[index]


class TestToolError(unittest.TestCase):
    def test_valid_error(self) -> None:
        error = ToolError(code="timeout", message="Operation timed out", details={"seconds": 30})
        self.assertEqual(error.details, {"seconds": 30})

    def test_rejects_invalid_code(self) -> None:
        for bad_code in ["", "   ", None]:
            with self.subTest(bad_code=bad_code):
                with self.assertRaises(ToolLayerError):
                    ToolError(code=bad_code, message="msg")

    def test_nested_error_details_are_immutable(self) -> None:
        error = ToolError(
            code="timeout",
            message="Operation timed out",
            details={"context": {"attempts": [1, 2]}},
        )
        with self.assertRaises(TypeError):
            error.details["context"]["attempts"] = (3,)  # type: ignore[index]


if __name__ == "__main__":
    unittest.main()