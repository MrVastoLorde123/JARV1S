from __future__ import annotations

import unittest

from src.tools.handlers.list_registered_tools import ListRegisteredToolsHandler
from src.tools.models import RiskLevel, ToolRequest
from src.tools.registry import ToolRegistry
from src.tools.tests.support import EchoHandler, make_definition


class ListRegisteredToolsHandlerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ToolRegistry()


class TestConstruction(ListRegisteredToolsHandlerTestCase):
    def test_rejects_non_registry(self) -> None:
        with self.assertRaises(TypeError):
            ListRegisteredToolsHandler({})  # type: ignore[arg-type]

    def test_definition_is_low_risk_and_read_only(self) -> None:
        handler = ListRegisteredToolsHandler(self.registry)
        definition = handler.definition()
        self.assertEqual(definition.name, "list_registered_tools")
        self.assertEqual(definition.risk_level, RiskLevel.LOW)
        self.assertFalse(definition.requires_confirmation)
        self.assertTrue(definition.metadata.get("read_only"))


class TestListing(ListRegisteredToolsHandlerTestCase):
    def test_lists_other_registered_tools(self) -> None:
        self.registry.register(EchoHandler(name="alpha"))
        self.registry.register(EchoHandler(name="beta"))
        handler = ListRegisteredToolsHandler(self.registry)

        result = handler.execute(ToolRequest(tool_name="list_registered_tools"))

        self.assertTrue(result.success)
        names = [t["name"] for t in result.content["tools"]]
        self.assertEqual(names, ["alpha", "beta"])
        self.assertEqual(result.content["count"], 2)

    def test_sees_itself_once_registered(self) -> None:
        handler = ListRegisteredToolsHandler(self.registry)
        self.registry.register(handler)

        result = handler.execute(ToolRequest(tool_name="list_registered_tools"))

        names = [t["name"] for t in result.content["tools"]]
        self.assertIn("list_registered_tools", names)
        self.assertEqual(result.content["count"], 1)

    def test_ordering_matches_registry_enumeration(self) -> None:
        self.registry.register(EchoHandler(name="zebra"))
        self.registry.register(EchoHandler(name="apple"))
        handler = ListRegisteredToolsHandler(self.registry)
        self.registry.register(handler)

        result = handler.execute(ToolRequest(tool_name="list_registered_tools"))

        names = [t["name"] for t in result.content["tools"]]
        self.assertEqual(names, [d.name for d in self.registry.list_definitions()])

    def test_empty_registry_before_self_registration(self) -> None:
        handler = ListRegisteredToolsHandler(self.registry)

        result = handler.execute(ToolRequest(tool_name="list_registered_tools"))

        self.assertEqual(result.content["tools"], [])
        self.assertEqual(result.content["count"], 0)

    def test_entry_shape(self) -> None:
        self.registry.register(
            EchoHandler(
                name="alpha",
                risk_level=RiskLevel.HIGH,
                requires_confirmation=True,
                metadata={"author": "team"},
            )
        )
        handler = ListRegisteredToolsHandler(self.registry)

        result = handler.execute(ToolRequest(tool_name="list_registered_tools"))

        entry = result.content["tools"][0]
        self.assertEqual(entry["name"], "alpha")
        self.assertEqual(entry["risk_level"], "high")
        self.assertTrue(entry["requires_confirmation"])
        self.assertNotIn("metadata", entry)


class TestMetadataFlag(ListRegisteredToolsHandlerTestCase):
    def test_metadata_excluded_by_default(self) -> None:
        self.registry.register(EchoHandler(name="alpha", metadata={"secret": "value"}))
        handler = ListRegisteredToolsHandler(self.registry)

        result = handler.execute(ToolRequest(tool_name="list_registered_tools"))

        self.assertNotIn("metadata", result.content["tools"][0])

    def test_metadata_included_when_requested(self) -> None:
        self.registry.register(EchoHandler(name="alpha", metadata={"author": "team"}))
        handler = ListRegisteredToolsHandler(self.registry)

        result = handler.execute(
            ToolRequest(
                tool_name="list_registered_tools", arguments={"include_metadata": True}
            )
        )

        self.assertEqual(result.content["tools"][0]["metadata"], {"author": "team"})

    def test_rejects_non_bool_include_metadata(self) -> None:
        handler = ListRegisteredToolsHandler(self.registry)

        result = handler.execute(
            ToolRequest(
                tool_name="list_registered_tools", arguments={"include_metadata": "yes"}
            )
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error.code, "invalid_argument")


if __name__ == "__main__":
    unittest.main()
