"""Proves the pattern holds for a tool with a fundamentally different
shape: one with no filesystem access at all, whose only dependency is
the registry it's about to be registered into.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.tools.bootstrap import build_tool_stack
from src.tools.handlers.list_directory import ListDirectoryHandler
from src.tools.handlers.list_registered_tools import ListRegisteredToolsHandler
from src.tools.handlers.read_file import ReadFileHandler
from src.tools.models import ToolRequest
from src.tools.registry import ToolRegistry


class ThreeToolStackTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)
        (self.base_dir / "notes.txt").write_text("hello workspace")

        # Construction order matters here: the registry must exist
        # before ListRegisteredToolsHandler can be built, so it's
        # created explicitly and threaded through build_tool_stack
        # via registry=, rather than letting the helper create one.
        self.registry = ToolRegistry()
        self.stack = build_tool_stack(
            [
                ReadFileHandler(self.base_dir),
                ListDirectoryHandler(self.base_dir),
                ListRegisteredToolsHandler(self.registry),
            ],
            registry=self.registry,
        )

    def test_all_three_tools_are_registered(self) -> None:
        names = sorted(d.name for d in self.stack.registry.list_definitions())
        self.assertEqual(names, ["list_directory", "list_registered_tools", "read_file"])

    def test_introspection_tool_sees_itself_and_its_siblings_through_the_gate(self) -> None:
        result = self.stack.gate.invoke(ToolRequest(tool_name="list_registered_tools"))

        self.assertTrue(result.success)
        names = sorted(t["name"] for t in result.content["tools"])
        self.assertEqual(names, ["list_directory", "list_registered_tools", "read_file"])

    def test_all_three_are_low_risk_and_need_no_confirmation_provider(self) -> None:
        for request in [
            ToolRequest(tool_name="read_file", arguments={"path": "notes.txt"}),
            ToolRequest(tool_name="list_directory"),
            ToolRequest(tool_name="list_registered_tools"),
        ]:
            with self.subTest(tool_name=request.tool_name):
                result = self.stack.gate.invoke(request)
                self.assertTrue(result.success)

    def test_discover_then_act_workflow(self) -> None:
        # A plausible real usage shape: ask what's available, then use
        # one of the discovered tools.
        catalog = self.stack.gate.invoke(ToolRequest(tool_name="list_registered_tools"))
        self.assertTrue(catalog.success)
        tool_names = {t["name"] for t in catalog.content["tools"]}
        self.assertIn("read_file", tool_names)

        result = self.stack.gate.invoke(
            ToolRequest(tool_name="read_file", arguments={"path": "notes.txt"})
        )
        self.assertTrue(result.success)
        self.assertEqual(result.content["content"], "hello workspace")

    def test_introspection_tool_has_no_filesystem_dependency(self) -> None:
        # Registering it against an *empty* registry (no base_dir
        # anywhere) still works -- unlike the other two tools, it
        # never touches a filesystem.
        empty_registry = ToolRegistry()
        handler = ListRegisteredToolsHandler(empty_registry)
        stack = build_tool_stack([handler], registry=empty_registry)

        result = stack.gate.invoke(ToolRequest(tool_name="list_registered_tools"))

        self.assertTrue(result.success)
        self.assertEqual(result.content["count"], 1)


if __name__ == "__main__":
    unittest.main()
