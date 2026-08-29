"""End-to-end validation of the whole stack against one real tool.

    ToolDefinition -> ToolRegistry -> PolicyGate -> Policy ->
    Confirmation -> ToolService -> ToolHandler -> ToolResult

These tests deliberately go through ``PolicyGate.invoke`` (never
``ToolService`` directly) and use real files on a real temporary
filesystem, no mocks -- this is the point of the milestone: prove the
plumbing works end to end before any HIGH/CRITICAL-risk tool is
attempted.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.tools.bootstrap import build_tool_stack
from src.tools.handlers.read_file import ReadFileHandler
from src.tools.models import ToolRequest


class ReadFileEndToEndTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        (self.base_dir / "hello.txt").write_text("hello from the workspace")

        self.stack = build_tool_stack([ReadFileHandler(self.base_dir)])

    def test_low_risk_tool_is_allowed_without_confirmation_provider(self) -> None:
        # DefaultPolicy + no confirmation provider configured at all:
        # a LOW-risk, non-confirmation tool must still succeed, since
        # ALLOW never touches the confirmation step.
        result = self.stack.gate.invoke(
            ToolRequest(tool_name="read_file", arguments={"path": "hello.txt"})
        )

        self.assertTrue(result.success)
        self.assertEqual(result.content["content"], "hello from the workspace")

    def test_tool_is_discoverable_via_registry_enumeration(self) -> None:
        names = [d.name for d in self.stack.registry.list_definitions()]
        self.assertIn("read_file", names)

    def test_missing_file_produces_a_failed_result_not_an_exception(self) -> None:
        result = self.stack.gate.invoke(
            ToolRequest(tool_name="read_file", arguments={"path": "nope.txt"})
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "file_not_found")

    def test_path_traversal_is_blocked_even_when_policy_would_allow(self) -> None:
        # The handler's own safety check fires regardless of policy --
        # policy/confirmation govern *whether the tool runs*, not what
        # a well-behaved handler refuses to do once it does run.
        with tempfile.TemporaryDirectory() as outside:
            secret = Path(outside) / "secret.txt"
            secret.write_text("do not read me")

            result = self.stack.gate.invoke(
                ToolRequest(tool_name="read_file", arguments={"path": "../secret.txt"})
            )

            self.assertFalse(result.success)
            self.assertEqual(result.error.code, "path_outside_base_dir")

    def test_case_insensitive_tool_lookup_through_the_gate(self) -> None:
        result = self.stack.gate.invoke(
            ToolRequest(tool_name="READ_FILE", arguments={"path": "hello.txt"})
        )
        self.assertTrue(result.success)


class BootstrapWiringTestCase(unittest.TestCase):
    """Confirms build_tool_stack wires the same components the earlier
    milestones defined, rather than inventing new ones."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)

    def test_service_can_still_be_used_directly_bypassing_policy(self) -> None:
        (self.base_dir / "f.txt").write_text("x")
        stack = build_tool_stack([ReadFileHandler(self.base_dir)])

        # Direct service use is still possible for callers that have
        # their own reason to bypass the confirmation boundary -- the
        # boundary lives in PolicyGate, not baked into ToolService.
        result = stack.service.invoke(
            ToolRequest(tool_name="read_file", arguments={"path": "f.txt"})
        )
        self.assertTrue(result.success)

    def test_registry_and_service_share_the_same_registration(self) -> None:
        handler = ReadFileHandler(self.base_dir)
        stack = build_tool_stack([handler])

        self.assertTrue(stack.registry.has("read_file"))
        self.assertIs(stack.registry.get("read_file"), handler)

    def test_can_reuse_an_existing_registry(self) -> None:
        from src.tools.registry import ToolRegistry

        registry = ToolRegistry()
        handler = ReadFileHandler(self.base_dir)
        stack = build_tool_stack([handler], registry=registry)

        self.assertIs(stack.registry, registry)
        self.assertTrue(registry.has("read_file"))


if __name__ == "__main__":
    unittest.main()
